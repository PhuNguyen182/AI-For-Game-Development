# Feature-Root Documents — `feature-development.md` step 4

> **Which documents a feature owes at completion, and who writes each.** Split out of
> `feature-development.md` under the promotion rule in `client/feature-documentation.md` — the rule this file
> implements. It is read once, after every implementation task in a root has returned.

`.claude/standards/client/feature-documentation.md` owns which documents exist and when each becomes owed; this
file owns only how the dispatch is placed and who receives it.

`feature-documentation.md` floors the full docset — `README.md` plus whichever of `CONTRACTS.md`,
`INTEGRATION.md` and `ARCHITECTURE.md` have fired — at **A4**, and `LEDGER.md`'s `## Decisions` half,
`DEBT.md` and `NOTES.md` at **A3**. `LEDGER.md` itself is already on disk at any tier, because the
orchestrator opened this feature's run state in it; the dispatch adds decisions to it, never a new file. Both floors key to **A**, not D: a feature is worth documenting because getting it wrong is
expensive, which is what C, R and X measure. **A1–A2 owes nothing** and writes nothing.

**Only documents whose trigger has also fired are dispatched.** The floor is necessary, never sufficient, and
an empty `CONTRACTS.md` written to look complete is a review finding rather than a delivery. `LEDGER.md` and
`DEBT.md` are the exception to the timing below — they are appended *in the submission that produced the
decision or the limitation*, never reconstructed at the end.

Everything else is dispatched as its own task **after every implementation task in that root has returned**,
to one named owner:

| Root | Owner |
|---|---|
| The `Game.Core.*` feature root | `csharp-engineer` — the only agent that writes there |
| The Unity `Assets/` feature root | `unity-engineer` when the breakdown names it, else `ui-ux-programmer`, else `technical-artist` |

The brief attaches every envelope returned for that root — one writer holding the whole picture beats several
isolated agents appending to one file, and each root's `README.md` links the other instead of duplicating it.
