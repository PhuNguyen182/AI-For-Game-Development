# The `Needs Confirmation` Ladder — `review-pipeline.md`

> **Read when `security-reviewer` returns `Needs Confirmation`.** Split out of `review-pipeline.md` under the
> promotion rule in `client/feature-documentation.md`: it fires only on a credential-shaped value the gate
> cannot place, which most submissions never produce.

`security-reviewer` returns this when it cannot tell a real secret from a public identifier, and its own
required-input table names exactly what is missing: **where the value is actually sourced from**. So this is
an input to supply and re-run, never a verdict to escalate, and never a strike.

Ask in this order:

| Ask | When |
|---|---|
| `tech-lead-sdk-platform` | The submission is an SDK or platform integration — it owns the config source and already reports `Config required:` naming which ids and keys come from where |
| The authoring agent | Anything else — it put the value there and can name its source |
| `gd` | Neither can name a documented source. A credential-shaped value with no known origin is theirs to resolve, and only they can say whether a real key exists |

Then re-run the security gate with the answer. **Never resolve it by guessing in either direction** — the
agent refuses to, and so does this pipeline. `security.md` is explicit: a value that cannot be confirmed as
vendor-documented public data is treated as a secret, never guessed clear to avoid a false positive.

## The one bound

Three asks is the ladder's whole length. If `gd` cannot name a source either, the value is treated as a real
secret and the submission goes back as `Request changes` — **that** is a strike, because the finding is now
a confirmed one rather than an open question. A fourth ask has nobody left to ask.

If the value is already in git history rather than only the working tree, it stops being this ladder's
problem: `security-reviewer` returns `Needs-decision`, `Routed to: cto`, and `review-pipeline.md`'s routing
table sends it straight there. Rotation and a history rewrite are radius-3 operations that no code-writing
agent self-remediates.
