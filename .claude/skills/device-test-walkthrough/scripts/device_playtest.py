#!/usr/bin/env python3
"""
Thin CLI of device primitives for the device-test-walkthrough QA skill.

Wraps adb (Android) and idb/idevice* (iOS) behind one uniform subcommand
surface: devices, doctor, install, launch, stop, uninstall, screenshot, tap,
swipe, text, keyevent, pull-logs.

This script only executes device-level actions and reports what the
underlying tool returned. It never inspects app behaviour, never judges
whether a result is correct, and never retries on its own — that judgment
belongs to whichever agent calls it, per .claude/rules/qa/verification-standards.md.
Every action is echoed to stderr before it runs, so the transcript itself is
usable as defect-reporting.md evidence.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


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
            start = max(0, i - before)
            end = min(len(lines), i + after + 1)
            matches.extend(lines[start:end])
            matches.append("--")
    return matches


# ---------------------------------------------------------------- Android

def android_prefix(device):
    prefix = ["adb"]
    if device:
        prefix += ["-s", device]
    return prefix


def android_devices():
    require("adb")
    result = echo_run(["adb", "devices", "-l"], capture=True)
    print(result.stdout)
    return result.returncode


def android_doctor():
    ok = True
    if shutil.which("adb") is None:
        print("MISSING: adb not found on PATH")
        return 1
    result = echo_run(["adb", "devices", "-l"], capture=True)
    lines = [line for line in result.stdout.splitlines()[1:] if line.strip()]
    if not lines:
        print("NO DEVICE: adb sees no connected/authorized device")
        ok = False
    else:
        print(f"OK: adb present, {len(lines)} device(s) visible")
    return 0 if ok else 1


def android_install(path, device):
    require("adb")
    result = echo_run(android_prefix(device) + ["install", "-r", path])
    return result.returncode


def android_launch(app_id, device, activity):
    require("adb")
    if activity:
        cmd = android_prefix(device) + ["shell", "am", "start", "-n", f"{app_id}/{activity}"]
    else:
        cmd = android_prefix(device) + [
            "shell", "monkey", "-p", app_id, "-c", "android.intent.category.LAUNCHER", "1",
        ]
    return echo_run(cmd).returncode


def android_stop(app_id, device):
    require("adb")
    return echo_run(android_prefix(device) + ["shell", "am", "force-stop", app_id]).returncode


def android_uninstall(app_id, device):
    require("adb")
    return echo_run(android_prefix(device) + ["uninstall", app_id]).returncode


def android_screenshot(out_path, device):
    require("adb")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = android_prefix(device) + ["exec-out", "screencap", "-p"]
    print(f"$ {' '.join(cmd)} > {out_path}", file=sys.stderr)
    with open(out_path, "wb") as handle:
        result = subprocess.run(cmd, stdout=handle)
    return result.returncode


def android_tap(x, y, device):
    require("adb")
    return echo_run(android_prefix(device) + ["shell", "input", "tap", str(x), str(y)]).returncode


def android_swipe(x1, y1, x2, y2, duration_ms, device):
    require("adb")
    cmd = android_prefix(device) + ["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2)]
    if duration_ms:
        cmd.append(str(duration_ms))
    return echo_run(cmd).returncode


def android_text(value, device):
    require("adb")
    escaped = value.replace(" ", "%s")
    return echo_run(android_prefix(device) + ["shell", "input", "text", escaped]).returncode


def android_keyevent(code, device):
    require("adb")
    return echo_run(android_prefix(device) + ["shell", "input", "keyevent", str(code)]).returncode


def android_pull_logs(out_dir, device, package):
    require("adb")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    crash = echo_run(android_prefix(device) + ["logcat", "-d", "-b", "crash"], capture=True)
    (out_dir / "logcat_crash.txt").write_text(crash.stdout)

    full = echo_run(android_prefix(device) + ["logcat", "-d"], capture=True)
    (out_dir / "logcat_full.txt").write_text(full.stdout)

    lines = full.stdout.splitlines()
    fatal = grep_context(lines, "FATAL EXCEPTION", before=0, after=50)
    (out_dir / "logcat_fatal_exception.txt").write_text("\n".join(fatal))

    if package:
        anr = grep_context(lines, f"ANR in {package}", before=5, after=30)
        (out_dir / "logcat_anr.txt").write_text("\n".join(anr))

    print(f"Logs written to {out_dir}")
    return 0


# --------------------------------------------------------------------- iOS

def ios_udid_prefix(device):
    return ["--udid", device] if device else []


def ios_devices():
    require("idevice_id")
    result = echo_run(["idevice_id", "-l"], capture=True)
    print(result.stdout)
    if shutil.which("idb"):
        echo_run(["idb", "list-targets"])
    return result.returncode


def ios_doctor():
    ok = True
    for binary in ("idevice_id", "idb", "idb_companion"):
        if shutil.which(binary) is None:
            print(f"MISSING: {binary} not found on PATH")
            ok = False
    if shutil.which("idevice_id"):
        result = echo_run(["idevice_id", "-l"], capture=True)
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        if not lines:
            print("NO DEVICE: idevice_id sees no paired device")
            ok = False
        else:
            print(f"OK: {len(lines)} paired device(s) visible")
    if ok:
        print(
            "NOTE: idb ui * (tap/swipe/text) additionally requires WebDriverAgent built, "
            "signed, and running on the device — see references/ios-idb-setup.md. "
            "This check cannot confirm WDA is currently running."
        )
    return 0 if ok else 1


def ios_install(path, device):
    require("idb")
    return echo_run(["idb", "install"] + ios_udid_prefix(device) + [path]).returncode


def ios_launch(bundle_id, device):
    require("idb")
    return echo_run(["idb", "launch"] + ios_udid_prefix(device) + [bundle_id]).returncode


def ios_stop(bundle_id, device):
    require("idb")
    return echo_run(["idb", "terminate"] + ios_udid_prefix(device) + [bundle_id]).returncode


def ios_uninstall(bundle_id, device):
    require("idb")
    return echo_run(["idb", "uninstall"] + ios_udid_prefix(device) + [bundle_id]).returncode


def ios_screenshot(out_path, device):
    require("idb")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    return echo_run(["idb", "screenshot"] + ios_udid_prefix(device) + [str(out_path)]).returncode


def ios_tap(x, y, device):
    require("idb")
    return echo_run(["idb", "ui", "tap"] + ios_udid_prefix(device) + [str(x), str(y)]).returncode


def ios_swipe(x1, y1, x2, y2, duration_ms, device):
    require("idb")
    cmd = ["idb", "ui", "swipe"] + ios_udid_prefix(device) + [str(x1), str(y1), str(x2), str(y2)]
    if duration_ms:
        cmd += ["--duration", str(duration_ms / 1000)]
    return echo_run(cmd).returncode


def ios_text(value, device):
    require("idb")
    return echo_run(["idb", "ui", "text"] + ios_udid_prefix(device) + [value]).returncode


def ios_keyevent(code, device):
    # idb has no numeric keycode equivalent — only named hardware buttons
    # (e.g. HOME, LOCK, SIRI). Document this asymmetry rather than papering
    # over it: an Android keycode passed here will simply fail.
    require("idb")
    return echo_run(["idb", "ui", "button"] + ios_udid_prefix(device) + [code]).returncode


def ios_pull_logs(out_dir, device):
    require("idevicecrashreport")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    echo_run(["idevicecrashreport", "-e", str(out_dir)])
    if shutil.which("idevicesyslog"):
        syslog_path = out_dir / "syslog.txt"
        print(f"$ idevicesyslog (5s capture) > {syslog_path}", file=sys.stderr)
        try:
            with open(syslog_path, "w") as handle:
                subprocess.run(["idevicesyslog"], stdout=handle, timeout=5)
        except subprocess.TimeoutExpired:
            pass
    print(f"Logs written to {out_dir}")
    return 0


# ------------------------------------------------------------------- CLI

def build_parser():
    parser = argparse.ArgumentParser(
        description="Device primitives for QA device test walkthroughs (Android via adb, iOS via idb)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_platform_device(subparser):
        subparser.add_argument("--platform", choices=["android", "ios"], required=True)
        subparser.add_argument(
            "--device", help="adb serial or iOS udid; omit to use the only connected device"
        )

    sub.add_parser("devices", help="List connected (Android) and paired (iOS) devices.")

    doctor = sub.add_parser(
        "doctor", help="Check required tooling is present and a device is reachable."
    )
    doctor.add_argument("--platform", choices=["android", "ios"], required=True)

    install = sub.add_parser("install", help="Install a build artifact onto the device.")
    add_platform_device(install)
    install.add_argument("path")

    launch = sub.add_parser("launch", help="Launch an installed app.")
    add_platform_device(launch)
    launch.add_argument("app_id", help="Android package name or iOS bundle id")
    launch.add_argument(
        "--activity",
        help="Android only: use `am start -n <app_id>/<activity>` instead of monkey",
    )

    stop = sub.add_parser("stop", help="Force-stop the running app.")
    add_platform_device(stop)
    stop.add_argument("app_id")

    uninstall = sub.add_parser("uninstall", help="Uninstall the app.")
    add_platform_device(uninstall)
    uninstall.add_argument("app_id")

    screenshot = sub.add_parser("screenshot", help="Capture a screenshot to a local file.")
    add_platform_device(screenshot)
    screenshot.add_argument("out_path")

    tap = sub.add_parser("tap", help="Tap at a screen coordinate.")
    add_platform_device(tap)
    tap.add_argument("x", type=int)
    tap.add_argument("y", type=int)

    swipe = sub.add_parser("swipe", help="Swipe between two screen coordinates.")
    add_platform_device(swipe)
    swipe.add_argument("x1", type=int)
    swipe.add_argument("y1", type=int)
    swipe.add_argument("x2", type=int)
    swipe.add_argument("y2", type=int)
    swipe.add_argument("--duration-ms", type=int, default=0)

    text = sub.add_parser("text", help="Type a text string into the focused field.")
    add_platform_device(text)
    text.add_argument("value")

    keyevent = sub.add_parser(
        "keyevent", help="Send a key/button event (Android: numeric keycode; iOS: named button)."
    )
    add_platform_device(keyevent)
    keyevent.add_argument("code")

    pull_logs = sub.add_parser("pull-logs", help="Pull crash/ANR-relevant logs to a local directory.")
    add_platform_device(pull_logs)
    pull_logs.add_argument("out_dir")
    pull_logs.add_argument("--package", help="Android only: app id, used to grep ANR entries")

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    is_android = getattr(args, "platform", None) == "android"

    try:
        if args.command == "devices":
            rc_android = android_devices() if shutil.which("adb") else 0
            rc_ios = ios_devices() if shutil.which("idevice_id") else 0
            return rc_android or rc_ios
        if args.command == "doctor":
            return android_doctor() if is_android else ios_doctor()
        if args.command == "install":
            return android_install(args.path, args.device) if is_android \
                else ios_install(args.path, args.device)
        if args.command == "launch":
            return android_launch(args.app_id, args.device, args.activity) if is_android \
                else ios_launch(args.app_id, args.device)
        if args.command == "stop":
            return android_stop(args.app_id, args.device) if is_android \
                else ios_stop(args.app_id, args.device)
        if args.command == "uninstall":
            return android_uninstall(args.app_id, args.device) if is_android \
                else ios_uninstall(args.app_id, args.device)
        if args.command == "screenshot":
            return android_screenshot(args.out_path, args.device) if is_android \
                else ios_screenshot(args.out_path, args.device)
        if args.command == "tap":
            return android_tap(args.x, args.y, args.device) if is_android \
                else ios_tap(args.x, args.y, args.device)
        if args.command == "swipe":
            return android_swipe(args.x1, args.y1, args.x2, args.y2, args.duration_ms, args.device) \
                if is_android \
                else ios_swipe(args.x1, args.y1, args.x2, args.y2, args.duration_ms, args.device)
        if args.command == "text":
            return android_text(args.value, args.device) if is_android \
                else ios_text(args.value, args.device)
        if args.command == "keyevent":
            return android_keyevent(args.code, args.device) if is_android \
                else ios_keyevent(args.code, args.device)
        if args.command == "pull-logs":
            return android_pull_logs(args.out_dir, args.device, args.package) if is_android \
                else ios_pull_logs(args.out_dir, args.device)
    except ToolError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"ERROR: unhandled command {args.command!r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
