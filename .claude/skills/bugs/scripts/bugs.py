"""Bug tracker: one record per bug in SQLite, with the tracked journal as the truth. No LLM, stdlib only.

Run with `python -I bugs.py --root <project root> <command>`. .workflow/bugs.jsonl is append-mostly and tracked;
.workflow/bugs.db is a gitignored cache rebuilt from it whenever the journal's hash changes. Format and state machine:
../references/schema.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import sqlite3
import subprocess
import sys
import unicodedata
import uuid
from pathlib import Path

SCHEMA_VERSION = 2
STATUSES = ("Request", "Processing", "Resolved", "Review", "Complete", "Reopen", "Backlog", "Won't fix", "Accepted", "As designed", "Duplicate")
TERMINAL = ("Complete", "Won't fix", "Accepted", "As designed", "Duplicate")
OPEN = tuple(s for s in STATUSES if s not in TERMINAL)
PRIORITIES = ("Low", "Medium", "High", "Highest")
DEFAULT_CAPS = {"fix": 2, "review": 3}
WINDOW = dt.timedelta(days=90)
SQL_SECONDS = 10
MAX_COUNT = 100  # one round or extra-round call; replay refuses more, so a counter's total stays a small integer
REFUSAL_LINE = 500
VALUE_MARK = "\ue000"  # brackets a caller's value inside refusal text; refusal_text() is the only reader
RX_SHOWN = re.compile("%s.*?%s" % (VALUE_MARK, VALUE_MARK), re.S)

# Moves anyone with the writer's role may make; GD-only moves and "any open" moves are in move_rule().
PLAIN_MOVES = {"Request": ("Processing",), "Reopen": ("Processing",), "Processing": ("Request", "Resolved"),
               "Resolved": ("Review",), "Review": ("Complete", "Reopen", "Resolved")}

REQUIRED = ("title", "description", "repro", "expected", "actual", "evidence")
OPTIONAL = ("feature", "owner", "regression_test", "root_cause")
TEXT_FIELDS = REQUIRED + OPTIONAL
UPDATABLE = TEXT_FIELDS + ("priority",)
LIMITS = {"title": 100, "description": 280, "repro": 500, "expected": 300, "actual": 300, "evidence": 300, "root_cause": 300,
          "note": 200, "feature": 100, "owner": 100, "regression_test": 200, "by": 100}
ONE_LINE = {"title", "description", "note", "feature", "owner", "regression_test", "by"}
DEFAULT_BY = "main session"

EVENT_TYPES = ("create", "update", "status", "round", "extra_round", "stop_rule", "renumber", "tombstone")
RX_ID = re.compile(r"BUG-(\d{4,})")
RX_TS = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z")
RX_BREAK = re.compile("[\r\n\v\f\x85  ]")
RX_CONTROL = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f  ]")
VI_LETTERS = "àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ"
RX_VIETNAMESE = re.compile("[%s%s]" % (VI_LETTERS, VI_LETTERS.upper()))
UID_NAMESPACE = uuid.UUID("6f1f3b52-8a44-5c0e-9b7d-2e0c4a7d1b90")
GIT_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_PREFIX", "GIT_OBJECT_DIRECTORY")

SCHEMA = (
    "CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL)",
    """CREATE TABLE bug(
        id TEXT NOT NULL, uid TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL,
        priority TEXT NOT NULL CHECK(priority IN (%s)),
        status TEXT NOT NULL CHECK(status IN (%s)),
        feature TEXT, owner TEXT, regression_test TEXT, repro TEXT, expected TEXT, actual TEXT, evidence TEXT,
        root_cause TEXT, duplicate_of TEXT,
        fix_used INTEGER NOT NULL DEFAULT 0, fix_cap INTEGER NOT NULL,
        review_used INTEGER NOT NULL DEFAULT 0, review_cap INTEGER NOT NULL,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL, closed_at TEXT)""" % (
        ",".join("'%s'" % p for p in PRIORITIES), ",".join("'%s'" % s.replace("'", "''") for s in STATUSES)),
    "CREATE INDEX bug_id ON bug(id)",
    "CREATE INDEX bug_status ON bug(status)",
    "CREATE INDEX bug_priority ON bug(priority)",
    "CREATE INDEX bug_feature ON bug(feature)",
    "CREATE INDEX bug_closed_at ON bug(closed_at)",
    """CREATE TABLE bug_event(
        event_uid TEXT PRIMARY KEY, bug_uid TEXT NOT NULL, ts TEXT NOT NULL, type TEXT NOT NULL,
        by_who TEXT, note TEXT, data TEXT NOT NULL)""",
    "CREATE INDEX bug_event_bug ON bug_event(bug_uid, ts)",
    """CREATE VIRTUAL TABLE bug_fts USING fts5(title, description, repro, expected, actual, evidence, root_cause, notes,
        tokenize="porter unicode61 remove_diacritics 2")""",
)


class Refused(Exception):
    """A rule said no: the message names the rule, the process exits non-zero."""


class Corrupt(Exception):
    """The journal cannot be replayed. Fails closed: the hook blocks on it."""


class UsageError(Refused):
    """argparse's complaint, which quotes the argument. Refused here so it leaves through the one exit in main()."""


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        raise UsageError("bad arguments: %s" % shown(message, 300))

    def parse_args(self, args=None, namespace=None):
        """Counted, never quoted: with a leading -, a pasted key is no longer the shape redaction looks for."""
        parsed, unrecognized = self.parse_known_args(args, namespace)
        if unrecognized:
            self.error("%d unrecognized argument(s)" % len(unrecognized))
        return parsed


def _after_append():
    """Between the journal append and the DB commit. Tests replace this to crash exactly there."""


def is_settled(status: str) -> bool:
    return status == "Backlog" or status in TERMINAL


def move_rule(frm: str, to: str) -> str | None:
    """'plain', 'gd', or None when the state machine has no such move."""
    if frm == to:
        return None
    if frm in TERMINAL:
        return "plain" if to == "Reopen" else None
    if to in ("Backlog", "Won't fix", "Accepted") or (frm == "Backlog" and to == "Request"):
        return "gd"
    if to in ("As designed", "Duplicate"):
        return "plain"
    return "plain" if to in PLAIN_MOVES.get(frm, ()) else None


# ---------------------------------------------------------------- time and ids

def fmt_ts(d: dt.datetime) -> str:
    return d.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (d.microsecond // 1000)


def parse_ts(s: str) -> dt.datetime:
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=dt.timezone.utc)


def now_utc() -> dt.datetime:
    override = os.environ.get("BUGS_NOW")  # test-only clock
    if not override:
        return dt.datetime.now(dt.timezone.utc)
    return parse_ts(override if "." in override else override[:-1] + ".000Z")


def next_ts(last: str | None) -> str:
    now = now_utc()
    if last:
        now = max(now, parse_ts(last) + dt.timedelta(milliseconds=1))
    return fmt_ts(now)


def fmt_id(num: int) -> str:
    return "BUG-%04d" % num


def shown(value, limit=40) -> str:
    """A caller's or a file's value inside refusal text. A long one is never echoed, not cut: the scan at the exit
    could miss a secret cut in half."""
    text = str(value).replace(VALUE_MARK, "")
    return VALUE_MARK + (text if len(text) <= limit else "<%d chars>" % len(text)) + VALUE_MARK


def shown_all(values) -> str:
    return ", ".join(shown(v) for v in values)


def parse_id(text: str) -> int:
    m = RX_ID.fullmatch(text) if isinstance(text, str) else None
    if not m:
        raise Refused("bad id '%s': expected BUG-####" % shown(text))
    return int(m.group(1))


def stable_uid(name: str) -> str:
    return str(uuid.uuid5(UID_NAMESPACE, name))


# ---------------------------------------------------------------- content rules

def check_english(field: str, text: str):
    m = RX_VIETNAMESE.search(unicodedata.normalize("NFC", text))
    if m:
        raise Refused("%s: Vietnamese diacritics ('%s'): the database is English only, translate first" % (field, m.group(0)))


_mem = None
MEM_API = ("load_secret_patterns", "redact", "redact_pii", "RX_PEM_BLOCK")


def mem_module():
    """mem.py owns the secret patterns and PII rules. -I removes the script dir from sys.path, hence importlib."""
    global _mem
    if _mem is None:
        path = Path(__file__).resolve().parents[2] / "mem" / "scripts" / "mem.py"
        if not path.exists():
            raise Refused("write refused: %s is missing, so secret shapes cannot be checked" % path)
        spec = importlib.util.spec_from_file_location("bugs_mem", path)
        module = importlib.util.module_from_spec(spec)
        keep, sys.dont_write_bytecode = sys.dont_write_bytecode, True
        try:
            spec.loader.exec_module(module)
            for name in MEM_API:
                getattr(module, name)
        except KeyboardInterrupt:
            raise
        except BaseException as ex:  # whatever the fault in that file, a SyntaxError or a sys.exit too: it leaves through main()
            raise Refused("write refused: %s cannot be loaded (%s), so secret shapes cannot be checked" % (path, type(ex).__name__)) from None
        finally:
            sys.dont_write_bytecode = keep
        _mem = module
    return _mem


def loaded_patterns(mem, root) -> list:
    """The one loading point. A list of (name, compiled regex) or it raises: an empty generator is truthy, and a one-shot
    iterator would scan only the first field."""
    patterns = list(mem.load_secret_patterns(root))
    if not patterns:
        raise ValueError("the list is empty")
    for name, rx in patterns:
        if not isinstance(name, str) or not isinstance(rx, re.Pattern):
            raise TypeError("not a (name, compiled regex) pair")
    return patterns


class Cleaner:
    """Applies every content rule to text about to be written. A missing pattern file refuses here, before any write."""

    def __init__(self, ctx):
        self.mem = mem_module()
        try:
            self.patterns = loaded_patterns(self.mem, ctx.root)
        except KeyboardInterrupt:
            raise
        except BaseException as ex:  # a missing or malformed file, or a fault in mem.py's own code
            raise Refused("write refused: secret patterns cannot be loaded (%s: %s)" % (type(ex).__name__, ex)) from None
        self.redacted = []

    def clean(self, field: str, value) -> str:
        if not isinstance(value, str):
            raise Refused("%s: must be a string" % field)
        text = value.strip()
        if field in ONE_LINE:
            if RX_BREAK.search(text):
                raise Refused("%s: must be one line" % field)
        else:
            text = text.replace("\r\n", "\n").replace("\r", "\n")
        if RX_CONTROL.search(text):
            raise Refused("%s: control character" % field)
        check_english(field, text)
        try:
            hits = [name for name, rx in self.patterns if rx.search(text)]
            if self.mem.RX_PEM_BLOCK.search(text) and "private key" not in hits:
                hits.append("private key")
            stored = "" if hits else self.mem.redact_pii(text)
            if not isinstance(stored, str):
                raise TypeError("redact_pii returned %s" % type(stored).__name__)
        except KeyboardInterrupt:
            raise
        except BaseException as ex:  # a fault in mem.py's own code; its type only, as its message can hold the value
            raise Refused("write refused: %s cannot be checked for secrets and PII (%s)" % (field, type(ex).__name__)) from None
        if hits:
            raise Refused("refused: secret-shaped value in %s (%s)" % (field, ", ".join(hits)))
        if stored != text:
            self.redacted.append(field)
        limit = LIMITS[field]
        if len(stored) > limit:
            raise Refused("%s: %d chars, limit %d" % (field, len(stored), limit))
        return stored

    def required(self, field: str, value) -> str:
        if value is None:
            raise Refused("%s: required" % field)
        text = self.clean(field, value)
        if not text:
            raise Refused("%s: required" % field)
        return text

    def priority(self, value) -> str:
        if value is None or value == "":
            raise Refused("priority: required, one of %s" % ", ".join(PRIORITIES))
        if value not in PRIORITIES:
            raise Refused("priority: must be one of %s (Critical maps to Highest)" % ", ".join(PRIORITIES))
        return value

    def report(self):
        if self.redacted:
            print("redacted PII in: %s" % ", ".join(sorted(set(self.redacted))), file=sys.stderr)


def read_stdin_json(required: bool):
    stream = getattr(sys.stdin, "buffer", None)
    if sys.stdin is None or stream is None or sys.stdin.isatty():
        raw = b""
    else:
        raw = stream.read()
    if not raw.strip():
        if required:
            raise Refused("expected a JSON object on stdin")
        return {}
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except UnicodeDecodeError as ex:
        raise Refused("stdin is not UTF-8 JSON: %s" % ex) from None
    except ValueError as ex:
        raise Refused("stdin is not valid JSON: %s" % ex) from None
    if not isinstance(data, dict):
        raise Refused("expected a JSON object on stdin")
    return data


def by_of(cleaner: Cleaner, a) -> str:
    if a.by is None:
        return DEFAULT_BY
    if a.by != "GD" and a.by.strip() == "GD":  # clean() trims, which would store a padded form as the GD's attribution
        raise Refused("by: must be exactly GD, with no padding")
    return cleaner.required("by", a.by)


def note_of(cleaner: Cleaner, a, required: bool, allowed=("note",)) -> tuple[str | None, dict]:
    """--note, else the JSON on stdin. Returns the cleaned note and the rest of the JSON."""
    data = {} if a.note is not None else read_stdin_json(False)
    unknown = sorted(set(data) - set(allowed))
    if unknown:
        raise Refused("unknown field: %s" % shown_all(unknown))
    raw = a.note if a.note is not None else data.get("note")
    note = cleaner.clean("note", raw) if raw is not None else None
    if required and not note:
        raise Refused("note: required (--note, or {\"note\": ...} on stdin): who, what, the evidence reference")
    return note or None, data


def parse_count(text: str) -> int:
    m = re.fullmatch(r"\+(\d{1,3})", text)
    n = int(m.group(1)) if m else 0
    if not 1 <= n <= MAX_COUNT:
        raise Refused("bad count '%s': expected +n with n from 1 to %d" % (shown(text), MAX_COUNT))
    return n


# ---------------------------------------------------------------- paths and git

def run_git(cwd: Path, *args) -> tuple[int, str]:
    env = {k: v for k, v in os.environ.items() if k not in GIT_ENV}
    r = subprocess.run(["git", "-C", str(cwd)] + list(args), capture_output=True, env=env, timeout=30)
    return r.returncode, r.stdout.decode("utf-8", "replace").strip()


def main_checkout(root: Path) -> tuple[Path, Path | None, bool]:
    """(the checkout holding the journal, its git dir, whether root is a linked worktree). The rule of Get-BugsRoot in
    hooks/common.ps1, kept the same in effect: hooks/tests/run.ps1 drives both over the same layouts. Only the root's own .git
    counts, since git itself walks up to any link planted above. A link that leads nowhere refuses, read or write."""
    link = root / ".git"
    if not link.is_file():
        return root, link if link.is_dir() else None, False
    m = re.search(r"(?m)^gitdir:\s*(.+?)\s*$", link.read_text(encoding="utf-8-sig", errors="replace"))
    if not m:
        raise Refused("%s names no gitdir, so the main checkout's bug journal cannot be found" % shown(link, 200))
    git_dir = Path(os.path.normpath(root / m.group(1)))
    if not git_dir.is_dir():
        raise Refused("%s, named by %s, does not exist" % (shown(git_dir, 200), shown(link, 200)))
    common_file = git_dir / "commondir"
    if not common_file.is_file():
        if (git_dir / "objects").is_dir():  # a full git dir: a submodule or --separate-git-dir
            return root, git_dir, False
        raise Refused("%s is missing and %s holds no objects, so the main checkout's bug journal cannot be found" % (shown(common_file, 200), shown(git_dir, 200)))
    common = Path(os.path.normpath(git_dir / common_file.read_text(encoding="utf-8-sig", errors="replace").strip()))
    if common.name != ".git":
        raise Refused("%s is no checkout's .git, so the bug journal cannot be found" % shown(common, 200))
    if not common.is_dir():
        raise Refused("%s, named by %s, does not exist" % (shown(common, 200), shown(common_file, 200)))
    return common.parent.resolve(), common, True


class Ctx:
    """The root per main_checkout: a linked worktree reads the main checkout's data, a root with no .git has no git context."""

    def __init__(self, arg: str | None):
        given = Path(arg).resolve() if arg else Path(__file__).resolve().parents[4]
        if not given.is_dir():
            raise Refused("root %s is not a directory" % shown(given, 200))
        self.root, self.git_dir, self.linked = main_checkout(given)
        self.git_failed = False
        if self.git_dir is None:
            return
        try:
            code, out = run_git(given, "rev-parse", "--git-common-dir")
        except (OSError, subprocess.SubprocessError):
            code, out = 1, ""
        # Git is missing, refuses, or walked past a .git it will not read to a repo above: cannot rule out a linked worktree.
        if code or (given / out).resolve() != self.git_dir.resolve():
            self.git_failed, self.git_dir = True, None

    @property
    def workflow(self) -> Path:
        return self.root / ".workflow"

    @property
    def journal(self) -> Path:
        return self.workflow / "bugs.jsonl"

    @property
    def db_path(self) -> Path:
        return self.workflow / "bugs.db"

    @property
    def md(self) -> Path:
        return self.workflow / "bugs.md"

    def require_writable(self):
        if self.linked:
            raise Refused("writes from a linked worktree are refused: run from the main checkout %s" % self.root)
        if self.git_failed:
            raise Refused("git failed in %s: cannot rule out a linked worktree, write refused" % self.root)


def read_journal(ctx: Ctx) -> bytes:
    try:
        return ctx.journal.read_bytes()
    except FileNotFoundError:
        return b""


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------- journal parsing and replay

def need(cond: bool, msg: str):
    if not cond:
        raise ValueError(msg)


def is_count(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 1


def check_fields(data: dict, allowed):
    for key, value in data.items():
        need(key in allowed, "unknown field '%s'" % shown(key))
        need(value is None or isinstance(value, str), "field '%s' is not text" % key)
    if data.get("priority") is not None:
        need(data["priority"] in PRIORITIES, "bad priority")


def check_event(ev):
    """Shape only: replay never enforces transitions, the history already happened."""
    need(isinstance(ev, dict), "not an object")
    for key in ("event_uid", "bug_uid", "ts", "type"):
        need(isinstance(ev.get(key), str) and ev[key], "missing %s" % key)
    need(ev["type"] in EVENT_TYPES, "unknown type")
    need(RX_TS.fullmatch(ev["ts"]) is not None, "bad ts")
    try:
        parse_ts(ev["ts"])
    except ValueError:
        need(False, "bad ts")
    for key in ("by", "note"):
        need(ev.get(key) is None or isinstance(ev[key], str), "%s is not text" % key)
    data = ev.get("data")
    need(isinstance(data, dict), "missing data")
    t = ev["type"]
    if t == "create":
        need(is_count(data.get("id")), "bad id")
        for key in ("title", "description", "priority"):
            need(isinstance(data.get(key), str), "missing %s" % key)
        need(data.get("status", "Request") in STATUSES, "bad status")
        check_fields({k: v for k, v in data.items() if k not in ("id", "status")}, UPDATABLE)
    elif t == "update":
        check_fields(data, UPDATABLE)
    elif t == "status":
        need(data.get("to") in STATUSES, "bad status")
        need(data.get("from") is None or data["from"] in STATUSES, "bad status")
        need(data.get("duplicate_of") is None or isinstance(data["duplicate_of"], str), "bad duplicate_of")
    elif t in ("round", "extra_round"):
        need(data.get("counter") in DEFAULT_CAPS, "bad counter")
        need(is_count(data.get("n")) and data["n"] <= MAX_COUNT, "bad n")
    elif t == "stop_rule":
        need(data.get("counter") in DEFAULT_CAPS, "bad counter")
        need(data.get("extra_dispatch") in ("unused", "used"), "bad extra_dispatch")
    elif t == "renumber":
        need(is_count(data.get("from")) and is_count(data.get("to")), "bad renumber")
    elif t == "tombstone":
        need(is_count(data.get("id")), "bad tombstone")


class Parsed:
    def __init__(self):
        self.events, self.errors, self.torn = [], [], False


def parse_journal(raw: bytes) -> Parsed:
    """A final line with no newline that is not JSON is a torn write: skipped here, removed by the next write."""
    out = Parsed()
    lines = raw.split(b"\n")
    tail = lines.pop()
    for i, line in enumerate(lines + [tail], 1):
        if not line.strip():
            continue
        is_tail = i == len(lines) + 1
        try:
            ev = json.loads(line.decode("utf-8"))
        except ValueError as ex:  # JSONDecodeError and UnicodeDecodeError are both ValueError
            if is_tail:
                out.torn = True
            else:
                out.errors.append("line %d: %s" % (i, type(ex).__name__))
            continue
        try:
            check_event(ev)
        except (ValueError, TypeError) as ex:  # TypeError: an unhashable value where a name belongs
            out.errors.append("line %d: %s" % (i, ex))
            continue
        out.events.append(ev)
    return out


def canon(ev: dict) -> str:
    return json.dumps(ev, sort_keys=True, ensure_ascii=False)


def high_water_of(events) -> int:
    top = 0
    for ev in events:
        d = ev["data"]
        if ev["type"] in ("create", "tombstone"):
            top = max(top, d["id"])
        elif ev["type"] == "renumber":
            top = max(top, d["from"], d["to"])
    return top


def replay_order(events) -> list:
    """Sort by (ts, event_uid), one copy per event_uid, tombstoned uids dropped, creates first."""
    best = {}
    for ev in events:
        key = (ev["ts"], canon(ev))
        if ev["event_uid"] not in best or key < best[ev["event_uid"]][0]:
            best[ev["event_uid"]] = (key, ev)
    unique = [v[1] for v in best.values()]
    dead = {ev["bug_uid"] for ev in unique if ev["type"] == "tombstone"}
    live = [ev for ev in unique if ev["type"] != "tombstone" and ev["bug_uid"] not in dead]
    live.sort(key=lambda ev: (ev["ts"], ev["event_uid"]))
    creates = [ev for ev in live if ev["type"] == "create"]
    uids = [ev["bug_uid"] for ev in creates]
    if len(set(uids)) != len(uids):
        raise Corrupt("corrupt journal: two create lines for one bug_uid")
    known = set(uids)
    for ev in live:
        if ev["bug_uid"] not in known:
            raise Corrupt("corrupt journal: %s line for a bug_uid with no create: %s" % (ev["type"], shown(ev["event_uid"])))
    return creates + [ev for ev in live if ev["type"] != "create"]


# ---------------------------------------------------------------- database

_connections = []  # closed by main()


def connect(target: str, **kw) -> sqlite3.Connection:
    db = sqlite3.connect(target, timeout=10, isolation_level=None, **kw)
    db.row_factory = sqlite3.Row
    _connections.append(db)
    return db


def create_schema(db):
    db.execute("BEGIN IMMEDIATE")
    try:
        if db.execute("PRAGMA user_version").fetchone()[0] == 0:
            for stmt in SCHEMA:
                db.execute(stmt)
            db.execute("PRAGMA user_version=%d" % SCHEMA_VERSION)
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise


def remove_db(ctx: Ctx):
    for db in list(_connections):
        db.close()
        _connections.remove(db)
    for f in ctx.workflow.glob("bugs.db*"):
        f.unlink()


def open_db(ctx: Ctx, create=False) -> sqlite3.Connection:
    """No journal, no DB, not a create: an empty in-memory store, so reads return nothing and create nothing."""
    if not create and not ctx.db_path.exists() and not ctx.journal.exists():
        db = connect(":memory:")
        create_schema(db)
        return db
    ctx.workflow.mkdir(parents=True, exist_ok=True)
    for _ in range(2):
        try:
            db = connect(str(ctx.db_path))
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, SCHEMA_VERSION):
                raise sqlite3.DatabaseError("schema version %d" % version)
            if version == 0:  # a read must not take the write lock when the schema is already there
                create_schema(db)
            db.execute("SELECT 1 FROM meta LIMIT 1").fetchall()
            return db
        except sqlite3.OperationalError as ex:
            if "lock" in str(ex):
                raise
            remove_db(ctx)  # the DB is a cache: a damaged one is rebuilt from the journal
        except sqlite3.DatabaseError:
            remove_db(ctx)
    raise RuntimeError("cannot open %s" % ctx.db_path)


def get_meta(db, key: str) -> str | None:
    row = db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row[0] if row else None


def set_meta(db, key: str, value):
    db.execute("INSERT OR REPLACE INTO meta(key, value) VALUES(?, ?)", (key, str(value)))


def apply_event(db, ev: dict):
    """The one path from a journal line to the tables, for replay and for a write alike."""
    t, uid, ts, data = ev["type"], ev["bug_uid"], ev["ts"], ev["data"]
    if t == "create":
        row = {k: data.get(k) for k in UPDATABLE}
        status = data.get("status", "Request")
        db.execute("""INSERT INTO bug(id, uid, title, description, priority, status, feature, owner, regression_test, repro, expected,
                      actual, evidence, root_cause, fix_cap, review_cap, created_at, updated_at, closed_at)
                      VALUES(:id, :uid, :title, :description, :priority, :status, :feature, :owner, :regression_test, :repro, :expected,
                      :actual, :evidence, :root_cause, :fix_cap, :review_cap, :ts, :ts, :closed)""",
                   dict(row, id=fmt_id(data["id"]), uid=uid, status=status, fix_cap=DEFAULT_CAPS["fix"], review_cap=DEFAULT_CAPS["review"],
                        ts=ts, closed=ts if status in TERMINAL else None))
    elif t == "update":
        for key in data:  # check_event limited the keys to UPDATABLE: column names never come from the journal unchecked
            if key not in UPDATABLE:
                raise Corrupt("corrupt journal: unknown field in %s" % shown(ev["event_uid"]))
            db.execute("UPDATE bug SET %s=? WHERE uid=?" % key, (data[key], uid))
    elif t == "status":
        to = data["to"]
        db.execute("UPDATE bug SET status=?, duplicate_of=?, closed_at=? WHERE uid=?",
                   (to, data.get("duplicate_of"), ts if to in TERMINAL else None, uid))
    elif t == "round":
        col = "fix_used" if data["counter"] == "fix" else "review_used"
        db.execute("UPDATE bug SET %s=%s+? WHERE uid=?" % (col, col), (data["n"], uid))
    elif t == "extra_round":
        col = "fix_cap" if data["counter"] == "fix" else "review_cap"
        db.execute("UPDATE bug SET %s=%s+? WHERE uid=?" % (col, col), (data["n"], uid))
    elif t == "renumber":
        db.execute("UPDATE bug SET id=? WHERE uid=?", (fmt_id(data["to"]), uid))
    db.execute("UPDATE bug SET updated_at=? WHERE uid=?", (ts, uid))
    db.execute("INSERT INTO bug_event(event_uid, bug_uid, ts, type, by_who, note, data) VALUES(?, ?, ?, ?, ?, ?, ?)",
               (ev["event_uid"], uid, ts, t, ev.get("by"), ev.get("note"), json.dumps(data, ensure_ascii=False, sort_keys=True)))


def sync_fts(db, uid: str):
    row = db.execute("SELECT rowid AS rid, * FROM bug WHERE uid=?", (uid,)).fetchone()
    db.execute("DELETE FROM bug_fts WHERE rowid=?", (row["rid"],))
    notes = " ".join(r[0] for r in db.execute("SELECT note FROM bug_event WHERE bug_uid=? AND note IS NOT NULL ORDER BY ts", (uid,)))
    db.execute("INSERT INTO bug_fts(rowid, title, description, repro, expected, actual, evidence, root_cause, notes) VALUES(?,?,?,?,?,?,?,?,?)",
               (row["rid"], row["title"], row["description"], row["repro"], row["expected"], row["actual"], row["evidence"], row["root_cause"], notes))


def rebuild_tables(db, raw: bytes):
    """Inside the caller's transaction. A corrupt journal raises and leaves the old cache, whose hash still mismatches."""
    parsed = parse_journal(raw)
    if parsed.errors:
        raise Corrupt("corrupt journal: %s" % "; ".join(parsed.errors[:5]))
    ordered = replay_order(parsed.events)
    for table in ("bug_event", "bug_fts", "bug", "meta"):
        db.execute("DELETE FROM %s" % table)
    try:
        for ev in ordered:
            apply_event(db, ev)
    except sqlite3.IntegrityError as ex:
        raise Corrupt("corrupt journal: %s" % ex) from None
    for row in db.execute("SELECT uid FROM bug").fetchall():
        sync_fts(db, row[0])
    set_meta(db, "high_water", high_water_of(parsed.events))
    set_meta(db, "purged_ids", json.dumps(sorted({ev["data"]["id"] for ev in parsed.events if ev["type"] == "tombstone"})))
    set_meta(db, "last_ts", max((ev["ts"] for ev in parsed.events), default=""))
    set_meta(db, "journal_hash", sha(raw))


def transaction_rebuild(ctx: Ctx, db, force=False):
    db.execute("BEGIN IMMEDIATE")
    try:
        raw = read_journal(ctx)
        if force or get_meta(db, "journal_hash") != sha(raw):
            rebuild_tables(db, raw)
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise


def open_read(ctx: Ctx) -> sqlite3.Connection:
    """Every command runs the hash check: it covers git switch, pull and merge."""
    db = open_db(ctx)
    if get_meta(db, "journal_hash") != sha(read_journal(ctx)):
        transaction_rebuild(ctx, db)
    return db


def high_water(db) -> int:
    return int(get_meta(db, "high_water") or 0)


def purged_numbers(db) -> set:
    return set(json.loads(get_meta(db, "purged_ids") or "[]"))


def holders(db, num: int, rows) -> int:
    """How many bug_uids hold this ID. A tombstone holds its ID: a live bug on it came in through a merge."""
    return len(rows) + (1 if num in purged_numbers(db) else 0)


def duplicate_ids(db) -> list:
    purged = {fmt_id(n) for n in purged_numbers(db)}
    live = db.execute("SELECT id, COUNT(*) FROM bug GROUP BY id ORDER BY CAST(substr(id, 5) AS INTEGER)").fetchall()
    return [r[0] for r in live if r[1] > 1 or r[0] in purged]


def warn_duplicates(db):
    for bug_id in duplicate_ids(db):
        print("warning: duplicate id %s held by two bug_uids: run doctor --fix" % bug_id, file=sys.stderr)


def live_bug(db, bug_id: str):
    """The one bug a write or counters may touch. A duplicate id fails closed."""
    num = parse_id(bug_id)
    rows = db.execute("SELECT * FROM bug WHERE id=?", (fmt_id(num),)).fetchall()
    if rows and holders(db, num, rows) > 1:
        raise Refused("duplicate id %s held by %d bug_uids: run doctor --fix" % (bug_id, holders(db, num, rows)))
    if rows:
        return rows[0]
    if num <= high_water(db):
        raise Refused("%s was purged" % bug_id)
    raise Refused("%s not found" % bug_id)


# ---------------------------------------------------------------- the write path

def encode_line(ev: dict) -> bytes:
    return json.dumps(ev, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"


def split_tail(raw: bytes) -> tuple[bytes, bytes]:
    cut = raw.rfind(b"\n") + 1
    return raw[:cut], raw[cut:]


def repaired(raw: bytes) -> bytes:
    """A final line with no newline: a whole event gets its newline, a torn fragment goes."""
    body, tail = split_tail(raw)
    if not tail.strip():
        return body
    try:
        json.loads(tail.decode("utf-8"))
    except ValueError:
        return body
    return body + tail + b"\n"


def append_lines(ctx: Ctx, lines: list) -> bytes:
    """LF only, UTF-8, no BOM, whatever the platform. Returns the journal's new bytes."""
    raw = read_journal(ctx)
    fixed = repaired(raw)
    if len(fixed) < len(raw):  # never rewrite the good lines: only the fragment goes
        with open(ctx.journal, "r+b") as f:
            f.truncate(len(fixed))
    blob = (b"\n" if len(fixed) > len(raw) else b"") + b"".join(lines)
    with open(ctx.journal, "ab") as f:
        f.write(blob)
        f.flush()
        os.fsync(f.fileno())
    return (raw if len(fixed) > len(raw) else fixed) + blob


def replace_journal(ctx: Ctx, raw: bytes):
    tmp = ctx.workflow / "bugs.db.jsonl.tmp"  # the bugs.db* ignore rule covers a leftover
    with open(tmp, "wb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, ctx.journal)


class Writer:
    """BEGIN IMMEDIATE, hash check, rebuild if different, the command validates, apply, append, commit.
    A crash after the append is healed by the next command's hash mismatch."""

    def __init__(self, ctx: Ctx, create=False):
        self.ctx, self.create, self.lines = ctx, create, []
        self.rewritten = None

    def __enter__(self):
        self.ctx.require_writable()
        Cleaner(self.ctx)  # every write, text-free ones too: a missing pattern file refuses here (schema.md, Fail closed)
        self.db = open_db(self.ctx, create=self.create)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            raw = read_journal(self.ctx)
            if get_meta(self.db, "journal_hash") != sha(raw):
                rebuild_tables(self.db, raw)
            self.last_ts = get_meta(self.db, "last_ts") or None
            self.top = high_water(self.db)
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        return self

    def emit(self, etype: str, uid: str, data: dict, by=None, note=None, ts=None, event_uid=None) -> dict:
        ev = {"event_uid": event_uid or str(uuid.uuid4()), "bug_uid": uid, "ts": ts or next_ts(self.last_ts), "type": etype, "data": data}
        if by is not None:
            ev["by"] = by
        if note is not None:
            ev["note"] = note
        apply_event(self.db, ev)
        sync_fts(self.db, uid)
        self.lines.append(encode_line(ev))
        self.last_ts = max(self.last_ts or "", ev["ts"])
        self.top = max(self.top, high_water_of([ev]))
        return ev

    def rewrite(self, drop: set, tombstones=()):
        """Drops the lines of `drop` and of every tombstoned uid, repairs the tail, appends tombstones. Atomic replace."""
        raw = repaired(read_journal(self.ctx))
        parsed = parse_journal(raw)
        drop = set(drop) | {ev["bug_uid"] for ev in parsed.events if ev["type"] == "tombstone"}
        kept = []
        for line in raw.split(b"\n")[:-1]:
            if line.strip():
                ev = json.loads(line.decode("utf-8"))
                if ev["type"] == "tombstone" or ev["bug_uid"] not in drop:
                    kept.append(line + b"\n")
        for num, uid in tombstones:
            ts = next_ts(self.last_ts)
            self.last_ts = ts
            # Same event_uid on every branch: two purges of one bug dedupe. Text-free by construction.
            kept.append(encode_line({"event_uid": stable_uid("tombstone/" + uid), "bug_uid": uid, "ts": ts, "type": "tombstone", "data": {"id": num}}))
        new = b"".join(kept)
        replace_journal(self.ctx, new)
        _after_append()
        rebuild_tables(self.db, new)
        self.last_ts = get_meta(self.db, "last_ts") or None
        self.top = high_water(self.db)

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.db.execute("ROLLBACK")
            return False
        try:
            if self.lines:
                new = append_lines(self.ctx, self.lines)
                _after_append()
                set_meta(self.db, "journal_hash", sha(new))
                set_meta(self.db, "high_water", self.top)
                set_meta(self.db, "last_ts", self.last_ts or "")
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        return False


# ---------------------------------------------------------------- write commands

def cmd_add(ctx, a):
    ctx.require_writable()
    cleaner = Cleaner(ctx)
    data = read_stdin_json(True)
    allowed = set(UPDATABLE) | {"note"}
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise Refused("add: unknown field: %s (status starts at Request; bugs have a priority, no severity)" % shown_all(unknown))
    record = {"priority": cleaner.priority(data.get("priority"))}
    for field in REQUIRED:
        record[field] = cleaner.required(field, data.get(field))
    for field in OPTIONAL:
        if data.get(field) not in (None, ""):
            record[field] = cleaner.clean(field, data[field])
    note = cleaner.clean("note", data["note"]) if data.get("note") else None
    by = by_of(cleaner, a)
    with Writer(ctx, create=True) as w:
        num = w.top + 1
        w.emit("create", str(uuid.uuid4()), dict(record, id=num, status="Request"), by=by, note=note)
    cleaner.report()
    print(fmt_id(num))
    return 0


def cmd_update(ctx, a):
    ctx.require_writable()
    parse_id(a.id)
    cleaner = Cleaner(ctx)
    data = read_stdin_json(True)
    unknown = sorted(set(data) - set(UPDATABLE) - {"note"})
    if unknown:
        raise Refused("update: unknown or read-only field: %s (status moves through set-status)" % shown_all(unknown))
    note = (cleaner.clean("note", data["note"]) or None) if data.get("note") else None
    changes = {}
    for field, value in data.items():
        if field == "note":
            continue
        if field == "priority":
            changes[field] = cleaner.priority(value)
        elif field in REQUIRED:
            changes[field] = cleaner.required(field, value)
        else:
            changes[field] = (cleaner.clean(field, value) or None) if value is not None else None
    by = by_of(cleaner, a)
    with Writer(ctx) as w:
        row = live_bug(w.db, a.id)
        changes = {k: v for k, v in changes.items() if row[k] != v}
        if changes or note:  # a note alone is evidence: /fix records it this way
            w.emit("update", row["uid"], changes, by=by, note=note)
    cleaner.report()
    written = sorted(changes) + (["note"] if note else [])
    print("%s updated: %s" % (a.id, ", ".join(written)) if written else "%s: no change" % a.id)
    return 0


def cmd_set_status(ctx, a):
    ctx.require_writable()
    parse_id(a.id)
    if a.status not in STATUSES:
        raise Refused("unknown status '%s': one of %s" % (shown(a.status), ", ".join(STATUSES)))
    cleaner = Cleaner(ctx)
    note, data = note_of(cleaner, a, True, ("note", "duplicate_of"))
    by = by_of(cleaner, a)
    dup = a.duplicate_of if a.duplicate_of is not None else data.get("duplicate_of")
    if a.status != "Duplicate" and dup is not None:
        raise Refused("duplicate_of: only with status Duplicate")
    with Writer(ctx) as w:
        row = live_bug(w.db, a.id)
        rule = move_rule(row["status"], a.status)
        if rule is None:
            raise Refused("%s: %s -> %s is not in the state machine (references/schema.md)" % (a.id, row["status"], a.status))
        if rule == "gd" and by != "GD":
            raise Refused("%s: %s -> %s is GD only (state machine in references/schema.md): pass --by GD on the GD's order" % (a.id, row["status"], a.status))
        payload = {"from": row["status"], "to": a.status}
        if a.status == "Duplicate":
            if not dup:
                raise Refused("duplicate_of: required for Duplicate")
            target = parse_id(dup)
            if fmt_id(target) == row["id"]:
                raise Refused("duplicate_of: a bug cannot duplicate itself")
            if target > w.top:
                raise Refused("duplicate_of: %s not found" % dup)
            payload["duplicate_of"] = fmt_id(target)
        w.emit("status", row["uid"], payload, by=by, note=note)
    cleaner.report()
    print("%s %s -> %s" % (a.id, row["status"], a.status))
    return 0


def counter_write(ctx, a, etype):
    ctx.require_writable()
    parse_id(a.id)
    n = parse_count(a.n)
    cleaner = Cleaner(ctx)
    note, _ = note_of(cleaner, a, True)
    by = by_of(cleaner, a)
    with Writer(ctx) as w:
        row = live_bug(w.db, a.id)
        w.emit(etype, row["uid"], {"counter": a.counter, "n": n}, by=by, note=note)
        used, cap = (w.db.execute("SELECT %s_used, %s_cap FROM bug WHERE uid=?" % (a.counter, a.counter), (row["uid"],)).fetchone())
    cleaner.report()
    print("%s %s %d/%d" % (a.id, a.counter, used, cap))
    return 0


def cmd_round(ctx, a):
    return counter_write(ctx, a, "round")


def cmd_extra_round(ctx, a):
    return counter_write(ctx, a, "extra_round")


def cmd_stop_rule(ctx, a):
    ctx.require_writable()
    parse_id(a.id)
    cleaner = Cleaner(ctx)
    note = cleaner.clean("note", a.note) if a.note is not None else None
    by = by_of(cleaner, a)
    with Writer(ctx) as w:
        row = live_bug(w.db, a.id)
        w.emit("stop_rule", row["uid"], {"counter": a.counter, "extra_dispatch": a.extra_dispatch}, by=by, note=note or None)
    cleaner.report()
    print("%s stop rule: %s, extra dispatch %s" % (a.id, a.counter, a.extra_dispatch))
    return 0


def cmd_delete(ctx, a):
    ctx.require_writable()
    parse_id(a.id)
    if a.by != "GD":
        raise Refused("delete is GD only: pass --by GD on the GD's order")
    with Writer(ctx) as w:
        row = live_bug(w.db, a.id)
        w.rewrite({row["uid"]}, [(parse_id(row["id"]), row["uid"])])
    print("deleted %s, journal uncommitted" % a.id)
    return 0


# ---------------------------------------------------------------- read commands

def public_row(row) -> dict:
    return {k: row[k] for k in row.keys()}


def record_of(db, uid: str) -> str:
    """The old record lines, so round-cap.ps1's New-Counter regexes keep matching."""
    stops, extras = {}, []
    for ev in db.execute("SELECT * FROM bug_event WHERE bug_uid=? AND type IN ('stop_rule','extra_round') ORDER BY ts, event_uid", (uid,)):
        data = json.loads(ev["data"])
        if ev["type"] == "stop_rule":
            stops[data["counter"]] = "- Stop rule: %s root-caused %s - extra dispatch: %s" % (data["counter"], ev["ts"][:10], data["extra_dispatch"])
        else:
            extras.append("extra round: %s +%d" % (data["counter"], data["n"]))
    return "\n".join([stops[k] for k in sorted(stops)] + extras)


def cmd_counters(ctx, a):
    db = open_read(ctx)
    num = parse_id(a.id)
    bug_id = fmt_id(num)
    rows = db.execute("SELECT * FROM bug WHERE id=?", (bug_id,)).fetchall()
    if rows and holders(db, num, rows) > 1:
        raise Refused("duplicate id %s held by %d bug_uids: run doctor --fix" % (bug_id, holders(db, num, rows)))
    if not rows:
        out = {"id": bug_id, "found": False, "settled": False, "status": None,
               "fix": {"used": 0, "cap": DEFAULT_CAPS["fix"]}, "review": {"used": 0, "cap": DEFAULT_CAPS["review"]}, "record": ""}
    else:
        r = rows[0]
        out = {"id": bug_id, "found": True, "settled": is_settled(r["status"]), "status": r["status"],
               "fix": {"used": r["fix_used"], "cap": r["fix_cap"]}, "review": {"used": r["review_used"], "cap": r["review_cap"]},
               "record": record_of(db, r["uid"])}
    print(json.dumps(out, ensure_ascii=False))
    return 0


def events_of(db, uid: str) -> list:
    out = []
    for ev in db.execute("SELECT * FROM bug_event WHERE bug_uid=? ORDER BY ts, event_uid", (uid,)):
        out.append({"ts": ev["ts"], "type": ev["type"], "by": ev["by_who"], "note": ev["note"], "data": ev["data"]})
    return out


def print_record(row, events):
    print("%s | %s | %s | uid %s" % (row["id"], row["priority"], row["status"], row["uid"]))
    labels = (("Title", "title"), ("Description", "description"), ("Feature", "feature"), ("Owner", "owner"), ("Regression test", "regression_test"),
              ("Repro", "repro"), ("Expected", "expected"), ("Actual", "actual"), ("Evidence", "evidence"), ("Root cause", "root_cause"),
              ("Duplicate of", "duplicate_of"), ("Created", "created_at"), ("Updated", "updated_at"), ("Closed", "closed_at"))
    for label, key in labels:
        if row[key] is not None:
            print("%s: %s" % (label, row[key]))
    print("Fix rounds: %d/%d" % (row["fix_used"], row["fix_cap"]))
    print("Review rounds: %d/%d" % (row["review_used"], row["review_cap"]))
    print("Events:")
    for ev in events:
        data = json.loads(ev["data"])
        what = "%s -> %s" % (data.get("from", "?"), data["to"]) if ev["type"] == "status" else ev["type"]
        print("- %s %s by %s%s" % (ev["ts"], what, ev["by"] or "unknown", ": " + ev["note"] if ev["note"] else ""))


def cmd_show(ctx, a):
    db = open_read(ctx)
    num = parse_id(a.id)
    rows = db.execute("SELECT * FROM bug WHERE id=?", (fmt_id(num),)).fetchall()
    if not rows:
        if num <= high_water(db):
            print(json.dumps({"id": fmt_id(num), "purged": True}) if a.json else "%s purged" % fmt_id(num))
            return 0
        raise Refused("%s not found" % a.id)
    if holders(db, num, rows) > 1:
        warn_duplicates(db)
    if a.json:
        items = [dict(public_row(r), events=events_of(db, r["uid"])) for r in rows]
        print(json.dumps(items[0] if len(items) == 1 else items, ensure_ascii=False, indent=1))
    else:
        for r in rows:
            print_record(r, events_of(db, r["uid"]))
    return 0


def cmd_list(ctx, a):
    db = open_read(ctx)
    where, params = [], []
    if a.status:
        where.append("status IN (%s)" % ",".join("?" * len(a.status)))
        params += a.status
    if a.priority:
        where.append("priority IN (%s)" % ",".join("?" * len(a.priority)))
        params += a.priority
    if a.feature:
        where.append("feature=?")
        params.append(a.feature)
    if a.open:
        where.append("status IN (%s)" % ",".join("?" * len(OPEN)))
        params += OPEN
    rows = db.execute("SELECT * FROM bug %s ORDER BY CAST(substr(id, 5) AS INTEGER), uid" % ("WHERE " + " AND ".join(where) if where else ""), params).fetchall()
    warn_duplicates(db)
    if a.json:
        print(json.dumps([public_row(r) for r in rows], ensure_ascii=False, indent=1))
        return 0
    if not rows:
        print("no bugs")
        return 0
    print("ID | Priority | Status | Closed | Feature | Title")
    for r in rows:
        print(" | ".join((r["id"], r["priority"], r["status"], (r["closed_at"] or "-")[:10], r["feature"] or "-", r["title"])))
    return 0


def cmd_search(ctx, a):
    terms = re.findall(r"\w+", a.text.lower())
    if not terms:
        raise Refused("search: no words in the query")
    db = open_read(ctx)
    expr = " OR ".join('"%s"*' % t for t in terms)
    rows = db.execute("""SELECT b.id, b.priority, b.status, b.title, snippet(bug_fts, -1, '[', ']', '...', 14) AS hit
                         FROM bug_fts JOIN bug b ON b.rowid = bug_fts.rowid WHERE bug_fts MATCH ?
                         ORDER BY bm25(bug_fts, 8, 4, 1, 1, 1, 1, 1, 1) LIMIT ?""", (expr, a.n)).fetchall()
    if not rows:
        print("no matches")
    for r in rows:
        print("%s | %s | %s | %s" % (r["id"], r["priority"], r["status"], r["title"]))
        print("  %s" % r["hit"].replace("\n", " "))
    return 0


def sql_authorizer(action, arg1, arg2, dbname, trigger):
    """Second wall behind mode=ro: mode=ro alone still allows temp tables and VACUUM INTO."""
    if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, getattr(sqlite3, "SQLITE_RECURSIVE", 33)):
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_FUNCTION:
        return sqlite3.SQLITE_DENY if (arg2 or "").lower() in ("load_extension", "fts3_tokenizer") else sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_PRAGMA and (arg1 or "").lower() == "data_version":  # FTS5 reads it on every MATCH
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def strip_sql_comments(text: str) -> str:
    return re.sub(r"--[^\n]*|/\*.*?(?:\*/|$)", " ", text, flags=re.S).strip()


def sql_cell(value):
    return "x'%s'" % value.hex() if isinstance(value, bytes) else value  # a BLOB prints as its SQL literal


def cmd_sql(ctx, a):
    query = strip_sql_comments(a.query)
    first = re.match(r"[A-Za-z]+", query)
    if not first or first.group(0).upper() not in ("SELECT", "WITH", "VALUES"):
        raise Refused("sql is read-only: only SELECT, WITH and VALUES")
    db = open_read(ctx)
    if ctx.db_path.exists():
        db.close()
        db = connect(ctx.db_path.resolve().as_uri() + "?mode=ro", uri=True)
    db.execute("PRAGMA query_only=ON")
    db.set_authorizer(sql_authorizer)
    deadline = dt.datetime.now() + dt.timedelta(seconds=SQL_SECONDS)
    expired = []

    def past_deadline():
        if dt.datetime.now() > deadline:
            expired.append(True)
        return bool(expired)

    db.set_progress_handler(past_deadline, 100000)
    try:
        cur = db.execute(a.query)
        rows = cur.fetchmany(1001)
    except (sqlite3.Error, sqlite3.Warning) as ex:
        # A Ctrl+C lands in the handler, and SQLite reports it as this error with the deadline not reached.
        if not expired and isinstance(ex, sqlite3.OperationalError) and str(ex) == "interrupted":
            raise KeyboardInterrupt from None
        raise Refused("sql refused: %s" % shown(ex, 200)) from None  # SQLite quotes the query
    names = [c[0] for c in cur.description or ()]
    more = len(rows) > 1000
    rows = rows[:1000]
    if a.json:
        print(json.dumps([dict(zip(names, map(sql_cell, tuple(r)))) for r in rows], ensure_ascii=False, indent=1))
    else:
        print("\t".join(names))
        for r in rows:
            print("\t".join("" if v is None else str(sql_cell(v)).replace("\n", "\\n") for v in tuple(r)))
    if more:
        print("(first 1000 rows)", file=sys.stderr)
    return 0


def cmd_stats(ctx, a):
    db = open_read(ctx)
    marks = ",".join("?" * len(OPEN))
    n = db.execute("SELECT COUNT(*) FROM bug WHERE status IN (%s)" % marks, OPEN).fetchone()[0]
    h = db.execute("SELECT COUNT(*) FROM bug WHERE status IN (%s) AND priority IN ('High','Highest')" % marks, OPEN).fetchone()[0]
    print("Bugs: %d open (%d High+)" % (n, h))
    return 0


# ---------------------------------------------------------------- purge, rebuild, doctor

def purge_candidates(db) -> list:
    now = now_utc()
    rows = db.execute("SELECT * FROM bug WHERE closed_at IS NOT NULL AND status IN (%s) ORDER BY CAST(substr(id, 5) AS INTEGER)" % ",".join("?" * len(TERMINAL)), TERMINAL).fetchall()
    return [r for r in rows if now - parse_ts(r["closed_at"]) > WINDOW]  # strictly more than 90 days


def auto_block_reason(ctx: Ctx) -> str | None:
    if ctx.linked:
        return "linked worktree"
    if ctx.git_failed:
        return "git failed"
    if ctx.git_dir is None:
        return "not a git repository"
    for marker, what in (("MERGE_HEAD", "merge"), ("rebase-merge", "rebase"), ("rebase-apply", "rebase"),
                         ("CHERRY_PICK_HEAD", "cherry-pick"), ("REVERT_HEAD", "revert")):
        if (ctx.git_dir / marker).exists():
            return "%s in progress" % what
    code, branch = run_git(ctx.root, "symbolic-ref", "--short", "-q", "HEAD")
    if code:
        return "detached HEAD"
    if branch.startswith("feature/"):
        return "on branch %s" % branch
    code, out = run_git(ctx.root, "status", "--porcelain", "--", ".workflow/bugs.jsonl")
    if code:
        return "git status failed"
    if out:
        return "journal not clean in git status"
    return None


def cmd_purge(ctx, a):
    if os.environ.get("BUGS_NOW"):
        print("warning: BUGS_NOW is set: time here reads as the test clock", file=sys.stderr)
    if a.auto:
        why = auto_block_reason(ctx)
        if why:
            print("purge skipped: %s" % why)
            return 0
    if a.dry_run:
        db = open_read(ctx)
        rows = purge_candidates(db)
        for r in rows:
            print("%s | %s | closed %s | %s" % (r["id"], r["status"], r["closed_at"], r["title"]))
        print("would purge %d" % len(rows))
        return 0
    ctx.require_writable()
    if not ctx.journal.exists():
        print("purged 0")
        return 0
    with Writer(ctx) as w:
        rows = purge_candidates(w.db)
        if rows:
            w.rewrite({r["uid"] for r in rows}, [(parse_id(r["id"]), r["uid"]) for r in rows])
    print("purged %d, journal uncommitted" % len(rows) if rows else "purged 0")
    return 0


def cmd_rebuild(ctx, a):
    db = open_db(ctx)
    transaction_rebuild(ctx, db, force=True)
    bugs_n = db.execute("SELECT COUNT(*) FROM bug").fetchone()[0]
    events_n = db.execute("SELECT COUNT(*) FROM bug_event").fetchone()[0]
    warn_duplicates(db)
    print("rebuilt: %d bugs, %d events" % (bugs_n, events_n))
    return 0


def journal_problems(raw: bytes, db) -> tuple[list, list, set]:
    parsed = parse_journal(raw)
    problems = list(parsed.errors)
    if parsed.torn:
        problems.append("torn final line: removed by the next write or doctor --fix")
    inert = set()
    if not parsed.errors:
        dead = {ev["bug_uid"] for ev in parsed.events if ev["type"] == "tombstone"}
        inert = {ev["bug_uid"] for ev in parsed.events if ev["type"] != "tombstone" and ev["bug_uid"] in dead}
        if inert:
            problems.append("%d purged bug(s) still have inert lines, a merge brought them back: doctor --fix removes them" % len(inert))
    dups = duplicate_ids(db) if db is not None else []
    problems += ["duplicate id %s held by two bug_uids: doctor --fix renumbers the later create" % d for d in dups]
    return problems, dups, inert


def renumber_duplicates(w: Writer) -> list:
    done = []
    for bug_id in duplicate_ids(w.db):
        rows = w.db.execute("SELECT uid FROM bug WHERE id=? ORDER BY created_at, uid", (bug_id,)).fetchall()
        # A tombstone keeps its ID, so no live bug may stay on it; between two live bugs the earlier create stays.
        for row in rows[0 if parse_id(bug_id) in purged_numbers(w.db) else 1:]:
            old, new = parse_id(bug_id), w.top + 1
            # Same event_uid on two machines fixing the same merge: the second copy dedupes.
            w.emit("renumber", row["uid"], {"from": old, "to": new}, by="doctor", event_uid=stable_uid("renumber/%s/%d/%d" % (row["uid"], old, new)))
            done.append("renumbered %s to %s" % (bug_id, fmt_id(new)))
    return done


def git_problems(ctx: Ctx) -> list:
    """What the project's own git rules do to the journal. No repair: the rules are the project's to change."""
    if ctx.git_dir is None:
        return []
    out = []
    path = ".workflow/bugs.jsonl"
    if not ctx.journal.exists():
        code, text = run_git(ctx.root, "status", "--porcelain", "--", path)
        if not code and "D" in text[:2]:
            out.append("journal deleted: git tracks %s and the file is gone. Restore it with git restore, or commit an empty one" % path)
    for attr, want, harm in (("merge", "union", "merges can conflict"), ("eol", "lf", "the journal can end up with mixed line endings")):
        code, text = run_git(ctx.root, "check-attr", attr, "--", path)
        got = text.rsplit(": ", 1)[-1] if not code else "unknown"
        if got != want:
            out.append("journal attributes: %s resolves to %s, not %s: %s. Put `%s text eol=lf merge=union` "
                       "in .gitattributes, after any rule that overrides it" % (attr, shown(got), want, harm, path))
    code, _ = run_git(ctx.root, "check-ignore", "-q", "--", path)
    if code == 0:
        out.append("journal ignored by git: %s must stay tracked, it is the truth. Remove the rule that ignores it" % path)
    elif code != 1:
        out.append("git check-ignore failed on %s" % path)
    return out


def cmd_doctor(ctx, a):
    if a.fix:
        ctx.require_writable()
        Cleaner(ctx)  # refuses before the checks, with or without something to repair
    raw = read_journal(ctx)
    parsed = parse_journal(raw)
    if parsed.errors:
        raise Refused("\n".join(["corrupt journal: %s" % e for e in parsed.errors] + ["doctor: fix those lines by hand, then rerun"]))
    replay_order(parsed.events)
    db = open_read(ctx)
    problems, _, inert = journal_problems(raw, db)
    if a.fix and problems:
        with Writer(ctx) as w:
            if parsed.torn or inert:
                w.rewrite(set())
            for line in renumber_duplicates(w):
                print(line)
        db = open_read(ctx)
        problems, _, _ = journal_problems(read_journal(ctx), db)
    problems += git_problems(ctx)
    if problems:
        raise Refused("\n".join(problems))
    print("doctor: clean")
    return 0


# ---------------------------------------------------------------- import-md

OLD_STATUS = {"Open": "Request", "Fixed": "Resolved", "Closed": "Complete", "Reopened": "Reopen",
              "Won't fix": "Won't fix", "Accepted": "Accepted", "As designed": "As designed", "Duplicate": "Duplicate"}
OLD_SEVERITY = {"Critical": "Highest", "High": "High", "Medium": "Medium", "Low": "Low"}
RX_HISTORY = re.compile(r"(?:(?<=\s)|^)(\d{4}-\d{2}-\d{2}) (Open|Fixed|Closed|Reopened|Won't fix|Accepted|As designed|Duplicate)\b(?:\s*[—–-]+\s*)?")
RX_DATED_WORD = re.compile(r"(?:^|\s)\d{4}-\d{2}-\d{2} [A-Z]")
RX_DUPLICATE_CELL = re.compile(r"Duplicate of (BUG-\d{4,})")  # the old lifecycle's own status form
RX_STOP_RULE = re.compile(r"(fix|review) root-caused (\d{4}-\d{2}-\d{2}) - extra dispatch: (unused|used)\b")
MD_LABELS = {"repro": "repro", "expected": "expected", "actual": "actual", "evidence": "evidence", "root cause": "root_cause",
             "fix rounds": "fix_rounds", "review rounds": "review_rounds", "stop rule": "stop_rule", "history": "history", "extra round": "extra_round"}
GAP_TS = "2000-01-01T00:00:00.000Z"


def md_cells(line: str) -> list:
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip()[1:-1 if line.strip().endswith("|") else None])]


def md_table(text: str, problems: list) -> dict:
    rows, header = {}, None
    for line in text.split("\n"):
        if line.startswith("## "):
            break
        if not line.startswith("|"):
            continue
        cells = md_cells(line)
        if header is None:
            header = [c.lower() for c in cells]
            missing = [c for c in ("id", "title", "severity", "status", "feature", "owner", "regression test") if c not in header]
            if missing:
                problems.append("table: missing column %s" % ", ".join(missing))  # our own names, not the file's
                return rows
            continue
        if all(re.fullmatch(r":?-+:?", c) for c in cells):
            continue
        if len(cells) != len(header):
            problems.append("table: row has %d cells, header has %d: %s" % (len(cells), len(header), shown(cells[0])))
            continue
        row = dict(zip(header, cells))
        rows[row["id"]] = row
    return rows


def md_records(text: str, problems: list) -> dict:
    records, current, bug_id, label = {}, None, None, None
    for raw in text.split("\n"):
        line = raw.rstrip()
        m = re.match(r"## (BUG-\d{4,})\b", line)
        if m:
            bug_id, label = m.group(1), None
            current = records.setdefault(bug_id, {})
            continue
        if line.startswith("## ") or line.startswith("# "):
            current = None
            continue
        if current is None or not line.strip():
            continue
        m = re.match(r"(?:- )?([A-Za-z][A-Za-z' ]*?):\s*(.*)$", line)
        known = m and m.group(1).strip().lower() in MD_LABELS
        if line.startswith("- ") and not known:
            problems.append("%s: unknown line '%s': nothing may be dropped" % (bug_id, shown(m.group(1) if m else line)))
            continue
        if known:
            label = MD_LABELS[m.group(1).strip().lower()]
            value = m.group(2).strip()
            if label == "expected" and re.search(r"\s·\s*Actual:", value):
                value, actual = re.split(r"\s·\s*Actual:\s*", value, maxsplit=1)
                current["actual"] = actual.strip()
            current[label] = value.strip()
        elif label:
            current[label] = current[label] + "\n" + line.strip()
        else:
            problems.append("%s: stray line '%s'" % (bug_id, shown(line)))
    return records


def md_history(bug_id: str, text: str, problems: list) -> list:
    marks = list(RX_HISTORY.finditer(text or ""))
    if not marks or text[:marks[0].start()].strip():
        problems.append("%s History: no parsable events" % bug_id)
        return []
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        note = text[m.end():end].strip()
        if RX_DATED_WORD.search(note):
            problems.append("%s History: unknown status in '%s'" % (bug_id, shown(note, 60)))
        out.append((m.group(1), m.group(2), note))
    return out


def stage_record(bug_id: str, row: dict, rec: dict, cleaner: Cleaner, problems: list, row_ids) -> list:
    """The journal lines of one bug, or nothing when it breaks a rule. Every break is reported, none is truncated."""
    say = lambda ex: problems.append("%s %s" % (bug_id, ex))
    fields = {}

    def take(field, value, required=True):
        try:
            if required:
                fields[field] = cleaner.required(field, value)
            elif value not in (None, ""):
                fields[field] = cleaner.clean(field, value)
        except Refused as ex:
            say(ex)

    severity = row["severity"]
    if severity in OLD_SEVERITY:
        fields["priority"] = OLD_SEVERITY[severity]
    else:
        say("severity: unknown '%s'" % shown(severity))
    take("title", row["title"])
    take("description", rec.get("actual"))
    for field in ("repro", "expected", "actual", "evidence"):
        take(field, rec.get(field))
    take("root_cause", rec.get("root_cause"), required=False)
    for field, cell in (("feature", row["feature"]), ("owner", row["owner"]), ("regression_test", row["regression test"])):
        take(field, None if cell in ("", "-", "—") else cell, required=False)

    history = md_history(bug_id, rec.get("history"), problems)
    if history and history[0][1] != "Open":
        problems.append("%s History: must start with Open" % bug_id)
    dup_cell = RX_DUPLICATE_CELL.fullmatch(row["status"])  # trailing text would be dropped: it stops as an unknown status
    status = "Duplicate" if dup_cell else row["status"]
    if status not in OLD_STATUS:
        problems.append("%s status: unknown '%s'" % (bug_id, shown(row["status"])))
    elif history and history[-1][1] != status:
        problems.append("%s History: ends at %s, the table says %s" % (bug_id, history[-1][1], shown(row["status"])))

    notes = []
    for date, word, note in history:
        try:
            notes.append(cleaner.clean("note", note) or None)
            parse_ts(date + "T00:00:00.000Z")
        except Refused as ex:
            say(ex)
        except ValueError:
            problems.append("%s History: bad date %s" % (bug_id, date))

    extras = []
    has_extra = "extra_round" in rec or any("extra round" in str(v).lower() for v in rec.values())
    for counter, key in (("fix", "fix_rounds"), ("review", "review_rounds")):
        if key not in rec:
            continue
        m = re.match(r"(\d+)\s*/\s*(\d+)", rec[key])
        if not m:
            problems.append("%s %s: expected n/cap" % (bug_id, key))
            continue
        used, cap = int(m.group(1)), int(m.group(2))
        if used > MAX_COUNT or cap - DEFAULT_CAPS[counter] > MAX_COUNT:  # one journal event each: replay would refuse it
            problems.append("%s %s: more than %d in one event" % (bug_id, key, MAX_COUNT))
            continue
        if used:
            extras.append(("round", {"counter": counter, "n": used}))
        if cap > DEFAULT_CAPS[counter]:
            if has_extra:
                extras.append(("extra_round", {"counter": counter, "n": cap - DEFAULT_CAPS[counter]}))
            else:
                print("%s: %s cap %d has no recorded extra round: the default applies, as in round-cap.ps1" % (bug_id, counter, cap), file=sys.stderr)
    stop = None
    if "stop_rule" in rec:
        stop = RX_STOP_RULE.search(rec["stop_rule"])
        if not stop:
            problems.append("%s stop_rule: expected '<counter> root-caused <date> - extra dispatch: unused|used'" % bug_id)

    dup_of = dup_cell.group(1) if dup_cell else None
    if status == "Duplicate" and not dup_of:
        for (_, word, _), note in zip(history, notes):  # only the Duplicate event: an earlier note may name another bug
            m = re.search(r"BUG-\d{4,}", note or "") if word == "Duplicate" else None
            dup_of = m.group(0) if m else dup_of
        if not dup_of:
            problems.append("%s History: Duplicate names no BUG-#### target" % bug_id)
    if dup_of == bug_id:  # what set-status refuses
        say("duplicate_of: a bug cannot duplicate itself")
    elif dup_of and dup_of not in row_ids:
        say("duplicate_of: %s is not in the table" % dup_of)

    if problems and any(p.startswith(bug_id) for p in problems):
        return []
    uid = stable_uid("import/%s" % bug_id)
    num = parse_id(bug_id)
    events, seq, prev, last_date = [], 0, "Request", history[0][0]

    def line(etype, data, date, note=None):
        nonlocal seq
        ts = fmt_ts(parse_ts(date + "T00:00:00.000Z") + dt.timedelta(milliseconds=seq))
        ev = {"event_uid": stable_uid("import/%s/%d" % (bug_id, seq)), "bug_uid": uid, "ts": ts, "type": etype, "data": data, "by": "import-md"}
        if note:
            ev["note"] = note
        seq += 1
        events.append(ev)

    line("create", dict(fields, id=num, status="Request"), history[0][0], notes[0])
    for (date, word, _), note in list(zip(history, notes))[1:]:
        to = OLD_STATUS[word]
        data = {"from": prev, "to": to}
        if to == "Duplicate":
            data["duplicate_of"] = dup_of
        line("status", data, date, note)
        prev, last_date = to, date
    for etype, data in extras:
        line(etype, data, last_date)
    if stop:
        line("stop_rule", {"counter": stop.group(1), "extra_dispatch": stop.group(3)}, stop.group(2))
    return events


def cmd_import_md(ctx, a):
    ctx.require_writable()
    if not ctx.md.exists():
        raise Refused(".workflow/bugs.md not found: nothing to import")
    cleaner = Cleaner(ctx)
    text = ctx.md.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    problems = []
    rows = md_table(text, problems)
    records = md_records(text, problems)
    for bug_id in sorted(set(rows) | set(records)):
        if bug_id not in rows:
            problems.append("%s: a record with no table row" % shown(bug_id))
        elif bug_id not in records:
            problems.append("%s: a table row with no record" % shown(bug_id))
    staged = []
    for bug_id in sorted(set(rows) & set(records), key=parse_id):
        staged += stage_record(bug_id, rows[bug_id], records[bug_id], cleaner, problems, rows)
    m = re.search(r"(?m)^Next ID:\s*BUG-(\d+)", text)
    next_id = int(m.group(1)) if m else 1
    if problems:
        raise Refused("import stopped, nothing written:\n" + "\n".join(problems))
    with Writer(ctx, create=True) as w:
        for bug_id in sorted(set(rows) & set(records)):
            held = w.db.execute("SELECT uid FROM bug WHERE id=?", (bug_id,)).fetchall()
            if any(r["uid"] != stable_uid("import/%s" % bug_id) for r in held):
                raise Refused("import stopped, nothing written:\n%s: already held by another bug_uid" % bug_id)
        seen = {r[0] for r in w.db.execute("SELECT event_uid FROM bug_event")}
        dead = parse_journal(read_journal(ctx))
        dead_uids = {ev["bug_uid"] for ev in dead.events if ev["type"] == "tombstone"}
        new_bugs = new_events = 0
        for ev in staged:
            if ev["event_uid"] in seen or ev["bug_uid"] in dead_uids:
                continue
            w.emit(ev["type"], ev["bug_uid"], ev["data"], by=ev["by"], note=ev.get("note"), ts=ev["ts"], event_uid=ev["event_uid"])
            new_events += 1
            new_bugs += ev["type"] == "create"
        top = max(w.top, high_water_of(staged))
        if next_id - 1 > top:  # Next ID above every record: IDs were spent, keep them spent.
            uid = stable_uid("import/gap/%d" % (next_id - 1))
            w.lines.append(encode_line({"event_uid": stable_uid("import/gap-event/%d" % (next_id - 1)), "bug_uid": uid, "ts": GAP_TS,
                                        "type": "tombstone", "data": {"id": next_id - 1}}))
            w.top = next_id - 1
            w.last_ts = max(w.last_ts or "", GAP_TS)
        if not w.lines and not ctx.journal.exists():  # zero rows: the file /release asks for must outlive the ordered delete
            ctx.journal.write_bytes(b"")
    cleaner.report()
    print("imported %d bugs, %d events; delete .workflow/bugs.md next" % (new_bugs, new_events))
    return 0


# ---------------------------------------------------------------- main

def build_parser() -> argparse.ArgumentParser:
    p = Parser(prog="bugs", description="Bug tracker: SQLite cache over the tracked journal .workflow/bugs.jsonl.")
    p.add_argument("--root", help="project root (default: derived from this script's location)")
    sub = p.add_subparsers(dest="cmd", required=True)
    counter_choices = sorted(DEFAULT_CAPS)

    def write_cmd(name, help_text):
        sp = sub.add_parser(name, help=help_text)
        sp.add_argument("--by", help="who writes; GD-only moves need exactly GD (default: %s)" % DEFAULT_BY)
        return sp

    write_cmd("add", "file a bug: JSON fields on stdin; prints its id")
    write_cmd("update", "change fields: JSON on stdin").add_argument("id")
    s = write_cmd("set-status", "move a bug through the state machine; note on stdin as JSON or --note")
    s.add_argument("id")
    s.add_argument("status")
    s.add_argument("--note")
    s.add_argument("--duplicate-of", dest="duplicate_of")
    for name, text in (("round", "add used rounds to a counter"), ("extra-round", "raise a counter's cap on the GD's order")):
        s = write_cmd(name, text)
        s.add_argument("id")
        s.add_argument("counter", choices=counter_choices)
        s.add_argument("n", help="+n, with n from 1 to %d" % MAX_COUNT)
        s.add_argument("--note")
    s = write_cmd("stop-rule", "record the stop rule for a counter")
    s.add_argument("id")
    s.add_argument("counter", choices=counter_choices)
    s.add_argument("--extra-dispatch", dest="extra_dispatch", required=True, choices=("unused", "used"))
    s.add_argument("--note")
    write_cmd("delete", "GD order only: drop a bug, keep a tombstone").add_argument("id")
    s = sub.add_parser("show", help="one record with its events")
    s.add_argument("id")
    s.add_argument("--json", action="store_true")
    s = sub.add_parser("list", help="records, filtered")
    s.add_argument("--status", action="append", choices=STATUSES)
    s.add_argument("--priority", action="append", choices=PRIORITIES)
    s.add_argument("--feature")
    s.add_argument("--open", action="store_true", help="every status but the five terminal ones")
    s.add_argument("--json", action="store_true")
    s = sub.add_parser("search", help="FTS5 search over text and notes, settled bugs included")
    s.add_argument("text")
    s.add_argument("-n", type=int, default=10)
    s = sub.add_parser("sql", help="one read-only SELECT")
    s.add_argument("query")
    s.add_argument("--json", action="store_true")
    s = sub.add_parser("counters", help="what round-cap.ps1 reads; always JSON")
    s.add_argument("id")
    s.add_argument("--json", action="store_true", help="accepted for clarity; the output is always JSON")
    sub.add_parser("stats", help="one line: Bugs: N open (H High+)")
    s = sub.add_parser("purge", help="drop terminal bugs more than 90 days past terminal")
    s.add_argument("--auto", action="store_true", help="session start: apply the trigger conditions; one line of output")
    s.add_argument("--dry-run", dest="dry_run", action="store_true", help="list, write nothing")
    sub.add_parser("rebuild", help="rebuild the DB from the journal")
    sub.add_parser("doctor", help="report journal problems").add_argument("--fix", action="store_true", help="renumber duplicates, repair the tail, sweep inert lines")
    sub.add_parser("import-md", help="one-way migration from .workflow/bugs.md; the caller deletes the file")
    return p


HANDLERS = {"add": cmd_add, "update": cmd_update, "set-status": cmd_set_status, "round": cmd_round, "extra-round": cmd_extra_round,
            "stop-rule": cmd_stop_rule, "delete": cmd_delete, "show": cmd_show, "list": cmd_list, "search": cmd_search, "sql": cmd_sql,
            "counters": cmd_counters, "stats": cmd_stats, "purge": cmd_purge, "rebuild": cmd_rebuild, "doctor": cmd_doctor, "import-md": cmd_import_md}


def given_root(argv) -> Path:
    """--root as typed, for the pattern lookup when the arguments themselves did not parse."""
    words = sys.argv[1:] if argv is None else list(argv)
    for i, word in enumerate(words):
        if word == "--root" and i + 1 < len(words):
            return Path(words[i + 1])
        if word.startswith("--root="):
            return Path(word[len("--root="):])
    return Path(__file__).resolve().parents[4]


def refusal_text(text: str, argv) -> str:
    """The only way refusal text reaches stderr. Everything passes the same secret and PII redaction as a write, because
    an ID, a status or a JSON key can be a pasted secret. Nothing to scan with: the values stay out."""
    try:
        mem = mem_module()
        patterns = loaded_patterns(mem, given_root(argv))
        lines = mem.redact_pii(mem.redact(text.replace(VALUE_MARK, ""), patterns)).split("\n")
    except KeyboardInterrupt:
        raise
    except BaseException:  # it is already reporting an error, whatever broke the module, the file or a redaction: it must not raise
        lines = RX_SHOWN.sub("<hidden: secret patterns unavailable>", text).split("\n")
    return "\n".join(line[:REFUSAL_LINE] for line in lines)


def main(argv=None) -> int:
    """An interrupt leaves here: raised inside a handler below, its traceback would chain the refusal holding the raw value."""
    try:
        return run(argv)
    except KeyboardInterrupt:
        print("bugs: interrupted", file=sys.stderr)
        return 130


def run(argv) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    try:
        a = build_parser().parse_args(argv)
        ctx = Ctx(a.root)
        if a.cmd != "import-md" and ctx.md.exists():
            raise Refused(".workflow/bugs.md exists: run import-md, delete the file, then retry")
        return HANDLERS[a.cmd](ctx, a)
    except UsageError as ex:
        print("bugs: %s" % refusal_text(str(ex), argv), file=sys.stderr)
        return 2
    except (Refused, Corrupt) as ex:
        print("bugs: %s" % refusal_text(str(ex), argv), file=sys.stderr)
        return 1
    except (RuntimeError, re.error, ValueError, OSError, sqlite3.Error, subprocess.SubprocessError) as ex:
        print("bugs: %s" % refusal_text(str(ex), argv), file=sys.stderr)  # e.g. a broken or missing secret-patterns.txt
        return 1
    finally:
        while _connections:
            _connections.pop().close()


if __name__ == "__main__":
    sys.exit(main())
