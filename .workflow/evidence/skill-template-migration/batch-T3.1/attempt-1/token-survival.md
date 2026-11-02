# Token survival explanations (T3.1 attempt 1)

Run: token-survival.ps1 -Base bdf5c9ec70bf -Skills <16 skills>. Result: 42 missing in 16 skills; every one explained below.

## Deleted by rule (batch brief "Remove or move")
- `Latent concerns`, `Future remediation` (two tokens each): git-forensics, git-recovery, git-safety-anchor, git-unity-repo, fastlane-mobile-delivery, firebase-app-distribution. Lines deleted.
- `Known limitations`, `Latent concerns`, `Future remediation`: ci-pipeline-failure-triage, build-fault-triage, secret-and-supply-chain-scan, secret-exposure-response. The "On request only, add ..." lines deleted.
- A domain-specific limit in git-unity-repo's `Known limitations: <Editor-side validation still owed>` moved into step 4 as an `Editor validation` bullet.

## Step titles split at the colon (content kept in title and body)
- git-recovery step 6: "Search every reflog and `ORIG_HEAD` before declaring a commit gone" is the title; "then `fsck` for objects once written" is the next clause in the body.
- git-unity-repo step 7: Track/Ignore/Already tracked bullets under one title. Step 11: title shortened to "Preview `git clean` with `-xdn`", "get that list confirmed" follows. Step 13 "Ask for the Unity version if unstated" became step 14 `Missing input` (inventory fix, class `Missing input`); step numbers 9 and 10 kept.
- jenkins-pipeline-authoring step 7: title "Collect logs and reports in `post { always }`", "build artifacts only on success" follows after the colon.
- firebase-app-distribution step 9: title "Missing input" (same condition: app id, group alias or credential id missing).
- unity-batchmode-cli step 8: "Log to a file and stdout (`-logFile`)" then "assert on a positive success line".
- secret-and-supply-chain-scan step 8: bold title ends with a colon as the format requires; text unchanged.

## Hardcoded script paths, replaced by the format
- device-test-walkthrough: `python .claude/skills/device-test-walkthrough/scripts/device_playtest.py <command> [args]` is now `python "${CLAUDE_SKILL_DIR}/scripts/device_playtest.py" <command> [args]`; `scripts/device_playtest.py` still exists.
- mem: `<python> -I .claude/skills/mem/scripts/mem.py <cmd>` is now `<python> -I "${CLAUDE_SKILL_DIR}/scripts/mem.py" <cmd>`; hooks keep their own paths (not edited).

## Description symbols (frontmatter unchanged in T3.1; lost in T2)
Compounds whose every part survives in the skill folder (checked per part): rebase/merge/cherry-pick (git-recovery), scene/prefab (git-unity-repo), agent/workspace and Library/package (ci-pipeline-failure-triage), junit/NUnit (jenkins), BuildPipeline.BuildPlayer/BuildReport (unity-batchmode-cli), tap/swipe/type (device-test-walkthrough; `type` survives in references, `tap`/`swipe` in the body). logs/logcat (build-fault-triage): `logcat` kept, `logs` is a plain word (already explained in T2).

## Moved code
- git-unity-repo: LFS fence (38 lines) is `scripts/unity.gitattributes`; jenkins-pipeline-authoring: skeleton fence (22 lines) is `scripts/Jenkinsfile`. Both found by the tool in `scripts/`, 0 tokens lost. Reference prose "as `LightingData.asset` above" changed to "in the sample".
