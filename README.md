# AI-For-Game-Development

A Claude Code setup for making Unity games. You direct as the Game Designer; agents write the code, review it and test it.

## Requirements

- [Claude Code](https://claude.com/claude-code) and a Unity project
- Git
- PowerShell 7 (`pwsh`). Without it, edits and commits are blocked, and the install and update commands do not run.
  - Windows: `winget install Microsoft.PowerShell`
  - macOS: `brew install --cask powershell`
  - Linux: `sudo snap install powershell --classic`
- Optional:
  - Python 3.10+, for session memory.
  - Unity CLI and a Unity MCP server, for Play Mode, profiling and in-Editor tests.

## Install

Clone this repo once, then run one command per Unity project. The project must be a git repo, and the target is its root. It works the same for a project with no `.claude/` and for one that already has it.

**Step 0: PowerShell 7 must be installed.** Check with `pwsh --version`. If the command is not found, install it first (Requirements above). The commands below fail without it on Windows, macOS and Linux.

**Install** (once per project). Template:

```powershell
pwsh -File <framework-clone>/.claude/tools/install-framework.ps1 -Target <unity-project>
```

Example with full paths, from anywhere:

```powershell
pwsh -File C:\Projects\AI-For-Game-Development\.claude\tools\install-framework.ps1 -Target C:\Projects\MyUnityGame
```

Example after `cd` into the project (`-Target` defaults to the current folder):

```powershell
cd C:\Projects\MyUnityGame
pwsh -File C:\Projects\AI-For-Game-Development\.claude\tools\install-framework.ps1
```

On macOS or Linux the same commands use `/` paths:

```bash
cd ~/Projects/MyUnityGame
pwsh -File ~/Projects/AI-For-Game-Development/.claude/tools/install-framework.ps1
```

**Update** (any time later). It needs no path to this repo: the install records where the framework came from. Template:

```powershell
pwsh -File <unity-project>/.claude/tools/update-framework.ps1
```

Example with full path, from anywhere:

```powershell
pwsh -File C:\Projects\MyUnityGame\.claude\tools\update-framework.ps1
```

Example after `cd` into the project (same on macOS and Linux):

```powershell
cd C:\Projects\MyUnityGame
pwsh -File .claude/tools/update-framework.ps1
```

Both commands accept `-DryRun` (print the report, write nothing) and `-Force` (take the framework's version on a conflict). Update also accepts `-Source <git url>` and `-Ref <branch or tag>`. Neither command commits or pushes: review the changes with `git status` and commit them yourself.

| Part of your project | Install and update do |
|---|---|
| `.claude/agents`, `skills`, `hooks`, `rules`, `workflows`, `templates`, `tools` | Add what is missing, update what the framework changed, remove what it retired |
| Your own agents and skills (names the framework does not have) | Leave alone |
| A framework file you edited | Keep yours and write the framework's version beside it as `<file>.framework-new`. Merge it, delete it, or rerun with `-Force`. Old versions are backed up under .claude/.framework-backup/ |
| `.claude/settings.json` | Merge: add the framework's permissions, env keys and hooks. Your other settings stay |
| `.gitignore` | Append the framework's missing lines |
| `CLAUDE.md`, `.xerjignore`, `.memory/sources.txt`, `.workflow/` | Create at install if missing, never overwrite |

The state of the last sync is in the file .claude/.framework-manifest.json. Commit it.

Open Claude Code in the project once and accept the trust dialog. Until you do, the project's permissions and hooks are ignored. Then run `/verify-layer` after an update, or after an install:

```
/new-project
```

The first session creates `.workflow/framework-backlog.md` from `.claude/templates/framework-backlog.md`: gaps found in the framework while working on this project go there. The project commits it. The framework repo ignores its own copy, so each clone starts with an empty one.

## Use

| You want | Type |
|---|---|
| Plan the game from a GDD | `/plan-game <gdd>` |
| Build a feature | `/feature <what you want>` |
| Fix a bug | `/fix <bug>` |
| Review code | `/review <path>` |
| Test a feature | `/qa <feature>` |
| Choose a tech or vendor | `/decide <need>` |
| Prepare a release | `/release <platform>` |

For anything else, just ask in plain words. It does not have to be in English.

The framework sizes each request and runs the right agents. It asks before it makes a decision that is yours, and it never commits or pushes unless you ask. Progress is saved in `.workflow/`, so a new session picks up where the last one stopped.

## Output style: Game Engineer

The file [.claude/output-styles/game-engineer.md](.claude/output-styles/game-engineer.md) sets how Claude writes its replies. It is an [output style](https://code.claude.com/docs/en/output-styles): a Markdown file with frontmatter whose body is added to the system prompt.

What it does:

| Area | Behaviour |
|---|---|
| Voice | Direct and professional, like a senior game developer, software engineer and game designer. No pleasantries, no hedging. |
| Address | Replies in your language. In Vietnamese: "Bạn" for you, "Tôi" for Claude. |
| Length | Short, result first, one idea per line. |
| Hard topics | Architecture, determinism, netcode, shaders and similar get a plain explanation: what it is, how it works, what breaks if done wrong. Everything else stays short. |
| Truthfulness | Never claims a test, build or review that did not run. No silent scope cuts. |
| Limits | Ends a finished task with a `Limits` list: what is incomplete, the impact, and the concrete fix for later. |

It sets `keep-coding-instructions: true`, so Claude Code's built-in coding behaviour stays on.

Turn it on:

1. In Claude Code, run `/output-style` and pick **Game Engineer**.
2. Or set it in `.claude/settings.local.json` (per user, not committed): `{ "outputStyle": "Game Engineer" }`.

The choice applies to new sessions. To go back, run `/output-style` and pick **default**.

To use it in every project, copy the file to `~/.claude/output-styles/`. To change it, edit the file and run `/verify-layer`. Install and update copy it into your project with the rest of `.claude/`.

## License

None yet. Add one before you distribute this.
