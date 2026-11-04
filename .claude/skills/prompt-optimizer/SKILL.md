---
name: prompt-optimizer
description: "Rewrite a prompt or prompt file as an English XML prompt for agents. Use to optimize a prompt."
argument-hint: "<prompt text | path to prompt file>"
allowed-tools: Read, AskUserQuestion
---

# /prompt-optimizer

## Steps
1. **Input:** `$ARGUMENTS` is a file path (the file exists) → Read it; otherwise it is the prompt text. Empty → ask for a prompt via `AskUserQuestion`.
2. **Understand:** extract the intent, context, scope, constraints, and expected output. Keep every requirement; add none.
3. **Clarify:** any ambiguous or missing requirement → ask via `AskUserQuestion` (2-4 options, recommended first) before rewriting; batch all questions in one call. Never guess.
4. **Classify:** pick the task type (analysis, refactor, survey, implementation, fix, review, docs) and shape the steps to it.
5. **Rewrite:** fill the template below. English only, imperative, concrete, no filler. Tags are free: rename, add or drop them to fit the task.
6. **Deliver:** reply in chat with the XML only, as plain text. Input was a file → do not write any file. Never execute the prompt.

## Rules
- **Fidelity:** the full original intent survives; translate non-English text, keep code, identifiers and paths verbatim.
- **Agent-ready:** state a verifiable goal, explicit scope, ordered steps, and a done condition an agent can check.
- **Gaps:** an unknown the user answered "unsure" to goes in `<open_questions>`; never invent facts.
- **Output:** the first character of the reply is `<`. No preface, no code fence, no explanation, no closing remark.
- **Brevity:** one idea per line; cut anything the agent would skip.

## Template
```xml
<prompt>
  <role>who the agent acts as</role>
  <goal>one-sentence outcome</goal>
  <context>background, current state, why it matters</context>
  <scope>
    <in>files, systems, behaviors in scope</in>
    <out>explicitly excluded</out>
  </scope>
  <requirements>
    <requirement>testable requirement</requirement>
  </requirements>
  <constraints>hard limits: tech, style, budget, compatibility</constraints>
  <steps>
    <step n="1">analyze / survey first</step>
    <step n="2">change or implement</step>
    <step n="3">verify</step>
  </steps>
  <output_format>what to return and how</output_format>
  <acceptance_criteria>
    <criterion>checkable done condition</criterion>
  </acceptance_criteria>
  <open_questions>only blocking unknowns</open_questions>
</prompt>
```
