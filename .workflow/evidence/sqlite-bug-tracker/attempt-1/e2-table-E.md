| Case | Input | Exp exit | pwsh 7 | 5.1 | Hook stderr (or stdout when no stderr), fixture path shortened | DB state after | 7 | 5.1 |
|---|---|---|---|---|---|---|---|---|
| E17 | PowerShell piped stdin form with quoted paths, at cap | 2 | 2 | 2 | Stop rule (routing.md): BUG-0022: fix 2/2 - at the cap: technical-architect root-causes once (run bugs.py stop-rule BUG-0022 fix --extra-dispatch unused), the owner gets ... | BUG-0022 Request fix 2/2 review 0/3 | pass | pass |
| E18 | Edit on .workflow/bugs.jsonl | 0 | 0 | 0 | - | n/a | pass | pass |
| E19 | non-bug shell call with a corrupt ledger | 0 | 0 | 0 | - | n/a | pass | pass |
| E20 | settings.json command string, at cap | 2 | 2 | 2 | Stop rule (routing.md): BUG-0022: fix 2/2 - at the cap: technical-architect root-causes once (run bugs.py stop-rule BUG-0022 fix --extra-dispatch unused), the owner gets ... | BUG-0022 Request fix 2/2 review 0/3 | pass | pass |
| E21 | from an agent worktree, at cap | 2 | 2 | 2 | Stop rule (routing.md): BUG-0022: fix 2/2 - at the cap: technical-architect root-causes once (run bugs.py stop-rule BUG-0022 fix --extra-dispatch unused), the owner gets ... | BUG-0022 Request fix 2/2 review 0/3 | pass | pass |
| EB01 | Bash real 'round BUG-0002 fix +1' leaves 1/2... 1 used | 0 | 0 | 0 | - | BUG-0002 Request fix 1/2 review 0/3 | pass | pass |
| EB02 | Bash real round pushes BUG-0002 to cap 2/2 | 2 | 2 | 2 | Stop rule (routing.md): BUG-0002: fix 2/2 - at the cap: technical-architect root-causes once (run bugs.py stop-rule BUG-0002 fix --extra-dispatch unused), the owner gets ... | BUG-0002 Request fix 2/2 review 0/3 | pass | pass |
| EB03 | Bash real round pushes BUG-0002 past cap 3/2 | 2 | 2 | 2 | Stop rule (routing.md): BUG-0002: fix 3/2 - past the cap: stop and report to the GD. | BUG-0002 Request fix 3/2 review 0/3 | pass | pass |
| EB04 | Bash review at cap 3/3 | 2 | 2 | 2 | Stop rule (routing.md): BUG-0003: review 3/3 - at the cap: technical-architect root-causes once (run bugs.py stop-rule BUG-0003 review --extra-dispatch unused), the owner... | BUG-0003 Request fix 0/2 review 3/3 | pass | pass |
| EB05 | Bash non-bug call naming an id: git log --grep BUG-0002 | 0 | 0 | 0 | - | n/a | pass | pass |
| EB06 | Bash non-bug call: git status | 0 | 0 | 0 | - | n/a | pass | pass |
| EB07 | Bash bugs.py with no id: list --open | 0 | 0 | 0 | - | n/a | pass | pass |
| EB08 | Bash set-status to Complete at the cap: settled | 0 | 0 | 0 | - | BUG-0004 Complete fix 2/2 review 3/3 | pass | pass |
| EB09 | Bash Backlog past cap | 0 | 0 | 0 | - | BUG-0005 Backlog fix 3/2 review 0/3 | pass | pass |
| EB10 | Bash at cap with the Stop rule recorded | 0 | 0 | 0 | - | BUG-0006 Request fix 2/2 review 0/3 | pass | pass |
| EB11 | Bash past cap with the Stop rule recorded | 2 | 2 | 2 | Stop rule (routing.md): BUG-0006: fix 3/2 - past the cap: stop and report to the GD. | BUG-0006 Request fix 3/2 review 0/3 | pass | pass |
| EB12 | Bash Stop rule on fix leaves review at cap warned | 2 | 2 | 2 | Stop rule (routing.md): BUG-0007: review 3/3 - at the cap: technical-architect root-causes once (run bugs.py stop-rule BUG-0007 review --extra-dispatch unused), the owner... | BUG-0007 Request fix 2/2 review 3/3 | pass | pass |
| EB13 | Bash extra-round: was at 2/2, now 2/3 | 0 | 0 | 0 | - | BUG-0008 Request fix 2/3 review 0/3 | pass | pass |
| EB14 | Bash two ids, one at cap | 2 | 2 | 2 | Stop rule (routing.md): BUG-0009: fix 2/2 - at the cap: technical-architect root-causes once (run bugs.py stop-rule BUG-0009 fix --extra-dispatch unused), the owner gets ... | 7: BUG-0009 Request fix 2/2 review 0/3; BUG-0010 Request fix 0/2 review 0/3<br>5.1: BUG-0009 BUG-0010 Request Request fix 2 0/2 2 review 0 0/3 3 | pass | pass |
| EB15 | Bash bugs.py call, no Python | 2 | 2 | 2 | round-cap: the round caps of BUG-0011 could not be read: no Python 3.10+ with SQLite FTS5 found. Install it, then retry (skill bugs). | Python unavailable to the hook | pass | pass |
| EB16 | Bash unknown id | 0 | 0 | 0 | - | n/a | pass | pass |
| EP01 | PowerShell real 'round BUG-0012 fix +1' leaves 1/2... 1 used | 0 | 0 | 0 | - | BUG-0012 Request fix 1/2 review 0/3 | pass | pass |
| EP02 | PowerShell real round pushes BUG-0012 to cap 2/2 | 2 | 2 | 2 | Stop rule (routing.md): BUG-0012: fix 2/2 - at the cap: technical-architect root-causes once (run bugs.py stop-rule BUG-0012 fix --extra-dispatch unused), the owner gets ... | BUG-0012 Request fix 2/2 review 0/3 | pass | pass |
| EP03 | PowerShell real round pushes BUG-0012 past cap 3/2 | 2 | 2 | 2 | Stop rule (routing.md): BUG-0012: fix 3/2 - past the cap: stop and report to the GD. | BUG-0012 Request fix 3/2 review 0/3 | pass | pass |
| EP04 | PowerShell review at cap 3/3 | 2 | 2 | 2 | Stop rule (routing.md): BUG-0013: review 3/3 - at the cap: technical-architect root-causes once (run bugs.py stop-rule BUG-0013 review --extra-dispatch unused), the owner... | BUG-0013 Request fix 0/2 review 3/3 | pass | pass |
| EP05 | PowerShell non-bug call naming an id: git log --grep BUG-0002 | 0 | 0 | 0 | - | n/a | pass | pass |
| EP06 | PowerShell non-bug call: git status | 0 | 0 | 0 | - | n/a | pass | pass |
| EP07 | PowerShell bugs.py with no id: list --open | 0 | 0 | 0 | - | n/a | pass | pass |
| EP08 | PowerShell set-status to Complete at the cap: settled | 0 | 0 | 0 | - | BUG-0014 Complete fix 2/2 review 3/3 | pass | pass |
| EP09 | PowerShell Backlog past cap | 0 | 0 | 0 | - | BUG-0015 Backlog fix 3/2 review 0/3 | pass | pass |
| EP10 | PowerShell at cap with the Stop rule recorded | 0 | 0 | 0 | - | BUG-0016 Request fix 2/2 review 0/3 | pass | pass |
| EP11 | PowerShell past cap with the Stop rule recorded | 2 | 2 | 2 | Stop rule (routing.md): BUG-0016: fix 3/2 - past the cap: stop and report to the GD. | BUG-0016 Request fix 3/2 review 0/3 | pass | pass |
| EP12 | PowerShell Stop rule on fix leaves review at cap warned | 2 | 2 | 2 | Stop rule (routing.md): BUG-0017: review 3/3 - at the cap: technical-architect root-causes once (run bugs.py stop-rule BUG-0017 review --extra-dispatch unused), the owner... | BUG-0017 Request fix 2/2 review 3/3 | pass | pass |
| EP13 | PowerShell extra-round: was at 2/2, now 2/3 | 0 | 0 | 0 | - | BUG-0018 Request fix 2/3 review 0/3 | pass | pass |
| EP14 | PowerShell two ids, one at cap | 2 | 2 | 2 | Stop rule (routing.md): BUG-0019: fix 2/2 - at the cap: technical-architect root-causes once (run bugs.py stop-rule BUG-0019 fix --extra-dispatch unused), the owner gets ... | 7: BUG-0019 Request fix 2/2 review 0/3; BUG-0020 Request fix 0/2 review 0/3<br>5.1: BUG-0019 BUG-0020 Request Request fix 2 0/2 2 review 0 0/3 3 | pass | pass |
| EP15 | PowerShell bugs.py call, no Python | 2 | 2 | 2 | round-cap: the round caps of BUG-0021 could not be read: no Python 3.10+ with SQLite FTS5 found. Install it, then retry (skill bugs). | Python unavailable to the hook | pass | pass |
| EP16 | PowerShell unknown id | 0 | 0 | 0 | - | n/a | pass | pass |
