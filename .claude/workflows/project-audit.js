export const meta = {
  name: 'project-audit',
  description:
    'Read-only audit of a Unity project: per-module risk and Core-boundary review plus one secret scan, verified and combined',
  whenToUse:
    'Adopting an existing project, before a release, or when the GD asks for a health check; never edits',
  phases: [
    { title: 'Discover', detail: 'list code modules by asmdef' },
    {
      title: 'Audit',
      detail: 'per module: perf/memory/crash risk and Core boundary; whole repo: secrets',
    },
    {
      title: 'Verify',
      detail: 'one skeptic over module findings; secret-scan findings pass through',
    },
  ],
}

/*
 * args: {
 *   root?: '<project path>',
 *   modules?: ['Assets/_Project/Scripts/Combat', ...], // omit to discover
 * }
 * At most MAX_MODULES are audited per run.
 */

// Configuration

const MAX_MODULES = 4
const SECRETS_SCOPE = 'secrets'
const SEVERITY_ORDER = { Critical: 0, High: 1, Medium: 2, Low: 3, Info: 4 }

// Every audit brief opens with this marker line so round-cap.ps1 never counts an audit
// as a failed review round.
const AUDIT = 'Mode: audit\n'

// A skeptic's refutation counts only when its reason cites a file:line.
const CITATION = /[\w./\\-]+:\d+/

const root = args?.root || '.'

// Run state: coverage gaps and the reasons this run counts as incomplete.

const notCovered = []
const reasons = []

// Output schemas

const MODULES_SCHEMA = {
  type: 'object',
  properties: {
    modules: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          path: { type: 'string' },
          asmdef: { type: 'string' },
          csFiles: { type: 'integer' },
        },
        required: ['path', 'asmdef', 'csFiles'],
      },
    },
  },
  required: ['modules'],
}

const FINDINGS_SCHEMA = {
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

const VERDICTS_SCHEMA = {
  type: 'object',
  properties: {
    results: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          index: { type: 'integer' },
          real: { type: 'boolean' },
          reason: { type: 'string' },
        },
        required: ['index', 'real', 'reason'],
      },
    },
  },
  required: ['results'],
}

// Helpers

function at(path) {
  return root === '.' ? path : `${root}/${path}`
}

function withScope(scope) {
  return result => result && { scope, ...result }
}

function markUnverified(finding) {
  return { ...finding, unverified: true }
}

function sortBySeverity(findings) {
  return [...findings].sort((a, b) => SEVERITY_ORDER[a.severity] - SEVERITY_ORDER[b.severity])
}

// A finding is dropped only by an explicit real=false whose reason cites a file:line;
// unanswered indexes stay, unverified. Returns null for a dropped finding.
function judgeFinding(finding, verdict) {
  if (!verdict) {
    return markUnverified(finding)
  }
  if (verdict.real !== false) {
    return finding
  }
  if (CITATION.test(verdict.reason || '')) {
    return null
  }
  return { ...markUnverified(finding), skeptic: verdict.reason }
}

// Prompts

function discoverPrompt() {
  return (
    `List the code modules of the Unity project at ${root}: every folder under Assets/ ` +
    '(excluding Plugins, ThirdParty, Packages and Library) that holds an .asmdef, ' +
    'with its .cs file count. Sort engine-free assemblies (noEngineReferences: true) first, ' +
    'then by .cs count descending. Read-only.'
  )
}

function moduleAuditPrompt(m) {
  return (
    `${AUDIT}Audit ${at(m.path)} (read-only). Lenses: (1) runtime perf, memory and crash/ANR risk ` +
    'in hot paths — the review-code-risks lens; ' +
    '(2) the Shared Core / Client boundary — skill shared-core-boundary-audit. ' +
    'Only findings confirmed in the file, each with path:line and the concrete fix.'
  )
}

function secretScanPrompt() {
  return (
    `${AUDIT}Scan the repository at ${root} for leaked secrets and Unity supply-chain risk ` +
    'with skill secret-and-supply-chain-scan. ' +
    'Scan only files git can see (`git ls-files -co --exclude-standard`); ' +
    'never open Temp/, Library/, Logs/ or UserSettings/ — Editor caches. ' +
    'Never flag allowlisted public ids. Read-only.'
  )
}

function skepticPrompt(findings) {
  const list = findings
    .map((f, i) => `${i}. [${f.severity}] ${f.file}:${f.line || '?'} — ${f.issue}`)
    .join('\n')

  return (
    'You are a skeptic. For each finding, open the cited file and try to REFUTE it: ' +
    'wrong line, handled elsewhere, cold path, allowlisted public id. ' +
    'Default to real=true unless you can cite the file:line that disproves it; ' +
    `when real=false, reason must cite that path:line. Answer every index.\n${list}`
  )
}

// Agents

async function discoverModules() {
  const found = await agent(discoverPrompt(), {
    label: 'discover',
    schema: MODULES_SCHEMA,
    model: 'haiku',
    effort: 'low',
  })

  if (!found) {
    notCovered.push('discover: agent did not return — no module was audited')
    reasons.push('discover: agent did not return')
    return []
  }
  if (found.modules.length === 0) {
    notCovered.push(
      'modules: discover found no .asmdef module — code outside an asmdef was not audited',
    )
  }
  return found.modules
}

function auditModule(m) {
  return agent(moduleAuditPrompt(m), {
    label: `audit:${m.path}`,
    phase: 'Audit',
    agentType: 'code-reviewer',
    // Sonnet below code-reviewer's Opus default: one agent per module fans out wide,
    // and an audit is not a gate (routing.md → Dispatch).
    model: 'sonnet',
    schema: FINDINGS_SCHEMA,
  }).then(withScope(m.path))
}

function auditSecrets() {
  return agent(secretScanPrompt(), {
    label: 'audit:secrets',
    phase: 'Audit',
    agentType: 'security-reviewer',
    schema: FINDINGS_SCHEMA,
  }).then(withScope(SECRETS_SCOPE))
}

function capModules(candidates) {
  if (candidates.length <= MAX_MODULES) {
    return candidates
  }

  const skipped = candidates.slice(MAX_MODULES)
  const skippedPaths = skipped.map(m => m.path).join(', ')
  log(
    `Auditing ${MAX_MODULES} of ${candidates.length} modules; not covered: ${skippedPaths}. ` +
      'Pass args.modules to choose.',
  )
  skipped.forEach(m => {
    notCovered.push(
      `${m.path}: not audited — over the per-run cap of ${MAX_MODULES}; ` +
        'pass args.modules to choose',
    )
  })
  return candidates.slice(0, MAX_MODULES)
}

// Discover

phase('Discover')

const candidates = args?.modules
  ? args.modules.map(path => ({ path, asmdef: '?', csFiles: 0 }))
  : await discoverModules()
const modules = capModules(candidates)

function buildResult(findings, refuted, unverified) {
  if (reasons.length) {
    log(`Incomplete: ${reasons.join('; ')}`)
  }
  return {
    modules: modules.map(m => m.path),
    findings: sortBySeverity(findings),
    refuted,
    unverified,
    notCovered,
    incomplete: reasons.length > 0,
    reasons,
  }
}

// Audit

const audits = await parallel([...modules.map(m => () => auditModule(m)), () => auditSecrets()])

const scopes = [...modules.map(m => m.path), SECRETS_SCOPE]
scopes.forEach((scope, i) => {
  if (!audits[i]) {
    notCovered.push(`${scope}: agent did not return`)
    reasons.push(`${scope}: agent did not return`)
  }
})

const completedAudits = audits.filter(Boolean)
completedAudits.forEach(audit => {
  notCovered.push(`${audit.scope}: ${audit.notCovered}`)
})

const allFindings = completedAudits.flatMap(audit =>
  audit.findings.map(finding => ({ scope: audit.scope, ...finding })),
)
// Secret-scan findings never go to the skeptic: they pass through as reported.
const secretFindings = allFindings.filter(f => f.scope === SECRETS_SCOPE)
const moduleFindings = allFindings.filter(f => f.scope !== SECRETS_SCOPE)

if (moduleFindings.length === 0) {
  return buildResult(secretFindings, 0, 0)
}

// Verify

phase('Verify')

const skeptic = await agent(skepticPrompt(moduleFindings), {
  label: 'verify',
  phase: 'Verify',
  schema: VERDICTS_SCHEMA,
  effort: 'high',
})

if (!skeptic) {
  reasons.push('verify: skeptic did not return — findings kept unverified')
  log('Skeptic did not return — all findings kept unverified')
  return buildResult(
    [...moduleFindings.map(markUnverified), ...secretFindings],
    0,
    moduleFindings.length,
  )
}

const verdictByIndex = new Map((skeptic.results || []).map(r => [r.index, r]))
const keptFindings = moduleFindings
  .map((finding, i) => judgeFinding(finding, verdictByIndex.get(i)))
  .filter(Boolean)
const refutedCount = moduleFindings.length - keptFindings.length
const unverifiedCount = keptFindings.filter(f => f.unverified).length

log(
  `${keptFindings.length} of ${moduleFindings.length} findings survived verification ` +
    `(${unverifiedCount} unverified); ${secretFindings.length} secret-scan findings passed through`,
)

return buildResult([...keptFindings, ...secretFindings], refutedCount, unverifiedCount)
