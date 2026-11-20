"""Bug tracker: one record per bug in SQLite, with the tracked journal as the truth. No LLM, stdlib only.

Run with `python -I bugs.py --root <project root> <command>`. .workflow/bugs.jsonl is append-mostly and tracked;
.workflow/bugs.db is a gitignored cache rebuilt from it whenever the journal's hash changes. Format and state machine:
../references/schema.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import re
import sqlite3
import subprocess
import sys
import uuid
from pathlib import Path


def _load_journal():
    """The shared engine, records/scripts/journal.py, by path: -I removes the script dir from sys.path, hence importlib."""
    path = Path(__file__).resolve().parents[2] / "records" / "scripts" / "journal.py"
    name = "records_journal"
    module = sys.modules.get(name)
    if module is not None and Path(getattr(module, "__file__", "")).resolve() == path:
        return module
    if not path.exists():
        sys.stderr.write("bugs: %s is missing: the shared journal engine (skill records)\n" % path)
        raise SystemExit(1)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    keep, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = keep
    sys.modules[name] = module
    return module


journal = _load_journal()

SCHEMA_VERSION = 2
STATUSES = ("Request", "Processing", "Resolved", "Review", "Complete", "Reopen", "Backlog", "Won't fix", "Accepted", "As designed", "Duplicate")
TERMINAL = ("Complete", "Won't fix", "Accepted", "As designed", "Duplicate")
OPEN = tuple(s for s in STATUSES if s not in TERMINAL)
PRIORITIES = ("Low", "Medium", "High", "Highest")
DEFAULT_CAPS = {"fix": 2, "review": 3}
WINDOW = dt.timedelta(days=90)
SQL_SECONDS = 10
MAX_COUNT = journal.MAX_COUNT  # one round or extra-round call; replay refuses more, so a counter's total stays a small integer
REFUSAL_LINE = journal.REFUSAL_LINE
VALUE_MARK = journal.VALUE_MARK  # brackets a caller's value inside refusal text; refusal_text() is the only reader
RX_SHOWN = journal.RX_SHOWN

# Moves anyone with the writer's role may make; main-GD-only moves and "any open" moves are in move_rule().
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
RX_TS, RX_BREAK, RX_CONTROL = journal.RX_TS, journal.RX_BREAK, journal.RX_CONTROL
VI_LETTERS, RX_VIETNAMESE = journal.VI_LETTERS, journal.RX_VIETNAMESE
UID_NAMESPACE, GIT_ENV = journal.UID_NAMESPACE, journal.GIT_ENV

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


# The engine's names, re-exported: callers and tests reach them through this module.
Refused, Corrupt, UsageError, Parser = journal.Refused, journal.Corrupt, journal.UsageError, journal.Parser


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

fmt_ts, parse_ts, now_utc, next_ts = journal.fmt_ts, journal.parse_ts, journal.now_utc, journal.next_ts


def fmt_id(num: int) -> str:
    return "BUG-%04d" % num


shown, shown_all = journal.shown, journal.shown_all


def parse_id(text: str) -> int:
    m = RX_ID.fullmatch(text) if isinstance(text, str) else None
    if not m:
        raise Refused("bad id '%s': expected BUG-####" % shown(text))
    return int(m.group(1))


stable_uid = journal.stable_uid


# ---------------------------------------------------------------- content rules

check_english = journal.check_english
MEM_API = journal.MEM_API
mem_module, loaded_patterns = journal.mem_module, journal.loaded_patterns


class Cleaner(journal.Cleaner):
    """Applies every content rule to text about to be written. A missing pattern file refuses here, before any write."""

    def __init__(self, ctx):
        super().__init__(ctx, LIMITS, ONE_LINE)

    def priority(self, value) -> str:
        if value is None or value == "":
            raise Refused("priority: required, one of %s" % ", ".join(PRIORITIES))
        if value not in PRIORITIES:
            raise Refused("priority: must be one of %s (Critical maps to Highest)" % ", ".join(PRIORITIES))
        return value


read_stdin_json, by_of, note_of, parse_count = journal.read_stdin_json, journal.by_of, journal.note_of, journal.parse_count


# ---------------------------------------------------------------- paths and git

git_exe, run_git = journal.git_exe, journal.run_git


def main_checkout(root: Path) -> tuple[Path, Path | None, bool]:
    return journal.main_checkout(root, "bug journal")


class Ctx(journal.Ctx):
    """The root per main_checkout: a linked worktree reads the main checkout's data, a root with no .git has no git context."""

    def __init__(self, arg: str | None):
        super().__init__(arg, "bugs.jsonl", "bugs.db", Path(__file__).resolve().parents[4], label="bug journal")

    def run_git(self, cwd: Path, *args) -> tuple[int, str]:
        return run_git(cwd, *args)  # this module's name, so a patch of bugs.run_git reaches the check


def read_journal(ctx: Ctx) -> bytes:
    return journal.read_journal(ctx.journal)


sha = journal.sha


# ---------------------------------------------------------------- journal parsing and replay

need, is_count = journal.need, journal.is_count


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


Parsed = journal.Parsed


def parse_journal(raw: bytes) -> Parsed:
    """A final line with no newline that is not JSON is a torn write: skipped here, removed by the next write."""
    return journal.parse_journal(raw, check_event)


canon = journal.canon


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
    return journal.replay_order(events, "bug_uid")


# ---------------------------------------------------------------- database

_connections = journal._connections  # one list with the engine's: closed by main()
connect = journal.connect


def create_schema(db):
    journal.create_schema(db, SCHEMA, SCHEMA_VERSION)


def remove_db(ctx: Ctx):
    journal.remove_db(ctx)


def open_db(ctx: Ctx, create=False) -> sqlite3.Connection:
    """No journal, no DB, not a create: an empty in-memory store, so reads return nothing and create nothing."""
    return journal.open_db(ctx, SCHEMA, SCHEMA_VERSION, create=create)


get_meta, set_meta = journal.get_meta, journal.set_meta


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

encode_line, split_tail, repaired = journal.encode_line, journal.split_tail, journal.repaired


def append_lines(ctx: Ctx, lines: list) -> bytes:
    """LF only, UTF-8, no BOM, whatever the platform. Returns the journal's new bytes."""
    return journal.append_lines(ctx.journal, lines)


def replace_journal(ctx: Ctx, raw: bytes):
    journal.replace_journal(ctx.journal, ctx.workflow / "bugs.db.jsonl.tmp", raw)  # the bugs.db* ignore rule covers a leftover


class Writer(journal.Writer):
    """BEGIN IMMEDIATE, hash check, rebuild if different, the command validates, apply, append, commit.
    A crash after the append is healed by the next command's hash mismatch. Each hook goes through this module's names,
    so a test patch of bugs.append_lines or bugs._after_append reaches the write path."""

    uid_key = "bug_uid"

    def check_writable(self):
        self.ctx.require_writable()
        Cleaner(self.ctx)  # every write, text-free ones too: a missing pattern file refuses here (schema.md, Fail closed)

    def open_db(self):
        return open_db(self.ctx, create=self.create)

    def read(self) -> bytes:
        return read_journal(self.ctx)

    def append(self, lines) -> bytes:
        return append_lines(self.ctx, lines)

    def after_append(self):
        _after_append()

    def stored_hash(self):
        return get_meta(self.db, "journal_hash")

    def rebuild(self, raw: bytes):
        rebuild_tables(self.db, raw)

    def load_state(self):
        self.last_ts = get_meta(self.db, "last_ts") or None
        self.top = high_water(self.db)

    def save_state(self, new: bytes):
        set_meta(self.db, "journal_hash", sha(new))
        set_meta(self.db, "high_water", self.top)
        set_meta(self.db, "last_ts", self.last_ts or "")

    def apply(self, ev: dict):
        apply_event(self.db, ev)
        sync_fts(self.db, ev["bug_uid"])

    def high_water_of(self, events) -> int:
        return high_water_of(events)

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
        if rule == "gd" and by != "main GD":
            raise Refused("%s: %s -> %s is main GD only (state machine in references/schema.md): pass --by 'main GD' on the main GD's order" % (a.id, row["status"], a.status))
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
        ev = w.emit("status", row["uid"], payload, by=by, note=note)
    cleaner.report()
    print("%s %s -> %s" % (a.id, row["status"], a.status))
    if a.status in MIRRORED:
        mirror_debt(ctx, row, by, note, ev["ts"])
    return 0


MIRRORED = ("Won't fix", "Accepted")  # a bug the main GD leaves unfixed is debt: records.py mirrors it, no hand step
RECORDS_PATH = Path(__file__).resolve().parents[2] / "records" / "scripts" / "records.py"


def _load_records():
    """records.py, by path like the engine: its mirror_bug writes the feature root's DEBT.csv or a debt record."""
    return journal.load_by_path("bugs_records", RECORDS_PATH, " (skill records)")


def mirror_debt(ctx: Ctx, row, by: str, note, ts: str):
    """After the move committed. A failure here cannot undo the move, so it names the one command that finishes the job."""
    command = '"%s" -I "%s" --root "%s" bug-mirror %s' % (sys.executable, RECORDS_PATH, ctx.root, row["id"])
    try:
        records = _load_records()
        print(records.mirror_bug(records.Ctx(str(ctx.root)), row["id"], row["title"], row["feature"], by, note, ts[:10]))
    except KeyboardInterrupt:
        raise
    except (Refused, Corrupt) as ex:
        raise Refused("moved, but the debt mirror failed: %s; run %s" % (ex, command)) from None
    except (Exception, SystemExit) as ex:  # whatever broke in the other CLI, the move stands and the repair is named
        raise Refused("moved, but the debt mirror failed: %s: %s; run %s" % (type(ex).__name__, shown(ex, 200), command)) from None


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
    if a.by != "main GD":
        raise Refused("delete is main GD only: pass --by 'main GD' on the main GD's order")
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


sql_authorizer, strip_sql_comments, sql_cell = journal.sql_authorizer, journal.strip_sql_comments, journal.sql_cell


def cmd_sql(ctx, a):
    return journal.run_sql(a.query, a.json, lambda: open_read(ctx), ctx.db_path, SQL_SECONDS)


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


# ---------------------------------------------------------------- main

def build_parser() -> argparse.ArgumentParser:
    p = Parser(prog="bugs", description="Bug tracker: SQLite cache over the tracked journal .workflow/bugs.jsonl.")
    p.add_argument("--root", help="project root (default: derived from this script's location)")
    sub = p.add_subparsers(dest="cmd", required=True)
    counter_choices = sorted(DEFAULT_CAPS)

    def write_cmd(name, help_text):
        sp = sub.add_parser(name, help=help_text)
        sp.add_argument("--by", help="who writes; main-GD-only moves need exactly main GD (default: %s)" % DEFAULT_BY)
        return sp

    write_cmd("add", "file a bug: JSON fields on stdin; prints its id")
    write_cmd("update", "change fields: JSON on stdin").add_argument("id")
    s = write_cmd("set-status", "move a bug through the state machine; note on stdin as JSON or --note")
    s.add_argument("id")
    s.add_argument("status")
    s.add_argument("--note")
    s.add_argument("--duplicate-of", dest="duplicate_of")
    for name, text in (("round", "add used rounds to a counter"), ("extra-round", "raise a counter's cap on the main GD's order")):
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
    write_cmd("delete", "main GD order only: drop a bug, keep a tombstone").add_argument("id")
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
    return p


HANDLERS = {"add": cmd_add, "update": cmd_update, "set-status": cmd_set_status, "round": cmd_round, "extra-round": cmd_extra_round,
            "stop-rule": cmd_stop_rule, "delete": cmd_delete, "show": cmd_show, "list": cmd_list, "search": cmd_search, "sql": cmd_sql,
            "counters": cmd_counters, "stats": cmd_stats, "purge": cmd_purge, "rebuild": cmd_rebuild, "doctor": cmd_doctor}


def given_root(argv) -> Path:
    """--root as typed, for the pattern lookup when the arguments themselves did not parse."""
    return journal.given_root(argv, Path(__file__).resolve().parents[4])


def refusal_text(text: str, argv) -> str:
    """The only way refusal text reaches stderr. Everything passes the same secret and PII redaction as a write, because
    an ID, a status or a JSON key can be a pasted secret. Nothing to scan with: the values stay out."""
    return journal.refusal_text(text, given_root(argv))


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
