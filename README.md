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

## License

None yet. Add one before you distribute this.
