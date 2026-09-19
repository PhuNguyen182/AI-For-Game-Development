# The Advisor⇄Critic Loop — `feature-intake.md` steps 3–4

> **The design loop, its trigger, and its 3-round cap.** Split out of `feature-intake.md` under the
> promotion rule in `client/feature-documentation.md`: it runs only at **D4–D5, or U3 at any D**, so most
> features never reach it and no reader needs it to follow the rest of that pipeline.

CP1 sits at the end of this loop and belongs to `feature-intake.md`, which also owns what rejecting it means.

## When it runs

**The direction must be genuinely open — D4–D5, or U3 at any D.** D restates the old trigger:
architecture-level work is where several credible directions exist. U3 is the addition and the more honest of
the two — a consequential unknown the GDD has not decided is *precisely* what a design loop settles, however
trivial the implementation. Nothing else reaches here: a C4 credential edit classifies A5 and gets no round,
because consequence buys verification, not deliberation.

The loop is **GD-in-the-middle**, not agent-to-agent. One round is:

```
advisor → Options → GD picks a direction → critic → Risk Findings → GD decides
```

`advisor` never recommends and `critic` only attacks a direction the GD already leans toward, so the two can
never run in the same round — one exists because no direction exists yet, the other requires one.

## What each dispatch must carry

An agent sees only its brief, and four of the rows below are a `Blocked` this pipeline is the only party able
to prevent. Each is keyed to the agent's own `If absent` behaviour, the same discipline
`references/development-brief.md` applies to the implementation dispatches.

| Dispatch | Attach | If the pipeline omits it |
|---|---|---|
| `advisor`, every round | The architect's `Open design question:` lines tagged `design` and `architecture`, **verbatim and all of them** — never a `technology` line, which is `research-decision.md`'s, and never one line standing in for several | `Blocked` — *"a broad topic yields a survey nobody can act on"*. Sending only the line that looked biggest is how the loop's trigger and its payload come apart: the shape fires the loop, but the question it is handed may be the one that belongs elsewhere |
| `advisor`, every round | **The constraints that would rule an option out** — platform, track, genre, monetization, the **social graph** (who players are matched with: strangers, or only people they already know), and whatever the GD has already fixed | It answers against constraints it guessed and says which. A shortlist filtered for a project that does not exist. The social graph earns its place on this list by evidence: a live run returned *"no matchmaking-with-strangers detail was given, so I flag where a precedent's moderation posture assumed strangers vs. only known teammates"* — it decides every safety, moderation and communication question the loop ever sees |
| `advisor`, rounds 2 and 3 | The options earlier rounds ruled out, and why | It re-proposes what the GD just rejected — it cannot hold them across runs |
| `critic` | **The whole `### <Option name>` block `advisor` returned** for the direction the GD picked — Precedent, Trade-off, Assumes | `Blocked` — *"a one-line summary yields only generic objections"* |
| `critic` | **What the feature is meant to achieve** — the acceptance criteria, or the GDD passage behind it | `Blocked` — *"a risk is only a risk relative to a goal"* |
| `critic` | The constraints already accepted | It attacks against constraints it assumed, and names them |

**The GD picks by name; `critic` needs the body.** Expanding that name back into the block `advisor` returned
is the pipeline's job and nobody else's — the GD says "option B", `critic` cannot read `advisor`'s return,
and neither agent can fetch it. Dispatching the name alone is the most likely `Blocked` in this loop, and it
is one the caller causes.

| Loop rule | Detail |
|---|---|
| **Who ends it** | The GD, by locking a direction. Neither agent can end it; both explicitly disclaim owning the round count. |
| **Hard cap** | **3 rounds.** Reaching round 3 without a lock stops the pipeline and reports non-convergence to the GD — it is not a failure to retry past. |
| **Rejected options** | The pipeline carries the list of options earlier rounds already ruled out into the next `advisor` call. `advisor` cannot remember them. |
| **A clean critic** | `critic` returning `Done` with an empty findings list is a **pass**, not a missing result. Proceed to CP1. |
| **Escalation** | `critic` is a leaf — it reports to the GD and routes to nobody, at every level. |
| **The cap is not the budget** | 3 rounds here is a pipeline counter and is unrelated to `execution-loop.md`'s attempt budget, which bounds one agent's own corrective cycles inside one dispatch. Both are counted, in the same ledger, and neither is spent because it was available. |
| **A Major change resets the round count** | And only a Major. The rounds settled a direction it invalidated (or, on a feature's first CP1, there were no rounds and the reset is 0 to 0) — `change-request.md` owns it, `references/loop-termination.md` records it as the one cap a re-entry clears. The ruled-out options still travel. |

## The limit this loop has, stated rather than hidden

The architect tags **each** of its `Open design question:` lines `design`, `architecture` or `technology`, and
the caller routes per line — a D4/U3 feature routinely carries one of each, so this loop and
`research-decision.md` can both be owed on the same feature. Every `technology` line goes there; **both of
the other two arrive here, and the loop serves them unequally.**

A `design` question is exactly what `advisor` is for: the GD owns the answer, precedent is what they lack,
and refusing to rank protects a decision that is genuinely theirs.

An `architecture` question — how to structure something with what the project already has — reaches the same
loop, and **no agent in it is permitted to say which option fits this codebase.** `advisor` is barred from
ranking, `critic` only attacks whichever one the GD already leans toward, `cto` handles technology rather
than structure, and `technical-architect` — the role that owns module boundaries and has read the code — is
not consulted until step 6, after the direction is locked.

That is a deliberate consequence of the GD being the single decision-maker, not an oversight. It is written
down here so that a GD picking between three architectures knows what they are and are not being given: real
options with honest trade-offs, and no engineering recommendation. **When that is not enough, the answer is
to ask for one explicitly** — a mode-3 dispatch to `technical-architect` before locking CP1 — rather than to
read a ranking into `advisor`'s output that it is contractually forbidden to supply.
