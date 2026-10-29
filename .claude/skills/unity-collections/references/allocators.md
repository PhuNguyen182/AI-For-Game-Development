# Allocators

Source: [Use allocators](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocation.html), [Allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-overview.html), [Rewindable allocator](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-rewindable.html), [Custom allocator](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-custom-use.html).

`Native-` and `Unsafe-` memory is outside the GC: every allocation is deallocated explicitly or it leaks.

## Built-in
| Allocator | Behaviour | Use when |
|---|---|---|
| `Temp` | Fastest; auto-freed at end of frame or job; cannot cross threads | Consumed within the frame or job that made it |
| `TempJob` | Dispose within ~4 frames or a leak warning is raised | Outlives one job, not the frame's job chain |
| `Persistent` | Slowest; indefinite; always disposed manually | Lives across frames with no defined checkpoint |

## Disposal
- `Dispose()`: frees now; illegal while a job still reads the container.
- `Dispose(JobHandle)`: defers the free until the handle completes and returns a new handle.
- `IsCreated`: per allocation, not per copy; every struct copy and alias reports `true` until the one allocation is freed, so it cannot say which copy owns it.

## Rewindable allocator
Use when many short-lived allocations share one release point and per-allocation `Dispose()` bookkeeping is the actual cost.
- Bump allocation from pre-allocated blocks; one rewind frees every allocation it made.
- Blocks are 64-byte aligned, double in size up to a cap, then grow linearly; a rewind keeps some blocks for reuse and releases others.
- Created through `AllocatorHelper`.

## Custom allocator
Use only for a lifetime or strategy neither the built-in three nor rewindable covers.
- Create via `AllocatorHelper`, register globally, then initialize.
- `Native-`: `CollectionHelper.CreateNativeArray` / `CollectionHelper.Dispose`. `Unsafe-`: `AllocatorManager.Allocate` / `AllocatorManager.Free`.
- Teardown order is load-bearing: rewind the handle, unregister it, then free its backing memory. Unregistering before rewinding leaks the held blocks, unreported.

## Example
An Editor importer makes thousands of small allocations over many frames, all dead at import end: `TempJob` fails (lifetime over ~4 frames), `Persistent` means thousands of `Dispose()` calls. Use a rewindable allocator, `CollectionHelper.CreateNativeArray`, one rewind at the end.
