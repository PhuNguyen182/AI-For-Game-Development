# Shared — Security Requirements

Applies to: every agent, in every scope, that writes, edits, generates, reviews, or commits code,
configuration, assets, tests, or documentation in this repository — `Game.Core.*`, `Game.Client.*`,
`Game.Server.*`, CI/CD pipelines, tooling scripts, and Tech Specs alike. Like `language-and-comments.md`,
this file sits above the `.claude/rules/<group>/` folders rather than inside one.

`security-reviewer` and its `secret-and-supply-chain-scan` skill are a **detection** gate, catching whatever
already reached a submission. This file is the **prevention** baseline every submission is expected to
already satisfy before it reaches that gate — a review that finds nothing is the normal outcome of following
this rule while writing, not a lucky pass.

## The rule, stated once

No code, configuration, comment, log statement, test fixture, prompt, or commit produced by any agent here
may contain, expose, transmit, or create a path to expose a real credential, secret, or piece of sensitive
user data — under any circumstance, in any scope, for any reason, including "just for now", "the GD asked
for it directly", or "it's only a test". The one rule with no severity tiers below Critical and no
tier-based exemption — the assurance tier in `task-classification.md` governs process weight and
verification depth elsewhere, never this. The axes actually run the other way: anything this rule covers is
**C4**, which classifies **A5** on its own. A violation is grounds for immediate rejection by whichever gate
catches it, regardless of what else the submission got right.

## What counts as a violation

Non-exhaustive by design — apply the same reasoning (does this expose access, reveal real personal data, or
let untrusted input control behavior it shouldn't?) to a case not listed, rather than treating absence from
this list as permission.

1. **Hardcoded secrets/credentials** — private API keys, private keys, `.keystore`/`.jks`/`.p12`/`.pfx`/
   `.pem`/`.mobileprovision` contents, passwords, auth/session/refresh tokens, `.env` values, service-account
   JSON (an unrestricted `google-services.json` key, `GoogleService-Info.plist` secrets), DB connection
   strings, signing credentials. Reference a credential id, config lookup, or secret-manager entry instead —
   already how `ci-cd-engineer`/`tech-lead-sdk-platform` are scoped; this makes it the baseline for everyone.
2. **Player/user PII** — real name, email, phone, precise location, payment/card data, government ID,
   biometric data, or a raw cross-app tracking device identifier. Never hardcoded, logged, or transmitted
   without the platform's stated consent/compliance path (store policy, GDPR/COPPA) already in place.
3. **Logging exposure** — a secret/token/PII value written to `Debug.Log`, console output, or a file, even
   behind an editor-only gate — a shipped debug build still carries the string. Tightens, doesn't replace,
   the hot-path logging discipline in `client/performance-and-algorithms.md`.
4. **Insecure transport/validation** — plaintext HTTP for auth/payment/personal data; disabling or bypassing
   TLS validation; trusting an unvalidated redirect or client-supplied URL as fixed.
5. **Injection/unsafe execution** — string-concatenated queries or shell commands, unsafe deserialization of
   untrusted input, path traversal from a user-controlled path, `eval`-equivalent dynamic execution of
   untrusted content. Standard OWASP Top 10 discipline, made a hard rule rather than a guideline.
6. **Client-side trust for authoritative outcomes** — gameplay-critical validation (currency, ownership,
   match result, anti-cheat) never depends on a client-alterable value — what `server-authoritative-engineer`
   already encodes architecturally, restated here as a security rule too.
7. **Unreviewed auto-executing or source-less third-party content** — a `.unitypackage`, Asset Store import,
   or vendored DLL with an `[InitializeOnLoad]`/`Editor/`-folder payload, or shipping with no source, is
   never adopted until `security-reviewer` clears it, per `secret-and-supply-chain-scan`.
8. **Swallowed security-relevant failures** — a caught exception around signature verification, token
   validation, or a payment callback is never silently absorbed into a default-allow path. Catch narrowly
   and fail closed, per the Exception handling section of `client/coding-principles.md`.

## The allowlist — the only exceptions

These identifiers ship inside a public client binary and are not secrets; not flagging them is part of this
rule — false-flagging a public identifier trains reviewers to distrust the gate, its own security failure
over time.

| Allowed | Examples |
|---|---|
| Ad SDK identifiers | AdMob App ID, Ad Unit IDs, mediation network app/placement IDs |
| Third-party App/Client IDs meant to be public | Steam App ID, Google Play application ID, Facebook App ID, Firebase project ID, bundle ID/package name |
| Analytics/event identifiers for client embedding | An event token/write key a vendor's own docs state is client-safe — never an account-level API secret |
| IAP identifiers | In-app purchase product IDs / SKUs |
| Test-only credentials | Sandbox/test API keys a vendor explicitly documents as test-only, and dummy data in unit/integration fixtures — never a production credential relabeled "test" |

A value belongs here only when its own vendor documents it as public/client-safe — this project's own
judgment that it "looks harmless" doesn't qualify it. When unsure, treat it as a violation and route to
`security-reviewer` — never guess it clear. Mirrors `security-reviewer`'s own `Needs Confirmation` standard
(`.claude/agents/qa/security-reviewer.md`) and the identical allowlist in `secret-and-supply-chain-scan` —
this file states the same boundary as a rule every writer follows, not only what the reviewer checks after.

## Rules

- Zero tolerance, every scope — `Game.Core.*`, `Game.Client.*`, `Game.Server.*`, CI/CD, tooling, tests,
  docs, commit messages, logs — no exemption anywhere.
- Fail closed on ambiguity: an identifier not confirmed as vendor-documented public data is treated as a
  secret, never guessed clear to avoid a false positive.
- The allowlist table is the complete exception list — nothing outside it is assumed safe by default;
  "it's just a game" or "it's only client-side" is never a reason to skip this rule.
- Writing it correctly the first time is every agent's job; `security-reviewer` and
  `secret-and-supply-chain-scan` catch what slips through, not the primary control.
- A violation already in git history, not only the working tree, is never self-remediated by any
  code-writing agent — route to `cto`, per `security-reviewer`'s own guardrail. Deleting it from the working
  tree alone leaves it in history and creates false confidence it's gone.
- No tier-based exemption — the assurance tier governs process weight and verification depth elsewhere,
  never security requirements. A credential-shaped value is C4 and therefore A5 regardless.
