# `device_playtest.py` — CLI reference

Every subcommand echoes the literal command it is about to run to stderr
before executing it, so the transcript itself is usable as
`defect-reporting.md` evidence. Exit code is non-zero only on a tool-level
failure (missing binary, device unreachable) — never on an app-level
outcome, since the script has no way to judge whether an app-level outcome
is right or wrong. That judgment stays with the calling agent.

Run `python3 scripts/device_playtest.py <command> --help` for the exact
flag list; this file documents what each command does per platform and why.

## Device targeting

Every command except `devices` takes `--platform android|ios` (required) and
`--device <id>` (optional — omit it to let `adb`/`idb` pick the only
connected device; required once more than one device is attached). `--device`
is an adb serial on Android, an iOS UDID on iOS.

## Device detection

Reuses `/investigate-device-crash`'s existing commands verbatim — this
script does not introduce a second device-detection convention.

| Command | What it runs |
|---|---|
| `devices` | `adb devices -l` (if `adb` is on `PATH`) and `idevice_id -l` (+ `idb list-targets` if `idb` is present) |
| `doctor --platform android` | Confirms `adb` is on `PATH` and at least one device answers `adb devices -l` |
| `doctor --platform ios` | Confirms `idevice_id`, `idb`, and `idb_companion` are all on `PATH`, and at least one device answers `idevice_id -l`. Cannot confirm WebDriverAgent is actually running — see `ios-idb-setup.md`. |

## Lifecycle

| Command | Android (`adb`) | iOS (`idb`) |
|---|---|---|
| `install <path>` | `adb [-s <serial>] install -r <path>` | `idb install [--udid <udid>] <path>` |
| `launch <app_id> [--activity <name>]` | Default: `adb shell monkey -p <app_id> -c android.intent.category.LAUNCHER 1` (no activity name needed). With `--activity`: `adb shell am start -n <app_id>/<activity>` | `idb launch [--udid <udid>] <bundle_id>` |
| `stop <app_id>` | `adb shell am force-stop <app_id>` | `idb terminate [--udid <udid>] <bundle_id>` |
| `uninstall <app_id>` | `adb uninstall <app_id>` | `idb uninstall [--udid <udid>] <bundle_id>` |

`launch` defaults to `monkey` on Android because it only needs the package
name, not the launcher activity's class name, which a caller often does not
have. Pass `--activity` when a specific entry point (not the launcher
activity) needs targeting.

## Evidence capture

| Command | Android | iOS |
|---|---|---|
| `screenshot <out_path>` | `adb exec-out screencap -p > <out_path>` | `idb screenshot [--udid <udid>] <out_path>` |
| `pull-logs <out_dir> [--package <id>]` | Writes `logcat_crash.txt` (`adb logcat -d -b crash`), `logcat_full.txt` (`adb logcat -d`), `logcat_fatal_exception.txt` (grep `FATAL EXCEPTION`, 50 lines after), and — if `--package` given — `logcat_anr.txt` (grep `ANR in <package>`, 5 before / 30 after) | Runs `idevicecrashreport -e <out_dir>`; if `idevicesyslog` is present, captures 5 seconds of it to `<out_dir>/syslog.txt` |

`pull-logs`'s grep patterns are the same ones `/investigate-device-crash`
already uses — if that convention changes, update both places together.

## Input injection

| Command | Android | iOS |
|---|---|---|
| `tap <x> <y>` | `adb shell input tap <x> <y>` | `idb ui tap [--udid <udid>] <x> <y>` |
| `swipe <x1> <y1> <x2> <y2> [--duration-ms <n>]` | `adb shell input swipe <x1> <y1> <x2> <y2> [<n>]` | `idb ui swipe [--udid <udid>] <x1> <y1> <x2> <y2> [--duration <n/1000>]` |
| `text <value>` | `adb shell input text <value with spaces escaped as %s>` | `idb ui text [--udid <udid>] "<value>"` |
| `keyevent <code>` | `adb shell input keyevent <code>` — numeric Android keycode | `idb ui button [--udid <udid>] <code>` — a **named** hardware button (`HOME`, `LOCK`, `SIRI`, `SIDE_BUTTON`, ...), not a numeric code |

**Platform asymmetry, stated rather than papered over:** `keyevent` takes a
numeric keycode on Android and a named button on iOS. Passing an Android
keycode on iOS (or vice versa) will simply fail — the calling agent must
know which platform it's targeting when choosing the `code` argument.

On real iOS devices, every `idb ui *` command depends on WebDriverAgent
already running on the device (idb drives WDA internally) — see
`ios-idb-setup.md` for what that requires before any `tap`/`swipe`/`text`
call will succeed.

## Exit codes

- `0` — the command ran to completion. This says nothing about whether the
  app behaved correctly; only that the device-level action itself succeeded.
- `1` — a required binary was missing from `PATH`, or the underlying
  `adb`/`idb`/`idevice*` invocation itself returned non-zero (e.g. device
  unreachable, package not found for `stop`/`uninstall`).

Never treat exit code `0` from `install`/`launch` as proof the app is
actually running — both can succeed at the OS level while the app then
crashes immediately after. Confirm with a `screenshot` per the SKILL.md
walkthrough method.
