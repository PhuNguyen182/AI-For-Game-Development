"""Check a data pack before any adviser reads it: aggregated data only. Stdlib only. Default deny, fails closed.

Identifier names and values are open sets, so nothing here lists what to block and lets the rest through.
A header passes only when every word is on a finite vocabulary of aggregate dimensions and metrics; a cell passes
only when it does not look like an identifier. The fix for a false positive is to rename the column, or to add the
word here in a reviewed change. Problems name the file and column number, and never print a value or an unknown word.
Run: python -I check_pack.py <pack folder>. Exit 0 clean, 1 problems, 2 cannot check. Tests: python -I test_check_pack.py.
"""
import csv
import ipaddress
import re
import sys
from pathlib import Path

SEPARATORS = (",", ";", "\t", "|")

# The only words allowed before a tail word: a tail after them names a thing in the game, not a person.
DIMENSIONS = set("""app build version platform os store country region language locale currency level stage world chapter quest
mission event screen step funnel sku product item offer bundle pack reward campaign creative source medium channel network
mediation placement ad unit format type category segment cohort experiment variant group tier season mode map model brand""".split())
TAILS = {"id", "name", "code", "number"}
# Counts of people: allowed as a word, but the column must be numeric.
COUNT = set("users players accounts devices installs sessions payers buyers spenders purchasers".split())
# A person word allowed only as the last word after "per" (revenue_per_user).
PER_OK = set("user player account device install session payer".split())
# Never allowed, whatever surrounds it (PER_OK words excepted as above).
NEVER = set("""user player account customer member payer buyer email mail phone mobile msisdn imei imsi mac ip ipv4 ipv6 idfa
idfv gaid aaid adid advertising pseudo uid uuid guid token hash key receipt username nickname gamertag firstname lastname
fullname surname displayname login password address latitude longitude lat lon lng gps agent useragent device install
installation instance session steam steamid playfab gamecenter facebook fb external order transaction birth birthday dob zip
postcode postal street userid playerid deviceid""".split())
METRICS = set("""date day days week weeks month months year hour hours time period start end first last new active returning
paying paid unique total net gross daily weekly monthly cumulative avg average mean median min max sum count rate ratio share
percent pct per of by in at to from and vs is has with all other local usd retention retained churn churned conversion
conversions converted revenue proceeds refunds refunded sales iap ads impressions impression imps ipm clicks ctr ecpm cpm cpi
cpc arpu arppu arpdau ltv roas dau wau mau stickiness fill requests matched shown shows views watched completed completion
completions started starts open opens wins losses attempts fails failures success purchases quantity price amount value
earned spent sinks sources balance coins gems gold crash crashes free anr anrs errors rating ratings reviews score stars
downloads uninstalls reinstalls playtime engagement length duration seconds sec minutes ms depth progress progression reached
rewarded interstitial banner video native appopen frequency transactions orders""".split())
ALLOWED = DIMENSIONS | TAILS | COUNT | METRICS
RX_PATTERN_WORD = re.compile(r"^([dwm]\d{1,3}|p\d{2})$")
# Bare numbers are an open set: a few short ones may sit beside words (level 10, season 2026), never make up a name.
RX_NUMBER_WORD = re.compile(r"^\d{1,4}$")
MAX_NUMBER_WORDS = 2
MAX_NUMBER_DIGITS = 4

RX_NUMBER = re.compile(r"^-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?%?$")
RX_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b")
RX_IPV4 = re.compile(r"(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)(?![\d.])")
RX_PHONE = re.compile(r"(?<![\w+])\+\d[\d ()-]{8,}\d\b")
RX_NATIONAL_PHONE = re.compile(r"(?<![\d.-])\(?0\d{1,4}\)?[ -]?\d{2,4}[ -]?\d{3,4}(?![\d-])")
RX_UUID = re.compile(r"\b[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}\b")
RX_IPV6_TOKEN = re.compile(r"[0-9A-Fa-f:]{2,}")
RX_DIGIT_RUN = re.compile(r"\d{9,}")
RX_ALNUM_RUN = re.compile(r"[A-Za-z0-9]{12,}")
RX_HEX_RUN = re.compile(r"[0-9A-Fa-f]{16,}")
MAX_TEXT = 80
LONG_NUMBER_DIGITS = 15


NON_ASCII_WORD = "<non-ascii>"  # never on the vocabulary


def words(header: str):
    spaced = re.sub(r"([a-z0-9])([A-Z][a-z])", r"\1 \2", header.strip())
    out = [w for w in re.split(r"[^a-z0-9]+", spaced.lower()) if w]
    if any(ord(ch) > 127 and ch.isalnum() for ch in header):
        out.append(NON_ASCII_WORD)  # splitting on ASCII would drop it and let "cohort 用户名" pass as "cohort"
    return out


def known(word: str) -> bool:
    return word in ALLOWED or word in NEVER or bool(RX_PATTERN_WORD.match(word)) or bool(RX_NUMBER_WORD.match(word))


def named(parts) -> bool:
    """Every word known, and bare numbers few, short and beside a word: a header made of digit groups
    (8.8.8.8, +84 912 345 678) is a value, never a name, and is never printed."""
    numbers = [p for p in parts if RX_NUMBER_WORD.match(p)]
    return (all(known(p) for p in parts) and len(numbers) < len(parts)
            and len(numbers) <= MAX_NUMBER_WORDS and sum(map(len, numbers)) <= MAX_NUMBER_DIGITS)


def header_problem(header: str):
    """None, or (rule, safe to print). Every word is checked before the decision."""
    parts = words(header)
    if not parts:
        return "has no header", False
    for i, w in enumerate(parts):
        if w in NEVER and not (w in PER_OK and i == len(parts) - 1 and "per" in parts[:i]):
            return "identifies a person or device", named(parts)
        if w in TAILS and (i == 0 or any(p not in DIMENSIONS for p in parts[:i])):
            return "identifies a person or device", named(parts)
    if not named(parts):
        return "uses a word outside the vocabulary; rename it or add the word in a reviewed change", False
    return None


def cell_problem(cell: str, numeric: bool, header_words):
    if numeric:
        integer = cell.lstrip("-").split(".")[0].split("e")[0].split("E")[0].rstrip("%")
        return "holds a long numeric id" if len(integer) >= LONG_NUMBER_DIGITS else None
    if len(cell) > MAX_TEXT:
        return "holds text over %d characters" % MAX_TEXT
    for what, rx in (("an email", RX_EMAIL), ("a phone number", RX_PHONE), ("a phone number", RX_NATIONAL_PHONE), ("a UUID", RX_UUID)):
        if rx.search(cell):
            return "holds " + what
    if RX_IPV4.search(cell) and not ({"version", "build"} & set(header_words)):
        return "holds an IP address"
    for token in RX_IPV6_TOKEN.findall(cell):
        if token.count(":") >= 2:
            try:
                ipaddress.ip_address(token)
                return "holds an IP address"
            except ValueError:
                pass
    if RX_DIGIT_RUN.search(cell):
        return "holds a long digit run"
    if any(re.search(r"[A-Za-z]", run) and re.search(r"\d", run) for run in RX_ALNUM_RUN.findall(cell)):
        return "holds an id-shaped letter and digit run"
    if RX_HEX_RUN.search(cell):
        return "holds a hex id"
    return None


def separator(path: Path, first_line: str) -> str:
    if path.suffix.lower() == ".tsv":
        return "\t"
    return max(SEPARATORS, key=first_line.count)


def label(n: int, header: str, safe: bool) -> str:
    return "column %d (%r)" % (n, header) if safe else "column %d" % n


def check_csv(path: Path):
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            first = f.readline()
            f.seek(0)
            rows = list(csv.reader(f, delimiter=separator(path, first)))
    except (csv.Error, UnicodeDecodeError) as ex:
        return ["%s: unreadable (%s)" % (path.name, type(ex).__name__)]
    if not rows or not rows[0]:
        return ["%s: no header row" % path.name]
    headers, body = rows[0], [(r, row) for r, row in enumerate(rows[1:], 2) if any(c.strip() for c in row)]
    problems = []
    for n, h in enumerate(headers, 1):
        if any(s in h for s in SEPARATORS):
            problems.append("%s: column %d header still holds a separator; the columns cannot be read" % (path.name, n))
            continue
        hp = header_problem(h)
        if hp:
            problems.append("%s: %s %s" % (path.name, label(n, h, hp[1]), hp[0]))
    for r, row in body:
        if len(row) != len(headers):
            problems.append("%s: row %d has %d cells; the header has %d" % (path.name, r, len(row), len(headers)))
    reported = set()
    for n, h in enumerate(headers, 1):
        cells = [row[n - 1].strip() for _, row in body if n - 1 < len(row) and row[n - 1].strip()]
        numeric = bool(cells) and all(RX_NUMBER.match(c) for c in cells)
        hw = words(h)
        if COUNT & set(hw) and cells and not numeric:
            problems.append("%s: column %d is a count column holding text" % (path.name, n))
        safe = header_problem(h) is None
        for c in cells:
            cp = cell_problem(c, numeric, hw)
            if cp and (n, cp) not in reported:
                reported.add((n, cp))
                problems.append("%s: %s %s" % (path.name, label(n, h, safe), cp))  # never the value itself
    for _, row in body:  # cells past the header width: scanned too, named by position
        for n in range(len(headers) + 1, len(row) + 1):
            cp = cell_problem(row[n - 1].strip(), False, []) if row[n - 1].strip() else None
            if cp and (n, cp) not in reported:
                reported.add((n, cp))
                problems.append("%s: column %d (past the header) %s" % (path.name, n, cp))
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
