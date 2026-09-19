# Shared — Unity Tooling Preference

Applies to: every agent that interacts with a Unity project or a running Unity Editor — creating or editing
scenes, assets and GameObjects, running builds or tests, inspecting the hierarchy, reading Editor/Console
logs, or any other operation Unity itself can perform. Like `language-and-comments.md`, this file sits above
the `.claude/rules/<group>/` folders rather than inside one.

## Why it exists

Two separate paths can drive Unity from an agent: the **Unity CLI** (`unity <command>` — the standalone
command-line tool documented at
[docs.unity.com/en-us/unity-cli/unity-cli-reference](https://docs.unity.com/en-us/unity-cli/unity-cli-reference),
not to be confused with the classic `Unity.exe -argument` Editor flags) and one or more **MCP servers**
exposing Unity or Editor operations as tools (for example `mcp__unity-mcp__*`). The Unity CLI is not
headless-only: through the Unity Pipeline package it can also install/manage Editors and projects, run
batch-mode builds and tests, manage VCS operations, and forward commands to (or read live status from) an
**already-running** Editor instance (`unity command`, `unity status`) — it covers most of the ground an MCP
tool would otherwise be reached for. Without a stated order, which path gets used varies call to call, which
makes behavior inconsistent and risks the exact conflict `orchestration.md` invariant I3 warns about — more
than one process reaching into the single project-wide Unity Editor at once. This file fixes the order once.

## The order

1. **Unity CLI first.** For any Unity operation the CLI can perform — Editor/project install and management,
   batch-mode builds and tests, VCS operations, log/status inspection, and forwarding a command to or reading
   status from an already-connected Editor instance — run it via the CLI (see the `unity:unity-cli` skill)
   before reaching for any MCP tool. This includes operations against a live Editor session, since the CLI's
   command-forwarding and status capabilities already reach a running Editor; "the Editor is already open" is
   not by itself a reason to skip straight to MCP.
2. **Fall back to an available MCP server** only when the Unity CLI:
   - cannot perform the specific operation at all (no CLI command or connected-Editor forwarding covers it),
     or
   - fails when actually attempted for that specific operation, or
   - is clearly the wrong fit for the task (e.g. an operation the CLI has no command surface for at all, such
     as a fine-grained in-Editor inspection or interaction only an MCP tool exposes).

   "MCP" here means **any MCP server actually available in this project that can perform the operation** —
   not specifically the Unity MCP server. If a non-Unity-specific MCP tool can accomplish the same Unity-
   adjacent task (e.g. a general file or build tool exposed over MCP), it is a valid fallback on the same
   footing as `mcp__unity-mcp__*`. Pick whichever available MCP tool actually fits the operation; do not
   assume the fallback must be Unity-branded. Note that the Unity CLI itself can also run its own MCP server
   (`unity mcp start`) — that remains part of the CLI path, not the fallback, when it's how the CLI exposes
   the operation.

Fall back only on actual failure or unfitness — not preemptively, and not because the CLI "might" not
support something. Attempt the CLI path first; move to MCP only once it has errored, is confirmed
unavailable for that operation, or is clearly the wrong tool for the specific task at hand.

## Relationship to the Unity Editor invariant

`orchestration.md` invariant I3 still governs: there is one Unity Editor, project-wide, whichever path
reaches it. Falling back to an MCP tool that talks to the live Editor does not relax that invariant — never
run two agents against the Editor at once regardless of which path (CLI or MCP) each one is using.

## Rules

- Default to the Unity CLI for every Unity operation it can perform; treat it as the first attempt, not an
  alternative to consider only when convenient.
- Drop to an MCP tool only when the CLI cannot do the operation, fails when attempted, or is clearly the
  wrong fit for that specific task.
- "MCP fallback" means any available MCP server capable of the operation, not exclusively a Unity-specific
  one — pick whichever fits, Unity-branded or not.
- Never let the MCP fallback bypass the single-Editor, single-device invariants in `orchestration.md` — the
  tooling path chosen does not change how many agents may touch the Editor at once.
- Never re-litigate this order per operation — apply it by default, and only deviate on an actual, observed
  failure or unfitness, not a hypothetical one.
