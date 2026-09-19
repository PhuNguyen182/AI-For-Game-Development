# iOS real-device setup — idb + WebDriverAgent

This is genuinely heavier than the Android path: `adb` needs only USB
debugging enabled on the device. Real-device iOS input injection needs a
signed, running on-device agent, which needs a paired macOS host and an
Apple developer identity. Read this before assuming `doctor --platform ios`
passing means input injection will actually work — `doctor` can only confirm
the binaries and pairing exist, not that WebDriverAgent is currently running.

## Why this is macOS-only

`idb_companion` depends on private Apple frameworks that only exist on
macOS — it cannot run on Linux or Windows, at all. If this skill is invoked
from a non-macOS host, the iOS branch of `device_playtest.py` cannot execute
regardless of setup; the same caveat `/investigate-device-crash` already
states for its own iOS section. On a Linux host, iOS device work under this
skill is structurally unavailable — report `Status: Blocked` rather than
attempting a workaround.

## One-time setup, on the macOS host

1. **Install `libimobiledevice`** (provides `idevice_id`, `idevicecrashreport`,
   `idevicesyslog`, `idevicepair`) — e.g. via Homebrew: `brew install
   libimobiledevice`.
2. **Pair the device with the host**: connect over USB, trust the host on
   the device when prompted, then confirm with `idevice_id -l`. If the
   device does not appear, `idevicepair pair` re-triggers the trust prompt.
3. **Install `idb` and `idb_companion`** (Facebook's iOS Debug Bridge) —
   e.g. `brew install idb-companion` then `pip3 install fb-idb`. Confirm with
   `idb list-targets`.
4. **Build and sign WebDriverAgent** for the target device — this needs a
   real Apple Developer Team ID and a provisioning profile that covers the
   device's UDID. `idb` can drive this via `idb_companion --udid <udid>` once
   Xcode has WDA's scheme configured with that team, or it can be built
   directly from Facebook's `WebDriverAgent` repo in Xcode
   (`xcodebuild ... -scheme WebDriverAgentRunner test`).
5. **Confirm WDA is actually running**: `idb ui tap --udid <udid> 1 1`
   against a foreground app should return without error. This is the only
   real confirmation — `doctor`'s checks stop at "the binaries and pairing
   exist" and cannot see whether WDA is currently alive on the device.

## Recurring maintenance

- **Signing expiry**: a free Apple ID's provisioning profile expires after
  7 days; a paid Apple Developer Program profile lasts about a year. When
  `idb ui *` starts failing with a signing/trust error after previously
  working, this is almost always why — rebuild and reinstall WDA rather than
  treating it as a device or script fault.
- **Device OS updates**: a major iOS update can require rebuilding WDA
  against a newer Xcode/SDK before it will install again.
- **Re-pairing after a host or device reset**: if `idevice_id -l` stops
  listing a previously-working device, re-run `idevicepair pair` and accept
  the trust prompt again before assuming a deeper fault.

## What `doctor --platform ios` does and does not confirm

Confirms: `idevice_id`, `idb`, and `idb_companion` are on `PATH`, and at
least one device is visible to `idevice_id -l`.

Does **not** confirm: that WebDriverAgent is built, signed, installed, or
currently running on that device. A `doctor` pass followed by an `idb ui
tap` failure almost always means WDA needs (re)building per step 4/5 above,
not that the script or device is broken.
