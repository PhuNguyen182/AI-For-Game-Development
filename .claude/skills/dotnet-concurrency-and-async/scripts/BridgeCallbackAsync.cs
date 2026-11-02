// TaskCompletionSource bridge: a callback-based SDK method awaited as a Task, handlers detached in finally.
// Adapt into: <Feature>/Server/<SdkWrapper>.cs or an IO/service wrapper outside the PlayerLoop, as a private static method.
// Unverified: not compiled or run (no Unity project in this repo).
private static async Task<int> BridgeCallbackAsync(ThirdPartySdk sdk)
{
    // RunContinuationsAsynchronously: the SDK's callback thread must not run our continuation inline.
    var tcs = new TaskCompletionSource<int>(TaskCreationOptions.RunContinuationsAsynchronously);
    void OnComplete(int result) => tcs.TrySetResult(result);
    void OnError(Exception ex) => tcs.TrySetException(ex);
    sdk.OnComplete += OnComplete;
    sdk.OnError += OnError;
    try
    {
        sdk.Start();
        return await tcs.Task;
    }
    finally
    {
        sdk.OnComplete -= OnComplete;
        sdk.OnError -= OnError;
    }
}
