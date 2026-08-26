# Shared — Language & Comment Protocol

Applies to: every agent, in every project that adopts this framework — regardless of role or group. This rule is not scoped to any single `.claude/rules/<group>/` folder; it sits above all of them. Every agent must follow it in addition to whatever group-specific rules also apply.

## Input language

- The GD/user's input may be Vietnamese, English, or a mix of both within the same message. Parse it as-is — never ask them to restate in a single language.

## Working language — English, always

- All internal work is written entirely in English, regardless of the input language: reasoning, technical documents (Tech Spec, Review Verdict, Test Report, Bug Report, Root Cause Report, Feasibility Report, Status Report, and any other handoff document), code, commit messages, file names, identifiers, and log messages.
- This applies even when the request was given entirely in Vietnamese — translate the intent first, then do the actual work in English.
- Exception: a verbatim quote from the GD's original request (e.g. exact GDD wording being cited for precision) may stay in its original language, but must be clearly marked as a quote — it is not the working language, just a reference.

## Final response — Vietnamese, always

- Once the work is complete, the reply delivered back to the GD/user is always written in Vietnamese, regardless of the input language and regardless of the English working language used internally.
- This applies to every role without exception — even an agent whose entire task was writing English code and English technical documents still reports the outcome back in Vietnamese.

## Code and comments — English only

- Every line of code, every identifier, and every comment (inline, block, or XML doc) is written in English — no exceptions, no mixed-language code, regardless of what language the Tech Spec, GDD, or the GD's request was written in.

## Comment depth policy

- **Small, simple** classes/structs/functions: no comment required, or at most a short one-liner stating mechanism and purpose. Don't force a comment where the name and signature already make the behavior obvious.
- **Long or complex** classes, structs, and functions: require a full comment. For functions specifically, use complete XML doc comments (`/// <summary>`, `<param>`, `<returns>`, `<remarks>` as needed for C#; that language's equivalent doc-comment convention otherwise) that clearly state:
  - The member's role/responsibility within its larger component.
  - Its key parts/components — what it coordinates, what state it touches.
  - How it operates — the mechanism, not a line-by-line restatement of the code.
- "Long or complex" is a judgment call, not a line-count threshold. A 50-line function doing one obvious loop is simple; a 15-line function juggling several edge cases and a non-obvious ordering constraint is complex. When in doubt, write the comment — favor anything another engineer would need to read carefully before touching.
- This section governs depth/coverage only. Per-language mechanical comment style (single-line vs. block, placement, capitalization) is set by that group's own coding-principles rule file.

## Rules

- Every agent follows this file in addition to any `.claude/rules/<group>/*.md` files that apply to its own group.
- Where a group-specific rule file discusses comment style, treat this file as the authority on depth/coverage and language — the group file should only add mechanical style details on top, not a conflicting depth policy.
