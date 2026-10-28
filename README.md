# AI-For-Game-Development

A Claude Code framework for producing Unity games — Windows/macOS/Linux, Android, iOS; hyper-casual to hard-core — with a Game Designer (GD) directing and agents doing the engineering. Copy `.claude/` and `CLAUDE.md` into a Unity project and work through slash commands.

## Install

Requirements: Claude Code; a Unity project (Unity CLI recommended — `com.unity.pipeline`); optionally a Unity MCP server and the official Unity plugin (`unity@claude-plugins-official`).

**PowerShell 7 (`pwsh`) on every machine** — the hooks are one PowerShell implementation for all three OS. The security hooks fail closed: without `pwsh`, edits and commits are blocked with an error instead of silently unchecked.

| OS | Install `pwsh` |
|---|---|
| Windows | `winget install Microsoft.PowerShell` (the scripts also run on the built-in Windows PowerShell 5.1) |
| macOS | `brew install --cask powershell` |
| Linux | Microsoft's package repo (`sudo apt install powershell` after adding it) or `sudo snap install powershell --classic` |

Check a machine: `pwsh -NoProfile -File .claude/hooks/tests/run.ps1` → `hooks: all tests passed`. Run it once on each new machine (Windows, macOS, Linux) before relying on the hooks.

**Python 3.10+ with SQLite FTS5** (python.org, Homebrew and Linux builds have it; stdlib only, no pip) for memory — skill `mem`. Without it the session still runs; memory capture and queries are off. Check: `python -I .claude/skills/mem/scripts/test_mem.py`.

**Optional: [XERJ](https://github.com/xerj-org/xerj)** for code search. When a node is up (`xerj --data-dir ~/xerj-data`, data dir outside the repo), agents search with `xerj search`/`xerj def` and a repo-wide Grep is denied — skill `code-search`.

```bash
git clone <this repo> /tmp/aigd
git -C /tmp/aigd archive HEAD .claude CLAUDE.md .gitignore .xerjignore .memory/sources.txt | tar -x -C <your-unity-project>   # tracked files only
cd <your-unity-project> && claude
> /new-project          # fills CLAUDE.md, asmdefs, git/LFS, perf budget, .workflow/
```

Open Claude Code **interactively once** in the project and accept the trust dialog: until then the project's permissions and hooks are ignored. Headless runs (`claude -p`) in an untrusted folder need `--settings .claude/settings.json`.

Editor agents name MCP tools exactly (`mcp__unity-mcp__…`). Check they match your server:
`grep -h '^tools:' .claude/agents/*.md | tr ',' '\n' | grep mcp__ | sort -u`. Without an Editor connection everything still runs except Play Mode, profiling and in-Editor tests, which QA reports as not covered.

## Use

| You want | Type |
|---|---|
| Set up a project | `/new-project` |
| GDD → milestones → sized backlog | `/plan-game <gdd>` |
| Build a feature | `/feature <request>` |
| Fix a bug | `/fix <bug or symptom>` |
| Review code | `/review <diff or path>` · large: workflow `review-gate` |
| Test / evidence | `/qa <feature>` |
| Tech or vendor decision | `/decide <capability>` |
| Release candidate | `/release <platforms> [--dry-run]` |
| Project health check | workflow `project-audit` |
| Crash on a test device | `/investigate-device-crash` |
| Test plan only | `/plan-test-coverage` · static risk review: `/review-code-risks` |
| Merge conflicts | `/resolve-merge-conflicts` |

Anything else: just ask. `rules/routing.md` routes it and states the route in one line.

## How it works

**Sizing** — every input is S, M or L, plus a risk flag.

| Size | Means | Flow |
|---|---|---|
| S | One role, judgeable by looking, no new contract | Directly or one agent; the reply closes it |
| M | 2+ roles, a new contract or screen, or touches `Game.Core.*` | `/feature`: spec → CP2 → build → review? → QA? → CP4 |
| L | Architecture, netcode, new Core system, or an undecided direction | `/feature` with CP1 (options → critic → GD locks) and CP3 |

Risk flag (signing, real-money IAP, store, PII, save migration, published history, released build, perf budget, anti-cheat) → verification by running, and review is recommended.

**Gates are optional** — review and QA are offered once when the code is built, with a recommendation and the cost of skipping; the GD decides. A declined gate is listed under known limitations and at CP4. Only the third-party supply-chain check and the secret hooks are always on.

**Profile** (`CLAUDE.md`) sets the defaults — hyper-casual skips CP1 and the full spec, hard-core turns on netcode, perf and automation QA. Table in `rules/routing.md`.

**Checkpoints** — CP1 direction · CP2 spec · CP3 built vs spec · CP4 closure. The GD answers every question through `AskUserQuestion`, recommended option first.

**One stop rule** — the same step failing twice gets one root-cause pass from `technical-architect`; failing again stops and reports to the GD.

**Shared Core** — game rules live once in `Game.Core.*` (pure C#, deterministic, no `UnityEngine`); `Game.Client.*` integrates them; `Game.Server.*` validates them when multiplayer.

**One Editor, one device** — implementers run one at a time, across sessions too (lock hook); read-only agents run in parallel.

**State** — `.workflow/features/<slug>.md` per M/L feature, `.workflow/bugs.md` for bugs, `.workflow/backlog.md` from `/plan-game`. Commit it. A new session lists in-flight features automatically.

## Agents (23)

| Group | Agents |
|---|---|
| Build | `csharp-engineer` (Core) · `gameplay-engineer` · `ui-engineer` · `unity-performance-engineer` · `technical-artist` · `netcode-engineer` · `sdk-platform-engineer` · `backend-engineer` (optional) |
| Design & decide | `technical-architect` · `cto` · `researcher` · `critic` · `rd-engineer` |
| Gates | `code-reviewer` · `security-reviewer` |
| QA | `qa-lead` · `qa-automation-engineer` · `playtest-tester` · `performance-qa-engineer` |
| Ship & ops | `build-release-engineer` · `ci-cd-engineer` · `git-expert` · `crash-anr-investigator` |

Every agent preloads skill `agent-protocol` (one return envelope) plus its standards (`csharp-standards`, `qa-standards`), and loads domain skills on demand.

## Layout

```
CLAUDE.md                 summary, identity, stack headline, tooling, overrides (template, ≤30 lines)
docs/tech-stack.md        every package, SDK and service (created by /new-project; read on demand)
.memory/                  Zero-Mem, committed: traces/ (sessions, by hook), notes/<type>/ (lessons, feedback), sources.txt (docs to index)
                          .index/ (SQLite FTS5) and .state/ are local and gitignored — rebuilt after every pull
.claude/
  rules/core.md           always loaded: language, GD, truth, security, tools
  rules/routing.md        always loaded: routes, sizing, profile, checkpoints, stop rule
  rules/csharp.md         loaded only when a .cs file is touched
  agents/                 23 agents
  skills/                 pipelines (/feature …), standards, ~90 domain skills
  workflows/*.js          Claude Code workflows: review-gate, project-audit
  hooks/*.ps1             secret scan, pre-commit secret + .meta check, layer verify, session resume, memory capture, search guard
  settings.json           permissions (deny force-push/reset --hard/keystores; ask push/checkout) + hooks
framework-docs/           design history, templates, backlog — not copied into projects
```

## Hooks

Scripts are ASCII-only PowerShell, compatible with pwsh 7 and Windows PowerShell 5.1 (`/verify-layer` enforces ASCII). Security hooks use `onFailure: block`.

| Event | Does |
|---|---|
| Edit/Write | Blocks content with a secret shape (private keys, AWS/Google/GitHub/Slack/Stripe keys, JWTs, password literals) |
| `git commit` | Blocks staged secrets; Unity assets without `.meta`, orphan or left-behind `.meta`; a changed `.meta` GUID; binaries and files over 5 MB outside Git LFS (`git config claude.lfs off` to opt out) |
| Agent dispatch, `unity …` | Cross-session Editor lock (`.workflow/editor.lock`): a second session cannot dispatch an Editor-holding agent or run `unity` while another holds it |
| Subagent stop | An Editor-holding agent left in Play Mode or with compile errors is sent back once to clean up; then its lock hold is released |
| `Packages/manifest.json` edit, `unity command package add/remove` | Reminds: security-reviewer for third-party packages, update `docs/tech-stack.md` |
| Edit under `.claude/` | Runs `/verify-layer` on the file |
| Session start | Lists in-flight features; one status line each for memory (counts, query command) and code search (XERJ up/down/absent); refreshes the XERJ index in the background when up. No memory content is preloaded |
| Turn end, session end | Copies the session's prompts, replies, agent briefs/returns and GD answers into `.memory/traces/` — no tool output, secrets redacted, no LLM. `MEM_CAPTURE=0` skips a session |
| Grep, `grep -r`/`rg`/`git grep`/`Select-String` | While XERJ is up, denies a repo-wide content search and names the `xerj search` command; files, deep folders, hidden folders and file lists stay allowed |

**Permissions** — deny: `xerj feedback` (it publishes to GitHub), force-push, `reset --hard`, `clean -f`, reading or editing keystores and `.env`, editing `Library/`, `Temp/`, `Logs/`, `UserSettings/`. Ask: `git push`, `git checkout`, player builds, build-target switch, Fastlane, Firebase App Distribution, `xcrun altool`/`notarytool`, `git filter-repo`/`filter-branch`, `git lfs migrate`.

## Extending

- New agent: only for a distinct tool sandbox, an independent gate, a model tier or an activation condition — template in `framework-docs/agent-template.md`. Domain knowledge is a skill.
- New skill: `.claude/skills/<name>/SKILL.md`, description ≤ 250 chars (what + when), detail in `references/`.
- Keep every file terse: bullets and tables, no rationale unless omitting it causes wrong behaviour. Line budgets (`/verify-layer`) are recommendations; longer is fine when it cannot be shorter.
- Run `/verify-layer` before committing changes under `.claude/`.

## Conventions

English for code, docs and commits; replies to the GD in Vietnamese. Commits: imperative subject, why-body, no `feat:` prefixes. Never push without asking.

## License

No license file is present in this repository. Add one before distributing.
