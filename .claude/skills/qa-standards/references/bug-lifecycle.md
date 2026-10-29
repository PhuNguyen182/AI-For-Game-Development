# Bug lifecycle

Part of skill `qa-standards`. Read before filing, matching, verifying or closing a bug, and before every QA sign-off.

- Main session is the only writer of `.workflow/bugs.md` and bug records. Agents propose; never invent an ID.
- Check existing bugs first: a match is evidence on that ID; a match on a closed bug reopens it.
- A defect seen out of scope, with evidence but no repro yet → record it `Open`, repro "not yet"; never drop it.
- Status: **Open** → **Fixed** (owner names the ID in `Fixes:`) → **Closed** (only a QA run with evidence) or **Reopened**. **Won't fix** / **Accepted** — only the GD; mirrored into `DEBT.md`. **As designed**, **Duplicate of BUG-####**.
- Settled: Closed, Won't fix, Accepted, As designed, Duplicate. QA sign-off needs zero unsettled. When QA was declined, CP4 lists each `Fixed` bug for the GD to accept unverified (→ Accepted) or send to QA.
- Verifying bugs by ID → one verdict per ID with evidence; unexercised → "unverified".
