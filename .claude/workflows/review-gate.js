export const meta = {
  name: 'review-gate',
  description: 'Code + security review of a diff in parallel, each finding verified, one merged report',
  whenToUse: 'A large diff or a feature-complete submission where /review alone would be slow; read-only, never edits',
  phases: [
    { title: 'Scope', detail: 'resolve the diff, its files and its spec' },
    { title: 'Review', detail: 'code-reviewer and security-reviewer in parallel' },
    { title: 'Verify', detail: 'one skeptic per gate tries to refute each finding' },
  ],
}

// args: { base?: 'develop', spec?: '.workflow/features/<slug>.md' } — or a plain diff range string.
const base = typeof args === 'string' ? args : (args && args.base) || 'develop'
const spec = (args && args.spec) || null

const SCOPE = {
  type: 'object',
  properties: {
    range: { type: 'string' },
    files: { type: 'array', items: { type: 'string' } },
    spec: { type: 'string' },
  },
  required: ['range', 'files', 'spec'],
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
          severity: { type: 'string', enum: ['Critical', 'High', 'Medium', 'Low', 'Info'] },
          category: { type: 'string' },
          issue: { type: 'string' },
          fix: { type: 'string' },
        },
        required: ['file', 'severity', 'issue', 'fix'],
      },
    },
    notCovered: { type: 'string' },
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

phase('Scope')
const scope = await agent(
  `Resolve the review scope. Run \`git diff --name-only ${base}...HEAD\` (fall back to \`git diff --name-only ${base}\` if the range is invalid). ` +
  `Return the range used, the changed files, and the spec: ${spec ? `read ${spec} and return its acceptance criteria verbatim` : 'the acceptance criteria if a .workflow/features/*.md file covers these files, else "none — audit"'}. Read-only.`,
  { label: 'scope', schema: SCOPE, effort: 'low' },
)
if (!scope || scope.files.length === 0) {
  log('Empty diff — nothing to review.')
  return { verdict: 'nothing to review', findings: [] }
}
log(`${scope.files.length} files in ${scope.range}`)

const GATES = [
  { key: 'code', agentType: 'code-reviewer', ask: 'correctness, spec drift, standards, Shared Core duplication' },
  { key: 'security', agentType: 'security-reviewer', ask: 'secrets, dangerous files, auto-executing imports, fraud logic' },
]

const results = await pipeline(
  GATES,
  g => agent(
    `Review the diff \`git diff ${scope.range}\` for ${g.ask}. Files: ${scope.files.join(', ')}. ` +
    `Spec / acceptance criteria: ${scope.spec}. Another gate runs in parallel — do not cover its lens. ` +
    `Report only findings confirmed in the file, each with path:line and the concrete fix.`,
    { label: `review:${g.key}`, phase: 'Review', agentType: g.agentType, schema: FINDINGS },
  ),
  (review, g) => {
    if (!review || review.findings.length === 0) return { gate: g.key, review, kept: [] }
    const list = review.findings.map((f, i) => `${i}. [${f.severity}] ${f.file}:${f.line || '?'} — ${f.issue}`).join('\n')
    return agent(
      `You are a skeptic. For each finding below, open the cited file and try to REFUTE it: wrong line, ` +
      `already handled elsewhere, not reachable, allowlisted public id, or not what the spec requires. ` +
      `Default to real=false when the file does not show it.\n${list}`,
      { label: `verify:${g.key}`, phase: 'Verify', schema: VERDICTS, effort: 'high' },
    ).then(v => {
      const real = new Set(((v && v.results) || []).filter(r => r.real).map(r => r.index))
      return { gate: g.key, review, kept: review.findings.filter((_, i) => real.has(i)) }
    })
  },
)

const done = results.filter(Boolean)
const dropped = done.reduce((n, r) => n + ((r.review && r.review.findings.length) || 0) - r.kept.length, 0)
if (dropped) log(`${dropped} findings refuted by verification and dropped`)
const order = { Critical: 0, High: 1, Medium: 2, Low: 3, Info: 4 }
const findings = done.flatMap(r => r.kept.map(f => ({ gate: r.gate, ...f })))
  .sort((a, b) => order[a.severity] - order[b.severity])

return {
  range: scope.range,
  verdicts: Object.fromEntries(done.map(r => [r.gate, r.review ? r.review.verdict : 'no result'])),
  findings,
  refuted: dropped,
  notCovered: done.map(r => `${r.gate}: ${r.review ? r.review.notCovered : 'gate did not return'}`),
}
