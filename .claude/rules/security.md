# Shared — Security Requirements

Applies to: every agent, in every scope, that writes, edits, generates, reviews, or commits code,
configuration, assets, tests, or documentation in this repository — `Game.Core.*`, `Game.Client.*`,
`Game.Server.*`, CI/CD pipelines, tooling scripts, and Tech Specs alike. Like `language-and-comments.md`,
this file sits above the `.claude/rules/<group>/` folders rather than inside one.

## Why it exists

`security-reviewer` and its `secret-and-supply-chain-scan` skill are a **detection** gate — they catch
whatever already reached a submission. This file is the **prevention** baseline every submission is expected
to already satisfy before it ever reaches that gate. A security review that finds nothing is the normal
outcome of following this rule while writing, not a lucky pass.

## The rule, stated once

No code, configuration, comment, log statement, test fixture, prompt, or commit produced by any agent in
this project may contain, expose, transmit, or create a path to expose a real credential, secret, or piece
of sensitive user data — under any circumstance, in any scope, for any reason, including "just for now",
"the GD asked for it directly", or "it's only a test". This is the one rule in this project with no severity
tiers below Critical and no tier-based exemption — Technical Architect's Simple/Medium/Complex triage
governs process weight elsewhere in this project (per `feature-documentation.md`), never this. A violation
is grounds for immediate rejection by whichever gate catches it, regardless of what else the submission got
right.

## What counts as a violation

Non-exhaustive by design — apply the same reasoning (does this expose something that grants access, reveals
a real person's data, or lets untrusted input control behaviour it shouldn't?) to a case not listed here,
rather than treating absence from this list as permission.

1. **Hardcoded secrets and credentials** — private API keys, private keys, the contents of
   `.keystore`/`.jks`/`.p12`/`.pfx`/`.pem`/`.mobileprovision` files, passwords, auth/session/refresh tokens,
   `.env` values, service-account JSON (an unrestricted key inside `google-services.json`, secrets inside
   `GoogleService-Info.plist`), database connection strings, signing credentials. Reference a credential id,
   a config lookup, or a secret-manager entry instead of the value itself — this is already how
   `ci-cd-engineer` and `tech-lead-sdk-platform` are scoped; this file makes it the baseline for every agent,
   not only theirs.
2. **Player/user PII** — real name, email, phone number, precise location, payment or card data, government
   ID, biometric data, or a raw device identifier used for cross-app tracking. Never hardcoded, logged, or
   transmitted without the platform's stated consent/compliance path (store policy, GDPR/COPPA where
   applicable) already in place.
3. **Logging exposure** — writing a secret, token, or PII value to `Debug.Log`, console output, or a file,
   even behind an editor-only gate — a debug build that ships still carries the string. This tightens, and
   does not replace, the hot-path logging discipline in `client/performance-and-algorithms.md`.
4. **Insecure transport and validation** — plaintext HTTP for anything carrying auth, payment, or personal
   data; disabling or bypassing TLS certificate validation; trusting an unvalidated redirect or a
   client-supplied URL as if it were fixed.
5. **Injection and unsafe execution** — string-concatenated queries or shell commands, unsafe deserialization
   of untrusted input, path traversal from a user-controlled path, or `eval`-equivalent dynamic execution of
   untrusted content. Standard OWASP Top 10 discipline, made a hard project rule rather than a general
   guideline.
6. **Client-side trust for authoritative outcomes** — gameplay-critical validation (currency, item ownership,
   match result, anti-cheat) must never depend on a value the client can alter. This is what
   `server-authoritative-engineer`'s existence already encodes architecturally; here it is restated as a
   security rule, not only a design pattern.
7. **Unreviewed auto-executing or source-less third-party content** — a `.unitypackage`, Asset Store import,
   or vendored DLL carrying an `[InitializeOnLoad]`/`Editor/`-folder payload, or shipping with no source, is
   never treated as adopted until `security-reviewer` has cleared it, per `secret-and-supply-chain-scan`.
8. **Swallowed security-relevant failures** — a caught exception around signature verification, token
   validation, or a payment callback must never be silently absorbed into a default-allow path. Catch
   narrowly and fail closed, per the Exception handling section of `client/coding-principles.md`.

## The allowlist — the only exceptions, and only when genuinely this

These identifiers are designed to ship inside a public client binary and are not secrets. Recognizing them
and not flagging them is itself part of this rule — false-flagging a public identifier trains reviewers to
stop trusting the gate, which is its own security failure over time.

| Allowed | Examples |
|---|---|
| Ad SDK identifiers | AdMob App ID, Ad Unit IDs, mediation network app/placement IDs |
| Third-party App/Client IDs meant to be public | Steam App ID, Google Play application ID, Facebook App ID, Firebase project ID, the app's bundle ID / package name |
| Analytics/event identifiers meant for client embedding | An event token or write key a vendor's own documentation states is safe client-side (e.g. an SDK write key) — never an account-level API secret |
| IAP identifiers | In-app purchase product IDs / SKUs |
| Test-only credentials | Sandbox or test API keys a vendor explicitly documents as test-only, and dummy data inside unit/integration test fixtures — never a production credential relabeled "test" |

A value only belongs here when its own vendor documents it as public or client-safe — this project's own
judgment that a value "looks harmless" does not qualify it. When unsure whether something is allowlisted or
a real secret, treat it as a violation and route to `security-reviewer` — never guess it clear. This mirrors
`security-reviewer`'s own `Needs Confirmation` standard (`.claude/agents/qa/security-reviewer.md`) and the
identical allowlist inside the `secret-and-supply-chain-scan` skill — this file is that same boundary,
stated as a rule every writer follows while producing code, not only what the reviewer checks afterward.

## Rules

- Zero tolerance, every scope: `Game.Core.*`, `Game.Client.*`, `Game.Server.*`, CI/CD pipelines, tooling,
  tests, documentation, commit messages, and logs are all covered — there is no scope this rule exempts.
- Fail closed on ambiguity: an identifier that cannot be confirmed as vendor-documented public data is
  treated as a secret, never guessed clear to avoid a false positive.
- The allowlist table above is the complete exception list. Nothing outside it is assumed safe by default —
  "it's just a game" or "it's only client-side" is never a reason to skip this rule.
- Writing it correctly the first time is every agent's job. `security-reviewer` and
  `secret-and-supply-chain-scan` exist to catch what slips through, not to be relied on as the primary
  control.
- A violation already in git history, not only the working tree, is never self-remediated by any
  code-writing agent — route it to `cto`, per `security-reviewer`'s own guardrail. Deleting it from the
  working tree alone leaves it in history and creates false confidence that it is gone.
- This rule carries no tier-based exemption — Triage tier governs process weight elsewhere in this project,
  never security requirements.
