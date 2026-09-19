# Shared — Shell Preference

Applies to: every agent and the orchestrator, whenever a task requires running a shell command. Like
`language-and-comments.md`, this file sits above the `.claude/rules/<group>/` folders rather than inside one.

## Why it exists

This project runs on Windows, where more than one shell can execute the same request — PowerShell, Bash (via
the Bash tool's POSIX layer), and `cmd.exe`. Without a stated order, the shell picked varies call to call,
which makes command behavior (quoting, path separators, environment variable syntax, exit-code semantics)
inconsistent across a single session and across agents. This file fixes that order once, so it never has to
be re-decided per command.

## The order

1. **The newest PowerShell available on the machine** — first choice, always. This is currently PowerShell 7
   (`pwsh`), but the rule is "newest installed", not a pinned version number — if a newer major version
   (e.g. PowerShell 8+) becomes the one actually present, that is the one to use, with no need to update this
   file. Prefer the PowerShell tool over the Bash tool when both could run the command. When more than one
   PowerShell version is present on the machine, use the newest one available, not whichever happens to be
   the tool's default.
2. **Windows PowerShell (5.x)** — used only when no newer PowerShell (7+) is present on the machine.
3. **Bash** — fallback when no PowerShell version is available, or when the specific command is genuinely a
   better fit for a POSIX shell (a script already written in Bash syntax, a Unix-specific tool with no
   practical PowerShell equivalent) or fails to run correctly under PowerShell.
4. **`cmd.exe`** — last resort, only when neither PowerShell nor Bash can run the command as needed.

Fall down this order only on actual failure or unavailability — not preemptively, and not because a command
"might" not work in PowerShell. Try the newest available PowerShell first; only move to the next option when
it errors, is missing, or is clearly the wrong tool for that specific command (e.g. a heredoc-heavy POSIX
script).

## How this applies to the available tools

- The **PowerShell tool** is the default choice for shell work. Use it unless the command at hand is
  POSIX-specific or PowerShell has already failed for it in this session.
- The **Bash tool** is the fallback — reach for it when no PowerShell version is installed, the installed
  PowerShell lacks behavior the command needs, or the command itself only makes sense as a POSIX script.
- Raw `cmd.exe` invocation (via either tool, using `cmd /c`) is the last resort and should be rare — most
  things `cmd.exe` can do, PowerShell can also do, natively and more safely.

## Rules

- Default to the newest PowerShell version available on the machine for every shell command; use the
  PowerShell tool unless there is a concrete reason not to.
- Never pin this rule to "PowerShell 7" specifically — treat it as "whatever the newest installed PowerShell
  is", so the rule stays correct as newer versions ship.
- Drop to Windows PowerShell 5.x only when no PowerShell 7+ is present on the machine.
- Drop to Bash only when no PowerShell version is available, or the command is not suited to PowerShell, or
  it demonstrably fails under PowerShell.
- Reach for `cmd.exe` only as a last resort, when neither PowerShell nor Bash can do the job.
- Never re-litigate this order per command — apply it by default, and only deviate on an actual, observed
  failure or unavailability, not a hypothetical one.
