"""Check a data pack before any adviser reads it: aggregated data only. Stdlib only. Fails closed.

Run: python -I check_pack.py <pack folder>. Exit 0 clean, 1 problems, 2 cannot check. Tests: python -I test_check_pack.py.
"""
import csv
import re
import sys
from pathlib import Path

# Normalised header names (lower case, separators removed) that identify one player, device or connection.
DENY_EXACT = {
    "uid", "userid", "user", "username", "playerid", "player", "playername", "accountid", "account", "customerid", "memberid",
    "email", "emailaddress", "mail", "phone", "phonenumber", "name", "fullname", "firstname", "lastname", "address",
    "deviceid", "androidid", "advertisingid", "adid", "gaid", "aaid", "idfa", "idfv", "installationid", "instanceid",
    "firebaseinstanceid", "appinstanceid", "pseudoid", "userpseudoid", "ip", "ipaddress", "clientip", "orderid", "transactionid",
    "purchasetoken", "receipt",
}
DENY_SUFFIX = ("userid", "playerid", "accountid", "deviceid", "email", "ipaddress", "pseudoid", "instanceid")


def normal(header: str) -> str:
    return re.sub(r"[^a-z0-9]", "", header.lower())


def banned(header: str) -> bool:
    n = normal(header)
    return n in DENY_EXACT or n.endswith(DENY_SUFFIX)


def check_csv(path: Path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        try:
            sample = f.read(4096)
            f.seek(0)
            delimiter = "\t" if sample.split("\n", 1)[0].count("\t") > sample.split("\n", 1)[0].count(",") else ","
            headers = next(csv.reader(f, delimiter=delimiter), None)
        except (csv.Error, UnicodeDecodeError) as ex:
            return ["%s: unreadable (%s)" % (path.name, ex)]
    if not headers:
        return ["%s: no header row" % path.name]
    return ["%s: column %r identifies a person or device" % (path.name, h) for h in headers if banned(h)]


def check_pack(folder: Path):
    if not folder.is_dir():
        raise OSError("not a folder: %s" % folder)
    problems = []
    manifest = folder / "manifest.md"
    if not manifest.is_file():
        problems.append("manifest.md missing: source, date range, filters and build versions are required")
    data = sorted(p for p in folder.rglob("*") if p.is_file() and p != manifest)
    tables = [p for p in data if p.suffix.lower() in (".csv", ".tsv")]
    if not tables:
        problems.append("no CSV or TSV file in the pack")
    for p in data:
        if p.suffix.lower() in (".csv", ".tsv"):
            problems += check_csv(p)
        else:
            problems.append("%s: only CSV or TSV can be checked, so it is refused" % p.name)
    return problems


def main(argv):
    if len(argv) != 2:
        print("usage: check_pack.py <pack folder>", file=sys.stderr)
        return 2
    try:
        problems = check_pack(Path(argv[1]))
    except OSError as ex:
        print("cannot check: %s" % ex, file=sys.stderr)
        return 2
    for p in problems:
        print("FAIL " + p)
    print("data pack: %s" % ("%d problem(s)" % len(problems) if problems else "OK"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
