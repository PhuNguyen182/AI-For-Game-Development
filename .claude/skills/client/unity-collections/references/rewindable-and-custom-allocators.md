# Rewindable & Custom Allocators

Covers SKILL.md step 6's escalation path (when the basic three allocators don't fit the data's actual lifetime).

## Manual
- [Rewindable allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-rewindable.html) — a fast, thread-safe custom allocator that behaves like a linear allocator: it pre-allocates memory blocks (64-byte minimum alignment), hands out ranges from them on request, and — its main advantage — lets you free every allocation it made at once by "rewinding" it, instead of disposing each one individually. Blocks double in size until a cap, then grow linearly; rewinding keeps some blocks around for reuse while releasing others. Use `AllocatorHelper` to create one.
- [Use a custom allocator](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-custom-use.html) — declare/create via `AllocatorHelper`, register it globally, and initialize it; allocate `Native-` collections through `CollectionHelper.CreateNativeArray`/`CollectionHelper.Dispose`, and `Unsafe-` collections through `AllocatorManager.Allocate`/`AllocatorManager.Free`; dispose by rewinding the allocator handle, unregistering, and freeing its backing memory. Reserve this for an intermediate-lifetime need neither Temp/TempJob/Persistent nor a rewindable allocator covers.
