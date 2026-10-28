# Core

## Language
- Work in English: code, comments, docs, commits, file names, reasoning. Parse Vietnamese/English/mixed input as-is.
- Reply to the GD in Vietnamese.

## GD
- Ask only via `AskUserQuestion`: 2–4 options, recommended first, labelled "(Khuyến nghị)". Never ask in chat prose.
- State the route picked in one line. Never ask which route, size or severity.
- GD rules: state the cost, then do what they asked. Exception: security below — the GD may drop the work, never order a violation.
- A GD-stated budget, platform or constraint is a hard requirement.
- Ask before: push, platform build, store submission, release tag, second Editor, history rewrite, paid service.
- Tell at once: a design flaw; a return needing config, a secret or a store-policy decision; a stop (`routing.md`).
- Only the GD accepts a gap or waives a requirement. Write every accepted gap into the feature file's known limitations.

## Truth
- Never claim a test, build, measurement or review that did not run. Unavailable → say so.
- Reading code is review; running it is verification. An author never signs off their own work.
- No silent scope cut: never drop a requirement, call partial work done, or give advice instead of doing the work.
- Before retrying a state-changing action (push, build, Editor mutation, device op), inspect real state — a failure is not proof of no side effect.

## Security — zero tolerance, every file and scope
- Never write, log, commit or send a real secret (API/private keys, tokens, passwords, keystore/jks/p12/pem/mobileprovision, `.env`, service-account JSON) or player PII. Reference a credential id or secret store.
- A public identifier is allowed only when its vendor documents it as client-safe (AdMob IDs, IAP SKUs, bundle id, Steam App ID). Unsure → treat as secret; run `secret-and-supply-chain-scan`.
- No plaintext HTTP for auth/payment/PII, no TLS bypass, no string-built queries or shell commands, no unsafe deserialization of untrusted input.
- Authoritative outcomes (currency, ownership, match result) never trust a client value.
- Fail closed: never swallow an exception around signature, token or payment validation.
- Third-party package, DLL or `.unitypackage` → `security-reviewer` before it lands.
- `Temp/`, `Library/`, `Logs/`, `UserSettings/` hold Editor session tokens: never copy them into evidence, reports, archives or tracked files.
- A secret already in git history → stop and route to `cto`. Deleting it from the working tree fixes nothing.

## Tools
- Shell: newest PowerShell → Bash → cmd. Drop a rung only on real failure.
- Unity: Unity CLI (`unity:unity-cli`) → any configured MCP server → classic batchmode. Drop a rung only on failure or a missing capability.
- Search: XERJ when session start says up (skill `code-search`) → Grep. Never `xerj feedback`, `share` or `init`.
- One Unity Editor and one physical device, project-wide: never two agents on either at once. Writing into `Assets/`, `Packages/` or `ProjectSettings/` holds the Editor.
- Commits: English imperative subject, blank line, body saying why; no `feat:`-style prefixes; one change per commit. Never push unasked.
- After any change under `.claude/`, run `/verify-layer`.

## Memory — Zero-Mem, skill `mem`
- Nothing is preloaded: `mem q` before work in an unfamiliar area; a hit is a lead — read its source. Never use an LLM to organise, summarise or rewrite memory.
- When the GD confirms a mistake: fix it, re-verify, then `mem add lesson`. A stated preference → `mem add feedback`. Never secrets or PII.
