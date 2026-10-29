# Performance

Pages: `MecanimPeformanceandOptimization`, `ModelingOptimizedCharacters`, `MecanimFAQ`, `TargetMatching`. Taking the measurement is `unity-profiler-diagnostics`; this is what to change once it blames animation.

## Cost sources
- Retargeting: Humanoid only; a character that never shares clips pays for nothing.
- Transform hierarchy: every bone is a transform written each frame — bone count scales, not clip count.
- Skinned renderers: each is separate skinning work; many pieces cost more than one mesh.
- Skinning quality (bones per vertex): direct cost; the highest setting is rarely visible on small characters.
- Layers and IK passes: evaluated each frame even at weight 0.

## Changes
| Change | Effect | Trade-off |
|---|---|---|
| Optimise transform hierarchy on import | Skeleton evaluated internally; biggest win on a crowd | Nothing parents to a bone unless listed as an exposed transform |
| Culling Mode off Always Animate ([animator-component.md](animator-component.md)) | Stops paying for unseen characters | Cull Completely can jump the pose |
| Generic instead of Humanoid | Drops retargeting | No retargeting, muscles or goal-based IK |
| Fewer bones | Less transform work | Deformation quality (faces, hands) |
| One skinned renderer per character | Fewer skinning batches/draw calls | Pieces cannot be hidden or swapped independently |

Each row sounds obviously right and several are wrong for a given scene (transform optimisation pays at two hundred characters, not ten). Capture before and after on the target device (`csharp-standards` → `performance-and-algorithms.md`, Verification).

## Related
- Target matching aligns a body part to a world position at a normalised clip point (vault/climb landing on the ledge).
- The muscle system normalises poses across rigs, so a retargeted clip can look subtly different rather than wrong.
