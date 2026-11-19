"""Workflow records: game backlog, framework backlog, project debt and the feature registry, each over its own tracked
journal, with one gitignored SQLite cache; plus the local round ledger. No LLM, stdlib only.

Run with `python -I records.py --root <project root> <store> <command>` (stores: backlog, fwbacklog, debt, feature) or
`... <rebuild|doctor|sql|stats|ledger>`. Each journal .workflow/<name>.jsonl is the truth; .workflow/records.db is a cache
whose meta holds one hash per journal, so a change in one journal rebuilds only that store's tables. The round ledger
.workflow/ledger.db is a local record, never journaled. Contract: ../references/schema.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import re
import sqlite3
import subprocess
import sys
import uuid
from pathlib import Path


def _load_journal():
    """The shared engine beside this file, by path: -I removes the script dir from sys.path, hence importlib."""
    path = Path(__file__).resolve().parent / "journal.py"
    name = "records_journal"
    module = sys.modules.get(name)
    if module is not None and Path(getattr(module, "__file__", "")).resolve() == path:
        return module
    if not path.exists():
        sys.stderr.write("records: %s is missing: the shared journal engine\n" % path)
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
Refused, Corrupt, UsageError = journal.Refused, journal.Corrupt, journal.UsageError
shown, shown_all, get_meta, set_meta, sha = journal.shown, journal.shown_all, journal.get_meta, journal.set_meta, journal.sha

SCHEMA_VERSION = 1
CLOCK_ENV = "RECORDS_NOW"  # test-only clock, like BUGS_NOW
DB_NAME = "records.db"
LEDGER_NAME = "ledger.db"
SQL_SECONDS = 10
DEFAULT_BY = journal.DEFAULT_BY
DEFAULT_ROOT = Path(__file__).resolve().parents[4]
EXIT_LEDGER_CORRUPT = 3
EXIT_BUSY = 75
LEDGER_BUSY_MS = 5000

RX_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
RX_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
RX_NUMS = re.compile(r"\d{1,6}(?:\s*,\s*\d{1,6})*")
RX_SOURCE = re.compile(r"BUG-\d{4,}|framework|[a-z0-9]+(?:-[a-z0-9]+)*")
COUNTERS = ("review", "qa", "rework")
BASE_CAPS = {"review": 3, "qa": 2}
REWORK_CAPS = {"S": 6, "M": 6, "L": 8}
COMMON_LIMITS = {"note": 200, "by": 100}


def _after_append():
    """Between a journal append and the DB commit. Tests replace this to crash exactly there."""


# ---------------------------------------------------------------- stores

class Field:
    def __init__(self, name, kind="text", limit=None, choices=(), required=False, label=None):
        self.name, self.kind, self.limit, self.choices, self.required = name, kind, limit, tuple(choices), required
        self.label = label or name.replace("_", " ").capitalize()


class Store:
    """One project-scope store: its journal, id shape, fields and state set."""

    def __init__(self, name, title, journal_name, prefix, fields, state_field, states, default_state, open_states,
                 gd_states=(), fts=(), render=(), list_cols=()):
        self.name, self.title, self.journal_name, self.prefix = name, title, journal_name, prefix
        self.fields = {f.name: f for f in fields}
        self.state_field, self.states, self.default_state = state_field, tuple(states), default_state
        self.open_states, self.gd_states = tuple(open_states), tuple(gd_states)
        self.fts, self.render_cols, self.list_cols = tuple(fts), tuple(render), tuple(list_cols)
        self.rx_id = re.compile(r"%s-(\d{4,})" % prefix) if prefix else None
        self.types = ("create", "update", "state", "renumber") if prefix else ("create", "update", "state", "round", "extra_round", "stop_rule")

    @property
    def numbered(self) -> bool:
        return self.prefix is not None

    @property
    def updatable(self) -> tuple:
        return tuple(f for f in self.fields if f != "slug")

    def limits(self) -> dict:
        out = dict(COMMON_LIMITS)
        out.update({f.name: f.limit for f in self.fields.values() if f.limit})
        return out

    def fmt_id(self, num: int) -> str:
        return "%s-%04d" % (self.prefix, num)

    def parse_id(self, text):
        """BL-#### and the like to a number; a feature's slug as it is."""
        if not isinstance(text, str):
            raise Refused("bad id")
        if not self.numbered:
            if not RX_SLUG.fullmatch(text) or len(text) > 100:
                raise Refused("bad slug '%s': expected kebab-case, a-z 0-9 and -" % shown(text))
            return text
        m = self.rx_id.fullmatch(text)
        if not m:
            raise Refused("bad id '%s': expected %s-####" % (shown(text), self.prefix))
        return int(m.group(1))


T = Field
STORES = {
    "backlog": Store(
        "backlog", "Backlog", "backlog.jsonl", "BL",
        [T("feature", limit=100, required=True), T("milestone", limit=60, required=True),
         T("size", "enum", choices=("S", "M", "L"), required=True), T("risk", limit=200),
         T("depends_on", "nums", limit=100, label="Depends on")],
        "status", ("todo", "in progress", "done", "dropped"), "todo", ("todo", "in progress"),
        fts=("feature", "milestone", "risk"),
        render=(("#", "num"), ("Feature", "feature"), ("Milestone", "milestone"), ("Size", "size"), ("Risk", "risk"),
                ("Depends on", "depends_on"), ("Status", "status")),
        list_cols=("id", "status", "milestone", "size", "feature")),
    "fwbacklog": Store(
        "fwbacklog", "Framework backlog", "framework-backlog.jsonl", "FW",
        [T("item", limit=1000, required=True), T("ref", limit=300, label="Ref")],
        "state", ("Open", "Done", "Recorded", "Recorded (main GD decision)", "Deferred"), "Open", ("Open", "Deferred"),
        gd_states=("Recorded (main GD decision)",), fts=("item", "ref"),
        render=(("ID", "id"), ("Item", "item"), ("State", "state"), ("Ref", "ref")),
        list_cols=("id", "state", "item")),
    "debt": Store(
        "debt", "Debt", "debt.jsonl", "DEBT",
        [T("text", limit=300, required=True), T("source", "source", limit=100, required=True),
         T("next_step", limit=300, label="Next step"), T("accepted_by", limit=100, required=True, label="Accepted by"),
         T("date", "date", limit=10, required=True)],
        "state", ("Open", "Paid"), "Open", ("Open",), fts=("text", "source", "next_step"),
        render=(("ID", "id"), ("Date", "date"), ("Source", "source"), ("Text", "text"), ("Next step", "next_step"),
                ("Accepted by", "accepted_by"), ("State", "state")),
        list_cols=("id", "state", "date", "source", "text")),
    "feature": Store(
        "feature", "Features", "features.jsonl", None,
        [T("slug", "slug", limit=100, required=True), T("cp", "enum", choices=("none", "CP1", "CP2", "build", "review", "CP3", "QA", "CP4"), label="CP"),
         T("next_step", limit=300, label="Next step"), T("session", limit=200), T("size", "enum", choices=("S", "M", "L")),
         T("risk", limit=200), T("profile", limit=100), T("feature_root", limit=200, label="Feature root"),
         T("branch", limit=200), T("base", limit=200), T("assemblies", limit=300),
         T("build_mode", "enum", choices=("serial", "lanes"), label="Build mode"), T("worktrees", limit=300)],
        "status", ("Open", "Closed", "Abandoned"), "Open", ("Open",), fts=("slug", "next_step", "risk", "branch"),
        render=(("Slug", "slug"), ("Status", "status"), ("CP", "cp"), ("Size", "size"), ("Risk", "risk"), ("Branch", "branch"),
                ("Next step", "next_step"), ("Review", "review"), ("QA", "qa"), ("Rework", "rework")),
        list_cols=("slug", "status", "cp", "size", "next_step")),
}


def store_ddl(s: Store) -> list:
    cols = ["id TEXT NOT NULL", "uid TEXT PRIMARY KEY"]
    if s.name == "backlog":
        cols.append("num INTEGER NOT NULL")
    for f in s.fields.values():
        if f.name == "slug":
            cols.append("slug TEXT NOT NULL UNIQUE")
        elif f.kind == "enum":
            cols.append("%s TEXT CHECK(%s IS NULL OR %s IN (%s))" % (f.name, f.name, f.name, ",".join("'%s'" % c for c in f.choices)))
        else:
            cols.append("%s TEXT%s" % (f.name, " NOT NULL" if f.required else ""))
    cols.append("%s TEXT NOT NULL CHECK(%s IN (%s))" % (s.state_field, s.state_field, ",".join("'%s'" % c for c in s.states)))
    if not s.numbered:
        for c in COUNTERS:
            cols += ["%s_used INTEGER NOT NULL DEFAULT 0" % c, "%s_extra INTEGER NOT NULL DEFAULT 0" % c, "%s_cap INTEGER NOT NULL DEFAULT 0" % c]
    cols += ["created_at TEXT NOT NULL", "updated_at TEXT NOT NULL"]
    return [
        "CREATE TABLE %s(%s)" % (s.name, ", ".join(cols)),
        "CREATE INDEX %s_id ON %s(id)" % (s.name, s.name),
        "CREATE INDEX %s_state ON %s(%s)" % (s.name, s.name, s.state_field),
        """CREATE TABLE %s_event(event_uid TEXT PRIMARY KEY, uid TEXT NOT NULL, ts TEXT NOT NULL, type TEXT NOT NULL,
            by_who TEXT, note TEXT, data TEXT NOT NULL)""" % s.name,
        "CREATE INDEX %s_event_uid ON %s_event(uid, ts)" % (s.name, s.name),
        'CREATE VIRTUAL TABLE %s_fts USING fts5(%s, notes, tokenize="porter unicode61 remove_diacritics 2")' % (s.name, ", ".join(s.fts)),
    ]


SCHEMA = ["CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL)"] + [stmt for s in STORES.values() for stmt in store_ddl(s)]


# ---------------------------------------------------------------- context

class Ctx(journal.Ctx):
    def __init__(self, arg, use_git=True):
        super().__init__(arg, "", DB_NAME, DEFAULT_ROOT, label="records journal", clock_env=CLOCK_ENV, use_git=use_git)

    @property
    def journal(self):
        raise AttributeError("records keeps one journal per store: use journal_of(store)")

    def run_git(self, cwd, *args):
        return run_git(cwd, *args)  # this module's name, so a patch of records.run_git reaches the check

    def journal_of(self, store: Store) -> Path:
        return self.workflow / store.journal_name

    def journals(self) -> list:
        return [self.journal_of(s) for s in STORES.values()]


run_git = journal.run_git


def now_utc() -> dt.datetime:
    return journal.now_utc(CLOCK_ENV)


def today() -> str:
    return now_utc().strftime("%Y-%m-%d")


# ---------------------------------------------------------------- journal shape

def check_value(store: Store, key: str, value):
    journal.need(key in store.fields, "unknown field '%s'" % shown(key))
    journal.need(value is None or isinstance(value, str), "field '%s' is not text" % key)
    f = store.fields[key]
    if value is not None and f.kind == "enum":
        journal.need(value in f.choices, "bad %s" % key)


def check_event(store: Store, ev):
    """Shape only: replay never enforces transitions, the history already happened."""
    need = journal.need
    need(isinstance(ev, dict), "not an object")
    for key in ("event_uid", "uid", "ts", "type"):
        need(isinstance(ev.get(key), str) and ev[key], "missing %s" % key)
    need(ev["type"] in store.types, "unknown type")
    journal.check_ts(ev)
    for key in ("by", "note"):
        need(ev.get(key) is None or isinstance(ev[key], str), "%s is not text" % key)
    data = ev.get("data")
    need(isinstance(data, dict), "missing data")
    t = ev["type"]
    if t == "create":
        if store.numbered:
            need(journal.is_count(data.get("id")), "bad id")
        else:
            need(isinstance(data.get("slug"), str) and RX_SLUG.fullmatch(data["slug"]) is not None, "bad slug")
        need(data.get(store.state_field, store.default_state) in store.states, "bad state")
        for key, value in data.items():
            if key not in ("id", store.state_field):
                check_value(store, key, value)
        for f in store.fields.values():
            if f.required:
                need(isinstance(data.get(f.name), str), "missing %s" % f.name)
    elif t == "update":
        for key, value in data.items():
            need(key != "slug", "slug is not updatable")
            check_value(store, key, value)
    elif t == "state":
        need(data.get("to") in store.states, "bad state")
        need(data.get("from") is None or data["from"] in store.states, "bad state")
        need(data.get("ref") is None or isinstance(data["ref"], str), "bad ref")
    elif t == "renumber":
        need(journal.is_count(data.get("from")) and journal.is_count(data.get("to")), "bad renumber")
    elif t in ("round", "extra_round"):
        need(data.get("counter") in COUNTERS, "bad counter")
        need(journal.is_count(data.get("n")) and data["n"] <= journal.MAX_COUNT, "bad n")
    elif t == "stop_rule":
        need(data.get("counter") in COUNTERS, "bad counter")
        need(data.get("extra_dispatch") in ("unused", "used"), "bad extra_dispatch")


def parse_store(store: Store, raw: bytes) -> journal.Parsed:
    return journal.parse_journal(raw, lambda ev: check_event(store, ev))


def high_water_of(events) -> int:
    top = 0
    for ev in events:
        d = ev["data"]
        if ev["type"] == "create" and isinstance(d.get("id"), int):
            top = max(top, d["id"])
        elif ev["type"] == "renumber":
            top = max(top, d["from"], d["to"])
    return top


def feature_uid(slug: str) -> str:
    """One uid per slug on every branch: two branches registering one feature meet on one record."""
    return journal.stable_uid("feature/" + slug)


# ---------------------------------------------------------------- database

def open_db(ctx: Ctx, create=False) -> sqlite3.Connection:
    return journal.open_db(ctx, SCHEMA, SCHEMA_VERSION, create=create, journals=ctx.journals())


def recompute_caps(db, uid: str):
    db.execute("""UPDATE feature SET review_cap=?+review_extra, qa_cap=?+qa_extra,
                  rework_cap=(CASE size WHEN 'L' THEN ? ELSE ? END)+rework_extra WHERE uid=?""",
               (BASE_CAPS["review"], BASE_CAPS["qa"], REWORK_CAPS["L"], REWORK_CAPS["M"], uid))


def apply_event(db, store: Store, ev: dict):
    """The one path from a journal line to the tables, for replay and for a write alike. Column names come from the
    store's field list, which check_event enforced on the line."""
    t, uid, ts, data = ev["type"], ev["uid"], ev["ts"], ev["data"]
    s = store.name
    if t == "create":
        row = {f: data.get(f) for f in store.fields}
        row[store.state_field] = data.get(store.state_field, store.default_state)
        if store.numbered:
            row["id"] = store.fmt_id(data["id"])
            if s == "backlog":
                row["num"] = data["id"]
        else:
            row["id"] = data["slug"]
        row.update(uid=uid, created_at=ts, updated_at=ts)
        cols = list(row)
        db.execute("INSERT INTO %s(%s) VALUES(%s)" % (s, ", ".join(cols), ", ".join("?" * len(cols))), [row[c] for c in cols])
    elif t == "update":
        for key in data:
            if key not in store.updatable:
                raise Corrupt("corrupt %s journal: unknown field in %s" % (s, shown(ev["event_uid"])))
            db.execute("UPDATE %s SET %s=? WHERE uid=?" % (s, key), (data[key], uid))
    elif t == "state":
        db.execute("UPDATE %s SET %s=? WHERE uid=?" % (s, store.state_field), (data["to"], uid))
        if "ref" in data and "ref" in store.fields:
            db.execute("UPDATE %s SET ref=? WHERE uid=?" % s, (data["ref"], uid))
    elif t == "renumber":
        db.execute("UPDATE %s SET id=? WHERE uid=?" % s, (store.fmt_id(data["to"]), uid))
        if s == "backlog":
            db.execute("UPDATE backlog SET num=? WHERE uid=?", (data["to"], uid))
    elif t == "round":
        col = data["counter"] + "_used"
        db.execute("UPDATE feature SET %s=%s+? WHERE uid=?" % (col, col), (data["n"], uid))
    elif t == "extra_round":
        col = data["counter"] + "_extra"
        db.execute("UPDATE feature SET %s=%s+? WHERE uid=?" % (col, col), (data["n"], uid))
    if not store.numbered:
        recompute_caps(db, uid)
    db.execute("UPDATE %s SET updated_at=? WHERE uid=?" % s, (ts, uid))
    db.execute("INSERT INTO %s_event(event_uid, uid, ts, type, by_who, note, data) VALUES(?, ?, ?, ?, ?, ?, ?)" % s,
               (ev["event_uid"], uid, ts, t, ev.get("by"), ev.get("note"), json.dumps(data, ensure_ascii=False, sort_keys=True)))


def sync_fts(db, store: Store, uid: str):
    s = store.name
    row = db.execute("SELECT rowid AS rid, * FROM %s WHERE uid=?" % s, (uid,)).fetchone()
    db.execute("DELETE FROM %s_fts WHERE rowid=?" % s, (row["rid"],))
    notes = " ".join(r[0] for r in db.execute("SELECT note FROM %s_event WHERE uid=? AND note IS NOT NULL ORDER BY ts" % s, (uid,)))
    cols = list(store.fts) + ["notes"]
    db.execute("INSERT INTO %s_fts(rowid, %s) VALUES(?, %s)" % (s, ", ".join(cols), ", ".join("?" * len(cols))),
               [row["rid"]] + [row[c] for c in store.fts] + [notes])


def meta_key(kind: str, store: Store) -> str:
    return "%s:%s" % (kind, store.name)


def rebuild_store(db, store: Store, raw: bytes):
    """Inside the caller's transaction, this store's tables only. A corrupt journal raises and leaves the old cache."""
    parsed = parse_store(store, raw)
    if parsed.errors:
        raise Corrupt("corrupt %s journal: %s" % (store.journal_name, "; ".join(parsed.errors[:5])))
    try:
        ordered = journal.replay_order(parsed.events, "uid")
    except Corrupt as ex:
        raise Corrupt("%s (%s)" % (ex, store.journal_name)) from None
    for table in ("%s_event", "%s_fts", "%s"):
        db.execute("DELETE FROM " + table % store.name)
    try:
        for ev in ordered:
            apply_event(db, store, ev)
    except sqlite3.IntegrityError as ex:
        raise Corrupt("corrupt %s journal: %s" % (store.journal_name, ex)) from None
    for row in db.execute("SELECT uid FROM %s" % store.name).fetchall():
        sync_fts(db, store, row[0])
    set_meta(db, meta_key("high_water", store), high_water_of(parsed.events))
    set_meta(db, meta_key("last_ts", store), max((ev["ts"] for ev in parsed.events), default=""))
    set_meta(db, meta_key("hash", store), sha(raw))


def transaction_rebuild(ctx: Ctx, db, store: Store, force=False):
    db.execute("BEGIN IMMEDIATE")
    try:
        raw = journal.read_journal(ctx.journal_of(store))
        if force or get_meta(db, meta_key("hash", store)) != sha(raw):
            rebuild_store(db, store, raw)
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise


def open_read(ctx: Ctx, stores) -> sqlite3.Connection:
    """Every command runs the hash check of the stores it reads: it covers git switch, pull and merge."""
    db = open_db(ctx)
    for store in stores:
        if get_meta(db, meta_key("hash", store)) != sha(journal.read_journal(ctx.journal_of(store))):
            transaction_rebuild(ctx, db, store)
    return db


def high_water(db, store: Store) -> int:
    return int(get_meta(db, meta_key("high_water", store)) or 0)


def duplicate_ids(db, store: Store) -> list:
    if not store.numbered:
        return []
    rows = db.execute("SELECT id, COUNT(*) FROM %s GROUP BY id HAVING COUNT(*) > 1 ORDER BY CAST(substr(id, %d) AS INTEGER)"
                      % (store.name, len(store.prefix) + 2)).fetchall()
    return [r[0] for r in rows]


def warn_duplicates(db, store: Store):
    for rid in duplicate_ids(db, store):
        print("warning: duplicate id %s held by two records: run doctor --fix" % rid, file=sys.stderr)


def live_row(db, store: Store, rid: str):
    """The one record a write or counters may touch. A duplicate id fails closed."""
    key = store.parse_id(rid)
    if store.numbered:
        rows = db.execute("SELECT * FROM %s WHERE id=?" % store.name, (store.fmt_id(key),)).fetchall()
        if len(rows) > 1:
            raise Refused("duplicate id %s held by %d records: run doctor --fix" % (store.fmt_id(key), len(rows)))
    else:
        rows = db.execute("SELECT * FROM feature WHERE slug=?", (key,)).fetchall()
    if not rows:
        raise Refused("%s not found" % shown(rid))
    return rows[0]


def order_by(store: Store) -> str:
    if store.numbered:
        return "CAST(substr(id, %d) AS INTEGER), uid" % (len(store.prefix) + 2)
    return "created_at, slug"


# ---------------------------------------------------------------- the write path

class StoreWriter(journal.Writer):
    """The engine's write path over one store's journal; the other stores' tables are not touched."""

    uid_key = "uid"

    def __init__(self, ctx: Ctx, store: Store, create=False):
        super().__init__(ctx, create)
        self.store = store
        self.path = ctx.journal_of(store)

    def check_writable(self):
        self.ctx.require_writable()
        journal.Cleaner(self.ctx)  # every write, text-free ones too: a missing pattern file refuses here (fail closed)

    def open_db(self):
        return open_db(self.ctx, create=self.create)

    def read(self) -> bytes:
        return journal.read_journal(self.path)

    def append(self, lines) -> bytes:
        return journal.append_lines(self.path, lines)

    def after_append(self):
        _after_append()

    def stored_hash(self):
        return get_meta(self.db, meta_key("hash", self.store))

    def rebuild(self, raw: bytes):
        rebuild_store(self.db, self.store, raw)

    def load_state(self):
        self.last_ts = get_meta(self.db, meta_key("last_ts", self.store)) or None
        self.top = high_water(self.db, self.store)

    def save_state(self, new: bytes):
        set_meta(self.db, meta_key("hash", self.store), sha(new))
        set_meta(self.db, meta_key("high_water", self.store), self.top)
        set_meta(self.db, meta_key("last_ts", self.store), self.last_ts or "")

    def apply(self, ev: dict):
        apply_event(self.db, self.store, ev)
        sync_fts(self.db, self.store, ev["uid"])

    def high_water_of(self, events) -> int:
        return high_water_of(events)

    def repair_tail(self):
        """A torn final line goes, a whole one gets its newline. Atomic replace, then this store is rebuilt."""
        new = journal.repaired(self.read())
        journal.replace_journal(self.path, self.ctx.workflow / (DB_NAME + "." + self.store.journal_name + ".tmp"), new)
        _after_append()
        rebuild_store(self.db, self.store, new)
        self.load_state()


# ---------------------------------------------------------------- content

def cleaner_for(ctx: Ctx, store: Store) -> journal.Cleaner:
    limits = store.limits()
    return journal.Cleaner(ctx, limits, set(limits))  # every record field is one line: it renders into a table cell


def clean_field(cleaner, store: Store, field: str, value, required: bool):
    """The stored value of one field, or None. Enums are checked against their set; the rest pass every content rule."""
    f = store.fields[field]
    if f.kind == "enum":
        if value is None or value == "":
            if required:
                raise Refused("%s: required, one of %s" % (field, ", ".join(f.choices)))
            return None
        if value not in f.choices:
            raise Refused("%s: must be one of %s" % (field, ", ".join(f.choices)))
        return value
    if value is None or (value == "" and not required):
        if required:
            raise Refused("%s: required" % field)
        return None
    text = cleaner.required(field, value) if required else (cleaner.clean(field, value) or None)
    if text is None:
        return None
    if f.kind == "nums":
        if not RX_NUMS.fullmatch(text):
            raise Refused("%s: a comma list of backlog numbers, e.g. 1, 4" % field)
        text = ", ".join(str(int(n)) for n in re.split(r"\s*,\s*", text))
    elif f.kind == "date":
        try:
            ok = RX_DATE.fullmatch(text) and dt.date.fromisoformat(text)
        except ValueError:
            ok = False
        if not ok:
            raise Refused("%s: expected YYYY-MM-DD" % field)
    elif f.kind == "source":
        if not RX_SOURCE.fullmatch(text):
            raise Refused("%s: expected BUG-####, a feature slug or framework" % field)
    elif f.kind == "slug":
        if not RX_SLUG.fullmatch(text):
            raise Refused("%s: expected kebab-case, a-z 0-9 and -" % field)
    return text


def check_state(store: Store, state):
    if state not in store.states:
        raise Refused("unknown %s '%s': one of %s" % (store.state_field, shown(state), ", ".join(store.states)))


def gd_rule(store: Store, frm, to, by: str):
    if (to in store.gd_states or frm in store.gd_states) and by != "main GD":
        raise Refused("%s -> %s is main GD only: pass --by 'main GD' on the main GD's order" % (frm or "(new)", to))


def by_of(cleaner, a) -> str:
    return journal.by_of(cleaner, a, DEFAULT_BY)


# ---------------------------------------------------------------- store write commands

def cmd_add(ctx, store: Store, a):
    ctx.require_writable()
    cleaner = cleaner_for(ctx, store)
    data = journal.read_stdin_json(True)
    allowed = set(store.fields) | {store.state_field, "note"}
    unknown = sorted(set(data) - allowed)
    if unknown:
        hint = " (num is assigned: the next free number)" if "num" in unknown and store.name == "backlog" else ""
        raise Refused("add: unknown field: %s%s" % (shown_all(unknown), hint))
    record = {}
    for name, f in store.fields.items():
        raw = data.get(name)
        if name == "date" and raw in (None, ""):
            raw = today()
        value = clean_field(cleaner, store, name, raw, f.required)
        if value is not None:
            record[name] = value
    state = data.get(store.state_field, store.default_state)
    check_state(store, state)
    note = (cleaner.clean("note", data["note"]) or None) if data.get("note") else None
    by = by_of(cleaner, a)
    gd_rule(store, None, state, by)
    if store.name == "fwbacklog" and state == "Done" and not record.get("ref"):
        raise Refused("ref: required for Done (a commit sha or a path)")
    record[store.state_field] = state
    with StoreWriter(ctx, store, create=True) as w:
        if store.numbered:
            num = w.top + 1
            w.emit("create", str(uuid.uuid4()), dict(record, id=num), by=by, note=note)
            rid = store.fmt_id(num)
        else:
            rid = record["slug"]
            if w.db.execute("SELECT 1 FROM feature WHERE slug=?", (rid,)).fetchone():
                raise Refused("feature %s is already registered: use update" % rid)
            w.emit("create", feature_uid(rid), record, by=by, note=note, event_uid=journal.stable_uid("feature/%s/create" % rid))
    cleaner.report()
    print(rid)
    return 0


def cmd_update(ctx, store: Store, a):
    ctx.require_writable()
    store.parse_id(a.id)
    cleaner = cleaner_for(ctx, store)
    data = journal.read_stdin_json(True)
    unknown = sorted(set(data) - set(store.updatable) - {"note"})
    if unknown:
        raise Refused("update: unknown or read-only field: %s (the %s moves through set-state)" % (shown_all(unknown), store.state_field))
    note = (cleaner.clean("note", data["note"]) or None) if data.get("note") else None
    changes = {}
    for field, value in data.items():
        if field != "note":
            changes[field] = clean_field(cleaner, store, field, value, store.fields[field].required)
    by = by_of(cleaner, a)
    with StoreWriter(ctx, store) as w:
        row = live_row(w.db, store, a.id)
        changes = {k: v for k, v in changes.items() if row[k] != v}
        if changes or note:
            w.emit("update", row["uid"], changes, by=by, note=note)
    cleaner.report()
    written = sorted(changes) + (["note"] if note else [])
    print("%s updated: %s" % (a.id, ", ".join(written)) if written else "%s: no change" % a.id)
    return 0


def cmd_set_state(ctx, store: Store, a):
    ctx.require_writable()
    store.parse_id(a.id)
    check_state(store, a.state)
    cleaner = cleaner_for(ctx, store)
    if a.ref is not None and "ref" not in store.fields:
        raise Refused("--ref: only for fwbacklog")
    note, data = journal.note_of(cleaner, a, True, ("note", "ref") if "ref" in store.fields else ("note",))
    by = by_of(cleaner, a)
    raw_ref = a.ref if a.ref is not None else data.get("ref")
    ref = clean_field(cleaner, store, "ref", raw_ref, False) if raw_ref is not None else None
    with StoreWriter(ctx, store) as w:
        row = live_row(w.db, store, a.id)
        frm = row[store.state_field]
        if frm == a.state:
            raise Refused("%s is already %s" % (a.id, a.state))
        gd_rule(store, frm, a.state, by)
        payload = {"from": frm, "to": a.state}
        if ref is not None:
            payload["ref"] = ref
        if store.name == "fwbacklog" and a.state == "Done" and not (ref or row["ref"]):
            raise Refused("ref: required for Done (--ref <commit sha or path>)")
        w.emit("state", row["uid"], payload, by=by, note=note)
    cleaner.report()
    print("%s %s -> %s" % (a.id, frm, a.state))
    return 0


# ---------------------------------------------------------------- feature counters

# Each source is f(ctx, slug) -> iterable of {"type": "extra_round"|"stop_rule", "counter", "n"|"extra_dispatch", "date"}.
# The journal is the first; T2 adds the feature's decisions.csv rows of kind extra-round and stop-rule here.
COUNTER_SOURCES = []


def journal_counter_events(db, uid: str) -> list:
    out = []
    for ev in db.execute("SELECT * FROM feature_event WHERE uid=? AND type IN ('extra_round','stop_rule') ORDER BY ts, event_uid", (uid,)):
        data = json.loads(ev["data"])
        out.append(dict(data, type=ev["type"], date=ev["ts"][:10]))
    return out


def record_of(events) -> str:
    """The record lines round-cap.ps1 matches: the last stop rule per counter, then one line per extra round."""
    stops, extras = {}, []
    for e in events:
        if e["type"] == "stop_rule":
            stops[e["counter"]] = "- Stop rule: %s root-caused %s · extra dispatch: %s" % (e["counter"], e["date"], e["extra_dispatch"])
        elif e["type"] == "extra_round":
            extras.append("extra round: %s +%d" % (e["counter"], e["n"]))
    return "\n".join([stops[k] for k in sorted(stops)] + extras)


def feature_counters(ctx: Ctx, db, slug: str) -> dict:
    """The one builder of `feature counters`: registry rounds, journal extra rounds and stop rules, then COUNTER_SOURCES."""
    rows = db.execute("SELECT * FROM feature WHERE slug=?", (slug,)).fetchall()
    if not rows:
        return {"slug": slug, "found": False, "open": False, "size": None,
                "review": {"used": 0, "cap": BASE_CAPS["review"]}, "qa": {"used": 0, "cap": BASE_CAPS["qa"]},
                "rework": {"used": 0, "cap": REWORK_CAPS["M"]}, "record": ""}
    r = rows[0]
    events = journal_counter_events(db, r["uid"])
    caps = {c: r["%s_cap" % c] for c in COUNTERS}
    for source in COUNTER_SOURCES:
        for e in source(ctx, slug):
            events.append(e)
            if e["type"] == "extra_round":
                caps[e["counter"]] += e["n"]
    out = {"slug": slug, "found": True, "open": r["status"] in STORES["feature"].open_states, "size": r["size"]}
    for c in COUNTERS:
        out[c] = {"used": r["%s_used" % c], "cap": caps[c]}
    out["record"] = record_of(events)
    return out


def cmd_counters(ctx, store, a):
    slug = store.parse_id(a.id)
    db = open_read(ctx, [store])
    print(json.dumps(feature_counters(ctx, db, slug)))  # ASCII: a console code page cannot mangle what the hook parses
    return 0


def feature_counter_write(ctx, store, a, etype):
    ctx.require_writable()
    store.parse_id(a.id)
    n = journal.parse_count(a.n)
    cleaner = cleaner_for(ctx, store)
    note, _ = journal.note_of(cleaner, a, True)
    by = by_of(cleaner, a)
    if etype == "extra_round" and by != "main GD":
        raise Refused("extra-round is main GD only: pass --by 'main GD' on the main GD's order")
    with StoreWriter(ctx, store) as w:
        row = live_row(w.db, store, a.id)
        w.emit(etype, row["uid"], {"counter": a.counter, "n": n}, by=by, note=note)
        used, cap = w.db.execute("SELECT %s_used, %s_cap FROM feature WHERE uid=?" % (a.counter, a.counter), (row["uid"],)).fetchone()
    cleaner.report()
    print("%s %s %d/%d" % (a.id, a.counter, used, cap))
    return 0


def cmd_round(ctx, store, a):
    return feature_counter_write(ctx, store, a, "round")


def cmd_extra_round(ctx, store, a):
    return feature_counter_write(ctx, store, a, "extra_round")


def cmd_stop_rule(ctx, store, a):
    ctx.require_writable()
    store.parse_id(a.id)
    cleaner = cleaner_for(ctx, store)
    note = cleaner.clean("note", a.note) if a.note is not None else None
    by = by_of(cleaner, a)
    with StoreWriter(ctx, store) as w:
        row = live_row(w.db, store, a.id)
        w.emit("stop_rule", row["uid"], {"counter": a.counter, "extra_dispatch": a.extra_dispatch}, by=by, note=note or None)
    cleaner.report()
    print("%s stop rule: %s, extra dispatch %s" % (a.id, a.counter, a.extra_dispatch))
    return 0


# ---------------------------------------------------------------- store read commands

def public_row(store: Store, row) -> dict:
    out = {k: row[k] for k in row.keys() if not k.endswith("_extra")}
    if not store.numbered:
        for c in COUNTERS:
            out[c] = {"used": out.pop("%s_used" % c), "cap": out.pop("%s_cap" % c)}
    return out


def events_of(db, store: Store, uid: str) -> list:
    return [{"ts": ev["ts"], "type": ev["type"], "by": ev["by_who"], "note": ev["note"], "data": ev["data"]}
            for ev in db.execute("SELECT * FROM %s_event WHERE uid=? ORDER BY ts, event_uid" % store.name, (uid,))]


def cmd_show(ctx, store, a):
    key = store.parse_id(a.id)
    db = open_read(ctx, [store])
    if store.numbered:
        rows = db.execute("SELECT * FROM %s WHERE id=?" % store.name, (store.fmt_id(key),)).fetchall()
    else:
        rows = db.execute("SELECT * FROM feature WHERE slug=?", (key,)).fetchall()
    if not rows:
        raise Refused("%s not found" % shown(a.id))
    if len(rows) > 1:
        warn_duplicates(db, store)
    if a.json:
        items = [dict(public_row(store, r), events=events_of(db, store, r["uid"])) for r in rows]
        print(json.dumps(items[0] if len(items) == 1 else items, ensure_ascii=False, indent=1))
        return 0
    for r in rows:
        print("%s | %s | uid %s" % (r["id"], r[store.state_field], r["uid"]))
        for name, f in store.fields.items():
            if name != "slug" and r[name] is not None:
                print("%s: %s" % (f.label, r[name]))
        if not store.numbered:
            for c in COUNTERS:
                print("%s rounds: %d/%d" % (c.capitalize() if c != "qa" else "QA", r["%s_used" % c], r["%s_cap" % c]))
        print("Created: %s" % r["created_at"])
        print("Updated: %s" % r["updated_at"])
        print("Events:")
        for ev in events_of(db, store, r["uid"]):
            data = json.loads(ev["data"])
            what = "%s -> %s" % (data.get("from", "?"), data["to"]) if ev["type"] == "state" else ev["type"]
            print("- %s %s by %s%s" % (ev["ts"], what, ev["by"] or "unknown", ": " + ev["note"] if ev["note"] else ""))
    return 0


def selected_rows(ctx, store, a):
    db = open_read(ctx, [store])
    where, params = [], []
    if a.state:
        for s in a.state:
            check_state(store, s)
        where.append("%s IN (%s)" % (store.state_field, ",".join("?" * len(a.state))))
        params += a.state
    if getattr(a, "open", False):
        where.append("%s IN (%s)" % (store.state_field, ",".join("?" * len(store.open_states))))
        params += store.open_states
    rows = db.execute("SELECT * FROM %s %s ORDER BY %s" % (store.name, "WHERE " + " AND ".join(where) if where else "", order_by(store)), params).fetchall()
    warn_duplicates(db, store)
    return rows


def cmd_list(ctx, store, a):
    rows = selected_rows(ctx, store, a)
    if a.json:
        print(json.dumps([public_row(store, r) for r in rows], ensure_ascii=False, indent=1))
        return 0
    if not rows:
        print("no records")
        return 0
    print(" | ".join(c.replace("_", " ").capitalize() if c not in ("id", "cp") else c.upper() for c in store.list_cols))
    for r in rows:
        print(" | ".join(r[c] if r[c] is not None else "-" for c in store.list_cols))
    return 0


def md_cell(value) -> str:
    return "" if value is None else str(value).replace("\\", "\\\\").replace("|", "\\|")


def cmd_render(ctx, store, a):
    db = open_read(ctx, [store])
    rows = db.execute("SELECT * FROM %s ORDER BY %s" % (store.name, order_by(store))).fetchall()
    warn_duplicates(db, store)
    heads = [h for h, _ in store.render_cols]
    print("| %s |" % " | ".join(heads))
    print("|%s|" % "|".join("---" for _ in heads))
    for r in rows:
        cells = []
        for _, col in store.render_cols:
            if col in COUNTERS:
                cells.append("%d/%d" % (r["%s_used" % col], r["%s_cap" % col]))
            else:
                cells.append(md_cell(r[col]))
        print("| %s |" % " | ".join(cells))
    return 0


def cmd_search(ctx, store, a):
    terms = re.findall(r"\w+", a.text.lower())
    if not terms:
        raise Refused("search: no words in the query")
    db = open_read(ctx, [store])
    expr = " OR ".join('"%s"*' % t for t in terms)
    s = store.name
    title = store.list_cols[-1]
    rows = db.execute("""SELECT r.id, r.%s AS state, r.%s AS title, snippet(%s_fts, -1, '[', ']', '...', 14) AS hit
                         FROM %s_fts JOIN %s r ON r.rowid = %s_fts.rowid WHERE %s_fts MATCH ?
                         ORDER BY bm25(%s_fts) LIMIT ?""" % (store.state_field, title, s, s, s, s, s, s), (expr, a.n)).fetchall()
    if not rows:
        print("no matches")
    for r in rows:
        print("%s | %s | %s" % (r["id"], r["state"], r["title"] or "-"))
        print("  %s" % (r["hit"] or "").replace("\n", " "))
    return 0


def store_stats(db, store: Store) -> str:
    marks = ",".join("?" * len(store.open_states))
    n = db.execute("SELECT COUNT(*) FROM %s WHERE %s IN (%s)" % (store.name, store.state_field, marks), store.open_states).fetchone()[0]
    total = db.execute("SELECT COUNT(*) FROM %s" % store.name).fetchone()[0]
    return "%s: %d open of %d" % (store.title, n, total)


def cmd_store_stats(ctx, store, a):
    print(store_stats(open_read(ctx, [store]), store))
    return 0


# ---------------------------------------------------------------- global commands

def cmd_stats(ctx, a):
    db = open_read(ctx, STORES.values())
    parts = []
    for s in STORES.values():
        marks = ",".join("?" * len(s.open_states))
        n = db.execute("SELECT COUNT(*) FROM %s WHERE %s IN (%s)" % (s.name, s.state_field, marks), s.open_states).fetchone()[0]
        parts.append("%s %d open" % (s.title.lower(), n))
    print("Records: " + " · ".join(parts))
    return 0


def cmd_rebuild(ctx, a):
    db = open_db(ctx)
    out = []
    for s in STORES.values():
        transaction_rebuild(ctx, db, s, force=True)
        warn_duplicates(db, s)
        out.append("%s %d" % (s.name, db.execute("SELECT COUNT(*) FROM %s" % s.name).fetchone()[0]))
    print("rebuilt: " + ", ".join(out))
    return 0


def cmd_sql(ctx, a):
    return journal.run_sql(a.query, a.json, lambda: open_read(ctx, STORES.values()), ctx.db_path, SQL_SECONDS)


def store_problems(ctx, db, store: Store) -> tuple[list, bool, list]:
    raw = journal.read_journal(ctx.journal_of(store))
    parsed = parse_store(store, raw)
    problems = ["%s: %s" % (store.journal_name, e) for e in parsed.errors]
    if parsed.torn:
        problems.append("%s: torn final line: removed by the next write or doctor --fix" % store.journal_name)
    dups = duplicate_ids(db, store) if db is not None else []
    problems += ["%s: duplicate id %s held by two records: doctor --fix renumbers the later create" % (store.journal_name, d) for d in dups]
    return problems, parsed.torn, dups


def renumber_duplicates(w: StoreWriter) -> list:
    done = []
    store = w.store
    for rid in duplicate_ids(w.db, store):
        rows = w.db.execute("SELECT uid FROM %s WHERE id=? ORDER BY created_at, uid" % store.name, (rid,)).fetchall()
        for row in rows[1:]:  # the earlier create keeps the id
            old, new = store.parse_id(rid), w.top + 1
            # Same event_uid on two machines fixing the same merge: the second copy dedupes.
            w.emit("renumber", row["uid"], {"from": old, "to": new}, by="doctor",
                   event_uid=journal.stable_uid("renumber/%s/%s/%d/%d" % (store.name, row["uid"], old, new)))
            done.append("renumbered %s to %s" % (rid, store.fmt_id(new)))
            if store.name == "backlog":  # depends_on names numbers; a renumber does not rewrite them
                deps = [r["id"] for r in w.db.execute("SELECT id, depends_on FROM backlog WHERE depends_on IS NOT NULL").fetchall()
                        if str(old) in re.split(r",\s*", r["depends_on"])]
                if deps:
                    done.append("check depends_on of %s: %d was held by two rows before the renumber" % (", ".join(deps), old))
    return done


def git_problems(ctx: Ctx) -> list:
    """What the project's own git rules do to the journals. No repair: the rules are the project's to change.
    The framework backlog journal may be ignored (the framework repo ignores its copy); then its attributes do not matter."""
    if ctx.git_dir is None:
        return []
    out = []
    for s in STORES.values():
        path = ".workflow/" + s.journal_name
        code, _ = run_git(ctx.root, "check-ignore", "-q", "--", path)
        if code == 0:
            if s.name != "fwbacklog":
                out.append("journal ignored by git: %s must stay tracked, it is the truth. Remove the rule that ignores it" % path)
            continue
        if code != 1:
            out.append("git check-ignore failed on %s" % path)
            continue
        if not ctx.journal_of(s).exists():
            code, text = run_git(ctx.root, "status", "--porcelain", "--", path)
            if not code and "D" in text[:2]:
                out.append("journal deleted: git tracks %s and the file is gone. Restore it with git restore, or commit an empty one" % path)
        for attr, want, harm in (("merge", "union", "merges can conflict"), ("eol", "lf", "the journal can end up with mixed line endings")):
            code, text = run_git(ctx.root, "check-attr", attr, "--", path)
            got = text.rsplit(": ", 1)[-1] if not code else "unknown"
            if got != want:
                out.append("journal attributes: %s resolves to %s, not %s for %s: %s. Put `%s text eol=lf merge=union` "
                           "in .gitattributes, after any rule that overrides it" % (attr, shown(got), want, path, harm, path))
    return out


def cmd_doctor(ctx, a):
    if a.fix:
        ctx.require_writable()
        journal.Cleaner(ctx)  # refuses before the checks, with or without something to repair
    for s in STORES.values():
        parsed = parse_store(s, journal.read_journal(ctx.journal_of(s)))
        if parsed.errors:
            raise Refused("\n".join(["corrupt %s journal: %s" % (s.journal_name, e) for e in parsed.errors] + ["doctor: fix those lines by hand, then rerun"]))
        journal.replay_order(parsed.events, "uid")
    db = open_read(ctx, STORES.values())
    problems = []
    for s in STORES.values():
        found, torn, dups = store_problems(ctx, db, s)
        if a.fix and (torn or dups):
            with StoreWriter(ctx, s) as w:
                if torn:
                    w.repair_tail()
                for line in renumber_duplicates(w):
                    print(line)
            db = open_read(ctx, [s])
            found, _, _ = store_problems(ctx, db, s)
        problems += found
    problems += git_problems(ctx)
    if problems:
        raise Refused("\n".join(problems))
    print("doctor: clean")
    return 0


# ---------------------------------------------------------------- the round ledger (.workflow/ledger.db, local)

class LedgerBusy(Exception):
    """SQLITE_BUSY past the timeout: the hook parks the events."""


class LedgerBroken(Exception):
    """A ledger file that cannot be read: the hook blocks on it."""


LEDGER_SCHEMA = ("CREATE TABLE IF NOT EXISTS round_event(key TEXT NOT NULL, counter TEXT NOT NULL, event_id TEXT NOT NULL, "
                 "ts TEXT NOT NULL, UNIQUE(key, counter, event_id))")


def utc_stamp() -> str:
    d = now_utc()
    return d.strftime("%Y%m%dT%H%M%S") + "%03d" % (d.microsecond // 1000)


def is_busy(ex) -> bool:
    return isinstance(ex, sqlite3.OperationalError) and ("locked" in str(ex) or "busy" in str(ex))


def is_corrupt(ex) -> bool:
    return isinstance(ex, sqlite3.DatabaseError) and not isinstance(ex, sqlite3.OperationalError)


def ledger_event(e) -> tuple:
    if not isinstance(e, dict):
        raise ValueError("not an object")
    vals = tuple(e.get(k) for k in ("key", "counter", "id"))
    if not all(isinstance(v, str) and v and len(v) <= 300 and "\n" not in v for v in vals):
        raise ValueError("key, counter and id must be one-line text")
    return vals


def parse_event_list(raw: bytes) -> list:
    """The hook's parked-file shape: a JSON list of {key, counter, id}; one object counts as a list of one."""
    data = json.loads(raw.decode("utf-8-sig")) if raw.strip() else []
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("not a list")
    return [ledger_event(e) for e in data]


def parse_rounds_json(raw: bytes) -> list:
    """Today's .workflow/rounds.json: { key: { counter: [ids] } }, in file order."""
    if not raw.strip():
        return []
    data = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("not an object")
    out = []
    for key, counters in data.items():
        if not isinstance(counters, dict):
            raise ValueError("key %s holds no counters" % shown(key))
        for counter, ids in counters.items():
            ids = [ids] if isinstance(ids, str) else ids
            if not isinstance(ids, list):
                raise ValueError("bad ids")
            for i in ids:
                out.append(ledger_event({"key": key, "counter": counter, "id": i}))
    return out


def ledger_files(ctx: Ctx, pattern: str) -> list:
    return sorted(ctx.workflow.glob(pattern)) if ctx.workflow.is_dir() else []


def ledger_marks(ctx: Ctx) -> list:
    return ledger_files(ctx, "ledger.corrupt-*.db") + ledger_files(ctx, "rounds.corrupt-*.json")


def ledger_connect(path: Path, create: bool) -> sqlite3.Connection:
    if create:
        db = sqlite3.connect(str(path), timeout=LEDGER_BUSY_MS / 1000, isolation_level=None)
    else:
        db = sqlite3.connect(path.resolve().as_uri() + "?mode=rw", uri=True, timeout=LEDGER_BUSY_MS / 1000, isolation_level=None)
    db.execute("PRAGMA busy_timeout=%d" % LEDGER_BUSY_MS)
    return db


def ledger_rows(path: Path) -> list:
    """The DB's events in insertion order. Raises LedgerBroken on a damaged file, LedgerBusy on a lock past the timeout."""
    if not path.exists():
        return []
    db = None
    try:
        db = ledger_connect(path, False)
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='round_event'").fetchone():
            return []
        return [tuple(r) for r in db.execute("SELECT key, counter, event_id FROM round_event ORDER BY rowid")]
    except sqlite3.Error as ex:
        if is_busy(ex):
            raise LedgerBusy() from None
        raise LedgerBroken("%s is unreadable (%s)" % (path.name, type(ex).__name__)) from None
    finally:
        if db is not None:
            db.close()


def ledger_view(events) -> dict:
    out = {}
    for key, counter, eid in events:
        ids = out.setdefault(key, {}).setdefault(counter, [])
        if eid not in ids:
            ids.append(eid)
    return out


def cmd_ledger_get(ctx, a):
    marks = ledger_marks(ctx)
    if marks:
        raise LedgerBroken("%d unreadable ledger file(s) in .workflow/ (%s): resolve them with the main GD" % (len(marks), ", ".join(m.name for m in marks)))
    events = ledger_rows(ctx.workflow / LEDGER_NAME)
    legacy = ctx.workflow / "rounds.json"
    if legacy.exists():  # not migrated yet: read-only, so no event is lost before `ledger migrate`
        try:
            events += parse_rounds_json(legacy.read_bytes())
        except (ValueError, OSError):
            raise LedgerBroken("rounds.json is unparsable: resolve it, then run ledger migrate") from None
    for f in ledger_files(ctx, "rounds.pending-*.json"):
        try:
            events += parse_event_list(f.read_bytes())
        except FileNotFoundError:
            continue  # merged by a parallel add
        except (ValueError, OSError):
            raise LedgerBroken("%s is unparsable: the next ledger add renames it" % f.name) from None
    print(json.dumps(ledger_view(events)))  # ASCII, as counters
    return 0


def take_pending(ctx: Ctx) -> tuple[list, list]:
    """(events of every parsable parked file, those files). An unparsable one is renamed rounds.corrupt-pending-<rest>, kept."""
    events, files = [], []
    for f in ledger_files(ctx, "rounds.pending-*.json"):
        try:
            events += parse_event_list(f.read_bytes())
            files.append(f)
        except FileNotFoundError:
            continue
        except (ValueError, OSError):
            try:
                f.rename(f.with_name("rounds.corrupt-pending-" + f.name[len("rounds.pending-"):]))
            except OSError:
                pass
    return events, files


def move_corrupt_ledger(ctx: Ctx, path: Path) -> Path:
    dest = ctx.workflow / ("ledger.corrupt-%s.db" % utc_stamp())
    path.rename(dest)
    for suffix in ("-wal", "-shm"):
        side = path.with_name(path.name + suffix)
        if side.exists():
            side.rename(dest.with_name(dest.name + suffix))
    return dest


def ledger_write(ctx: Ctx, events: list, pre=None) -> int:
    """INSERT OR IGNORE under BEGIN IMMEDIATE, parked files merged inside the same transaction. Returns rows inserted.
    `pre` runs inside the transaction too and returns more events (migrate's rounds.json)."""
    ctx.workflow.mkdir(parents=True, exist_ok=True)
    path = ctx.workflow / LEDGER_NAME
    for attempt in (1, 2):
        db = None
        try:
            db = ledger_connect(path, True)
            db.execute("PRAGMA journal_mode=WAL")
            db.execute(LEDGER_SCHEMA)
            db.execute("BEGIN IMMEDIATE")
            try:
                parked, files = take_pending(ctx)
                extra = pre() if pre else []
                ts = journal.fmt_ts(now_utc())
                n = 0
                for key, counter, eid in list(events) + extra + parked:
                    n += db.execute("INSERT OR IGNORE INTO round_event(key, counter, event_id, ts) VALUES(?, ?, ?, ?)",
                                    (key, counter, eid, ts)).rowcount
                db.execute("COMMIT")
            except BaseException:
                db.execute("ROLLBACK")
                raise
            for f in files:
                try:
                    f.unlink()
                except FileNotFoundError:
                    pass
            return n
        except sqlite3.Error as ex:
            if is_busy(ex):
                raise LedgerBusy() from None
            if not is_corrupt(ex) or attempt == 2:
                raise
            db.close()
            db = None
            dest = move_corrupt_ledger(ctx, path)
            print("records: unreadable ledger moved to %s; a new one starts" % dest.name, file=sys.stderr)
        finally:
            if db is not None:
                db.close()
    raise RuntimeError("unreachable")


def cmd_ledger_add(ctx, a):
    ctx.require_writable()
    data = journal.read_stdin_json(True, list)
    try:
        events = [ledger_event(e) for e in data]
    except ValueError as ex:
        raise Refused("ledger add: %s" % ex) from None
    n = ledger_write(ctx, events)
    print("ledger: %d new" % n)
    return 0


def cmd_ledger_migrate(ctx, a):
    ctx.require_writable()
    legacy = ctx.workflow / "rounds.json"
    seen = {"found": False, "events": 0}

    def read_legacy():
        if not legacy.exists():
            return []
        try:
            events = parse_rounds_json(legacy.read_bytes())
        except (ValueError, OSError) as ex:
            raise Refused("rounds.json is unparsable (%s): left in place, fix it by hand, then rerun" % type(ex).__name__) from None
        seen.update(found=True, events=len(events))
        return events

    n = ledger_write(ctx, [], pre=read_legacy)
    if seen["found"]:
        dest = ctx.workflow / ("rounds.migrated-%s.json" % utc_stamp())
        legacy.rename(dest)
        print("migrated %d event(s) from rounds.json (%d new); renamed it %s" % (seen["events"], n, dest.name))
    else:
        print("nothing to migrate (%d parked event(s) merged)" % n)
    return 0


# ---------------------------------------------------------------- parser and main

STORE_HANDLERS = {"add": cmd_add, "update": cmd_update, "set-state": cmd_set_state, "list": cmd_list, "show": cmd_show,
                  "search": cmd_search, "render": cmd_render, "stats": cmd_store_stats, "round": cmd_round,
                  "extra-round": cmd_extra_round, "stop-rule": cmd_stop_rule, "counters": cmd_counters}
GLOBAL_HANDLERS = {"rebuild": cmd_rebuild, "doctor": cmd_doctor, "sql": cmd_sql, "stats": cmd_stats}
LEDGER_HANDLERS = {"get": cmd_ledger_get, "add": cmd_ledger_add, "migrate": cmd_ledger_migrate}


def build_parser() -> argparse.ArgumentParser:
    p = journal.Parser(prog="records", description="Workflow records over tracked journals, a gitignored records.db cache, and the local round ledger.")
    p.add_argument("--root", help="project root (default: derived from this script's location)")
    top = p.add_subparsers(dest="area", required=True)
    for store in STORES.values():
        sp = top.add_parser(store.name, help="%s (.workflow/%s)" % (store.title, store.journal_name))
        sub = sp.add_subparsers(dest="cmd", required=True)
        idname = "slug" if not store.numbered else "id"

        def write_cmd(name, help_text):
            s = sub.add_parser(name, help=help_text)
            s.add_argument("--by", help="who writes; main-GD-only moves need exactly main GD (default: %s)" % DEFAULT_BY)
            return s

        write_cmd("add", "a new record: JSON fields on stdin; prints its %s" % idname)
        write_cmd("update", "change fields: JSON on stdin").add_argument("id", metavar=idname)
        s = write_cmd("set-state", "move the %s; note on stdin as JSON or --note" % store.state_field)
        s.add_argument("id", metavar=idname)
        s.add_argument("state")
        s.add_argument("--note")
        s.add_argument("--ref", help="fwbacklog: the commit sha or path that closed it")
        s = sub.add_parser("list", help="records, filtered")
        s.add_argument("--state", action="append")
        s.add_argument("--open", action="store_true", help="only %s" % ", ".join(store.open_states))
        s.add_argument("--json", action="store_true")
        s = sub.add_parser("show", help="one record with its events")
        s.add_argument("id", metavar=idname)
        s.add_argument("--json", action="store_true")
        s = sub.add_parser("search", help="FTS5 search over text and notes")
        s.add_argument("text")
        s.add_argument("-n", type=int, default=10)
        sub.add_parser("render", help="GitHub markdown table of the store")
        sub.add_parser("stats", help="one line")
        if not store.numbered:
            for name, text in (("round", "add used file-only rounds to a counter"), ("extra-round", "raise a counter's cap: main GD only")):
                s = write_cmd(name, text)
                s.add_argument("id", metavar="slug")
                s.add_argument("counter", choices=COUNTERS)
                s.add_argument("n", help="+n, with n from 1 to %d" % journal.MAX_COUNT)
                s.add_argument("--note")
            s = write_cmd("stop-rule", "record the stop rule for a counter")
            s.add_argument("id", metavar="slug")
            s.add_argument("counter", choices=COUNTERS)
            s.add_argument("--extra-dispatch", dest="extra_dispatch", required=True, choices=("unused", "used"))
            s.add_argument("--note")
            s = sub.add_parser("counters", help="what round-cap.ps1 reads; always JSON")
            s.add_argument("id", metavar="slug")
            s.add_argument("--json", action="store_true", help="accepted for clarity; the output is always JSON")
    top.add_parser("rebuild", help="rebuild every store's tables from its journal")
    top.add_parser("doctor", help="report journal problems").add_argument("--fix", action="store_true", help="renumber duplicates, repair torn tails")
    s = top.add_parser("sql", help="one read-only SELECT over every table")
    s.add_argument("query")
    s.add_argument("--json", action="store_true")
    top.add_parser("stats", help="one line: Records: ... open per store")
    sp = top.add_parser("ledger", help="the local round ledger .workflow/ledger.db")
    sub = sp.add_subparsers(dest="cmd", required=True)
    sub.add_parser("get", help="the ledger as {key: {counter: [ids]}}").add_argument("--json", action="store_true", help="always JSON")
    sub.add_parser("add", help="stdin: [{key, counter, id}]").add_argument("--json", action="store_true", help="stdin is JSON")
    sub.add_parser("migrate", help="import .workflow/rounds.json and parked files")
    return p


def main(argv=None) -> int:
    """An interrupt leaves here: raised inside a handler below, its traceback would chain the refusal holding the raw value."""
    try:
        return run(argv)
    except KeyboardInterrupt:
        print("records: interrupted", file=sys.stderr)
        return 130


def run(argv) -> int:
    journal.reconfigure_streams()
    root = journal.given_root(argv, DEFAULT_ROOT)

    def say(text):
        print("records: %s" % journal.refusal_text(str(text), root), file=sys.stderr)

    try:
        a = build_parser().parse_args(argv)
        if a.area == "ledger":
            ctx = Ctx(a.root, use_git=False)
            try:
                return LEDGER_HANDLERS[a.cmd](ctx, a)
            except LedgerBusy:
                say("ledger busy past %d ms: park the events and retry" % LEDGER_BUSY_MS)
                return EXIT_BUSY
            except LedgerBroken as ex:
                say(ex)
                return EXIT_LEDGER_CORRUPT
        ctx = Ctx(a.root)
        if a.area in STORES:
            store = STORES[a.area]
            return STORE_HANDLERS[a.cmd](ctx, store, a)
        return GLOBAL_HANDLERS[a.area](ctx, a)
    except UsageError as ex:
        say(ex)
        return 2
    except (Refused, Corrupt) as ex:
        say(ex)
        return 1
    except (RuntimeError, re.error, ValueError, OSError, sqlite3.Error, subprocess.SubprocessError) as ex:
        say(ex)
        return 1
    finally:
        journal.close_all()


if __name__ == "__main__":
    sys.exit(main())
