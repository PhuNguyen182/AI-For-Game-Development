# Root Links — Input System 1.20

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to `com.unity.inputsystem@1.20`. Unlike
several other Unity subjects, this package has no built-in engine counterpart
to reconcile — everything here lives in one package with one Manual tree. The
one genuine split is this package against the legacy Input Manager that still
ships with the Editor, which [migration-and-settings.md](migration-and-settings.md) owns.

## Roots

| Root | Holds | Source |
|---|---|---|
| Manual | Concepts, workflows, components, platform notes | [Input System Manual index](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/index.html) |
| Full table of contents | The complete chapter tree, for anything no file here cites | [Table of contents](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/TableOfContents.html) |
| Scripting API | Every type in `UnityEngine.InputSystem` and its sub-namespaces | [API index](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/api/UnityEngine.InputSystem.html) |

## Which file answers which question

| Question | File | Source |
|---|---|---|
| Which backend is the project even running | [migration-and-settings.md](migration-and-settings.md) | [Enable the correct input system](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/enable-correct-input-system.html) |
| How do I author what the player can do | [actions-bindings-and-assets.md](actions-bindings-and-assets.md) | [Actions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Actions.html) |
| Why does this action never reach Performed | [interactions-and-processors.md](interactions-and-processors.md) | [Interactions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Interactions.html) |
| Why do input and physics disagree | [architecture-and-update-loop.md](architecture-and-update-loop.md) | [Update Mode](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/update-mode.html) |
| How do several local players work | [player-input-and-multiplayer.md](player-input-and-multiplayer.md) | [Player Input component](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/player-input-component.html) |
| How does UI or a touch control receive input | [devices-and-ui-integration.md](devices-and-ui-integration.md) | [Input for user interfaces](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/ui-input.html) |
| How do players change their own controls | [rebinding.md](rebinding.md) | [User rebinding at runtime](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/user-rebinding-runtime.html) |
| Why is the binding not resolving at runtime | [editor-tooling-and-debugging.md](editor-tooling-and-debugging.md) | [Input debugger window](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/the-input-debugger-window.html) |

## Core type index

| Type | Source |
|---|---|
| `InputSystem` | [InputSystem](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/api/UnityEngine.InputSystem.InputSystem.html) |
| `InputAction`, `InputActionMap`, `InputActionAsset` | [UnityEngine.InputSystem namespace](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/api/UnityEngine.InputSystem.html) |
| `InputActionReference` | [InputActionReference](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/api/UnityEngine.InputSystem.InputActionReference.html) |
| `PlayerInput`, `PlayerInputManager` | [PlayerInput](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/api/UnityEngine.InputSystem.PlayerInput.html) |
| `InputDevice`, `InputControl\<TValue\>` | [InputDevice](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/api/UnityEngine.InputSystem.InputDevice.html) |
| `InputActionRebindingExtensions` | [InputActionRebindingExtensions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/api/UnityEngine.InputSystem.InputActionRebindingExtensions.html) |

Keep the `@1.20` segment when following any link from this skill; page slugs
are stable across nearby package versions, so substitute the installed
version from `Packages/manifest.json` rather than assuming this one.
