# Avatar Creation and Setup

Sources: `https://docs.unity3d.com/Manual/AvatarCreationandSetup.html`, and sub-pages (see [root-links.md](root-links.md)).

## Humanoid vs Generic rig
Unity's Mecanim system identifies animated models through an **Avatar**, which maps a model's bone structure to standardized body parts (legs, arms, head, spine). Set the rig type on the model's **Rig** tab (Import Settings) via the **Animation Type** dropdown:

| Animation Type | Behavior |
|---|---|
| `None` | No animation import. |
| `Legacy` | Old pre-Mecanim animation system. |
| `Generic` | Uses a **Root Node** transform for root motion; no standardized bone mapping; animation clips are tied to that specific skeleton — no retargeting across different rigs. |
| `Humanoid` | Uses the **Body Transform**/Avatar bone-mapping system; enables retargeting animation clips across any other correctly configured Humanoid Avatar, regardless of skeleton differences. |

Key capability that motivates Humanoid: "Because of the similarity in bone structure between different humanoid characters, it is possible to map animations from one humanoid character to another" — this is what enables animation reuse/retargeting (see Retargeting below).

## Avatar Configuration workflow
1. On the model, set **Animation Type = Humanoid** in the **Rig** tab.
2. Define the Avatar: **Create From This Model** (auto-generate) or **Copy From Other Avatar** (reuse an existing Avatar definition).
3. Click **Configure...** to enter Avatar Configuration mode (or select an existing Avatar asset and click **Configure Avatar** in its Inspector).
4. In the **Mapping** tab, verify/correct bone-to-humanoid-skeleton mapping.
5. Optionally adjust the **Muscles & Settings** tab (limits, stretch).
6. Optionally save the mapping as a **Human Template** (`.ht`) file for reuse on other models.
7. Optionally author an **Avatar Mask** to restrict which body parts specific animations/layers affect.

### Mapping tab (Avatar Configuration mode)
Reached via Avatar asset Inspector → **Configure Avatar**, or Model Rig tab → **Configure...**.

| Element | Description |
|---|---|
| Tab toggle (Mapping / Muscles & Settings) | Switch configuration views; must **Apply** or **Revert** pending changes before switching. |
| Body section buttons | Navigate the mapping diagram by region: Body, Head, Left Hand, Right Hand. |
| Dropdown menus | Mapping tools: **Clear**, **Automap**, **Load/Save** (Human Template `.ht`), Pose tools (**Sample Bind-Pose**, **Enforce T-Pose**). |
| Accept / Revert / Done | Commit, discard, or exit Avatar Configuration mode. |
| Bone indicators | Solid circle = required bone; dotted circle = optional (Unity interpolates automatically if unmapped). |
| Bone color | Green = successfully matched/valid; red = invalid/doesn't fit Avatar requirements. |

If automatic mapping fails, the manual workflow is: **Clear** existing mapping → **Sample Bind-Pose** → **Automap** → **Enforce T-Pose** → manually drag bones from the Scene/Hierarchy onto mapping slots → manually rotate any remaining misaligned bones.

### T-pose requirement
The **T-pose** — "the pose in which the character has their arms straight out to the sides, forming a 'T'" — is the mandatory default/bind pose for Humanoid Avatar setup. A `"Character not in T-Pose"` warning can appear even when bone assignment is otherwise correct, indicating a pose (not mapping) problem. Fix via the Mapping-tab pose tools (**Sample Bind-Pose** / **Enforce T-Pose**) rather than by re-mapping bones.

### Muscles & Settings tab
Configures per-muscle range of motion so retargeted animation deforms convincingly without self-overlap/artifacts across different body proportions.

| Section | Contents |
|---|---|
| Muscle Group Preview | High-level preset sliders (Torso, Head, Arms, Legs) that manipulate multiple bones at once for a quick visual check. |
| Per-Muscle Settings | Expandable per-bone range-of-motion limits, e.g. Head-Nod / Head-Tilt default range is −40 to 40 degrees — narrow this to add stiffness. |
| Additional Settings | `Left Arm Stretch` / `Right Arm Stretch`, `Left Leg Stretch` / `Right Leg Stretch`, `Feet Spacing`, Hand/Feet orientation, `Translate DoF` (enables translation, not just rotation, animation for Chest/UpperChest/Neck and leg/shoulder muscles — needed when rotation-only isn't enough). |

## Human Template (`.ht` files)
A **Human Template** stores a saved Humanoid bone mapping (YAML format) so it can be reused across multiple models. Save/Load it from the Mapping tab's dropdown menu. The **Human Template window** (opened by editing a `.ht` asset) shows each mapping entry as a **First** (target Humanoid bone name) / **Second** (source model bone name) pair, editable as text with full Undo support while the window is open.

## Avatar Mask
An `AvatarMask` (`class-AvatarMask`) defines which body parts/transforms an animation affects, reducing memory/CPU by excluding unused curves. Two authoring modes:

| Mode | Use case | How to author |
|---|---|---|
| Humanoid (body diagram) | Humanoid Avatars | Click body regions (Head, both Arms, both Hands, both Legs, Root) to cycle green (included) / red (excluded); double-click empty space to toggle all. Includes a separate IK toggle for hands/feet controlling whether IK curves are included in blending. |
| Transform hierarchy | Non-humanoid rigs, or fine-grained control | Assign an Avatar reference, click **Import Skeleton** to populate the hierarchy, check individual bones/transforms to include. |

Avatar Masks are used in two places:
- **Animation Layers** — assign a mask to a layer in the Animator Controller so that layer only drives the masked body parts (see [animator-controller.md](animator-controller.md)).
- **Import-time clip masking** — on the model importer's animation clip **Mask** tab, choose **Definition**: `Create From This Model` (single-use mask) or `Copy From Other Mask` (reuse a mask asset across clips); pick **Humanoid** (body diagram) or **Transform** (bone list) mode. This permanently strips unused curve data from the imported clip at import time — different from a runtime layer mask, which is applied live in the Animator Controller.

## Retargeting animation between Humanoid Avatars
Requirements: both the source (already animated, in-scene) and replacement model must be **Humanoid** with a properly configured Avatar; the replacement model should not yet be added to the scene when you configure its Avatar.

Workflow:
1. Set the replacement model's **Animation Type = Humanoid** in Import Settings.
2. Create its Avatar (**Create From This Model**).
3. Drag the replacement model into the scene.
4. Assign the **same Animator Controller** from the original model to the replacement's `Animator` component.
5. Assign the replacement's own configured **Avatar** to its `Animator` component.
6. Copy over any additional scripts/components from the original, adjusting values as needed.
7. Remove the original once the replacement behaves identically.

Both models must be in T-pose during Avatar configuration for retargeting to produce correct results.

## Root Motion (Humanoid)
- **Body Transform**: the character's mass-center reference used by Mecanim's retargeting engine; stores world-space orientation (averaged lower/upper body orientation relative to the Avatar's T-Pose). All muscle curves and IK goals (hands/feet) are stored relative to it.
- **Root Transform**: a runtime Y-plane projection of the Body Transform; Unity computes per-frame positional deltas from it and applies them to move the GameObject.
- Per-clip settings (Animation Clip Inspector, see [mecanim-overview.md](mecanim-overview.md)): **Root Transform Rotation**, **Root Transform Position (Y)**, **Root Transform Position (XZ)** — each has a **Bake Into Pose** toggle and a **Based Upon** choice (Body Orientation / Feet / Original / Offset). `Bake Into Pose` for Y effectively sets `Animator.gravityWeight`, determining whether physics or the animation curve drives vertical movement.
- Generic-rig models use a **Root Node** transform instead of the Body Transform for root motion, functioning similarly but without the humanoid muscle/IK relative-storage layer.
- **Scripting root motion**: when a clip is authored "in place" (no inherent translation), drive movement manually via the `OnAnimatorMove()` MonoBehaviour callback:

```csharp
private void OnAnimatorMove()
{
    Animator animator = this.GetComponent<Animator>();
    if (animator)
    {
        Vector3 newPosition = this.transform.position;
        newPosition.z += animator.GetFloat("Runspeed") * Time.deltaTime;
        this.transform.position = newPosition;
    }
}
```
Once `OnAnimatorMove` is implemented, the Animator component's **Apply Root Motion** field shows `Handled by Script`.

## Inverse Kinematics (Humanoid)
IK lets you drive a limb from a target/goal position and solve backward for joint orientation (opposite of forward kinematics). To enable:
1. Animator window → **Layers** pane → cog icon on the target layer → enable **IK Pass**.
2. This causes Unity to send an `OnAnimatorIK()` callback on that layer's evaluation.
3. Inside `OnAnimatorIK`, drive limbs via `Animator.SetIKPositionWeight`, `SetIKRotationWeight`, `SetIKPosition`, `SetIKRotation`, `SetLookAtPosition`, and `bodyPosition`/`bodyRotation`. Targets use `AvatarIKGoal` (e.g. `AvatarIKGoal.RightHand`, `AvatarIKGoal.LeftFoot`), each with independent position/rotation weight (0–1). Knee and elbow IK hints are also supported beyond the four limb goals.

This built-in Animator IK pass is distinct from Unity's separate **Animation Rigging** package (`com.unity.animation.rigging`, constraint-based runtime rigging) — that package is not covered by this skill; see Edge cases in [SKILL.md](../SKILL.md).

## Practical guidance
- Configure Avatars **before** adding a model to the scene when retargeting — the workflow assumes the replacement is still a Project asset at configuration time.
- Always verify/enforce T-pose before trusting a red/yellow mapping diagnostic — a `"Character not in T-Pose"` warning is a pose problem, not necessarily a bone-mapping problem; don't waste time re-mapping bones for a pose issue.
- Name bones descriptively (e.g. `LeftArm`, `RightForearm`) — Unity's **Automap** relies partly on naming heuristics, and clear names reduce manual-mapping work.
- Only required (solid-circle) bones must be mapped for a valid Humanoid Avatar; optional (dotted-circle) bones are auto-interpolated if left unmapped — don't over-map for gameplay you don't need.
- Prefer using a **Human Template** (`.ht`) to replicate a known-good bone mapping across many similarly-rigged characters instead of hand-mapping each one from scratch — faster and removes a class of manual-mapping error.
- Use an **Avatar Mask** on an Animator layer (not import-time clip masking) when you need runtime-adjustable body-part restriction (e.g. an upper-body-only action layer over a full-body locomotion layer); use import-time masking instead when the restriction is permanent and you want the smaller processed clip data (memory/CPU win) baked in at import.
- `Translate DoF` in Muscles & Settings is off by default — only enable it for the specific muscles that actually need translation (not just rotation) animation; leaving it on unnecessarily adds retargeting complexity for no gameplay benefit (YAGNI, per `coding-principles.md`).
- Because Shared Core (`Game.Core.*`) must stay Unity-free (per `coding-principles.md`'s Shared Core integrity rule), IK/Avatar decisions belong in `Game.Client.*` — `OnAnimatorMove`/`OnAnimatorIK` callbacks and any Avatar/IK-goal resolution stay in Client-layer MonoBehaviours; only pass the already-resolved outcome (e.g. a target `Vector3`) into Shared Core if gameplay rules need to react to it.
