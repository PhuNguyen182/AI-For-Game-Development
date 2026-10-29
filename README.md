# AI-For-Game-Development

A Claude Code setup for making Unity games. You direct as the Game Designer; agents write the code, review it and test it.

## Requirements

- [Claude Code](https://claude.com/claude-code) and a Unity project
- PowerShell 7 (`pwsh`). Without it, edits and commits are blocked.
  - Windows: `winget install Microsoft.PowerShell`
  - macOS: `brew install --cask powershell`
  - Linux: `sudo snap install powershell --classic`
- Optional:
  - Python 3.10+, for session memory.
  - Unity CLI and a Unity MCP server, for Play Mode, profiling and in-Editor tests.

## Install

```bash
git clone <this repo> /tmp/aigd
git -C /tmp/aigd archive HEAD .claude CLAUDE.md .gitignore .xerjignore .memory/sources.txt | tar -x -C <your-unity-project>
cd <your-unity-project> && claude
```

Open Claude Code in the project once and accept the trust dialog. Until you do, the project's permissions and hooks are ignored. Then run:

```
/new-project
```

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
