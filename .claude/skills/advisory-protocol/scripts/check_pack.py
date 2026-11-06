"""Check a data pack before any adviser reads it: aggregated data only. Stdlib only. Fails closed.

Headers are split on every separator a spreadsheet writes (, ; tab |), so a locale's CSV cannot hide a column.
A header naming a person, device or connection fails, and so does any cell shaped like an email, IP, phone or UUID.
Run: python -I check_pack.py <pack folder>. Exit 0 clean, 1 problems, 2 cannot check. Tests: python -I test_check_pack.py.
"""
import csv
import re
import sys
from pathlib import Path

SEPARATORS = (",", ";", "\t", "|")
# Whole normalised names (lower case, separators removed) that identify one player, device or connection.
DENY_EXACT = {
    "uid", "user", "username", "player", "playername", "account", "customer", "member", "email", "emailaddress", "mail",
    "phone", "phonenumber", "name", "fullname", "firstname", "lastname", "address", "adid", "gaid", "aaid", "idfa", "idfv",
    "steamid", "playfabid", "gamecenterid", "pushtoken", "fcmtoken", "apnstoken", "useragent", "latitude", "longitude",
    "lat", "lon", "lng", "ip", "ipaddress", "clientip", "receipt", "purchasetoken", "userhash", "userpseudoid", "pseudoid",
}
# A header whose last word is one of these names one thing, unless the words before it name a dimension, not a person.
ID_WORDS = {"id", "uuid", "guid", "hash", "token", "key"}
DIMENSIONS = {
    "build", "level", "cohort", "sku", "placement", "product", "item", "campaign", "unit", "adunit", "event", "stage",
    "world", "chapter", "quest", "offer", "experiment", "variant", "segment", "country", "platform", "store", "version",
    "bundle", "network", "mediation", "currency", "reward", "pack", "mode", "map", "season", "tier",
}
RX_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b")
RX_IPV4 = re.compile(r"(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)(?![\d.])")
RX_PHONE = re.compile(r"(?<![\w+])\+\d[\d ()-]{8,}\d\b")
RX_UUID = re.compile(r"\b[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}\b")
CELL_SHAPES = (("an email", RX_EMAIL), ("an IP address", RX_IPV4), ("a phone number", RX_PHONE), ("a UUID", RX_UUID))


def words(header: str):
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", header.strip())
    return [w for w in re.split(r"[^a-z0-9]+", spaced.lower()) if w]


def banned(header: str) -> bool:
    parts = words(header)
    if not parts:
        return False
    if "".join(parts) in DENY_EXACT:
        return True
    if parts[-1] in ID_WORDS:
        return not any(p in DIMENSIONS for p in parts[:-1])
    joined = "".join(parts)
    return any(joined.endswith(w) and joined != w and joined[:-len(w)] in DENY_EXACT | {"device", "android", "installation", "instance", "advertising", "firebaseinstance", "appinstance", "order", "transaction"}
               for w in ID_WORDS)


def separator(first_line: str) -> str:
    return max(SEPARATORS, key=first_line.count)


def check_csv(path: Path):
    problems = []
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            first = f.readline()
            f.seek(0)
            reader = csv.reader(f, delimiter=separator(first))
            headers = next(reader, None)
            if not headers:
                return ["%s: no header row" % path.name]
            for h in headers:
                if any(s in h for s in SEPARATORS):
                    problems.append("%s: header %r still holds a separator; the columns cannot be read" % (path.name, h))
                elif banned(h):
                    problems.append("%s: column %r identifies a person or device" % (path.name, h))
            flagged = set()
            for row in reader:
                for col, cell in zip(headers, row):
                    for what, rx in CELL_SHAPES:
                        if (col, what) not in flagged and rx.search(cell):
                            flagged.add((col, what))
                            problems.append("%s: column %r holds %s" % (path.name, col, what))  # never the value itself
    except (csv.Error, UnicodeDecodeError) as ex:
        return ["%s: unreadable (%s)" % (path.name, ex)]
    return problems


def check_pack(folder: Path):
    if not folder.is_dir():
        raise OSError("not a folder: %s" % folder)
    problems = []
    manifest = folder / "manifest.md"
    if not manifest.is_file():
        problems.append("manifest.md missing: source, date range, filters and build versions are required")
    data = sorted(p for p in folder.rglob("*") if p.is_file() and p != manifest)
    if not any(p.suffix.lower() in (".csv", ".tsv") for p in data):
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
