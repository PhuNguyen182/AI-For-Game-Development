// Members for an OSA adapter that adopts pre-made rows: OnInitialized buffers them, CreateViewsHolder binds each one to a negative index.
// Adapt into: the project's OSA adapter class (derives OSA<TParams, TItemViewsHolder>), or Assets/_Project/Scripts/<Feature>/Views/<Name>Adapter.cs when none exists (members only)
// Needs in the host class: a _PreMadeViews list of pre-made row roots, and the project's MyItemViewsHolder type.
// Unverified: not compiled or run (no Unity project in this repo).
protected override void OnInitialized()
{
    base.OnInitialized();
    var vhs = CreateBufferredRecycleableItems(_PreMadeViews.Count);
    AddBufferredRecycleableItems(vhs);
    // Buffered items must survive count changes and rebuilds.
    _Params.optimization.KeepItemsPoolOnEmptyList = true;
    _Params.optimization.KeepItemsPoolOnLayoutRebuild = true;
}

protected override MyItemViewsHolder CreateViewsHolder(int itemIndex)
{
    var instance = new MyItemViewsHolder();
    if (itemIndex < 0)
    {
        var root = _PreMadeViews[_PreMadeViews.Count - 1];
        _PreMadeViews.RemoveAt(_PreMadeViews.Count - 1);
        instance.InitWithExistingRoot(root, _Params.Content, itemIndex);
    }
    else
        instance.Init(_Params.ItemPrefab, _Params.Content, itemIndex); // or throw
    return instance;
}
