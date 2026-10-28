---
name: agent-protocol
description: The return envelope and Implementation Note every dispatched agent uses, plus how to read a brief and what to read on arrival. Preloaded by every agent.
user-invocable: false
---

# Agent protocol

## On arrival
- The brief is your whole context. Missing input you need → return `Blocked` naming it. Never guess a game rule or a contract.
- Read the feature's docs per skill `feature-docs` (README → INTEGRATION → CONTRACTS), then only the source those name.
- Attempts: the brief's budget is a ceiling. Each retry changes the cause, not the wording. Apply every cheap, sure fix now.
- Stay in scope. Notice something outside it → list it under `Out of scope`, never fix it.
- Leave no side effects: Play Mode stopped, no unsaved scene changes, Editor settings you changed restored (Game view size, Run In Background), PlayerPrefs keys you wrote removed, background processes you started stopped.
- A claim about a file's content comes from reading it in this run — never from memory or the brief.
- Evidence (screenshots, logs, reports) → `.workflow/evidence/<slug>/`, never under `Assets/`. A temporary Editor helper is deleted before you return, or listed under `Changed`.

## Return — always this envelope
```
Status: Done | Partial | Blocked | Needs-decision | Failed
Summary: <1–3 lines>
Changed: <paths, one line each: what it now does> | none
Verified: <what you ran and its result> · Not verified: <what, why>
Attempts: <used>/<budget> — <what the last one improved, past the first>
Assumptions: <every gap you filled> | none
Limitations: <what this does not do> | none
Out of scope: <noticed, left alone, owner agent> | none
Fixes: <bug ids> | none
Needs GD: <config, secret, store-policy or design decision> | none
Next: <agent or step you recommend> | none
```

- `Verified` names commands and results. "Compiles" is not "tested". Unrunnable → say why.
- `Partial` / `Failed` add: best result, last verified state, likely root cause, methods that did not work, safe resume point.
- A design flaw (the spec itself is wrong) → `Needs-decision`, `Next: gd`.
- The `Changed` … `Fixes` fields are the Implementation Note a reviewer reads; never argue the design in it.
