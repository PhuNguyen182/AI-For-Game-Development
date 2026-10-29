# `device_playtest.py` commands

Synthesized from [device_playtest.py](../scripts/device_playtest.py).

`--platform` is required on every command but `devices`; `--device` (adb serial or iOS UDID) is accepted on every command but `devices` and `doctor`, and needed once two devices are attached.

| Command | Args | Non-obvious |
|---|---|---|
| `devices` | — | `adb devices -l`, `idevice_id -l` (+ `idb list-targets`), for whichever is on PATH |
| `doctor` | — | Android: `adb` + one device in state `device` (authorized). iOS: `idevice_id`, `idb`, `idb_companion` + one paired device |
| `install` | `path` | Android `install -r` replaces an installed build |
| `launch` | `app_id [--activity]` | Android default is `monkey -p <app_id>` (launcher, no activity name needed); `--activity` → `am start -n` |
| `stop`, `uninstall` | `app_id` | — |
| `screenshot` | `out_path` | — |
| `tap`, `swipe` | `x y` / `x1 y1 x2 y2 [--duration-ms]` | — |
| `text` | `value` | Android sends spaces as `%s` |
| `keyevent` | `code` | Android: numeric keycode. iOS: named button (`HOME`, `LOCK`, `SIRI`, `SIDE_BUTTON`). The wrong kind fails |
| `pull-logs` | `out_dir [--package]` | Android: `logcat_crash.txt`, `logcat_full.txt`, `logcat_fatal_exception.txt`, and `logcat_anr.txt` with `--package`. iOS: crash reports of all apps, left on the device so earlier ones return — use a fresh `out_dir` per pull; + 5 s `syslog.txt` |
