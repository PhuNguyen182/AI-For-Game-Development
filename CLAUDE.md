# CLAUDE.md — `<Project Name>` (template)

> Template — copied alongside `.claude/` into a new Unity project (see `README.md` → Installation). Fill in
> every `<!-- TODO -->`, delete this notice when done. `.claude/rules/` already governs everything true for
> every project; this file only carries what those rules can't know — identity, stack, and the few overrides
> the framework allows. Never restate a rule here — reference it.

## Project identity

| Field | Value |
|---|---|
| Name | `<!-- TODO -->` |
| Genre / core loop | `<!-- TODO -->` |
| Target platform(s) | `<!-- TODO -->` |
| Unity version | `<!-- TODO -->` |
| Render pipeline | `<!-- TODO: URP / HDRP / Built-in -->` |
| Track | `<!-- TODO: client-only, or client+server -->` |

Track matters beyond documentation: with none stated, `orchestration.md` I1 has `technical-architect` assume
client-only, silently.

## Tech stack

- Language: C# `<!-- version -->`
- Networking: `<!-- none / Netcode for GameObjects / custom -->`
- Backend & live-ops: `<!-- Firebase / UGS / custom / none -->`
- Monetization: `<!-- ad network, IAP provider, none -->`
- Other SDKs in active use: `<!-- list, or none -->`

## Unity tooling — CLI → any MCP → classic batchmode

Base rule (unchanged): `.claude/rules/unity-tooling-preference.md` — Unity CLI first, MCP only on actual
failure or a real capability gap. This project adds one rung and widens the fallback's scope:

1. **Unity CLI** — first attempt for anything it can do.
2. **Any MCP server actually configured here — not only a Unity-branded one.** Never assume the fallback
   means `mcp__unity-mcp__*` specifically; pick whichever available server fits the operation.
3. **Classic batchmode** (`Unity.exe -batchmode -quit -executeMethod ...`), used directly only once both
   above were tried for that specific operation and neither can do it, or both failed.

Drop a rung only on observed failure or a confirmed gap — never pre-emptively.

| Field | Value |
|---|---|
| CLI's Unity install/version alias | `<!-- TODO -->` |
| Default build target(s) | `<!-- TODO -->` |
| Routine test command(s) | `<!-- TODO -->` |
| MCP server(s) configured, and what each covers | `<!-- TODO, or none configured yet -->` |
| Legacy batchmode entry points still relied on | `<!-- TODO, or none -->` |

## Framework overrides

Leave a row untouched to keep the default; fill it in only with a stated reason.

| Default | Override | Why |
|---|---|---|
| `<state-root>` = `.workflow/` | `<!-- TODO -->` | `<!-- TODO -->` |
| `Game.Core/Client/Server.*` namespaces | `<!-- TODO -->` | `<!-- TODO -->` |
| Feature roots co-located with code | `<!-- TODO -->` | `<!-- TODO -->` |

Any other deviation from a rule or standard goes here too — a stated exception, never a silent one.

## Known constraints

- Performance budget: `<!-- TODO -->`
- Minimum spec / OS versions: `<!-- TODO -->`
- Compliance: `<!-- TODO: COPPA/GDPR, store policies, or none -->`

---

Everything else — agents, pipelines, rules, skills — is in `README.md` at the repo root. Keep this file
short: it loads into every session alongside the rules layer.
