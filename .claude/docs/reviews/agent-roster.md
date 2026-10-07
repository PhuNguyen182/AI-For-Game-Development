# Agent Roster Review — redundancy and packaging

> **Status: Proposed — nothing here has been executed.** A read of all 28 files in `.claude/agents/`, asking
> two questions: is any role redundant, and should any set of roles ship as a separate, optional pack rather
> than inside the template every project copies. Method: read, no agents dispatched, no score owed.

## Why packaging matters at all

Every agent's frontmatter `description` is loaded into every session, whether or not the project can ever use
the agent. An agent that cannot run in a given project still costs context and still competes in routing.
Splitting a role out is worth it when the role is **inactive by construction** in a large share of projects —
not merely when it is rarely used.

The harness resolves agents one level deep, so a pack cannot be a subfolder of `.claude/agents/`. Two viable
mechanisms, undecided: a `packs/<name>/{agents,skills}` folder copied in at install time, or a Claude Code
plugin per pack. Either way, `orchestrator.md` step 0 needs a route for "that pack is not installed".

## 1. Proposed optional packs

| Pack | Agents | Skills that travel with it | Why it should be optional | Workflow files that name it today |
|---|---|---|---|---|
| **Multiplayer** — strongest case | `netcode-engineer`, `server-authoritative-engineer` | `netcode-for-gameobjects`, `netcode-for-entities`, `unity-transport`, `magiconion-rpc-networking`, `netcode-architecture-decision`, `anti-cheat-strategy`, `backend-build-vs-buy` | Both agents return `Blocked` unless the backend track is on — they are dead weight in every client-only project. Installing the pack *is* turning the track on | 9 (netcode) / 6 (server) |
| **Live-ops** | `crash-anr-investigator` | `crash-anr-reporting-gate`, `crash-anr-symbolication`, `crash-anr-fault-domain-triage`, `live-ops-content-pipeline`, `analytics-telemetry-platform` | Works only from released production telemetry (Play Console, Crashlytics, App Store Connect). A pre-launch project has nothing for it to read | 6 |
| **CI/CD, per stack** | `ci-cd-engineer` | `jenkins-pipeline-authoring`, `fastlane-mobile-delivery`, `firebase-app-distribution`, `ci-pipeline-failure-triage` | Hard-wired to Jenkins + Fastlane + Firebase App Distribution. A project on GitHub Actions or Unity Build Automation receives an agent for the wrong stack. Better shipped as one pack per stack | 3 |

Considered and **not** proposed as packs: the strategy roles (`cto`, `advisor`, `critic`, `researcher`,
`rd-engineer`) — `feature-intake.md` and `research-decision.md` depend on them in every project.

## 2. Redundant or mislabeled roles

| Agent | Finding | Proposal |
|---|---|---|
| `producer` | **Redundant.** Read-only, synthesizes without judging, and has no independence value. The orchestrator already holds every report it would summarise, and must hand all of them over anyway — one agent call to re-read what the caller has | Retire it. The status/CP4 report becomes a template the orchestrator fills itself. Named by 11 workflow files today |
| `tech-lead-sdk-platform` | **Mislabeled.** Its own file says it is the only owner of its scope with nobody beneath it — an implementer, not an escalation lead. Its scope (Firebase, ads, IAP, Steamworks, GPGS, StoreKit, store policy) is broad and it names no skills | Rename to `sdk-platform-engineer`. Optionally split later into mobile (ads / IAP / Firebase) and PC (Steamworks) |
| `qa-lead` (sign-off) vs `assurance-evaluator` | **Partial overlap.** At A3+ two Opus calls run back to back over the same reports | **Keep both.** They answer different questions — "is coverage sufficient?" and "did the claimed verification actually happen?" — and merging them makes one agent grade its own coverage verdict |

Checked and found **not** redundant: `advisor` / `critic` / `researcher` / `cto` / `rd-engineer` (clear,
non-overlapping boundaries); `build-run-engineer` / `ci-cd-engineer` / `build-verification-tester` (execute vs
author vs verify); `performance-qa-engineer` (separated from the optimizer on purpose, for independence).

## 3. Side defects found during the read

1. **`netcode-engineer` and `server-authoritative-engineer` do not read the client standards.**
   `rules/standards-index.md` lists both as readers of `coding-principles.md`, `naming-convention.md` and the
   rest, but neither agent's guardrails table names them — and that table is the only mechanism that loads a
   standard. Both write C# without the style and naming standards in context.
2. **Seven agents hold `Bash` but not `PowerShell`**, against `rules/shell-preference.md`: `csharp-engineer`,
   `netcode-engineer`, `server-authoritative-engineer`, `tech-lead-sdk-platform`, `security-reviewer`,
   `build-verification-tester`, `git-expert`. For `git-expert` and `security-reviewer` this may be deliberate;
   for the rest it reads as an omission.

## 4. Proposed order

1. Fix the two side defects — cheap, and nothing else depends on them.
2. Retire `producer`. After the workflow-layer slimming this reduces to "the CP4 report becomes an
   orchestrator template".
3. Rename `tech-lead-sdk-platform`.
4. Split out the Multiplayer pack — the cleanest boundary, and the track switch already exists.
5. Split out Live-ops and CI/CD.
