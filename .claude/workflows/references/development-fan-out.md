# Why the Client Fan-Out Is Serial — `feature-development.md` step 2

> **Read when somebody proposes running the client agents in parallel**, and before adding a fourth agent to
> that fan-out. Split out of `feature-development.md` under the promotion rule in
> `client/feature-documentation.md`: following the pipeline top to bottom needs the *order*, which stays in
> step 2. This file is the *argument*, and it is read once, by whoever doubts it.

This is the settled form of **open decision C** in `workflow-checklist.md`. It was settled, not deferred.

## Three compounding reasons, not one

1. **One Unity Editor, project-wide** — invariant **I3** in `.claude/rules/orchestration.md`. Three of these
   agents hold `mcp__unity-mcp__*` tools pointed at the same process.
2. **Any `.cs` write triggers a domain reload**, which ends the Play Mode session another agent is verifying
   in. Even two agents that never touch the same file interfere through the engine.
3. **Agents cannot coordinate.** Each is isolated and stateless, and there is no orchestrator inside the
   fan-out to arbitrate a collision — the pipeline is the only thing sequencing them, and it does so by
   dispatching one at a time.

## Three ways out, tested and rejected

| Escape | Why it fails |
|---|---|
| A git worktree per agent | It splits the *files*. The single Editor **process** is what is contended, and a worktree does not give a second one |
| "Author now, verify later" | Each of the three is *required* to verify in the Editor before returning: `unity-engineer` *"in Play Mode with a screenshot or console evidence"*, `ui-ux-programmer` *"at more than one aspect ratio"*, `technical-artist` *"with a scene capture and a frame-cost reading"*. Deferring the verification is not a scheduling change — it changes what each agent is contractually allowed to return |
| A second Editor instance | It exists, and it is not free: extra instances need an explicit GD request routed to `build-run-engineer`, which is a different agent and a different authorisation. It is not something the fan-out can arrange for itself |

## What does run concurrently

**Review.** `code-reviewer` and `security-reviewer` hold no Unity tools and write nothing, so both gates run
alongside the fan-out and against each other — which is why step 1 can hold the fan-out for the Core's
verdict without the wait costing Editor time it would otherwise have used.

The backend track also runs independently of the Editor: `netcode-engineer` and
`server-authoritative-engineer` hold no `mcp__` tools either. Step 3 sits after the fan-out in the diagram as
an artifact of drawing a sequence, never as a dependency — it depends on step 1 alone.

## Before adding a fourth agent here

Ask which of the three reasons above it trips. An agent with no `mcp__unity-mcp__*` tool in its frontmatter
trips none of them and does not belong in the serial chain — that is exactly why
`tech-lead-sdk-platform` takes any slot, and why putting it in the order table as row "any" is a statement
about its tools rather than about its seniority.
