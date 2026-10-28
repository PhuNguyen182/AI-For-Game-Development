---
name: ask-via-multiple-choice
description: Every question to the GD is a multiple-choice AskUserQuestion call, never a question typed in chat
type: feedback
tags: [gd, questions]
paths: [.claude/rules/core.md]
status: active
updated: 2026-10-07
---

Ask only through `AskUserQuestion`: single-select when answers exclude each other, multi-select when independent,
recommended option first, 2-4 concrete options each stating its cost. Never end a reply with a chat-prose question
("Bạn có muốn tôi push không?"). Question text in Vietnamese.

**Why:** the GD stated it on 2026-10-07 after a turn closed by asking in chat whether to push. They answer by picking, not typing.

**How to apply:** yes/no, approach choice, approval, "what next" → `AskUserQuestion`; free text only via its "Other".
Encoded in `.claude/rules/core.md` → GD. Related: m:feedback/terse-framework-content.
