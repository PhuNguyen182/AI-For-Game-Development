export const meta = {
  name: 'project-audit',
  description: 'Read-only audit of a Unity project: per-module risk and Core-boundary review plus one secret scan, verified and combined',
  whenToUse: 'Adopting an existing project, before a release, or when the GD asks for a health check; never edits',
  phases: [
    { title: 'Discover', detail: 'list code modules by asmdef' },
    { title: 'Audit', detail: 'per module: perf/memory/crash risk and Core boundary; whole repo: secrets' },
    { title: 'Verify', detail: 'one skeptic over module findings; secret-scan findings pass through' },
  ],
}

// args: { root?: '<project path>', modules?: ['Assets/_Project/Scripts/Combat', ...] } — omit modules to discover. At most MAX are audited per run.
const MAX = 4
const root = (args && args.root) || '.'
const at = p => (root === '.' ? p : `${root}/${p}`)

const MODULES = {
  type: 'object',
  properties: {
    modules: {
      type: 'array',
      items: {
        type: 'object',
        properties: { path: { type: 'string' }, asmdef: { type: 'string' }, csFiles: { type: 'integer' } },
        required: ['path', 'asmdef', 'csFiles'],
      },
    },
  },
  required: ['modules'],
}
const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' },
          line: { type: 'integer' },
          severity: { type: 'string', enum: ['Critical', 'High', 'Medium', 'Low', 'Info'] },
          category: { type: 'string' },
          issue: { type: 'string' },
          fix: { type: 'string' },
        },
        required: ['file', 'severity', 'category', 'issue', 'fix'],
      },
    },
    notCovered: { type: 'string' },
  },
  required: ['findings', 'notCovered'],
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

phase('Discover')
const notCovered = []
const reasons = []
let modules = (args && args.modules) ? args.modules.map(p => ({ path: p, asmdef: '?', csFiles: 0 })) : null
if (!modules) {
  const found = await agent(
    `List the code modules of the Unity project at ${root}: every folder under Assets/ (excluding Plugins, ThirdParty, ` +
    'Packages and Library) that holds an .asmdef, with its .cs file count. Sort engine-free assemblies (noEngineReferences: true) first, then by .cs count descending. Read-only.',
    { label: 'discover', schema: MODULES, model: 'haiku', effort: 'low' },
  )
  if (!found) {
    notCovered.push('discover: agent did not return — no module was audited')
    reasons.push('discover: agent did not return')
  } else if (found.modules.length === 0) {
    notCovered.push('modules: discover found no .asmdef module — code outside an asmdef was not audited')
  }
  modules = (found && found.modules) || []
}
if (modules.length > MAX) {
  const cut = modules.slice(MAX)
  log(`Auditing ${MAX} of ${modules.length} modules; not covered: ${cut.map(m => m.path).join(', ')}. Pass args.modules to choose.`)
  cut.forEach(m => notCovered.push(`${m.path}: not audited — over the per-run cap of ${MAX}; pass args.modules to choose`))
  modules = modules.slice(0, MAX)
}

// Every audit brief opens with this marker line so round-cap.ps1 never counts an audit as a failed review round.
const AUDIT = 'Mode: audit\n'
const audits = await parallel([
  // Sonnet below code-reviewer's Opus default: one agent per module fans out wide, and an audit is not a gate (routing.md → Dispatch).
  ...modules.map(m => () => agent(
    `${AUDIT}Audit ${at(m.path)} (read-only). Lenses: (1) runtime perf, memory and crash/ANR risk in hot paths — the ` +
    `review-code-risks lens; (2) the Shared Core / Client boundary — skill shared-core-boundary-audit. ` +
    `Only findings confirmed in the file, each with path:line and the concrete fix.`,
    { label: `audit:${m.path}`, phase: 'Audit', agentType: 'code-reviewer', model: 'sonnet', schema: FINDINGS },
  ).then(r => r && { scope: m.path, ...r })),
  () => agent(
    `${AUDIT}Scan the repository at ${root} for leaked secrets and Unity supply-chain risk with skill secret-and-supply-chain-scan. ` +
    'Scan only files git can see (`git ls-files -co --exclude-standard`); never open Temp/, Library/, Logs/ or UserSettings/ — Editor caches. ' +
    'Never flag allowlisted public ids. Read-only.',
    { label: 'audit:secrets', phase: 'Audit', agentType: 'security-reviewer', schema: FINDINGS },
  ).then(r => r && { scope: 'secrets', ...r }),
])

const scopes = [...modules.map(m => m.path), 'secrets']
scopes.forEach((s, i) => {
  if (!audits[i]) {
    notCovered.push(`${s}: agent did not return`)
    reasons.push(`${s}: agent did not return`)
  }
})
const done = audits.filter(Boolean)
done.forEach(r => notCovered.push(`${r.scope}: ${r.notCovered}`))
const order = { Critical: 0, High: 1, Medium: 2, Low: 3, Info: 4 }
const sort = list => list.sort((a, b) => order[a.severity] - order[b.severity])
const all = done.flatMap(r => r.findings.map(f => ({ scope: r.scope, ...f })))
// Secret-scan findings never go to the skeptic: they pass through as reported.
const secrets = all.filter(f => f.scope === 'secrets')
const sent = all.filter(f => f.scope !== 'secrets')
const result = (findings, refuted, unverified) => {
  if (reasons.length) log(`Incomplete: ${reasons.join('; ')}`)
  return {
    modules: modules.map(m => m.path),
    findings: sort(findings),
    refuted,
    unverified,
    notCovered,
    incomplete: reasons.length > 0,
    reasons,
  }
}
if (sent.length === 0) return result(secrets, 0, 0)

phase('Verify')
const list = sent.map((f, i) => `${i}. [${f.severity}] ${f.file}:${f.line || '?'} — ${f.issue}`).join('\n')
const v = await agent(
  `You are a skeptic. For each finding, open the cited file and try to REFUTE it: wrong line, handled elsewhere, ` +
  `cold path, allowlisted public id. Default to real=true unless you can cite the file:line that disproves it; ` +
  `when real=false, reason must cite that path:line. Answer every index.\n${list}`,
  { label: 'verify', phase: 'Verify', schema: VERDICTS, effort: 'high' },
)
if (!v) {
  reasons.push('verify: skeptic did not return — findings kept unverified')
  log('Skeptic did not return — all findings kept unverified')
  return result([...sent.map(f => ({ ...f, unverified: true })), ...secrets], 0, sent.length)
}
// A finding is dropped only by an explicit real=false whose reason cites a file:line; unanswered indexes stay, unverified.
const CITE = /[\w./\\-]+:\d+/
const byIndex = new Map((v.results || []).map(r => [r.index, r]))
const kept = []
sent.forEach((f, i) => {
  const r = byIndex.get(i)
  if (r && r.real === false && CITE.test(r.reason || '')) return
  if (!r) kept.push({ ...f, unverified: true })
  else if (r.real === false) kept.push({ ...f, unverified: true, skeptic: r.reason })
  else kept.push(f)
})
const refuted = sent.length - kept.length
const unverified = kept.filter(f => f.unverified).length
log(`${kept.length} of ${sent.length} findings survived verification (${unverified} unverified); ${secrets.length} secret-scan findings passed through`)
return result([...kept, ...secrets], refuted, unverified)
