# Placeholder Sprites

Source: https://docs.unity3d.com/Manual/sprite/placeholder/placeholder-landing.html

## What they are

Placeholder sprites are built-in, white, primitive 2D shapes Unity ships so a scene can be blocked out before final art exists. They let a feature get wired up (Sprite Renderer, sorting, colliders, animation) without waiting on the art pass.

## How to add one

1. Confirm the **2D Sprite** package is installed in the project.
2. **GameObject > 2D Object > Sprites**.
3. Pick a shape from the menu (primitive shapes such as square, circle/round, capsule, diamond, hexagon, and a 9-sliced variant are exposed here — the exact list is Unity-version-dependent; check the live menu rather than assuming a fixed set).

This creates a GameObject with a `SpriteRenderer` already wired to the chosen placeholder sprite — no manual component setup needed.

## Key constraint

> "You can't edit a placeholder sprite or its texture in the Sprite Editor."

Placeholder sprites are not backed by an importable texture asset in the project — they're generated procedurally. To move from a placeholder to final art:

1. Select the placeholder GameObject.
2. On its `SpriteRenderer` component, click the Sprite picker.
3. Choose the imported sprite that replaces it.

Nothing else about the GameObject (sorting layer, order in layer, collider, animation bindings) needs to change — only the `Sprite` reference is swapped.

## When to use this vs. skipping straight to real art

- Use placeholders when a Tech Spec's gameplay logic needs to be testable before art is ready, or when blocking out layout/composition in the Scene view.
- Don't use placeholders as a substitute for real import settings review — once real art lands, the full [import-settings.md](import-settings.md) pass (Sprite Mode, Pixels Per Unit, Mesh Type, pivot, physics shape) still applies; a placeholder swap does not carry those decisions over automatically.
