---
name: agent-protocol
description: "Return envelope (Status/Summary/Changed/Verified/…), Implementation Note, on-arrival rules for dispatched agents."
user-invocable: false
---

# Agent protocol

## On arrival
- **Brief:** the brief is your whole context.
- **Missing input:** missing input you need → return `Blocked` naming it. Never guess a game rule or a contract.
- **Feature docs:** read the feature's docs per skill `feature-docs`, then only the source those name.
- **Memory hits:** memory hits in the brief → read those paths.
- **Memory and code search:** with a shell, `mem q` (skill `mem`) before touching an area the brief does not cover; search code per skill `code-search`.
- **Attempt budget:** the brief's attempt budget is a ceiling.
- **Retries:** each retry changes the cause, not the wording.
- **Cheap fixes:** apply every cheap, sure fix now.
- **Scope:** stay in scope. Something outside it → `Out of scope`, never fix it.
- **Side effects:** leave none:
  - **Play Mode:** stopped.
  - **Scenes:** no unsaved scene changes.
  - **Editor settings:** changed Editor settings restored (Game view size, Run In Background).
  - **PlayerPrefs:** written PlayerPrefs keys removed.
  - **Background processes:** started background processes stopped.
- **File claims:** a claim about a file's content comes from reading it in this run, never from memory or the brief.
- **Evidence location:** evidence (screenshots, logs, reports) → `.workflow/evidence/<slug>/attempt-<n>/`, never under `Assets/`.
- **Committed evidence:** only `.md` reports and `.png` screenshots there are committed.
- **Raw logs:** raw logs and device dumps stay local (gitignored, refused by pre-commit); a report cites their path or a redacted excerpt.
- **Failed attempts:** a failed attempt's folder stays; never delete evidence.
- **Editor helpers:** a temporary Editor helper is deleted before you return, or listed under `Changed`.

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

- **`Verified` evidence:** `Verified` names commands and results. "Compiles" is not "tested". Unrunnable → say why.
- **`Verified` checklists:** `Verified` reports every `## Checklist` item of your agent file and every item of the `checklist.md` of any skill you followed.
  - **Item form:** `<label>: pass | fail | n/a — why`.
  - **Item failure:** a fail or an unreported item → `Partial`, never `Done`.
- **`Partial` / `Failed` additions:** `Partial` / `Failed` add: best result, last verified state, likely root cause, methods that did not work, safe resume point.
- **Bug verification brief:** a brief with a `Verify: BUG-####` line → add one line per bug: `Repro: BUG-#### reproduces | gone` (the hook counts `reproduces` as a failed fix round).
- **`Repro:` limit:** reproducing a bug, or a regression test that must fail first, never uses the `Repro:` line.
- **Proven impossible:** within the brief (a budget, platform, engine or spec limit no retry can change) → `Failed` plus `Infeasible: <the limit and the evidence>`; stop spending attempts.
- **Design flaw:** a design flaw (the spec itself is wrong) → `Needs-decision`, `Next: gd`.
- **Implementation Note:** the `Changed` … `Fixes` fields are the Implementation Note a reviewer reads; never argue the design in it.
