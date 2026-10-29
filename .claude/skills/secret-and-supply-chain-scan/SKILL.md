---
name: secret-and-supply-chain-scan
description: "Scan for secrets (keys, keystores, .env, service JSON, tokens) and Unity supply-chain risk (InitializeOnLoad, Editor scripts in packages, source-less DLLs) without flagging public SDK ids. Use before commit, import or release."
user-invocable: false
---

# Secret and Supply-Chain Scan

Not for: correctness and spec drift (`shared-core-boundary-audit`), repairing an integration (`sdk-platform-engineer`), whether a credential entered git history (`git-forensics`; this scan reads the working tree only, so clean here never means clean history), key rotation and history rewrite (`cto`), released-build faults (`crash-anr-investigator`). Run also when a config, signing or SDK file changes or a value of unknown origin looks sensitive.
Precision is the deliverable: a scanner that flags every hex string trains reviewers to wave findings through. Severity per `qa-standards` (impact if shipped).

## Steps
1. **Sweep for credential file types first** — `.keystore`, `.jks`, `.p12`, `.pfx`, `.pem`, `.mobileprovision`, `.cer`, `.p8` (App Store Connect / APNs key), `.env`, `id_rsa`, `.upmconfig.toml`, `.npmrc` with a token, `google-services.json`, `GoogleService-Info.plist`, any JSON with `"type": "service_account"`. A committed keystore, `.p8` or service-account file is Critical on sight. Never sweep or quote `Library/`, `Temp/`, `Logs/`, `UserSettings/` (`core.md` Security).
2. **Sweep contents for credential shapes, not keywords** — `BEGIN PRIVATE KEY`, `BEGIN RSA PRIVATE KEY`, `AKIA`, `AIza`, `ya29.`, `GOCSPX-`, `ghp_`/`github_pat_`, `xoxb-`/`xoxp-`, `sk_live_`, `Bearer ` + long opaque string, `eyJ` JWT, and `password`/`secret`/`apiKey`/`token`/`connectionString` assigned a literal, not a lookup.
3. **Classify each hit against the public-identifier allowlist** — AdMob App/Ad Unit IDs, IAP product/SKU IDs, bundle IDs, Steam App IDs and the Firebase client config identifiers (`google-services.json`, `GoogleService-Info.plist`: project id, app id, sender id; Firebase documents them as non-secret, https://firebase.google.com/docs/projects/api-keys) ship in the app by design — the Firebase API key in those files goes to step 4, never dismissed here; flagging one is a false positive. Dismiss it by name in the report.
4. **Unresolvable value → `Needs Confirmation`** naming what would settle it (e.g. a Firebase API key is Clear only when confirmed restricted to Firebase APIs, ideally also to the app package + signing cert or bundle id; unconfirmed → `Needs Confirmation`; a key with the Gemini Developer API or another billable non-Firebase API enabled, or an embedded service-account block, is Critical). Guessing Clear risks the leak; guessing Critical trains everyone to ignore you.
5. **Scan imported third-party content for code that runs on import** — `[InitializeOnLoad]`, `[InitializeOnLoadMethod]`, `[DidReloadScripts]`, `[RuntimeInitializeOnLoadMethod]`, build hooks (`IPreprocessBuildWithReport`, `IPostprocessBuildWithReport`, `[PostProcessBuild]`), `csc.rsp`, and any script under an `Editor/` folder in a package the project did not author. In `Packages/manifest.json`, flag a `scopedRegistries` host the project did not approve and a git dependency not pinned to a commit hash. Report with `path:line`; if already imported, state that it already executed.
6. **Flag source-less binaries** (`.dll`, native plugin, obfuscated script) as unreviewable with their origin; route accept-or-reject, do not decide.
7. **Look for behaviour contradicting stated purpose** — network calls from "local-only" code, reflection into payment or analytics paths, strings decoded at runtime, build steps reaching external hosts (`csharp-standards` → `coding-principles.md` POLA).
8. **Report each finding with `path:line`, category and severity, then stop.**

## Never
- Remove, move, rewrite or rotate a found secret — deleting from the working tree leaves it in history and creates a false belief it is gone. Report and route.
- Run anything that changes repo state, installs, or sends data; only search and read.
- Decompile, execute or "test" a suspicious binary.
- Accept "it only has read access to a public bucket" as clearing a key — scope is credential config, not the committed string; report Critical, route rotation to `cto`.
- Rotate a key, revoke a certificate or rewrite history without the GD's explicit confirmation in the current conversation.

## Output
```
## Security Scan — CLEAR | BLOCKED | NEEDS CONFIRMATION
- Scope scanned: <paths; fresh submission | standalone audit>
- Credential files: <path, type | none>
- Credential shapes: <path:line, pattern | none>
- Allowlisted dismissed: <what, why public>
- Auto-executing imported code: <path:line, attribute/folder | none>
- Unreviewable binaries: <path, origin | none>
- Behaviour contradicting purpose: <path:line, mismatch | none>
- Findings: <category, severity, path:line each>
- Decision: clear | block | confirm before deciding
- Routed to: <sdk-platform-engineer | cto | none>
```
On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- Ad mediation diff adds an AdMob App ID, Ad Unit ID and `google-services.json` → NEEDS CONFIRMATION: both AdMob IDs dismissed as allowlisted; the JSON's API key restriction decides the verdict, stated, not guessed.
