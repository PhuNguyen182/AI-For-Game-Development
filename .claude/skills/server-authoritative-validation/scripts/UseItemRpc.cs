// NGO server Rpc: sender from RpcParams, rate limit first, owner check, Core decides, rejection to the sender only.
// Adapt into: the NetworkBehaviour that owns the Rpc (method only)
// Unverified: not compiled or run (no Unity project in this repo).
[Rpc(SendTo.Server)]
public void UseItemRpc(int slot, RpcParams rpcParams = default)
{
    ulong sender = rpcParams.Receive.SenderClientId;
    if (!this._limiter.TryConsume(sender, this._clock.Tick))
        return;

    if (this.OwnerClientId != sender)
    {
        this.RejectToSender(sender, UseItemRejection.NotAllowed);
        return;
    }

    // Core decides; the handler only applies an accepted result.
    UseItemResult result = this._inventoryRules.TryUse(this._inventory, slot, this._clock.Tick);
    if (!result.IsAccepted)
    {
        this.RejectToSender(sender, result.Rejection);
        return;
    }

    this._inventory = result.Inventory;
}
