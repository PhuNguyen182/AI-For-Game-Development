# iOS real-device setup — idb + WebDriverAgent

Sources: [a] https://fbidb.io/docs/installation, [b] https://libimobiledevice.org.

`idb_companion` is macOS-only; on Windows/Linux iOS is `Status: Blocked`.

## One-time setup, macOS host

| Step | How |
|---|---|
| libimobiledevice (`idevice_id`, `idevicecrashreport`, `idevicesyslog`, `idevicepair`) | `brew install libimobiledevice` [b] |
| Pair | USB, trust the host on the device, check `idevice_id -l`; not listed → `idevicepair pair` |
| idb | `brew install idb-companion`, `pip3 install fb-idb`; check `idb list-targets` [a] |
| WebDriverAgent (every `idb ui *` call needs it running) | Build and sign from Facebook's `WebDriverAgent` repo (`xcodebuild ... -scheme WebDriverAgentRunner test`) with an Apple Team ID and a provisioning profile covering the device UDID |
| Confirm WDA | `idb ui tap --udid <udid> 1 1` on a foreground app returns without error — the only check. `doctor` stops at binaries + pairing; a `doctor` pass then a `idb ui` failure means rebuild WDA |

## Recurring failures

| Symptom | Cause → fix |
|---|---|
| `idb ui *` signing/trust error after it worked | Profile expired (free Apple ID 7 days, paid ~1 year) → rebuild and reinstall WDA, not a device or script fault |
| WDA will not install after a major iOS update | Rebuild WDA against the newer Xcode/SDK |
| `idevice_id -l` drops a known device | Host or device reset → `idevicepair pair`, accept trust again |
