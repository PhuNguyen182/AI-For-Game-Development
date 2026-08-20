# Baking & Authoring Workflow

Covers SKILL.md step 4 (converting GameObject-based authoring data into entities).

## Manual
- [Baking](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/baking.html) — transforms GameObject authoring data in the Editor into entities written to entity scenes; runs only in-Editor, never at runtime.
- [Baking overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/baking-overview.html) — how authoring GameObjects/MonoBehaviours become optimized ECS entities/components.
- [Baker overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/baking-baker-overview.html) — the `Baker<TAuthoring>` class defines the conversion from an authoring component to entity data.
- [Baking phases](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/baking-phases.html) — Baker phase (authoring → entities/components) followed by baking-systems phase (additional processing on the baked entities).
- [ECS authoring and baking workflow](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/ecs-workflow-example-authoring-baking.html) — worked example of the full authoring-component → Baker → baked-entity pipeline.
