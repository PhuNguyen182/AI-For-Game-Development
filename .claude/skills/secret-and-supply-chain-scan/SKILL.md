---
name: secret-and-supply-chain-scan
description: "Secrets (keys, keystores, .env) and supply-chain risk (InitializeOnLoad, DLLs). Use before commit, import or release."
user-invocable: false
---

# Secret and Supply-Chain Scan

- **Not for:** correctness and spec drift (`shared-core-boundary-audit`), repairing an integration (`sdk-platform-engineer`).
- **Not for:** whether a credential entered git history (`git-forensics`); this scan reads the working tree only, so clean here never means clean history.
- **Not for:** key rotation and history rewrite (`cto`), released-build faults (`crash-anr-investigator`).
- **Also run when:** a config, signing or SDK file changes or a value of unknown origin looks sensitive.
- **Precision:** the deliverable; a scanner that flags every hex string trains reviewers to wave findings through.
- **Severity:** per `qa-standards` (impact if shipped).

## Steps
1. **Sweep for credential file types first:**
   - **Extensions:** `.keystore`, `.jks`, `.p12`, `.pfx`, `.pem`, `.mobileprovision`, `.cer`, `.p8` (App Store Connect / APNs key).
   - **Names:** `.env`, `id_rsa`, `.upmconfig.toml`, `.npmrc` with a token, `google-services.json`, `GoogleService-Info.plist`, any JSON with `"type": "service_account"`.
   - **Critical on sight:** a committed keystore, `.p8` or service-account file.
   - **Excluded folders:** never sweep or quote `Library/`, `Temp/`, `Logs/`, `UserSettings/` (`core.md` Security).
2. **Sweep contents for credential shapes, not keywords:**
   - **Keys and prefixes:** `BEGIN PRIVATE KEY`, `BEGIN RSA PRIVATE KEY`, `AKIA`, `AIza`, `ya29.`, `GOCSPX-`, `ghp_`/`github_pat_`, `xoxb-`/`xoxp-`, `sk_live_`.
   - **Tokens:** `Bearer ` + long opaque string, `eyJ` JWT.
   - **Assignments:** `password`/`secret`/`apiKey`/`token`/`connectionString` assigned a literal, not a lookup.
3. **Classify each hit against the public-identifier allowlist:**
   - **Allowlisted:** AdMob App/Ad Unit IDs, IAP product/SKU IDs, bundle IDs, Steam App IDs and the Firebase client config identifiers ship in the app by design.
   - **False positive:** flagging an allowlisted id is a false positive; dismiss it by name in the report.
   - **Firebase client config:** identifiers in `google-services.json` and `GoogleService-Info.plist` (project id, app id, sender id); Firebase documents them as non-secret.
   - **Source:** https://firebase.google.com/docs/projects/api-keys.
   - **Firebase API key:** the key in those files goes to step 4, never dismissed here.
4. **Unresolvable value → `Needs Confirmation`:** naming what would settle it.
   - **Firebase API key:** Clear only when confirmed restricted to Firebase APIs, ideally also to the app package + signing cert or bundle id; unconfirmed → `Needs Confirmation`.
   - **Critical:** a key with the Gemini Developer API or another billable non-Firebase API enabled, or an embedded service-account block.
   - **Why:** guessing Clear risks the leak; guessing Critical trains everyone to ignore you.
5. **Scan imported third-party content for code that runs on import:**
   - **Attributes:** `[InitializeOnLoad]`, `[InitializeOnLoadMethod]`, `[DidReloadScripts]`, `[RuntimeInitializeOnLoadMethod]`.
   - **Build hooks:** `IPreprocessBuildWithReport`, `IPostprocessBuildWithReport`, `[PostProcessBuild]`, `csc.rsp`.
   - **Editor scripts:** any script under an `Editor/` folder in a package the project did not author.
   - **`Packages/manifest.json`:** flag a `scopedRegistries` host the project did not approve and a git dependency not pinned to a commit hash.
   - **Report:** with `path:line`; if already imported, state that it already executed.
6. **Flag source-less binaries:** `.dll`, native plugin, obfuscated script, as unreviewable with their origin; route accept-or-reject, do not decide.
7. **Look for behaviour contradicting stated purpose:** network calls from "local-only" code, reflection into payment or analytics paths.
   - **Also:** strings decoded at runtime, build steps reaching external hosts.
   - **Principle:** `csharp-standards` → `coding-principles.md` POLA.
8. **Report each finding:** with `path:line`, category and severity, then stop.

## Never
- **Fixing a found secret:** removing, moving, rewriting or rotating it; deleting from the working tree leaves it in history and creates a false belief it is gone. Report and route.
- **State changes:** running anything that changes repo state, installs, or sends data; only search and read.
- **Running binaries:** decompiling, executing or "testing" a suspicious binary.
- **Scope excuses:** accepting "it only has read access to a public bucket" as clearing a key; scope is credential config, not the committed string. Report Critical, route rotation to `cto`.
- **Unconfirmed rotation:** rotating a key, revoking a certificate or rewriting history without the GD's explicit confirmation in the current conversation.

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

## Example
- **Ad mediation diff adds an AdMob App ID, Ad Unit ID and `google-services.json`:** NEEDS CONFIRMATION — both AdMob IDs dismissed as allowlisted.
  - **Decided by:** the JSON's API key restriction decides the verdict, stated, not guessed.
