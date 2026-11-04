# <Feature name>

- Status: Open | Closed | Abandoned
- CP: none | CP1 | CP2 | build | review | CP3 | QA | CP4 — next step: <what>
- Session: <session id> · <utc>
- Size: S | M | L · Risk flag: no | yes (<why>)
- Rounds: review 0/3 · QA 0/2 · rework 0/<M 6 | L 8> (only events the hook cannot see: workflow review rounds, CP3 drift, a GD-reported reopen, CP4 fix-gaps rework)
- Profile: <from CLAUDE.md>
- Feature root: <feature root from CLAUDE.md>/<Feature>/
- Branch: feature/<slug> · Base: <branch it was cut from>
- Assemblies: <asmdef names, from the spec>
- Build mode: serial | lanes
- Worktrees: <path · branch · lane task> | none

## Request (verbatim)
> <the GD's words>

## GD decisions
- <date> <decision, accepted risk or waived requirement — with its stated cost>

## Spec
<acceptance criteria, then the spec — or a link to `.workflow/features/<slug>.spec.md` when long>

## Log
| # | Agent | Lane | Changed | Verified | Attempts n/N | Limitations / Needs GD |
|---|---|---|---|---|---|---|

## Tests
| Criterion | Test id | Mode | Owner | Last result |
|---|---|---|---|---|

## Bugs
| ID | Title | Priority |
|---|---|---|

## Known limitations
- <accepted gaps; mirrored into the feature root's DEBT.md at closure>

<!-- Only when the stop rule fires: - Stop rule: <counter or task> root-caused <date> · extra dispatch: unused|used -->
