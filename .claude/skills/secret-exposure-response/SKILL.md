---
name: secret-exposure-response
description: "Respond to a secret or player PII found in git history: treat it as compromised, set the rotate-then-verify order, name the owner per credential type, decide purge or not, frame the GD actions. Use when a leak reaches cto."
user-invocable: false
---

# Secret Exposure Response

Not for: whether a match is a real secret (`security-reviewer`), locating it in history (`git-forensics`), running the rewrite (`git-recovery` via `git-expert`), the working-tree scan (`secret-and-supply-chain-scan`), CI credential wiring (`jenkins-pipeline-authoring`).

`cto` decides and plans; the GD acts in vendor consoles; `git-expert` runs any purge. No agent ever holds the old or the new value.

## Steps
1. **Require both inputs before planning** — `security-reviewer` verdict (real, what it grants) and a `git-forensics` sweep (introducing commit, ref scopes covered, pushed or not). Missing → `Blocked`, `Next: security-reviewer` | `git-expert` (Opus, forensics).
2. **Ever pushed, in a CI cache, a fork or another clone → compromised.** No local sweep proves nobody fetched it. Rotation is the fix; a purge is hygiene and never replaces it.
3. **Classify by what it grants and whether it can be invalidated:**
   | Credential | Invalidate by | If it cannot be |
   |---|---|---|
   | API key, token, CI/webhook secret | Revoke or regenerate in the issuing console | — |
   | Cloud service-account JSON | Delete that key id in IAM, issue a new one | — |
   | Android upload key (Play App Signing on) | Upload-key reset in Play Console | — |
   | Android app signing key (no Play App Signing) | Not revocable | Permanent exposure: anyone can sign updates the device accepts → `Needs GD` now |
   | iOS distribution cert / `.p12`, App Store Connect API key | Revoke in Apple Developer / App Store Connect, reissue | — |
   | Payment, IAP receipt or server-authority secret | Rotate, then audit the ledger for the exposure window | — |
   | Player PII | Not rotatable | Purge is mandatory; GDPR breach notice clock (72 h) may run → `Needs GD` now |
4. **Fix the order: revoke/rotate → repoint consumers → verify the old value is rejected → audit the window.** Consumers (CI credential ids, secret store, build configs) are updated by reference, never by pasting the value. Verify means a real call with the old credential failing. Audit window = first push to revocation, read from the vendor's own access logs.
5. **Decide purge on what stays dangerous, not on tidiness.** Rotated and verified dead → no purge by default: a dead key in history grants nothing, and rewriting published history costs every clone a re-clone and breaks open branches. Purge when the value cannot be invalidated, is PII, or a contract or policy demands it — and state that the host may keep objects in pull-request refs or caches until its support removes them.
6. **Name how it entered and the guard that failed** — missing ignore rule, bypassed hook, CI script, copied config. A second occurrence of the same path → a standard via `engineering-standard-adr-authoring`.
7. **Frame every GD action in product terms with a deadline** — what an attacker can do today, what each step costs (downtime, re-clone, store contact), who does it. The history rewrite needs the GD's ask (`core.md` → GD).

## Never
- Print, quote or copy the secret; cite sha, path and line only.
- Ask the GD to paste an old or new value into chat or any file.
- Let a purge, a revert or a deleted file stand in for rotation, or delay rotation until a purge is ready.
- Declare it contained from a local sweep or from the remote no longer showing the branch.

## Output
```
## Secret Exposure Response — <credential type, sha:path:line>
- Exposure: pushed yes/no · scopes reached <remote, forks, CI caches, clones> · first exposed <date>
- Grants: <what an attacker can do with it>
- Invalidatable: yes — <console, action> | no — <permanent consequence>
- Order: 1 revoke/rotate (<owner>) · 2 repoint <consumers> · 3 verify old rejected (<how>) · 4 audit <window, log source>
- Purge: no — <why dead> | yes — <why>; host residue: <PR refs, caches, support request>
- Entry path / failed guard: <...> · Standard: none | ADR via engineering-standard-adr-authoring
- Needs GD: <actions, deadline, cost in product terms>
- Routed to: GD (console) · git-expert (purge, radius 3) | none · sdk-platform-engineer (consumer config)
```
On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Force-push the history clean and we are fine" → declined: the key was pushed four days ago, so it is compromised whatever the history holds. Rotate in the console, repoint the Jenkins credential id, confirm the old key returns 401, read four days of access logs; purge not needed once the key is dead.
