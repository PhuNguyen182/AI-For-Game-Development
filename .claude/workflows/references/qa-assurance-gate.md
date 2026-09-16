# The Assurance Gate — `qa-pipeline.md` step 4b

> **The last gate, and the only place a score is produced.** Split out of `qa-pipeline.md` under the
> promotion rule in `client/feature-documentation.md`: it runs only at **A3 and above**, and scoring A1/A2
> work is the overhead `effort-allocation.md` forbids.

`assurance-evaluator` runs **last, after every other verdict is in**, and never below A3 — scoring A1/A2 work
is the overhead `effort-allocation.md` forbids, and the agent declines it by contract. It exists for the two
things no other gate can see from inside its own domain: whether **a verification a submission claimed
actually happened**, and whether **the effort spent matched what the tier needed**.

It re-decides nothing. `code-reviewer` owns correctness, `security-reviewer` owns exposure, `qa-lead` owns
coverage — all three verdicts are consumed as given and cited. Dispatch it with every one of them, the
Implementation Notes, the H/M/Q list, the tier, and **attempts used against the budget**; missing the last,
it assumes Attempt 1 and says so, which silently scores an iterated submission as a first pass.

**Where the GD declined review, say so** rather than dispatching without those verdicts and letting the gate
infer. *Given* includes *absent*: it then scores what exists and records the missing gate as an unclosed gap,
which is what it is. An acceptance state reached over a silence is the same defect the gate exists to catch.

| It returns | This pipeline does |
|---|---|
| `FAIL` — a claim no report supports, or a failed integrity gate | Straight back to the named owner at `feature-development.md` **E3**. A false verification claim is not a score to average away, and `effort-allocation.md` puts it beyond any GD waiver |
| `REVISE` | The named dimension is short of its tier target. Close it if the coverage is still runnable; otherwise it joins the gap list for CP4 |
| `CONDITIONAL PASS` | An unwaived gap remains. It goes to CP4 as exactly that — only the GD accepts it |
| `PASS` and above | On to `producer` |
| `Needs-decision` | A gate verdict contradicts its own evidence → `technical-architect`; the work is correct and what it was told to do is wrong → the GD, immediately, per I5 |

**A score is produced here and nowhere else.** No other agent self-scores, and `effort-allocation.md` is
explicit that self-review is not independent verification — which is the whole reason this gate runs after
the authors and the other gates have finished, rather than beside them.
