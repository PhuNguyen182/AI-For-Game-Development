# Build checks

Synthesized from project decisions. Commands behind the compile check and the test run of `/feature` step 4; `/fix` step 5 runs the same compile check.

## Compile check
- **Commands:** `unity command script recompile` → poll `unity command script recompile_status` until `completed` → `unity command console status` (compile-failure flag) / `unity command console get --level error`.
- **`up_to_date`:** does not prove the edits compiled — confirm a changed type exists (`script eval`).
- **No Editor:** `unity pipeline list` (Safe Mode?) and grep `Editor.log` for `error CS`.

## Test run
- **`unity test`:** `unity test <project> --mode EditMode|PlayMode -- -assemblyNames <assembly>` (it imports, compiles and writes the NUnit report).
