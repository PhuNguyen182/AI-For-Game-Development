# Body batch brief (T3, T4)

Read this with the spec and `framework-docs/skill-template.md`. The dispatch names the batch.

## Inputs
- **Skills:** your batch's rows in `batches.md`, with its fence list, section classes and traps.
- **Anchors:** rows for your skills in `anchors.md`, including "must keep step numbers".
- **Ask:** rows for your skills in `ask-inventory.md`; each hit's class and intended fix.
- **Base:** `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`.

## Rewrite each SKILL.md
- **Format:** the template's shape; every item `- **<title>:** <short description>`; steps `1. **<title>:** ...`.
- **Top lines:** `- **Not for:** ...`, `- **Docs:** ...`.
- **References and scripts:** bullets under `## References` and `## Scripts`, replacing their tables. Keep each trigger's wording.
- **Line length:** one fact per item, under 200 chars. Split long items into nested titled bullets, or into more bullets.
- **Prose:** none. A sentence after a bullet or a fence becomes its own titled bullet.
- **Other tables:** data tables may stay.
- **Code fences in a body:** stay unless they are 15+ lines.

## Failures comparators found; check your own text for each
- **Dropped condition:** a split lost "with player-to-player item trading" or "if ... does not carry over", so a conditional rule became unconditional.
- **Dropped limiter:** "wins only here" became "wins"; "never a summary" moved onto the wrong clause.
- **Shifted qualifier:** "per screen" qualified one item, and as a title it covered all three.
- **Invented claim:** a new title or lead-in stated something Base never said ("each option fits one model", "price each tier"). A title names the existing text; it adds no fact.
- **Orphan reference:** "it", "this", "them" must point to the same thing after a split; repeat the noun.
- **Shared scope:** when one sentence covers several subjects, every split bullet still covers all of them.
- **Title widening:** a title holding a rule covers every bullet beneath it. Put a rule that applies to some bullets in its own bullet, naming them.
- **Moved-code wording:** a reference must say the adapt target and the stored form exactly, and keep any fact the fence alone carried. A fact that lived only in the code stays stated in the reference.
- **Size is never a reason:** 8,000 is soft. T3.4 cut required checks to reach it and had them restored. Never remove a check, a `## Scripts` entry for a usable file, or a pinned value to save chars; report the size instead.
- **Fragment targets:** a members-only sample names its host class first, path as the fallback; never a new file that holds only members.
- **Headers invent nothing:** a script header states only what Base states. Adapt targets follow `naming-convention.md`: MonoBehaviour and UI under `<Feature>/Views/`.
- **Verified lines with domain content:** a `Verified` line naming a specific check ("frame time and allocations vs budget") moves that check into a step before the line goes.
- **Rules are not scope:** a ban or boundary rule never becomes a `Not for:` bullet; it goes in `## Never` or a step.
- **Circular checks:** a new step must be falsifiable. "Verify on what was run" passes on any run.
- **Named triggers:** a deleted "On request only" line that names domain triggers (volume, region, pricing) becomes a last step: `**Re-decision triggers:** on request, name what re-opens this decision: <triggers>.`

## Remove or move
- **`Latent concerns` / `Future remediation` line:** delete.
- **`Verified`, `Known limitations` in `Output`:** delete; the envelope owns them. A domain-specific limit inside that line becomes a `## Never` bullet or a step.
- **Hardcoded script paths:** `"${CLAUDE_SKILL_DIR}/scripts/x"`, through the interpreter.
- **Scripts not named:** name them in `## Scripts`.
- **`Never` bullets that restate a step:** delete only when the step holds the same condition and the same consequence.

## Keep exactly
- **Criteria:** every threshold, condition, ban, required order, output field, routing target, version caveat, exception. Reword for shape only.
- **Example lines:** content kept, in titled form.
- **Step numbers:** in any skill the inventory marks, keep each number with its subject. A split becomes nested titled bullets under the same number. `Missing input` and `Final check`, when added, go after the last step.
- **Cited headings and labels:** exact text.
- **Frontmatter:** unchanged. Descriptions were finished in T2.
- **Folder and reference names:** unchanged.

## Ask fix
- **Apply the inventory's fix per hit.** A hit you disagree with goes to `Assumptions`, with your reason.
- **Missing input step:** add it only for skills whose inventory class needs it.
- **Allowlisted lines:** their fragments must keep matching `ask-allowlist.txt`, even when reformatted. If a rewrite breaks a fragment, update that row and list it in `Changed`.

## Moved code (15+ line fences in references)
- **Target:** `<skill>/scripts/<name>` in the real language, content byte-identical to the fence body.
- **Trap:** `git-unity-repo` uses `unity.gitattributes`. Never create a file named `.gitattributes`.
- **Header:** ≤5 lines in that language's comment form: what it shows; `Adapt into: <target path>`; `Unverified: not compiled or run (no Unity project in this repo).`
- **Reference:** replace the fence with a link to `../scripts/<name>` plus any fact the code alone carried. Edit references only for moved code, links and "ask" fixes.
- **SKILL.md:** lists the file under `## Scripts` only when usable without the reference. Each adapt bullet says `adapt into <target path>`.

## Do not
- **Add a `checklist.md`.** Propose one under `Next:` if a skill clearly needs it.
- **Change behaviour, add knowledge, or fix a fact you think is wrong.** Report it under `Out of scope`.
- **Commit, or edit** `verify.ps1`, the spec, the feature file, `anchors.md` or another batch's skills.

## Verify before returning (PowerShell tool; `pwsh` is not on Bash's path)
- **Each changed SKILL.md:** `pwsh -NoProfile -File .claude/skills/verify-layer/scripts/verify.ps1 -File <path>` prints no skill-format WARN. Justify any remaining one.
- **Whole layer:** same script with no argument, exit 0.
- **Token survival:** `pwsh -NoProfile -File .workflow/evidence/skill-template-migration/token-survival.ps1 -Base <sha> <skill> <skill> ...`; skills are positional. Fix or explain every miss in `batch-<id>/attempt-<k>/token-survival.md`.
- **Ask:** `pwsh -NoProfile -File .workflow/evidence/skill-template-migration/ask-check.ps1` shows no open hit in your skills.
- **Scope:** `git status --short` shows only your batch's files, plus untracked `.workflow/`.

Return the `agent-protocol` envelope.
