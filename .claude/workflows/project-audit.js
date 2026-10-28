export const meta = {
  name: 'project-audit',
  description: 'Read-only audit of a Unity project: per-module risk and Core-boundary review plus one secret scan, verified and combined',
  whenToUse: 'Adopting an existing project, before a release, or when the GD asks for a health check; never edits',
  phases: [
    { title: 'Discover', detail: 'list code modules by asmdef' },
    { title: 'Audit', detail: 'per module: perf/memory/crash risk and Core boundary; whole repo: secrets' },
    { title: 'Verify', detail: 'one skeptic over all findings' },
  ],
}

// args: { root?: '<project path>', modules?: ['Assets/Game.Core', ...] } — omit modules to discover. At most MAX are audited per run.
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
let modules = (args && args.modules) ? args.modules.map(p => ({ path: p, asmdef: '?', csFiles: 0 })) : null
if (!modules) {
  const found = await agent(
    `List the code modules of the Unity project at ${root}: every folder under Assets/ (excluding Plugins, ThirdParty, ` +
    'Packages and Library) that holds an .asmdef, with its .cs file count. Sort by Game.Core first, then by .cs count descending. Read-only.',
    { label: 'discover', schema: MODULES, effort: 'low' },
  )
  modules = (found && found.modules) || []
}
if (modules.length > MAX) {
  log(`Auditing ${MAX} of ${modules.length} modules; not covered: ${modules.slice(MAX).map(m => m.path).join(', ')}. Pass args.modules to choose.`)
  modules = modules.slice(0, MAX)
}

const audits = parallel([
  ...modules.map(m => () => agent(
    `Audit ${at(m.path)} (read-only). Lenses: (1) runtime perf, memory and crash/ANR risk in hot paths — the ` +
    `review-code-risks lens; (2) the Game.Core / Game.Client boundary — skill shared-core-boundary-audit. ` +
    `Only findings confirmed in the file, each with path:line and the concrete fix.`,
    { label: `audit:${m.path}`, phase: 'Audit', agentType: 'code-reviewer', schema: FINDINGS },
  ).then(r => r && { scope: m.path, ...r })),
  () => agent(
    `Scan the repository at ${root} for leaked secrets and Unity supply-chain risk with skill secret-and-supply-chain-scan. ` +
    'Scan only files git can see (`git ls-files -co --exclude-standard`); never open Temp/, Library/, Logs/ or UserSettings/ — Editor caches. ' +
    'Never flag allowlisted public ids. Read-only.',
    { label: 'audit:secrets', phase: 'Audit', agentType: 'security-reviewer', schema: FINDINGS },
  ).then(r => r && { scope: 'secrets', ...r }),
])

const done = (await audits).filter(Boolean)
const all = done.flatMap(r => r.findings.map(f => ({ scope: r.scope, ...f })))
if (all.length === 0) return { modules: modules.map(m => m.path), findings: [], notCovered: done.map(r => `${r.scope}: ${r.notCovered}`) }

phase('Verify')
const list = all.map((f, i) => `${i}. [${f.severity}] ${f.file}:${f.line || '?'} — ${f.issue}`).join('\n')
const v = await agent(
  `You are a skeptic. For each finding, open the cited file and try to REFUTE it: wrong line, handled elsewhere, ` +
  `cold path, allowlisted public id. Default to real=false when the file does not show it.\n${list}`,
  { label: 'verify', phase: 'Verify', schema: VERDICTS, effort: 'high' },
)
const real = new Set(((v && v.results) || []).filter(r => r.real).map(r => r.index))
const order = { Critical: 0, High: 1, Medium: 2, Low: 3, Info: 4 }
const kept = all.filter((_, i) => real.has(i)).sort((a, b) => order[a.severity] - order[b.severity])
log(`${kept.length} of ${all.length} findings survived verification`)

return {
  modules: modules.map(m => m.path),
  findings: kept,
  refuted: all.length - kept.length,
  notCovered: done.map(r => `${r.scope}: ${r.notCovered}`),
}
