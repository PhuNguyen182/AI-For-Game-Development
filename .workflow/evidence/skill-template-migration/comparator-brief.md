# Comparator brief (T3, T4)

You are not the batch's author. Read-only: edit no tracked file. Write only `batch-<id>/attempt-<k>/comparison.md` in this folder.

## Inputs
- **Rules:** spec section "Comparator"; `framework-docs/skill-template.md`; `batch-brief.md`.
- **Scope:** your batch's skills in `batches.md`. The author's changes are uncommitted in the working tree.
- **Base:** `git show bdf5c9ec70bf217ee9ed2763abd75fa4280b717c:<path>`, never `HEAD`.
- **Author's reports:** claims to test, not to trust.

## Checks, per skill
1. **Criteria:** walk every Base `SKILL.md` line in order. A criterion is any line carrying a threshold, condition, ban, required order, output field, routing target, version caveat or exception. Disposition: kept; moved to `file:line`; or cut, naming a template class.
2. **Plain words:** `token-survival.ps1` catches only symbols. Plain-word conditions, limits and consequences are yours to catch by reading.
3. **Tokens:** run `token-survival.ps1 -Base <sha> <skills...>` (positional) from the PowerShell tool. Confirm or refute each explanation.
4. **Anchors:** every `anchors.md` row for these skills resolves to the same subject.
5. **Ask:** run `ask-check.ps1`; check each hit's class against the fix applied.
6. **Moved code:** each moved file's body equals the Base fence byte for byte; header meets the brief; the reference links it; no trimmed block.
7. **Sections:** the skill matches its class in `batches.md`.
8. **Scope:** frontmatter unchanged from `HEAD`; no change beyond the brief; no behaviour change or added knowledge.

## Findings
- **Automatic finding:** a "Common knowledge" cut that held a number, version or gotcha.
- **Not a finding:** a wording preference.
- **Row:** skill | check | Base text | current text | why it fails | exact fix.

## Report
- **Contents:** only cuts, moves, resolved tokens and findings.
- **Verdict:** pass, or fail with the failing skills only.
- **Return:** the `agent-protocol` envelope, verdict in `Summary`.
