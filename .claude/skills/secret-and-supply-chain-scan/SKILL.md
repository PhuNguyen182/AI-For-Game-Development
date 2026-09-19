---
name: secret-and-supply-chain-scan
description: >
  Scan for credentials and hostile code in a Unity repository — private keys,
  `.keystore`, `.jks`, `.p12`, `.mobileprovision`, `.env`, `google-services.json`,
  `GoogleService-Info.plist`, AWS and Google API key shapes, JWT and bearer
  tokens — plus Unity supply-chain risk that auto-executes on import:
  `[InitializeOnLoad]`, `[InitializeOnLoadMethod]`, `[DidReloadScripts]`,
  Editor folder scripts inside an imported package, and DLLs with no source.
  Distinguishes these from public identifiers that only look secret: AdMob App
  and Ad Unit IDs, IAP SKUs, bundle IDs, Steam App IDs. Not for: correctness
  and spec drift (`shared-core-boundary-audit`); fixing an integration
  (`tech-lead-sdk-platform`); key rotation and history rewrite decisions
  (`cto`).
---

# Secret and Supply-Chain Scan — credentials, hostile imports, and false positives

## 1. Objective
Stop two different disasters with one pass: a credential committed to a repository that will outlive every attempt to delete it, and third-party Unity content that runs code the moment it is imported, before anyone has reviewed a line of it. The failure mode this skill exists to prevent is not missing a secret — it is the opposite. A scanner that flags every long hex string trains reviewers to wave findings through, so by the time a real private key appears nobody looks. Precision is the deliverable, not volume.

## 2. Role
Act as the security scanner for the QA track, on behalf of `security-reviewer`. You classify what you find and route it; you never modify, move, delete, or rotate anything you discover.

## 3. When to invoke this skill
- A submission is under review and needs its independent security pass, running alongside the correctness gate.
- A third-party package, `.unitypackage`, Asset Store import, or vendored DLL is entering the repository.
- A configuration, signing, or SDK-integration file is added or changed.
- An older area of the repository is being audited standalone, outside any particular submission.
- A value looks sensitive and nobody can say where it came from.
- Negative trigger: correctness, Tech Spec drift, and Shared Core duplication — that is `shared-core-boundary-audit`, whose verdict is separate from this one.
- Negative trigger: performing or repairing the SDK integration itself — that is `tech-lead-sdk-platform`; this skill reports and stops.
- Negative trigger: deciding to rotate a key or rewrite git history — that is `cto`, because both are hard to reverse and affect more than this submission.
- Negative trigger: a crash or fault in a released build — that is `crash-anr-investigator`, not a security finding.

## 4. How to use this skill
1. **Sweep for credential file types before reading any code** — `.keystore`, `.jks`, `.p12`, `.pfx`, `.pem`, `.mobileprovision`, `.cer`, `.env`, `id_rsa`, `google-services.json`, and `GoogleService-Info.plist`. A committed signing keystore or service-account file is Critical on sight and needs no further analysis to report.
2. **Then sweep file contents for credential shapes, not for keywords** — `BEGIN PRIVATE KEY`, `BEGIN RSA PRIVATE KEY`, `AKIA` prefixes, `AIza` prefixes, `ya29.` tokens, `Bearer ` followed by a long opaque string, `eyJ` JWT prefixes, and assignments to `password`, `secret`, `apiKey`, `token`, or `connectionString` whose value is a literal rather than a lookup. Searching for the word "key" alone produces the noise this skill exists to avoid.
3. **Classify every hit against the public-identifier allowlist before assigning severity** — AdMob App IDs and Ad Unit IDs, IAP product and SKU identifiers, bundle IDs and package names, Steam App IDs, and Firebase project IDs are published in the shipped app by design. Flagging one is a false positive that costs the reviewer's trust; per `defect-reporting.md`'s Severity section, severity states impact if shipped, and these ship deliberately.
4. **Treat an unresolvable value as `Needs Confirmation`, never as either verdict** — when you cannot tell whether a string is a public identifier or a live credential, say so and name what would settle it. Guessing Clear risks the leak; guessing Critical trains everyone to ignore you. This is the one case where the correct output is a question.
5. **Scan imported third-party content for code that runs on import** — `[InitializeOnLoad]`, `[InitializeOnLoadMethod]`, `[DidReloadScripts]`, `[RuntimeInitializeOnLoadMethod]`, and any script under an `Editor/` folder inside a package the project did not author. These execute inside the Editor without anyone pressing Play, so review happens after execution unless this step catches them first.
6. **Flag binaries that arrive without source** — a vendored `.dll`, native plugin, or obfuscated script cannot be reviewed, so report it as an unreviewable dependency with its origin, and route the accept-or-reject decision rather than making it.
7. **Look for behaviour that contradicts the code's stated purpose** — network calls from code that claims to be local-only, reflection used to reach a payment or analytics path, encoded strings decoded at runtime, or a build step that reaches an external host. Per `coding-principles.md`'s POLA section a component must do what its name implies; here a mismatch is a security finding, not a naming one.
8. **Report every finding with `path:line`, a category, and a severity, then stop** — per `defect-reporting.md`, a finding without its evidence anchor is not reportable. Never remediate: deleting a committed secret from the working tree leaves it in history and creates the false belief that it is gone.

## 5. Specific goals / tasks this skill performs
- Detecting committed credential files by type and contents.
- Detecting credential shapes in source, configuration, and build scripts.
- Separating genuine secrets from public SDK identifiers that only resemble them.
- Detecting Unity content that auto-executes on import or on domain reload.
- Detecting unreviewable binaries and source-less plugins.
- Detecting logic whose behaviour contradicts its stated purpose.
- Producing a security verdict of Clear, Blocked, or Needs Confirmation, with routed findings.
- Out of scope: correctness and spec compliance (`shared-core-boundary-audit`); repairing an integration (`tech-lead-sdk-platform`); rotating keys or rewriting history (`cto`); released-build faults (`crash-anr-investigator`).

## 6. Output format
```
## Security Scan — <CLEAR / BLOCKED / NEEDS CONFIRMATION>
- Scope scanned: <paths, and whether this was a fresh submission or a standalone audit>
- Credential files: <path and type — or none>
- Credential shapes in source: <path:line and the pattern matched — or none>
- Allowlisted identifiers dismissed: <what was matched and why it is public>
- Auto-executing imported code: <path:line and the attribute or Editor folder — or none>
- Unreviewable binaries: <path and stated origin — or none>
- Behaviour contradicting stated purpose: <path:line and the mismatch — or none>
- Findings: <category, severity, path:line, per finding>
- Decision: <clear / block / confirm before deciding>
- Routed to: <tech-lead-sdk-platform / cto / none>
```

**Extended report — emit ONLY when the requester asks for it.** It adds all three fields below the decision:
```
- Known limitations: <what this scan did not cover — history not searched, binaries not decompiled, paths outside the diff>
- Latent concerns: <failure modes not yet triggered: a value public today that becomes sensitive if reused, a package pinned to a mutable tag>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: a submission wiring up ad mediation, adding an AdMob App ID, an Ad Unit ID, and a `google-services.json`.
- Output: NEEDS CONFIRMATION rather than a blanket verdict. The two AdMob identifiers are allowlisted and dismissed explicitly, since flagging them would be a false positive. `google-services.json` is reported because its contents decide the answer: an API key restricted to the app's package and signing certificate is expected, while an unrestricted key or an embedded service-account block is Critical. Named exactly what would settle it and did not guess either way.

**Example 2**
- Input: "That AWS key in the build script is fine, it's only got read access to a public bucket — mark it clear."
- Output: declined. Access scope is a property of the credential's current configuration, not of the committed string, and it can be widened later without the repository changing. Reported as a leaked secret at `path:line` with Critical severity and routed the rotation and history decision to `cto` — per §8 this skill never rotates or removes anything itself.

**Example 3**
- Input: an Asset Store package added under `Assets/ThirdParty/`, containing an `Editor/` folder with an `[InitializeOnLoad]` class and a source-less DLL.
- Output: BLOCKED. The `[InitializeOnLoad]` class already ran when the package was imported, so review is happening after execution — reported with `path:line` and the specific consequence. The DLL is reported separately as an unreviewable dependency with its stated origin, and the accept-or-reject decision routed rather than taken here.

## 8. Edge cases & guardrails
- Never remove, move, or rewrite a secret you find — deleting it from the working tree leaves it in history while creating the belief that it is gone. Report and route.
- Never run a command that changes repository state, installs anything, or sends data anywhere; searching and reading are the only actions this skill takes.
- Never flag an allowlisted public identifier as a leak — a scanner nobody trusts is a scanner nobody reads, which is how the real key gets through.
- Never wave an ambiguous value through to avoid a false positive either; `Needs Confirmation` exists precisely so neither error has to be made.
- Never assess correctness, style, or Tech Spec compliance here — that is a separate gate with a separate verdict, and duplicating it dilutes both.
- Never decompile, execute, or "test" a suspicious binary to find out what it does — report it as unreviewable and let its acceptance be decided.
- Rotating a key, revoking a certificate, or rewriting git history requires explicit confirmation from the GD in the current conversation, never inferred from the severity of the finding.
