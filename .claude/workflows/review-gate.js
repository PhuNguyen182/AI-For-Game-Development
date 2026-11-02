export const meta = {
  name: 'review-gate',
  description: 'Code + security review of the working tree vs a base in parallel, each finding verified, one merged report',
  whenToUse: 'A large diff or a feature-complete submission where /review alone would be slow; read-only, never edits',
  phases: [
    { title: 'Scope', detail: 'resolve the working-tree diff, its files and its spec' },
    { title: 'Review', detail: 'code-reviewer and security-reviewer in parallel' },
    { title: 'Verify', detail: 'one skeptic tries to refute each code finding with a cited file:line; security findings pass through' },
  ],
}

// args: { root?: '<repo path>', base?: 'develop', spec?: '<spec path>', feature?: '.workflow/features/<slug>.md',
//         bug?: 'BUG-0007', target?: '<path or base>', audit?: true, gates?: ['code'|'security'], round?: 2, previous?: { findings: [...], tree: '<sha>' } }
//         — or a plain base ref string. The result's `tree` is the next round's previous.tree.
// The reviewed state is the working tree (staged, unstaged and untracked) against the merge base with `base`.
const root = (args && args.root) || '.'
const git = root === '.' ? 'git' : `git -C "${root}"`
const base = typeof args === 'string' ? args : (args && args.base) || 'develop'
const spec = (args && args.spec) || null
const feature = (args && args.feature) || null
const bug = (args && args.bug) || null
const target = (args && args.target) || null
const round = (args && args.round) || null
const previous = (args && args.previous) || null
const range = `--merge-base ${base}`

const SCOPE = {
  type: 'object',
  properties: {
    resolved: { type: 'boolean' },
    error: { type: 'string' },
    files: { type: 'array', items: { type: 'string' } },
    untracked: { type: 'array', items: { type: 'string' } },
    spec: { type: 'string' },
    tree: { type: 'string' },
  },
  required: ['resolved', 'files', 'untracked', 'spec', 'tree'],
}
const FINDINGS = {
  type: 'object',
  properties: {
    verdict: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' },
          line: { type: 'integer' },
          severity: { type: 'string', enum: ['Critical', 'High', 'Medium', 'Low'] },
          category: { type: 'string' },
          issue: { type: 'string' },
          fix: { type: 'string' },
        },
        required: ['file', 'severity', 'issue', 'fix'],
      },
    },
    notCovered: { type: 'string' },
    next: { type: 'string' },
  },
  required: ['verdict', 'findings', 'notCovered'],
}
const VERDICTS = {
  type: 'object',
  properties: {
    results: {
      type: 'array',
      items: {
        type: 'object',
        properties: { index: { type: 'integer' }, real: { type: 'boolean' }, reason: { type: 'string' } },
        required: ['index', 'real', 'reason'],
      },
    },
  },
  required: ['results'],
}

const specSource = spec || feature
phase('Scope')
const scope = await agent(
  `Resolve the review scope in ${root}. The reviewed state is the working tree, not HEAD. ` +
  `Changed tracked files: \`${git} diff --name-only ${range}\` (merge base to working tree, staged and unstaged). ` +
  `Untracked files: \`${git} ls-files --others --exclude-standard\`. Return both lists (files = tracked + untracked, untracked = the untracked list). ` +
  `Tree: the output of \`${git} stash create\`, or \`${git} rev-parse HEAD\` when that prints nothing; return it as tree. ` +
  `If any git command fails (bad base ref, not a repo), set resolved=false and put the command and its error in error; never return an empty list for a failed command. ` +
  `Spec: ${specSource ? `read ${specSource} and return its acceptance criteria verbatim` : 'the acceptance criteria if a .workflow/features/*.md file covers these files, else exactly "none"'}. Read-only.`,
  { label: 'scope', schema: SCOPE, model: 'haiku', effort: 'low' },
)
if (!scope) {
  log('Scope agent did not return — review incomplete.')
  return { verdict: 'incomplete', incomplete: true, reason: 'scope agent did not return', findings: [] }
}
if (!scope.resolved) {
  log(`Scope not resolved: ${scope.error || 'unknown error'}`)
  return { verdict: 'incomplete', incomplete: true, reason: `scope not resolved: ${scope.error || 'unknown error'}`, findings: [] }
}
if (scope.files.length === 0) {
  log('Empty diff — nothing to review.')
  return { verdict: 'nothing to review', range, findings: [] }
}
log(`${scope.files.length} files in ${range} (${scope.untracked.length} untracked)`)

// A submission without a spec file is still a submission (a /fix diff, S work): audit mode only when asked.
const audit = !!(args && args.audit)
// args.gates (e.g. ['security']) re-runs only a gate an incomplete result named, on the same round and tree.
const only = args && Array.isArray(args.gates) && args.gates.length ? args.gates : null
const GATES = [
  { key: 'code', agentType: 'code-reviewer', ask: 'correctness, spec drift, standards, Shared Core duplication' },
  { key: 'security', agentType: 'security-reviewer', ask: 'secrets, dangerous files, auto-executing imports, fraud logic' },
].filter(g => !only || only.includes(g.key))
// A mistyped gate name must not read as a clean run of nothing.
const unknown = only ? only.filter(k => !['code', 'security'].includes(k)) : []
if (unknown.length || GATES.length === 0) {
  log(`Unknown gate(s) in args.gates: ${unknown.join(', ') || 'none selected'}`)
  return { verdict: 'incomplete', incomplete: true, reason: `unknown gate(s) in args.gates: ${unknown.join(', ') || 'none selected'}; valid: code, security`, findings: [] }
}

// Context lines every reviewer and skeptic gets.
const context = g => {
  const lines = []
  if (round) lines.push(`Round: ${round}`)
  if (feature) lines.push(`Feature: ${feature}`)
  else if (bug) lines.push(`Bug: ${bug}`)
  else if (target) lines.push(`Target: ${target}`)
  // Mode: workflow — round-cap.ps1 never counts these gates; the main session records the round from the verified
  // verdicts this workflow returns (a skeptic may relax Request changes). The previous tree is the re-review diff base.
  lines.push('Mode: workflow')
  if (scope.tree) lines.push(`Tree: ${scope.tree}`)
  if (audit) lines.push('Mode: audit — no spec or acceptance criteria')
  else lines.push(`Spec / acceptance criteria:\n${scope.spec}`)
  if (previous) {
    const prev = (previous.findings || []).filter(f => !f.gate || f.gate === g.key)
    lines.push('Re-review: confirm each previous finding is fixed, then review lines changed since the previous tree.')
    if (previous.tree) lines.push(`Previous tree: ${previous.tree}`)
    lines.push(`Previous findings (${g.key}):\n${prev.length ? prev.map(f => `- [${f.severity}] ${f.file}:${f.line || '?'} — ${f.issue}`).join('\n') : '- none'}`)
  }
  return lines.join('\n')
}

// A finding is refuted only by an explicit real=false whose reason cites a file:line.
const CITE = /[\w./\\-]+:\d+/
const refuted = r => r && r.real === false && CITE.test(r.reason || '')

// Refuted code findings no longer back the code verdict: it may only relax Request changes → Approve.
// Skeptic dead → the reviewer's verdict stands. The security verdict is never relaxed here.
const verdictAfterVerify = (gate, verdict, kept, verified) => {
  if (!verified || gate !== 'code') return verdict
  return verdict === 'Request changes' && !kept.some(f => f.severity !== 'Low') ? 'Approve' : verdict
}

// A generic skeptic must not clear a security finding ("unsure → treat as secret"): every one passes through.
const passThrough = g => g.key === 'security'

const results = await pipeline(
  GATES,
  g => agent(
    `Review the working tree of repo ${root} against base ${base}: \`${git} diff ${range}\` plus these untracked files read in full: ${scope.untracked.join(', ') || 'none'}. ` +
    `Lens: ${g.ask}. Files: ${scope.files.join(', ')}.\n${context(g)}\n` +
    `Another gate runs in parallel — do not cover its lens. Report only findings confirmed in the file, each with path:line and the concrete fix; put your Next: recommendation in next.`,
    { label: `review:${g.key}`, phase: 'Review', agentType: g.agentType, schema: FINDINGS },
  ),
  (review, g) => {
    if (!review) return { gate: g.key, review, kept: [], refuted: 0, verdict: 'no result', reasons: [`${g.key}: reviewer did not return`] }
    if (review.findings.length === 0) return { gate: g.key, review, kept: [], refuted: 0, verdict: review.verdict, reasons: [] }
    const held = review.findings.map((f, i) => ({ f, i })).filter(() => passThrough(g))
    const sent = review.findings.map((f, i) => ({ f, i })).filter(() => !passThrough(g))
    const unverifiedHeld = held.map(x => ({ ...x.f, unverified: true }))
    if (sent.length === 0) return { gate: g.key, review, kept: unverifiedHeld, refuted: 0, verdict: review.verdict, reasons: [] }
    const list = sent.map(x => `${x.i}. [${x.f.severity}] ${x.f.file}:${x.f.line || '?'} — ${x.f.issue}`).join('\n')
    return agent(
      `You are a skeptic for the ${g.key} gate (lens: ${g.ask}). Reviewed state: working tree of repo ${root}, \`${git} diff ${range}\` plus untracked files ${scope.untracked.join(', ') || 'none'}.\n${context(g)}\n` +
      `For each finding below, open the cited file and try to REFUTE it: wrong line, already handled elsewhere, not reachable, allowlisted public id, or not what the spec requires. ` +
      `Default to real=true unless you can cite the file:line that disproves it; when real=false, reason must cite that path:line. Answer every index.\n${list}`,
      { label: `verify:${g.key}`, phase: 'Verify', schema: VERDICTS, effort: 'high' },
    ).then(v => {
      if (!v) {
        const kept = [...sent.map(x => ({ ...x.f, unverified: true })), ...unverifiedHeld]
        return { gate: g.key, review, kept, refuted: 0, verdict: review.verdict, reasons: [`${g.key}: skeptic did not return — findings kept unverified`] }
      }
      const byIndex = new Map((v.results || []).map(r => [r.index, r]))
      const kept = []
      let dropped = 0
      for (const x of sent) {
        const r = byIndex.get(x.i)
        if (refuted(r)) dropped++
        else if (!r) kept.push({ ...x.f, unverified: true })
        else if (r.real === false) kept.push({ ...x.f, unverified: true, skeptic: r.reason })
        else kept.push(x.f)
      }
      kept.push(...unverifiedHeld)
      return { gate: g.key, review, kept, refuted: dropped, verdict: verdictAfterVerify(g.key, review.verdict, kept, true), reasons: [] }
    })
  },
)

const reasons = []
GATES.forEach((g, i) => { if (!results[i]) reasons.push(`${g.key}: gate did not return`) })
const done = results.filter(Boolean)
done.forEach(r => reasons.push(...r.reasons))
const dropped = done.reduce((n, r) => n + r.refuted, 0)
if (dropped) log(`${dropped} findings refuted with a cited file:line and dropped`)
const unverified = done.reduce((n, r) => n + r.kept.filter(f => f.unverified).length, 0)
if (unverified) log(`${unverified} findings kept unverified`)
if (reasons.length) log(`Incomplete: ${reasons.join('; ')}`)
const order = { Critical: 0, High: 1, Medium: 2, Low: 3 }
const findings = done.flatMap(r => r.kept.map(f => ({ gate: r.gate, ...f })))
  .sort((a, b) => order[a.severity] - order[b.severity])

return {
  range,
  round,
  tree: scope.tree,
  // This round's id: the main session records it (Mode: workflow keeps the hook from counting); for a Target key it
  // is the entry added to .workflow/rounds.json.
  roundId: round ? `round-${round}${scope.tree ? `-${scope.tree.slice(0, 12)}` : ''}` : null,
  verdicts: Object.fromEntries(GATES.map((g, i) => [g.key, results[i] ? results[i].verdict : 'no result'])),
  next: Object.fromEntries(done.filter(r => r.review && r.review.next).map(r => [r.gate, r.review.next])),
  findings,
  refuted: dropped,
  unverified,
  notCovered: GATES.map((g, i) => `${g.key}: ${results[i] && results[i].review ? results[i].review.notCovered : 'gate did not return'}`),
  incomplete: reasons.length > 0,
  reasons,
}
