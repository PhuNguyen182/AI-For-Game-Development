# Comparison: batch T3.1, attempt 1

- **Base:** `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`.
- **Verdict:** fail. Failing skills: `secret-and-supply-chain-scan`, `git-commit`.
- **Everything else in the 16 skills:** every Base criterion kept or moved as listed below. Kept lines are not listed.

## Findings

| Skill | Check | Base text | Current text | Why it fails | Exact fix |
|---|---|---|---|---|---|
| `secret-and-supply-chain-scan` | 1, 2 (step 3) | `:15` "AdMob App/Ad Unit IDs, IAP product/SKU IDs, bundle IDs, Steam App IDs and the Firebase client config identifiers (...) ship in the app by design — ...; flagging one is a false positive. Dismiss it by name in the report." | `:27` holds "ship in the app by design", "false positive" and "Dismiss it by name" for the four non-Firebase ids only. `:28` gives the Firebase identifiers only "are documented as non-secret". | The split narrowed three conditions. Firebase identifiers lost "ship by design", "flagging one is a false positive" and the dismissal, so no disposition remains for them. Step 1 sweeps those same files, and `security-reviewer.md:29` requires each public id dismissed by name. | Replace `:27`-`:28` with three bullets. `- **Allowlisted:** AdMob App/Ad Unit IDs, IAP product/SKU IDs, bundle IDs, Steam App IDs and the Firebase client config identifiers ship in the app by design.` `- **False positive:** flagging an allowlisted id is a false positive; dismiss it by name in the report.` `- **Firebase client config:** identifiers in `google-services.json` and `GoogleService-Info.plist` (project id, app id, sender id); Firebase documents them as non-secret.` Leave `:29`-`:30` as they are. |
| `git-commit` | 1 (step 5) | `:27` "Report quoting it." `it` is the `git log -1 --stat` output of step 4. | `:36` "**Report:** quote the commit." | The referent widened: a sha or a subject now satisfies it, so the required quote of the recorded result is gone. The flow text is exact everywhere else. | `5. **Report:** quote that `git log -1 --stat` output. Never push unless the GD ordered it; when ordered, push without asking.` |

## Cuts

| Skill | Base text | Class |
|---|---|---|
| `git-forensics`, `git-recovery`, `git-safety-anchor`, `git-unity-repo`, `fastlane-mobile-delivery`, `firebase-app-distribution` | "On request only, add `Latent concerns` and `Future remediation`, each with its trigger." | Batch brief "Remove or move" |
| `ci-pipeline-failure-triage`, `build-fault-triage`, `secret-and-supply-chain-scan`, `secret-exposure-response` | "On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its trigger." | Batch brief "Remove or move" |
| `git-recovery`, `jenkins-pipeline-authoring`, `fastlane-mobile-delivery`, `firebase-app-distribution`, `unity-batchmode-cli` | Output `- Known limitations: <...>` | Envelope field; empty, no domain limit |
| `git-forensics` | Output `- Known limitations: <what this trace does not establish>` | Envelope field; restates envelope `Limitations`, no domain limit |
| `git-recovery` | Output `- Verified: <shas and branch positions compared to the stated intent>` | Envelope field; condition stays in step 10 (`:42`) |
| `git-safety-anchor` | Output `- Verified: <what rev-parse / cat-file -e returned>` | Envelope field; condition stays in step 8 (`:49`) |

- **"Common knowledge" cuts:** none, so no automatic finding.
- **Words dropped, no criterion:** `git-recovery` `Not for` "Unity scenes" is now "scenes"; `git-forensics` Never "of a change"; `secret-and-supply-chain-scan` step 4 "e.g.".

## Moves

| Skill | Base | Now |
|---|---|---|
| `git-unity-repo` | Output `Known limitations: <Editor-side validation still owed>` | `SKILL.md:33` step 4 `Editor validation` (the only domain limit in any deleted line) |
| `git-unity-repo` | Step 13 "Ask for the Unity version if unstated" | `SKILL.md:49` step 14 `Missing input`; step 13 keeps the English rule at `:48` |
| `git-unity-repo` | `ignore-surface-and-lfs.md:54` fence, 38 lines | `scripts/unity.gitattributes`, body byte-identical (1,719 bytes, LF); header 4 lines; linked at reference `:54`; listed at `SKILL.md:22` |
| `jenkins-pipeline-authoring` | `declarative-syntax-and-stages.md:7` fence, 22 lines | `scripts/Jenkinsfile`, body byte-identical (942 bytes, LF); header 3 lines; linked at reference `:7`; listed at `SKILL.md:21` |
| `git-forensics` | Step 1 "ask" | `SKILL.md:25` points to step 11, `:54`; no assumption branch; "never pick one" kept |
| `git-safety-anchor` | Step 1 parenthetical lists | `SKILL.md:21`-`:30`; all 10 deleting commands, every radius 2 item and the 4 further radius 3 items present, none changed radius |
| `ci-pipeline-failure-triage` | Table in `Steps`, `:29`-`:40` | `## Classes`, `SKILL.md:36`; rows identical; step 3 points to it at `:25` |
| `ci-pipeline-failure-triage` | "Reading a Jenkins run" prose `:42` | `## Reading a Jenkins run`, `SKILL.md:51`-`:57`; all six facts present |
| `secret-exposure-response` | Table inside step 3, `:17`-`:25` | `## Credential classes`, `SKILL.md:33`; rows identical; step 3 points to it at `:19` |
| `device-test-walkthrough` | Script row and exit-code prose `:20`-`:22` | `## Scripts`, `SKILL.md:18`-`:21` |
| `mem` | Run line `:9` | `## Scripts` `SKILL.md:16`; `<python>` source at `:10` |
| `mem` | `:33` "Query words, file names, symbols, ..." | `SKILL.md:36`; "words" now sits in the title and in `q "<words>"` at `:30`. Not a criterion, so no finding. |
| `code-search` | `:23` "Ask the GD first." | `SKILL.md:24` `Approval` bullet, per inventory |
| `fastlane-mobile-delivery` | Never `:31` "Declining 'it's a private repo'" | `SKILL.md:42`, own bullet in `Never` |

## Resolved tokens

- **Run:** `token-survival.ps1 -Base bdf5c9ec... <16 skills>`: 1,849 tokens, 42 missing, matching the author's count. All 42 explained below.
- **Deleted by rule (24):** `Latent concerns`, `Future remediation`, `Known limitations`. Confirmed by the Output diff above.
- **Bold titles split at a colon (8):** `git-recovery` step 6; `git-unity-repo` steps 7, 11, 13; `jenkins-pipeline-authoring` step 7; `firebase-app-distribution` step 9; `unity-batchmode-cli` step 8; `secret-and-supply-chain-scan` step 8. Content confirmed by reading.
- **Hardcoded paths (2):** `device-test-walkthrough`, `mem`. Now `"${CLAUDE_SKILL_DIR}/scripts/..."`; both scripts exist; hooks keep their own paths.
- **Description compounds (8):** frontmatter equals `HEAD`. Parts confirmed in the folder: `cherry-pick`, `scene`, `prefab`, `agent`, `workspace`, `Library`, `package`, `junit`, `NUnit`, `BuildPlayer`, `BuildReport`, `tap`, `swipe`, `logcat`. `logs` is a plain word.

### Author explanations refuted, no content lost
- **`type` (`device-test-walkthrough`):** the report says it survives in references. References hold 0 hits; the 2 script hits are Python `type=`. The real command is `text` (`SKILL.md:27`, `cli-reference.md:16`), so nothing was lost.
- **Moved code:** the report says the tool found both files in `scripts/`. The tool prints `0 found only in scripts/` for both. "0 lost" stands on the byte comparison, not on the tool.

## "ask" status

- **Run:** `ask-check.ps1` on the 16 skills: 8 hits, 8 allowlisted, 0 open, 0 unused rows. Whole-layer run lists no open hit or unused row in these skills.
- **Fixes:** all 12 instruction hits match their inventory class, including the 6 in references.
- **`git-recovery/SKILL.md|The requester asked for a rewrite`:** used. It matches `SKILL.md:18`, capital kept. Not unused in this run; no action.
- **`secret-exposure-response/SKILL.md|asking the GD to paste`:** edited row is correct. It matches `SKILL.md:47`, inside `## Never`, so it stays a ban and not an instruction.
