# Bug lifecycle

Part of skill `qa-standards`. Read before filing, matching, verifying or closing a bug, and before every QA sign-off. Commands, record limits and the state machine: skill `bugs`.

- Main session is the only writer of bug records, through `bugs.py`. Agents propose; never invent an ID. An agent with no shell gets `bugs.py show` output in its brief.
- Check existing bugs first (`bugs.py search`): a match is evidence on that ID; a match on a terminal bug moves it to Reopen; a match on a Backlog bug adds evidence with `update`, as Backlog cannot move to Reopen; a hit on a Duplicate: follow `duplicate_of` and judge the target.
- A defect seen out of scope, with evidence but no repro yet → file it `Request`, repro `not yet`; never drop it.

| Status | Set when |
|---|---|
| **Request** | Filed; an attempt `Failed` or `Blocked` with no fix; the GD takes it out of Backlog |
| **Processing** | Main session dispatches the owner, from Request or Reopen |
| **Resolved** | Owner names the ID in `Fixes:` and `/fix` step 6's checks pass; a verify run returned no `Repro:` line |
| **Review** | Main session dispatches a `Verify:` brief |
| **Complete** | Only an executor's `Repro: BUG-#### gone` from a `Verify:` brief, cited in the note; a written-repro bug: its written steps re-run; qa-lead never sets Complete |
| **Reopen** | `Repro: BUG-#### reproduces`; a new match on a terminal bug |
| **Backlog** | Only the GD |
| **Won't fix**, **Accepted** | Only the GD (`--by GD`); mirrored into the feature root's `DEBT.md`, or `.workflow/DEBT.md` for a bug with no feature |
| **As designed** | QA or main session |
| **Duplicate** | QA or main session, with `--duplicate-of BUG-####` |

- Settled: Complete, Won't fix, Accepted, As designed, Duplicate (hook `round-cap.ps1` never caps a settled bug). QA sign-off needs zero unsettled bugs of that feature. When QA was declined, CP4 lists each `Resolved` bug for the GD to accept unverified (→ Accepted) or send to QA.
- Backlog: only the GD moves a bug in, or out to Request. It counts as settled for QA sign-off with a `Known limitations` line naming the ID. A High or Highest bug in Backlog still blocks `/release`. `round-cap.ps1` never caps it.
- Purge: a terminal bug is deleted more than 90 days after it reached terminal; open and Backlog bugs never are; IDs are never reused. The feature file's `Bugs` table and `DEBT.md` stay as the permanent record.
- Priority: a filed bug carries Low, Medium, High or Highest, never Severity (`qa-standards` → "A finding has" maps it).
- Verifying bugs by ID → one verdict per ID with evidence; unexercised → "unverified".
