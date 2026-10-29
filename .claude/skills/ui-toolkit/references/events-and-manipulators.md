# Events and Manipulators

Sources: [Events](https://docs.unity3d.com/Manual/UIE-Events.html), [Dispatch](https://docs.unity3d.com/Manual/UIE-Events-Dispatching.html), [Handling](https://docs.unity3d.com/Manual/UIE-Events-Handling.html), [Custom control](https://docs.unity3d.com/Manual/UIE-events-handling-custom-control.html), [Pointer](https://docs.unity3d.com/Manual/UIE-Pointer-Events.html), [Click](https://docs.unity3d.com/Manual/UIE-Click-Events.html), [Focus order](https://docs.unity3d.com/Manual/UIE-focus-order.html), [Focus events](https://docs.unity3d.com/Manual/UIE-Focus-Events.html), [Capture](https://docs.unity3d.com/Manual/UIE-capture-the-pointer.html), [Manipulators](https://docs.unity3d.com/Manual/UIE-manipulators.html), [Synthesize](https://docs.unity3d.com/Manual/UIE-Events-Synthesizing.html).

## Propagation
- TrickleDown (root → target) then BubbleUp (target → root). Registered for both = received twice.
- `target` is fixed for the dispatch; `currentTarget` is the element whose callback is running.
- Default `PickingMode.Position` (hit-test on position rect). Disabled/hidden elements get no event but propagation passes through.
- `RegisterCallback<T>(cb, TrickleDown.TrickleDown)` = trickle phase; default is bubble. The same callback registers once per event type + phase.
- `StopPropagation()` lets the current element finish its callbacks; `StopImmediatePropagation()` skips even those.
- Inside a custom control, override `HandleEventBubbleUp`/`HandleEventTrickleDown` instead of `RegisterCallback` (skips registry lookup).
- `SetValueWithoutNotify(v)` sets a value without firing `ChangeEvent<T>`.
- Restrict a bubbling handler to the target: `if (evt.propagationPhase != PropagationPhase.AtTarget) return;`

```csharp
button.RegisterCallback<ClickEvent>(OnAttackClicked);   // named method
button.UnregisterCallback<ClickEvent>(OnAttackClicked); // in the teardown path
```

## Pointer vs mouse
- Pointer events precede the matching Mouse event; use Pointer for new code (touch, pen, mouse). Touch/pen never raise Mouse events.
- `PointerEnter`/`PointerLeave`: trickle only, no bubble, cover descendants. `PointerOver`/`PointerOut`: trickle and bubble.
- `ClickEvent`: pointer-down and -up on the same element (pointer may move between); trickles, bubbles, cancellable.

## Focus
- `tabIndex`: `0` = default depth-first order; `>0` prioritized; `<0` removed from tabbing. `delegatesFocus` forwards focus to a suitable child.
- `Focus()`/`Blur()` take effect after the current callback finishes.
- `FocusOut`/`FocusIn`: bubble, sent just before the change. `Focus`/`Blur`: target-only, sent right after.

## Pointer capture
- `PointerCaptureHelper.CapturePointer()`/`ReleasePointer()`: one holder app-wide; it receives all pointer events except wheel. A new capture forces the old holder to lose it (`PointerCaptureOutEvent`).
- Capture on `PointerDownEvent` so a drag keeps reaching the control outside its bounds.

## Manipulators
- Separate interaction logic from the element. `AddManipulator()`/`RemoveManipulator()`; a custom one overrides `RegisterCallbacksOnTarget()`/`UnregisterCallbacksFromTarget()`. `Clickable` extends `PointerManipulator`.

## Synthesizing
- Get events from the pool (`SomeEvent.GetPooled(...)` in a `using`), send with `panel.visualTree.SendEvent()`. Untargeted events go to the root; keyboard to the focused element; pointer to the element under it.
- Never send a non-OS-derived event (e.g. `PointerCaptureEvent`): elements assume conditions that did not change.
