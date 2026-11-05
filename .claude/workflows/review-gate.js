export const meta = {
  name: 'review-gate',
  description:
    'Code + security review of the working tree vs a base in parallel, each finding verified, one merged report',
  whenToUse:
    'A large diff or a feature-complete submission where /review alone would be slow; read-only, never edits',
  phases: [
    { title: 'Scope', detail: 'resolve the working-tree diff, its files and its spec' },
    { title: 'Review', detail: 'code-reviewer and security-reviewer in parallel' },
    {
      title: 'Verify',
      detail:
        'one skeptic tries to refute each code finding with a cited file:line; security findings pass through',
    },
  ],
}

/*
 * args: a plain base ref string, or {
 *   root?: '<repo path>',
 *   base?: 'develop',
 *   spec?: '<spec path>',
 *   feature?: '.workflow/features/<slug>.md',
 *   bug?: 'BUG-0007',
 *   target?: '<path or base>',
 *   audit?: true,
 *   gates?: ['code' | 'security'],
 *   round?: 2,
 *   previous?: { findings: [...], tree: '<sha>' },
 * }
 * The result's `tree` is the next round's previous.tree.
 * The reviewed state is the working tree (staged, unstaged and untracked)
 * against the merge base with `base`.
 */

// Configuration

const SEVERITY_ORDER = { Critical: 0, High: 1, Medium: 2, Low: 3 }

// A finding is refuted only by an explicit real=false whose reason cites a file:line.
const CITATION = /[\w./\\-]+:\d+/

const GATE_DEFINITIONS = [
  {
    key: 'code',
    agentType: 'code-reviewer',
    ask: 'correctness, spec drift, standards, Shared Core duplication',
    passThrough: false,
  },
  {
    key: 'security',
    agentType: 'security-reviewer',
    ask: 'secrets, dangerous files, auto-executing imports, fraud logic',
    // A generic skeptic must not clear a security finding ("unsure → treat as secret"):
    // every one passes through and the security verdict is never relaxed here.
    passThrough: true,
  },
]

const root = args?.root || '.'
const git = root === '.' ? 'git' : `git -C "${root}"`
const base = typeof args === 'string' ? args : args?.base || 'develop'
const feature = args?.feature || null
const bug = args?.bug || null
const target = args?.target || null
const round = args?.round || null
const previous = args?.previous || null
const specSource = args?.spec || feature
const range = `--merge-base ${base}`

// A submission without a spec file is still a submission (a /fix diff, S work):
// audit mode only when asked.
const audit = Boolean(args?.audit)

// args.gates (e.g. ['security']) re-runs only a gate an incomplete result named,
// on the same round and tree.
const requestedGates = Array.isArray(args?.gates) && args.gates.length ? args.gates : null

// Output schemas

const SCOPE_SCHEMA = {
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

const FINDINGS_SCHEMA = {
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

function incompleteResult(reason) {
  return { verdict: 'incomplete', incomplete: true, reason, findings: [] }
}

function describeFinding(finding) {
  return `[${finding.severity}] ${finding.file}:${finding.line || '?'} — ${finding.issue}`
}

function untrackedList(scope) {
  return scope.untracked.join(', ') || 'none'
}

function markUnverified(finding) {
  return { ...finding, unverified: true }
}

// Returns null for a refuted finding; an unanswered or uncited one stays, unverified.
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

// Refuted code findings no longer back the code verdict:
// it may only relax Request changes → Approve.
function relaxVerdict(verdict, keptFindings) {
  const hasBlockingFinding = keptFindings.some(f => f.severity !== 'Low')
  return verdict === 'Request changes' && !hasBlockingFinding ? 'Approve' : verdict
}

function gateResult(gate, review, overrides = {}) {
  return {
    gate: gate.key,
    review,
    kept: [],
    refuted: 0,
    verdict: review?.verdict,
    reasons: [],
    ...overrides,
  }
}

function gateVerdict(result) {
  return result ? result.verdict : 'no result'
}

function gateCoverage(result) {
  return result && result.review ? result.review.notCovered : 'gate did not return'
}

// Prompts

function scopePrompt() {
  const specInstruction = specSource
    ? `read ${specSource} and return its acceptance criteria verbatim`
    : 'the acceptance criteria if a .workflow/features/*.md file covers these files, ' +
      'else exactly "none"'

  return (
    `Resolve the review scope in ${root}. The reviewed state is the working tree, not HEAD. ` +
    `Changed tracked files: \`${git} diff --name-only ${range}\` ` +
    '(merge base to working tree, staged and unstaged). ' +
    `Untracked files: \`${git} ls-files --others --exclude-standard\`. ` +
    'Return both lists (files = tracked + untracked, untracked = the untracked list). ' +
    `Tree: the output of \`${git} stash create\`, or \`${git} rev-parse HEAD\` ` +
    'when that prints nothing; ' +
    'return it as tree. ' +
    'If any git command fails (bad base ref, not a repo), set resolved=false ' +
    'and put the command and its error in error; never return an empty list for a failed command. ' +
    `Spec: ${specInstruction}. Read-only.`
  )
}

// Context lines every reviewer and skeptic gets.
function reviewContext(gate, scope) {
  const lines = []

  if (round) {
    lines.push(`Round: ${round}`)
  }
  if (feature) {
    lines.push(`Feature: ${feature}`)
  } else if (bug) {
    lines.push(`Bug: ${bug}`)
  } else if (target) {
    lines.push(`Target: ${target}`)
  }

  // Mode: workflow — round-cap.ps1 never counts these gates; the main session records the round
  // from the verified verdicts this workflow returns (a skeptic may relax Request changes).
  // The previous tree is the re-review diff base.
  lines.push('Mode: workflow')
  if (scope.tree) {
    lines.push(`Tree: ${scope.tree}`)
  }

  if (audit) {
    lines.push('Mode: audit — no spec or acceptance criteria')
  } else {
    lines.push(`Spec / acceptance criteria:\n${scope.spec}`)
  }

  if (previous) {
    const gateFindings = (previous.findings || []).filter(f => !f.gate || f.gate === gate.key)
    const findingLines = gateFindings.length
      ? gateFindings.map(f => `- ${describeFinding(f)}`).join('\n')
      : '- none'

    lines.push(
      'Re-review: confirm each previous finding is fixed, ' +
        'then review lines changed since the previous tree.',
    )
    if (previous.tree) {
      lines.push(`Previous tree: ${previous.tree}`)
    }
    lines.push(`Previous findings (${gate.key}):\n${findingLines}`)
  }

  return lines.join('\n')
}

function reviewPrompt(gate, scope) {
  return (
    `Review the working tree of repo ${root} against base ${base}: \`${git} diff ${range}\` ` +
    `plus these untracked files read in full: ${untrackedList(scope)}. ` +
    `Lens: ${gate.ask}. Files: ${scope.files.join(', ')}.\n${reviewContext(gate, scope)}\n` +
    'Another gate runs in parallel — do not cover its lens. ' +
    'Report only findings confirmed in the file, each with path:line and the concrete fix; ' +
    'put your Next: recommendation in next.'
  )
}

function skepticPrompt(gate, findings, scope) {
  const list = findings.map((f, i) => `${i}. ${describeFinding(f)}`).join('\n')

  return (
    `You are a skeptic for the ${gate.key} gate (lens: ${gate.ask}). ` +
    `Reviewed state: working tree of repo ${root}, \`${git} diff ${range}\` ` +
    `plus untracked files ${untrackedList(scope)}.\n${reviewContext(gate, scope)}\n` +
    'For each finding below, open the cited file and try to REFUTE it: wrong line, ' +
    'already handled elsewhere, not reachable, allowlisted public id, ' +
    'or not what the spec requires. ' +
    'Default to real=true unless you can cite the file:line that disproves it; ' +
    `when real=false, reason must cite that path:line. Answer every index.\n${list}`
  )
}

// Agents

function runReview(gate, scope) {
  return agent(reviewPrompt(gate, scope), {
    label: `review:${gate.key}`,
    phase: 'Review',
    agentType: gate.agentType,
    schema: FINDINGS_SCHEMA,
  })
}

async function verifyReview(review, gate, scope) {
  if (!review) {
    return gateResult(gate, review, {
      verdict: 'no result',
      reasons: [`${gate.key}: reviewer did not return`],
    })
  }

  const { findings } = review
  if (findings.length === 0) {
    return gateResult(gate, review)
  }
  if (gate.passThrough) {
    return gateResult(gate, review, { kept: findings.map(markUnverified) })
  }

  const skeptic = await agent(skepticPrompt(gate, findings, scope), {
    label: `verify:${gate.key}`,
    phase: 'Verify',
    schema: VERDICTS_SCHEMA,
    effort: 'high',
  })

  // Skeptic dead → the reviewer's verdict stands.
  if (!skeptic) {
    return gateResult(gate, review, {
      kept: findings.map(markUnverified),
      reasons: [`${gate.key}: skeptic did not return — findings kept unverified`],
    })
  }

  const verdictByIndex = new Map((skeptic.results || []).map(r => [r.index, r]))
  const kept = findings
    .map((finding, i) => judgeFinding(finding, verdictByIndex.get(i)))
    .filter(Boolean)

  return gateResult(gate, review, {
    kept,
    refuted: findings.length - kept.length,
    verdict: relaxVerdict(review.verdict, kept),
  })
}

// Scope

phase('Scope')

const scope = await agent(scopePrompt(), {
  label: 'scope',
  schema: SCOPE_SCHEMA,
  model: 'haiku',
  effort: 'low',
})

if (!scope) {
  log('Scope agent did not return — review incomplete.')
  return incompleteResult('scope agent did not return')
}
if (!scope.resolved) {
  const scopeError = scope.error || 'unknown error'
  log(`Scope not resolved: ${scopeError}`)
  return incompleteResult(`scope not resolved: ${scopeError}`)
}
if (scope.files.length === 0) {
  log('Empty diff — nothing to review.')
  return { verdict: 'nothing to review', range, findings: [] }
}

log(`${scope.files.length} files in ${range} (${scope.untracked.length} untracked)`)

const gates = GATE_DEFINITIONS.filter(g => !requestedGates || requestedGates.includes(g.key))

// A mistyped gate name must not read as a clean run of nothing.
const validGateKeys = GATE_DEFINITIONS.map(g => g.key)
const unknownGates = (requestedGates || []).filter(key => !validGateKeys.includes(key))

if (unknownGates.length || gates.length === 0) {
  const named = unknownGates.join(', ') || 'none selected'
  log(`Unknown gate(s) in args.gates: ${named}`)
  return incompleteResult(
    `unknown gate(s) in args.gates: ${named}; valid: ${validGateKeys.join(', ')}`,
  )
}

// Review and Verify

const results = await pipeline(
  gates,
  gate => runReview(gate, scope),
  (review, gate) => verifyReview(review, gate, scope),
)

// Report

const completed = results.filter(Boolean)

const reasons = []
gates.forEach((gate, i) => {
  if (!results[i]) {
    reasons.push(`${gate.key}: gate did not return`)
  }
})
completed.forEach(result => {
  reasons.push(...result.reasons)
})

const refutedCount = completed.reduce((sum, result) => sum + result.refuted, 0)
const unverifiedCount = completed.reduce(
  (sum, result) => sum + result.kept.filter(f => f.unverified).length,
  0,
)

if (refutedCount) {
  log(`${refutedCount} findings refuted with a cited file:line and dropped`)
}
if (unverifiedCount) {
  log(`${unverifiedCount} findings kept unverified`)
}
if (reasons.length) {
  log(`Incomplete: ${reasons.join('; ')}`)
}

const findings = completed
  .flatMap(result => result.kept.map(finding => ({ gate: result.gate, ...finding })))
  .sort((a, b) => SEVERITY_ORDER[a.severity] - SEVERITY_ORDER[b.severity])

const treeSuffix = scope.tree ? `-${scope.tree.slice(0, 12)}` : ''

return {
  range,
  round,
  tree: scope.tree,
  // This round's id: the main session records it (Mode: workflow keeps the hook from counting);
  // for a Target key it is the entry added to .workflow/rounds.json.
  roundId: round ? `round-${round}${treeSuffix}` : null,
  verdicts: Object.fromEntries(gates.map((gate, i) => [gate.key, gateVerdict(results[i])])),
  next: Object.fromEntries(
    completed
      .filter(result => result.review?.next)
      .map(result => [result.gate, result.review.next]),
  ),
  findings,
  refuted: refutedCount,
  unverified: unverifiedCount,
  notCovered: gates.map((gate, i) => `${gate.key}: ${gateCoverage(results[i])}`),
  incomplete: reasons.length > 0,
  reasons,
}
