# Animator Override Controller

Pages: `AnimatorOverrideController`, `ScriptReference/AnimatorOverrideController`.

- Replaces which clip each state plays; states, transitions, parameters and layers stay shared, so one graph is the single source of truth. A duplicated controller drifts the first time a transition is edited in one copy.
- Can be chained (species variant + equipment variant compose). An empty slot falls back to the base clip, so list only what differs.
- Apply overrides as one batch (`ApplyOverrides` with the list of pairs): the indexer replaces one clip and re-resolves per assignment. `GetOverrides` reads current pairs, to change some without discarding others.
- Swapping the runtime controller resets state: apply on a deliberate event (equip change), not per frame.

**Timing constraint:** a transition with a fixed duration in seconds can outlast a shorter override clip, so it never visibly completes, only on the short variants. Author transition timing in normalised time (exit time as a fraction and transition offset are already normalised) on any graph that will be overridden.
