# Events & Manipulators — Propagation, Pointer/Mouse, Focus, Capture

Sources: [Control behavior with events](https://docs.unity3d.com/Manual/UIE-Events.html), [Event dispatch](https://docs.unity3d.com/Manual/UIE-Events-Dispatching.html), [Handle events](https://docs.unity3d.com/Manual/UIE-Events-Handling.html), [Handle events in a custom control](https://docs.unity3d.com/Manual/UIE-events-handling-custom-control.html), [Pointer events](https://docs.unity3d.com/Manual/UIE-Pointer-Events.html), [Mouse events](https://docs.unity3d.com/Manual/UIE-Mouse-Events.html), [Click events](https://docs.unity3d.com/Manual/UIE-Click-Events.html), [Focus order](https://docs.unity3d.com/Manual/UIE-focus-order.html), [Focus events](https://docs.unity3d.com/Manual/UIE-Focus-Events.html), [Capture the pointer](https://docs.unity3d.com/Manual/UIE-capture-the-pointer.html), [Capture events](https://docs.unity3d.com/Manual/UIE-Capture-Events.html), [Manipulators](https://docs.unity3d.com/Manual/UIE-manipulators.html), [Synthesize events](https://docs.unity3d.com/Manual/UIE-Events-Synthesizing.html), [IMGUI events](https://docs.unity3d.com/Manual/UIE-IMGUI-Events.html).
Covers: SKILL.md §4 — **"Wire behavior through typed `RegisterCallback<T>` events and Manipulators, never string-based dispatch"**.

How input reaches a `VisualElement` and how a control reacts to it: the
propagation model, the pointer/mouse event families, focus, pointer
capture, and packaging interaction logic as a `Manipulator`.

## Table of contents
- [Propagation](#propagation)
- [Pointer vs Mouse events](#pointer-vs-mouse-events)
- [Focus and focus ring](#focus-and-focus-ring)
- [Pointer capture](#pointer-capture)
- [Manipulators](#manipulators)
- [Synthesizing events](#synthesizing-events)

## Propagation

| Subject | What it decides | Source |
|---|---|---|
| Two-phase dispatch | **TrickleDown** (root → target) runs first, then **BubbleUp** (target → root); an element registered for both receives the event twice | [Event dispatch](https://docs.unity3d.com/Manual/UIE-Events-Dispatching.html) |
| `EventBase.target` vs `.currentTarget` | `target` is fixed for the whole dispatch; `currentTarget` changes to whichever element's callback is currently executing | [Event dispatch](https://docs.unity3d.com/Manual/UIE-Events-Dispatching.html) |
| Default picking | `PickingMode.Position` — hit-testing uses the element's position rectangle | [Event dispatch](https://docs.unity3d.com/Manual/UIE-Events-Dispatching.html) |
| Disabled/hidden elements | Don't receive the event themselves, but propagation still passes through them on the path | [Event dispatch](https://docs.unity3d.com/Manual/UIE-Events-Dispatching.html) |
| `RegisterCallback<T>(cb, TrickleDown.TrickleDown)` | Registers for the trickle-down phase; omitting the argument registers bubble-up. Same callback can only be registered once per event type + phase | [Handle events](https://docs.unity3d.com/Manual/UIE-Events-Handling.html) |
| `StopPropagation()` vs `StopImmediatePropagation()` | The former lets the current element finish its remaining callbacks then halts; the latter halts immediately, skipping even the current element's other callbacks | [Handle events in a custom control](https://docs.unity3d.com/Manual/UIE-events-handling-custom-control.html) |
| `HandleEventBubbleUp`/`HandleEventTrickleDown` overrides | Preferred inside a custom control's own class — skips the callback-registry lookup cost `RegisterCallback` pays | [Handle events in a custom control](https://docs.unity3d.com/Manual/UIE-events-handling-custom-control.html) |
| `SetValueWithoutNotify(v)` | Sets a control's value without firing `ChangeEvent<T>` — the deliberate way to avoid re-triggering listeners | [Handle events](https://docs.unity3d.com/Manual/UIE-Events-Handling.html) |

```csharp
// Named-method registration — required for anything tied to a control's
// lifetime, per coding-principles.md's Event handlers rule.
button.RegisterCallback<ClickEvent>(OnAttackClicked);
// ... and in a matching teardown path:
button.UnregisterCallback<ClickEvent>(OnAttackClicked);
```

## Pointer vs Mouse events

| Subject | What it decides | Source |
|---|---|---|
| Ordering | Pointer events always precede their corresponding Mouse event; use Pointer events for new code — they unify touch, pen, and mouse | [Pointer events](https://docs.unity3d.com/Manual/UIE-Pointer-Events.html) |
| Mouse event scope | "Mouse" means a physical or virtual mouse only — touch/pen never raise Mouse events, only Pointer events | [Mouse events](https://docs.unity3d.com/Manual/UIE-Mouse-Events.html) |
| `PointerEnterEvent`/`PointerLeaveEvent` | Trickle only, **do not bubble** — fire when the pointer enters/leaves the element and all its descendants | [Pointer events](https://docs.unity3d.com/Manual/UIE-Pointer-Events.html) |
| `PointerOverEvent`/`PointerOutEvent` | Trickle **and** bubble, unlike Enter/Leave | [Pointer events](https://docs.unity3d.com/Manual/UIE-Pointer-Events.html) |
| `ClickEvent` | Fires when a pointer-down and pointer-up occur on the same element (pointer may move between); trickles + bubbles + cancellable | [Click events](https://docs.unity3d.com/Manual/UIE-Click-Events.html) |
| Restricting a handler to the target only | `if (evt.propagationPhase != PropagationPhase.AtTarget) return;` inside a bubbling handler | [Click events](https://docs.unity3d.com/Manual/UIE-Click-Events.html) |

## Focus and focus ring

| Subject | What it decides | Source |
|---|---|---|
| `tabIndex` | `0` = default DFS tab order; `>0` = prioritized ahead of `0`; `<0` = removed from tab navigation entirely | [Focus order](https://docs.unity3d.com/Manual/UIE-focus-order.html) |
| Default order | A depth-first search over the visual tree, unless `tabIndex` overrides it | [Focus order](https://docs.unity3d.com/Manual/UIE-focus-order.html) |
| `delegatesFocus` | When true, forwards focus to a suitable child instead of taking it directly | [Focus order](https://docs.unity3d.com/Manual/UIE-focus-order.html) |
| `Focus()`/`Blur()` | Programmatic requests; the actual change is deferred until the current callback finishes | [Focus order](https://docs.unity3d.com/Manual/UIE-focus-order.html) |
| `FocusOutEvent`/`FocusInEvent` | Bubble; sent along the whole path **just before** the change occurs | [Focus events](https://docs.unity3d.com/Manual/UIE-Focus-Events.html) |
| `FocusEvent`/`BlurEvent` | Target-only, do **not** bubble; sent **immediately after** the change completes | [Focus events](https://docs.unity3d.com/Manual/UIE-Focus-Events.html) |

## Pointer capture

| Subject | What it decides | Source |
|---|---|---|
| `PointerCaptureHelper.CapturePointer()`/`.ReleasePointer()` | Only one element application-wide can hold capture; while held, that element is the target of all subsequent pointer events except mouse wheel | [Capture the pointer](https://docs.unity3d.com/Manual/UIE-capture-the-pointer.html) |
| Forced release | Capturing while another element already holds capture forces that element to lose it, firing `PointerCaptureOutEvent` on it | [Capture the pointer](https://docs.unity3d.com/Manual/UIE-capture-the-pointer.html) |
| Typical use | Buttons/sliders/scrollbars capture on `PointerDownEvent` so drag continues to reach them even once the pointer leaves the control's bounds | [Capture the pointer](https://docs.unity3d.com/Manual/UIE-capture-the-pointer.html) |

## Manipulators

| Subject | What it decides | Source |
|---|---|---|
| `Manipulator` base class | Separates interaction logic from the element it attaches to, so it is reusable without subclassing the element itself | [Manipulators](https://docs.unity3d.com/Manual/UIE-manipulators.html) |
| `Clickable` | Extends `PointerManipulator`; tracks whether a press and release both landed on the same element | [Manipulators](https://docs.unity3d.com/Manual/UIE-manipulators.html) |
| `AddManipulator()`/`RemoveManipulator()` | Attach/detach API on `VisualElement` | [Manipulators](https://docs.unity3d.com/Manual/UIE-manipulators.html) |
| Required overrides | `RegisterCallbacksOnTarget()`/`UnregisterCallbacksFromTarget()` — the two methods a custom `Manipulator` must implement | [Manipulators](https://docs.unity3d.com/Manual/UIE-manipulators.html) |
| Drag tracking | Expected to use pointer capture to track a drag reliably once the pointer leaves the element's bounds | [Manipulators](https://docs.unity3d.com/Manual/UIE-manipulators.html) |

## Synthesizing events

| Subject | What it decides | Source |
|---|---|---|
| `SomeEvent.GetPooled(...)` | Events come from an internal pool, not `new` — wrap in a `using` block so the event returns to the pool | [Synthesize events](https://docs.unity3d.com/Manual/UIE-Events-Synthesizing.html) |
| `panel.visualTree.SendEvent()` | Entry point for dispatching a manually synthesized event | [Synthesize events](https://docs.unity3d.com/Manual/UIE-Events-Synthesizing.html) |
| Default targets | Untargeted events route to the root; keyboard events target the focused element; pointer events target whatever is under the pointer | [Synthesize events](https://docs.unity3d.com/Manual/UIE-Events-Synthesizing.html) |

**Critical caveat**: never manually send an event that is not OS-derived
(e.g. a `PointerCaptureEvent`) — the Manual warns this "causes elements to
assume underlying conditions are met without actual state changes," an
undefined-behavior trap rather than a convenience shortcut.
