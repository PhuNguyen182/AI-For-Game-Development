# The Depth Check — `research-decision.md` step 0

> **Picking how far a research run should go, before anything is dispatched.** Split out of
> `research-decision.md` under the promotion rule in `client/feature-documentation.md`: it is a lookup made
> once at entry, and the rest of that pipeline reads only the lane it produced.

Not every technology question is a technology bet. This step reads the question before anything is dispatched
and picks how far the run should go, so a one-package answer costs one round instead of four.

The lane is this pipeline's own classification and is independent of the feature's tier — `task-classification.md`'s
axes applied to the *research question*, where **U** is what it came here to resolve and **R/X** are what
adopting the answer would cost. A D1 feature can carry an Escalate research question, and an A5 feature can
carry a Direct one.

| Lane | Observable at entry | Steps | What comes back |
|---|---|---|---|
| **Direct** | One capability, nothing strategic to commit, nothing to measure | 1 | A named solution pinned to a version, with its licence and caveats |
| **Considered** | Several plausible approaches, or the first-party answer is missing or deprecated; reversible at a known cost | 1 → 4 | A ranked shortlist, and the decision that picked one |
| **Escalate** | Hard to reverse, a paid commitment, or a number nobody can settle by reading | 1 → 2 → 3 → 4 → 5 | A measured decision, and the standard it sets |

Escalate is R2–R3 or C3–C4 restated: hard to reverse, or expensive to get wrong. Both push the *evidence*
required up to E2 or better — a measurement, a primary source, a tool output — which is why the lane ends at
a spike and a decision rather than at a report.

| Rule | Detail |
|---|---|
| **The lane sets the brief, not just the step list** | A Direct brief asks `researcher` to confirm the first-party answer; an Escalate brief asks it to sweep all three source tiers and name the deciding criterion. This is what makes a Direct run come back in one round. |
| **Upward only** | `researcher`'s returned `Assessed:` overrides the entry lane **upward, never downward**. The pipeline guesses from the question; the agent that actually looked is the authority. Downgrading would let a cheap-looking brief dodge `cto`. |
| **Ambiguous starts higher** | When the entry evidence does not clearly fit a lane, start one lane up — the same rule the agents apply to themselves. |
| **Step 1 is never skipped** | Only E6 reaches a candidate without it, and it does so through a Feasibility Report instead. |
