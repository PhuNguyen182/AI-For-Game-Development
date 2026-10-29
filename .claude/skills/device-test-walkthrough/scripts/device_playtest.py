#!/usr/bin/env python3
"""adb (Android) / idb + idevice* (iOS) device primitives for device-test-walkthrough.

Echoes each underlying command to stderr before running it. Never judges app
behaviour or retries; exits 1 only on a missing binary or a failed tool call.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# devices/doctor and the pull-logs logcat greps mirror `investigate-device-crash`
# steps 1 and 3; change both together. That skill runs `idevicecrashreport -e`
# without -k, which removes reports from the device.


class ToolError(Exception):
    """A required binary is missing."""


def echo_run(cmd, capture=False, **kwargs):
    print(f"$ {' '.join(str(c) for c in cmd)}", file=sys.stderr)
    if capture:
        return subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    return subprocess.run(cmd, **kwargs)


def require(binary):
    if shutil.which(binary) is None:
        raise ToolError(f"required binary not found on PATH: {binary}")


def grep_context(lines, needle, before, after):
    matches = []
    for i, line in enumerate(lines):
        if needle in line:
            matches.extend(lines[max(0, i - before):i + after + 1])
            matches.append("--")
    return matches


# ---------------------------------------------------------------- Android

def adb(a, *args):
    require("adb")
    return ["adb"] + (["-s", a.device] if a.device else []) + [str(x) for x in args]


def android_devices():
    require("adb")
    result = echo_run(["adb", "devices", "-l"], capture=True)
    print(result.stdout)
    return result.returncode


def android_doctor(a):
    if shutil.which("adb") is None:
        print("MISSING: adb not found on PATH")
        return 1
    result = echo_run(["adb", "devices", "-l"], capture=True)
    states = [line.split()[1] for line in result.stdout.splitlines()[1:] if len(line.split()) > 1]
    ready = states.count("device")
    if not ready:
        print(f"NO DEVICE: adb sees no authorized device (states: {', '.join(states) or 'none'})")
        return 1
    print(f"OK: adb present, {ready} authorized device(s)")
    return 0


def android_install(a):
    return echo_run(adb(a, "install", "-r", a.path)).returncode


def android_launch(a):
    if a.activity:
        return echo_run(adb(a, "shell", "am", "start", "-n", f"{a.app_id}/{a.activity}")).returncode
    return echo_run(adb(a, "shell", "monkey", "-p", a.app_id,
                        "-c", "android.intent.category.LAUNCHER", "1")).returncode


def android_stop(a):
    return echo_run(adb(a, "shell", "am", "force-stop", a.app_id)).returncode


def android_uninstall(a):
    return echo_run(adb(a, "uninstall", a.app_id)).returncode


def android_screenshot(a):
    cmd = adb(a, "exec-out", "screencap", "-p")
    out_path = Path(a.out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"$ {' '.join(cmd)} > {out_path}", file=sys.stderr)
    with open(out_path, "wb") as handle:
        return subprocess.run(cmd, stdout=handle).returncode


def android_tap(a):
    return echo_run(adb(a, "shell", "input", "tap", a.x, a.y)).returncode


def android_swipe(a):
    cmd = adb(a, "shell", "input", "swipe", a.x1, a.y1, a.x2, a.y2)
    if a.duration_ms:
        cmd.append(str(a.duration_ms))
    return echo_run(cmd).returncode


def android_text(a):
    return echo_run(adb(a, "shell", "input", "text", a.value.replace(" ", "%s"))).returncode


def android_keyevent(a):
    return echo_run(adb(a, "shell", "input", "keyevent", a.code)).returncode


def android_pull_logs(a):
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    crash = echo_run(adb(a, "logcat", "-d", "-b", "crash"), capture=True)
    (out_dir / "logcat_crash.txt").write_text(crash.stdout)
    full = echo_run(adb(a, "logcat", "-d"), capture=True)
    (out_dir / "logcat_full.txt").write_text(full.stdout)
    lines = full.stdout.splitlines()
    fatal = grep_context(lines, "FATAL EXCEPTION", before=0, after=50)
    (out_dir / "logcat_fatal_exception.txt").write_text("\n".join(fatal))
    if a.package:
        anr = grep_context(lines, f"ANR in {a.package}", before=5, after=30)
        (out_dir / "logcat_anr.txt").write_text("\n".join(anr))
    print(f"Logs written to {out_dir}")
    return 1 if crash.returncode or full.returncode else 0


# --------------------------------------------------------------------- iOS

def idb(a, verb, *args):
    """`idb <verb> [--udid <udid>] <args>`; verb may be two words ("ui tap")."""
    require("idb")
    return ["idb"] + verb.split() + (["--udid", a.device] if a.device else []) + [str(x) for x in args]


def udid(a):
    # libimobiledevice tools take -u/--udid.
    return ["-u", a.device] if a.device else []


def ios_devices():
    require("idevice_id")
    result = echo_run(["idevice_id", "-l"], capture=True)
    print(result.stdout)
    if shutil.which("idb"):
        echo_run(["idb", "list-targets"])
    return result.returncode


def ios_doctor(a):
    ok = True
    for binary in ("idevice_id", "idb", "idb_companion"):
        if shutil.which(binary) is None:
            print(f"MISSING: {binary} not found on PATH")
            ok = False
    if shutil.which("idevice_id"):
        result = echo_run(["idevice_id", "-l"], capture=True)
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        if lines:
            print(f"OK: {len(lines)} paired device(s) visible")
        else:
            print("NO DEVICE: idevice_id sees no paired device")
            ok = False
    if ok:
        print("NOTE: cannot confirm WebDriverAgent is running; idb ui * needs it "
              "(references/ios-idb-setup.md).")
    return 0 if ok else 1


def ios_install(a):
    return echo_run(idb(a, "install", a.path)).returncode


def ios_launch(a):
    return echo_run(idb(a, "launch", a.app_id)).returncode


def ios_stop(a):
    return echo_run(idb(a, "terminate", a.app_id)).returncode


def ios_uninstall(a):
    return echo_run(idb(a, "uninstall", a.app_id)).returncode


def ios_screenshot(a):
    out_path = Path(a.out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    return echo_run(idb(a, "screenshot", out_path)).returncode


def ios_tap(a):
    return echo_run(idb(a, "ui tap", a.x, a.y)).returncode


def ios_swipe(a):
    cmd = idb(a, "ui swipe", a.x1, a.y1, a.x2, a.y2)
    if a.duration_ms:
        cmd += ["--duration", str(a.duration_ms / 1000)]
    return echo_run(cmd).returncode


def ios_text(a):
    return echo_run(idb(a, "ui text", a.value)).returncode


def ios_keyevent(a):
    return echo_run(idb(a, "ui button", a.code)).returncode


def ios_pull_logs(a):
    require("idevicecrashreport")
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    before = set(out_dir.rglob("*"))
    # -k keeps the reports on the device; -e also extracts raw .crash files.
    result = echo_run(["idevicecrashreport", "-k", "-e"] + udid(a) + [str(out_dir)], capture=True)
    if result.returncode != 0:
        tail = (result.stderr or result.stdout).strip().splitlines()
        print(f"ERROR: idevicecrashreport exit {result.returncode}: {tail[-1] if tail else ''}",
              file=sys.stderr)
    out = result.stdout.splitlines()  # filenames name the crashed process
    if out:
        print("\n".join(out[:50]) + (f"\n(+{len(out) - 50} more)" if len(out) > 50 else ""))
    new = sum(1 for p in set(out_dir.rglob("*")) - before if p.is_file())
    print(f"{new} new file(s) copied to {out_dir} (all apps, may include earlier crashes)")
    if shutil.which("idevicesyslog"):
        syslog_path = out_dir / "syslog.txt"
        cmd = ["idevicesyslog"] + udid(a)
        print(f"$ {' '.join(cmd)} (5s) > {syslog_path}", file=sys.stderr)
        try:
            with open(syslog_path, "w") as handle:
                subprocess.run(cmd, stdout=handle, timeout=5)
        except subprocess.TimeoutExpired:
            pass
        print(f"syslog: {syslog_path}")
    return 1 if result.returncode else 0


# ------------------------------------------------------------------- CLI

COMMANDS = {  # command: (android, ios)
    "doctor": (android_doctor, ios_doctor),
    "install": (android_install, ios_install),
    "launch": (android_launch, ios_launch),
    "stop": (android_stop, ios_stop),
    "uninstall": (android_uninstall, ios_uninstall),
    "screenshot": (android_screenshot, ios_screenshot),
    "tap": (android_tap, ios_tap),
    "swipe": (android_swipe, ios_swipe),
    "text": (android_text, ios_text),
    "keyevent": (android_keyevent, ios_keyevent),
    "pull-logs": (android_pull_logs, ios_pull_logs),
}


COORDS = {"x", "y", "x1", "y1", "x2", "y2"}
HELP = {"app_id": "Android package name or iOS bundle id"}


def build_parser():
    parser = argparse.ArgumentParser(
        description="Device primitives for QA device test walkthroughs (Android via adb, iOS via idb)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name, help_text, *positionals, device=True):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--platform", choices=["android", "ios"], required=True)
        if device:
            p.add_argument("--device", help="adb serial or iOS udid; omit to use the only connected device")
        for positional in positionals:
            p.add_argument(positional, type=int if positional in COORDS else str, help=HELP.get(positional))
        return p

    sub.add_parser("devices", help="List connected (Android) and paired (iOS) devices.")
    add("doctor", "Check required tooling is present and a device is reachable.", device=False)
    add("install", "Install a build artifact onto the device.", "path")
    launch = add("launch", "Launch an installed app.", "app_id")
    launch.add_argument("--activity", help="Android only: use `am start -n <app_id>/<activity>` instead of monkey")
    add("stop", "Force-stop the running app.", "app_id")
    add("uninstall", "Uninstall the app.", "app_id")
    add("screenshot", "Capture a screenshot to a local file.", "out_path")
    add("tap", "Tap at a screen coordinate.", "x", "y")
    swipe = add("swipe", "Swipe between two screen coordinates.", "x1", "y1", "x2", "y2")
    swipe.add_argument("--duration-ms", type=int, default=0)
    add("text", "Type a text string into the focused field.", "value")
    add("keyevent", "Send a key/button event (Android: numeric keycode; iOS: named button).", "code")
    pull_logs = add("pull-logs", "Pull crash/ANR-relevant logs to a local directory.", "out_dir")
    pull_logs.add_argument("--package", help="Android only: app id, used to grep ANR entries")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == "devices":
            rc_android = android_devices() if shutil.which("adb") else 0
            rc_ios = ios_devices() if shutil.which("idevice_id") else 0
            return rc_android or rc_ios
        return COMMANDS[args.command][args.platform == "ios"](args)
    except ToolError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
