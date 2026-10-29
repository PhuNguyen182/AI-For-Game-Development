---
name: agent-protocol
description: Return envelope (Status/Summary/Changed/Verified/Attempts/…) and Implementation Note for every dispatched agent; how to read a brief and what to read on arrival.
user-invocable: false
---

# Agent protocol

## On arrival
- The brief is your whole context. Missing input you need → return `Blocked` naming it. Never guess a game rule or a contract.
- Read the feature's docs per skill `feature-docs`, then only the source those name.
- Memory hits in the brief → read those paths. With a shell, `mem q` (skill `mem`) before touching an area the brief does not cover; search code per skill `code-search`.
- The brief's attempt budget is a ceiling. Each retry changes the cause, not the wording. Apply every cheap, sure fix now.
- Stay in scope. Something outside it → `Out of scope`, never fix it.
- Leave no side effects: Play Mode stopped, no unsaved scene changes, changed Editor settings restored (Game view size, Run In Background), written PlayerPrefs keys removed, started background processes stopped.
- A claim about a file's content comes from reading it in this run, never from memory or the brief.
- Evidence (screenshots, logs, reports) → `.workflow/evidence/<slug>/attempt-<n>/`, never under `Assets/`. A failed attempt's folder stays; never delete evidence. A temporary Editor helper is deleted before you return, or listed under `Changed`.

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
