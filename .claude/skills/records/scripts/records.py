"""Workflow records: game backlog, framework backlog, project debt and the feature registry, each over its own tracked
journal, with one gitignored SQLite cache; the local round ledger; and the feature-scope CSV tables. No LLM, stdlib only.

Run with `python -I records.py --root <project root> <store> <command>` (stores: backlog, fwbacklog, debt, feature) or
`... <rebuild|doctor|sql|stats|ledger|csv|bug-mirror|migrate>`. Each journal .workflow/<name>.jsonl is the truth;
.workflow/records.db is a cache whose meta holds one hash per journal, so a change in one journal rebuilds only that store's
tables. The round ledger .workflow/ledger.db is a local record, never journaled. A feature's CSV tables are files the CLI
owns, one per table. Contract: ../references/schema.md.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import datetime as dt
import importlib.util
import io
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
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
    """`base` is where files are read and written: the root, or a migration's staging folder (StagedCtx). Every file path
    goes through file(rel), so a staged run touches nothing under the root."""

    def __init__(self, arg, use_git=True):
        super().__init__(arg, "", DB_NAME, DEFAULT_ROOT, label="records journal", clock_env=CLOCK_ENV, use_git=use_git)
        self.base = self.root

    @property
    def journal(self):
        raise AttributeError("records keeps one journal per store: use journal_of(store)")

    @property
    def workflow(self) -> Path:
        return self.base / ".workflow"

    def file(self, rel: str) -> Path:
        return self.base / rel

    def exists(self, rel: str) -> bool:
        return (self.base / rel).exists()

    def run_git(self, cwd, *args):
        return run_git(cwd, *args)  # this module's name, so a patch of records.run_git reaches the check

    def journal_of(self, store: Store) -> Path:
        return self.file(".workflow/" + store.journal_name)

    def journals(self) -> list:
        return [self.journal_of(s) for s in STORES.values()]


class StagedCtx(Ctx):
    """The real root's rules (worktree, git, patterns) over a staging folder: a file is copied in from the root the first
    time it is asked for, and every write lands in the folder. `migrate` swaps the folder's files in at the end."""

    def __init__(self, real: Ctx, stage: Path, dry_run=False):  # no super().__init__: the real context's checks already ran
        self.__dict__.update(real.__dict__)
        self.real, self.base, self.dry_run = real, Path(stage), dry_run
        self.copied = {}  # rel -> sha of the root's file when it was copied in: the swap refuses if it changed since

    def require_writable(self):
        """A dry run writes only the staging folder, so a linked worktree may run one; a real run keeps the root's rule."""
        if not self.dry_run:
            super().require_writable()

    def file(self, rel: str) -> Path:
        path, source = self.base / rel, self.real.root / rel
        if not path.exists() and source.is_file():
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, path)
            self.copied[rel] = sha(path.read_bytes())
        return path

    def exists(self, rel: str) -> bool:
        return (self.base / rel).exists() or (self.real.root / rel).exists()


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
    if t in ("extra_round", "stop_rule"):  # a migrated event keeps its source date; a live one has none
        need(data.get("date") is None or (isinstance(data["date"], str) and RX_DATE.fullmatch(data["date"]) is not None), "bad date")


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
    rid = create_record(ctx, store, data, by_of(cleaner, a), cleaner)
    cleaner.report()
    print(rid)
    return 0


def create_record(ctx, store: Store, data: dict, by: str, cleaner, guard=None) -> str:
    """One new record through every rule of `add`. `guard(w)` runs inside the write transaction and may return an existing
    id instead (the bug mirror's idempotency check)."""
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
    gd_rule(store, None, state, by)
    if store.name == "fwbacklog" and state == "Done" and not record.get("ref"):
        raise Refused("ref: required for Done (a commit sha or a path)")
    record[store.state_field] = state
    with StoreWriter(ctx, store, create=True) as w:
        existing = guard(w) if guard else None
        if existing:
            return existing
        if store.numbered:
            num = w.top + 1
            w.emit("create", str(uuid.uuid4()), dict(record, id=num), by=by, note=note)
            rid = store.fmt_id(num)
        else:
            rid = record["slug"]
            if w.db.execute("SELECT 1 FROM feature WHERE slug=?", (rid,)).fetchone():
                raise Refused("feature %s is already registered: use update" % rid)
            w.emit("create", feature_uid(rid), record, by=by, note=note, event_uid=journal.stable_uid("feature/%s/create" % rid))
    return rid


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
# The journal is the only source today: decisions.csv rows are the human-readable copy, never counted.
COUNTER_SOURCES = []


def journal_counter_events(db, uid: str) -> list:
    out = []
    for ev in db.execute("SELECT * FROM feature_event WHERE uid=? AND type IN ('extra_round','stop_rule') ORDER BY ts, event_uid", (uid,)):
        data = json.loads(ev["data"])
        out.append(dict(data, type=ev["type"], date=data.get("date") or ev["ts"][:10]))
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
    pending = None
    if etype == "extra_round":  # validated and staged before the journal write, moved in after it
        pending = prepare_decision(ctx, a.id, "extra-round", "%s +%d: %s" % (a.counter, n, note))
    with journal_then(pending, "%s extra round %s +%d" % (a.id, a.counter, n), a.id):
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
    pending = prepare_decision(ctx, a.id, "stop-rule", "%s root-caused · extra dispatch: %s" % (a.counter, a.extra_dispatch))
    with journal_then(pending, "%s stop rule %s" % (a.id, a.counter), a.id):
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


def render_lines(ctx, store) -> list:
    db = open_read(ctx, [store])
    rows = db.execute("SELECT * FROM %s ORDER BY %s" % (store.name, order_by(store))).fetchall()
    warn_duplicates(db, store)
    heads = [h for h, _ in store.render_cols]
    out = ["| %s |" % " | ".join(heads), "|%s|" % "|".join("---" for _ in heads)]
    for r in rows:
        cells = []
        for _, col in store.render_cols:
            if col in COUNTERS:
                cells.append("%d/%d" % (r["%s_used" % col], r["%s_cap" % col]))
            else:
                cells.append(md_cell(r[col]))
        out.append("| %s |" % " | ".join(cells))
    return out


def cmd_render(ctx, store, a):
    print("\n".join(render_lines(ctx, store)))
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
    line = "Records: " + " · ".join(parts)
    if not a.json:
        print(line)
        return 0
    # session-start.ps1: the line and the in-flight features in one Python start. ASCII JSON, as counters.
    features = [{"slug": r["slug"], "cp": r["cp"], "next_step": r["next_step"]}
                for r in db.execute("SELECT slug, cp, next_step FROM feature WHERE status='Open' ORDER BY slug")]
    print(json.dumps({"line": line, "open_features": features}))
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
    print(ledger_migrate(ctx))
    return 0


def ledger_migrate(ctx) -> str:
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
        return "migrated %d event(s) from rounds.json (%d new); renamed it %s" % (seen["events"], n, dest.name)
    return "nothing to migrate (%d parked event(s) merged)" % n


# ---------------------------------------------------------------- feature CSV tables

CSV_LIMIT = 1000  # per value; the longest line of the data migrated from markdown is 818
BOM = b"\xef\xbb\xbf"
DECISION_KINDS = ("decision", "extra-round", "stop-rule", "waiver", "accepted-gap")
JOURNAL_KINDS = ("extra-round", "stop-rule")  # written by feature extra-round / stop-rule beside their journal event
RX_NOTE_STATE = re.compile(r"Open|Debt|Promoted:\S.*")
# A cell a spreadsheet would run as a formula when the CSV is opened: refused, never rewritten. "- item" and "--by" stay.
RX_FORMULA = re.compile(r"[=+@\t\r]|-[^ -]")
FORMULA_RULE = "no value starts with = + @ TAB CR, or with - before anything but a space or -"


class Table:
    """One feature-scope CSV table: its file, id prefix and fixed columns. `scope` "feature" lives in
    .workflow/features/<slug>/, "root" in the feature root the registry names."""

    def __init__(self, name, file, prefix, columns, scope, labels, required=(), enums=None, defaults=None, internal=()):
        self.name, self.file, self.prefix, self.scope = name, file, prefix, scope
        self.columns, self.labels = tuple(columns), tuple(labels)
        self.fields = self.columns[1:]
        self.required, self.enums, self.defaults, self.internal = tuple(required), dict(enums or {}), dict(defaults or {}), tuple(internal)
        self.rx_id = re.compile(r"%s-(\d{3,})" % prefix)

    def fmt_id(self, num: int) -> str:
        return "%s-%03d" % (self.prefix, num)


TABLES = {
    "log": Table("log", "log.csv", "L", ("id", "agent", "lane", "changed", "verified", "attempts", "limitations"), "feature",
                 ("ID", "Agent", "Lane", "Changed", "Verified", "Attempts", "Limitations"), required=("agent",)),
    "tests": Table("tests", "tests.csv", "T", ("id", "criterion", "test_id", "mode", "owner", "last_result"), "feature",
                   ("ID", "Criterion", "Test id", "Mode", "Owner", "Last result"), required=("criterion",)),
    "decisions": Table("decisions", "decisions.csv", "D", ("id", "date", "kind", "decision", "cost"), "feature",
                       ("ID", "Date", "Kind", "Decision", "Cost"), required=("kind", "decision"),
                       enums={"kind": DECISION_KINDS}, defaults={"kind": "decision"}),
    "limitations": Table("limitations", "limitations.csv", "LIM", ("id", "date", "text", "accepted_by", "mirrored"), "feature",
                         ("ID", "Date", "Text", "Accepted by", "Mirrored"), required=("text",), internal=("mirrored",)),
    "debt": Table("debt", "DEBT.csv", "DEBT", ("id", "date", "kind", "text", "source", "accepted_by", "next_step", "state"), "root",
                  ("ID", "Date", "Kind", "Text", "Source", "Accepted by", "Next step", "State"), required=("kind", "text"),
                  enums={"kind": ("workaround", "limitation", "accepted-gap"), "state": ("Open", "Paid")}, defaults={"state": "Open"}),
    "notes": Table("notes", "NOTES.csv", "N", ("id", "date", "topic", "text", "anchor", "state"), "root",
                   ("ID", "Date", "Topic", "Text", "Anchor", "State"), required=("text",), defaults={"state": "Open"}),
}


def csv_cleaner(ctx) -> journal.Cleaner:
    names = {c for t in TABLES.values() for c in t.columns}
    return journal.Cleaner(ctx, {n: CSV_LIMIT for n in names}, names)  # every value is one line: it renders into a table cell


def formula_check(field: str, value: str):
    """Refuses a value a spreadsheet would run as a formula. Names the column and the rule, never echoes the value."""
    m = RX_FORMULA.match(value)
    if m:
        lead = {"\t": "a TAB", "\r": "a CR", "-": "- before a character other than a space or -"}.get(m.group(0)[0], m.group(0)[0])
        raise Refused("%s: starts with %s, which a spreadsheet runs as a formula (%s): reword it" % (field, lead, FORMULA_RULE))


def csv_value(cleaner, table: Table, field: str, value, required: bool) -> str:
    """The stored form of one value: enums from their set, the rest through every content rule of the DB stores
    and the formula-prefix rule, on the value as given and as stored (clean() trims)."""
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise Refused("%s: must be a string" % field)
    formula_check(field, value)
    if field in table.enums:
        if value == "":
            if required:
                raise Refused("%s: required, one of %s" % (field, ", ".join(table.enums[field])))
            return ""
        if value not in table.enums[field]:
            raise Refused("%s: must be one of %s" % (field, ", ".join(table.enums[field])))
        return value
    text = cleaner.clean(field, value) if value != "" else ""
    if required and not text:
        raise Refused("%s: required" % field)
    if not text:
        return ""
    formula_check(field, text)
    if field == "date":
        try:
            ok = RX_DATE.fullmatch(text) and dt.date.fromisoformat(text)
        except ValueError:
            ok = False
        if not ok:
            raise Refused("date: expected YYYY-MM-DD")
    elif field == "source" and not RX_SOURCE.fullmatch(text):
        raise Refused("source: expected BUG-####, a feature slug or framework")
    elif table.name == "notes" and field == "state" and not RX_NOTE_STATE.fullmatch(text):
        raise Refused("state: expected Open, Debt or Promoted:<doc>")
    return text


def journal_kind_refusal(kind: str) -> Refused:
    return Refused("kind %s: use records.py feature %s: it writes the journal the counters read, and this row beside it"
                   % (kind, "extra-round" if kind == "extra-round" else "stop-rule"))


def csv_row(table: Table, data: dict, cleaner, internal=False, fill_date=True) -> dict:
    """A new row's values (no id), or a refusal. `internal`: records itself (mirror, migrate) may set any column."""
    if not isinstance(data, dict):
        raise Refused("expected a JSON object")
    if "id" in data:
        raise Refused("id: assigned by the CLI, never given")
    unknown = sorted(set(data) - set(table.fields))
    if unknown:
        raise Refused("unknown field: %s (columns: %s)" % (shown_all(unknown), ", ".join(table.fields)))
    if not internal:
        for f in table.internal:
            if data.get(f) not in (None, ""):
                raise Refused("%s: set by csv mirror, never by hand" % f)
        if table.name == "decisions" and data.get("kind") in JOURNAL_KINDS:
            raise journal_kind_refusal(data["kind"])
    row = {}
    for f in table.fields:
        raw = data.get(f)
        if raw in (None, "") and f in table.defaults:
            raw = table.defaults[f]
        if f == "date" and raw in (None, "") and fill_date:
            raw = today()
        row[f] = csv_value(cleaner, table, f, raw, f in table.required)
    return row


def csv_bytes(table: Table, rows) -> bytes:
    """Header plus rows (dicts or raw lists), LF, UTF-8 with no BOM, RFC 4180 quoting by the csv module. Every new
    value passed csv_value, so none is a formula; a planted one in an old row is written back as it is and csv doctor
    reports it for a hand fix."""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(table.columns)
    for r in rows:
        w.writerow([r.get(c, "") for c in table.columns] if isinstance(r, dict) else r)
    return buf.getvalue().encode("utf-8")


class Pending:
    """A file's new bytes, written beside it and moved in by commit(): atomic, and prepared before a journal write."""

    def __init__(self, path: Path, data: bytes):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.tmp = path.with_name(".%s.%s.tmp" % (path.name, uuid.uuid4().hex[:8]))
        with open(self.tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())

    def commit(self):
        try:
            os.replace(self.tmp, self.path)
        except BaseException:
            self.discard()
            raise

    def discard(self):
        try:
            self.tmp.unlink()
        except FileNotFoundError:
            pass


def write_atomic(path: Path, data: bytes):
    Pending(path, data).commit()


class CsvFile:
    """One table file as read: its rows, and every problem a reader or a merge could leave in it."""

    def __init__(self, table: Table, path: Path, rel: str):
        self.table, self.path, self.rel = table, path, rel
        self.records = []  # (line, cells) per data row, as parsed
        self.problems = []  # (kind, text): kind is "block" (writes refused), "fix" (doctor --fix repairs) or "dup"
        self.readable = True
        self.exists = path.exists()
        if self.exists:
            self.load(path.read_bytes())

    def problem(self, kind, text):
        self.problems.append((kind, "%s: %s" % (self.rel, text)))

    def load(self, raw: bytes):
        body = raw
        if raw.startswith(BOM):
            self.problem("fix", "UTF-8 BOM")
            body = raw[len(BOM):]
        if b"\r" in body:
            self.problem("fix", "CRLF line endings")
        try:
            text = body.decode("utf-8")
        except UnicodeDecodeError as ex:
            self.problem("block", "not UTF-8 (byte %d)" % ex.start)
            self.readable = False
            return
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        parsed, last = [], 0
        try:
            for cells in reader:
                parsed.append((last + 1, cells))
                last = reader.line_num
        except csv.Error as ex:
            self.problem("block", "line %d: %s" % (reader.line_num, ex))
            self.readable = False
            return
        if not parsed:
            self.problem("fix", "empty file: never written by the CLI; doctor --fix deletes it")
            return
        header = parsed[0][1]
        if tuple(header) != self.table.columns:
            self.problem("block", "header is %s, expected %s" % (shown(",".join(header), 200), ",".join(self.table.columns)))
            self.readable = False
            return
        seen = {}
        for line, cells in parsed[1:]:
            if not cells:
                self.problem("fix", "line %d: blank line" % line)
                continue
            if tuple(cells) == self.table.columns:
                self.problem("fix", "line %d: repeated header row (a union merge of two new files)" % line)
                continue
            self.records.append((line, cells))
            if len(cells) != len(self.table.columns):
                self.problem("block", "line %d: %d values, expected %d" % (line, len(cells), len(self.table.columns)))
                continue
            for col, v in zip(self.table.columns, cells):
                if "\n" in v or "\r" in v:
                    self.problem("block", "line %d: a line break in %s" % (line, col))
            if not self.table.rx_id.fullmatch(cells[0]):
                self.problem("block", "line %d: bad id %s, expected %s-###" % (line, shown(cells[0]), self.table.prefix))
            seen.setdefault(cells[0], []).append(line)
        for rid, lines in seen.items():
            if len(lines) > 1:
                self.problem("dup", "duplicate id %s on lines %s (a union merge): doctor --fix renumbers the later rows"
                             % (shown(rid), ", ".join(map(str, lines))))
        if not self.records:
            self.problem("fix", "header-only file: never written by the CLI; doctor --fix deletes it")

    def rows(self) -> list:
        n = len(self.table.columns)
        return [dict(zip(self.table.columns, cells)) for _, cells in self.records if len(cells) == n]

    def top(self) -> int:
        nums = [int(m.group(1)) for _, cells in self.records if cells and (m := self.table.rx_id.fullmatch(cells[0]))]
        return max(nums, default=0)

    def refuse_blocking(self):
        blocking = [t for k, t in self.problems if k == "block"]
        if blocking:
            raise Refused("\n".join(blocking + ["writes refused: run records.py csv doctor %s --feature <slug>, fix those lines by hand" % self.table.name]))

    def with_row(self, row: dict) -> tuple[str, bytes]:
        """(the new id, the file's new bytes): the old rows, normalized, then the new one."""
        self.refuse_blocking()
        rid = self.table.fmt_id(self.top() + 1)
        return rid, csv_bytes(self.table, self.rows() + [dict(row, id=rid)])

    def append(self, row: dict) -> str:
        rid, data = self.with_row(row)
        write_atomic(self.path, data)
        self.__init__(self.table, self.path, self.rel)
        return rid


def parse_slug(text) -> str:
    if not isinstance(text, str) or not RX_SLUG.fullmatch(text) or len(text) > 100:
        raise Refused("bad slug '%s': expected kebab-case, a-z 0-9 and -" % shown(text))
    return text


def registry_row(ctx, slug: str):
    db = open_read(ctx, [STORES["feature"]])
    return db.execute("SELECT * FROM feature WHERE slug=?", (slug,)).fetchone()


def safe_root(ctx, value: str) -> str:
    """A registry feature_root as a path relative to the project root, or a refusal: never absolute, never above the root."""
    rel = value.strip().strip("`").strip().replace("\\", "/").strip("/")
    parts = rel.split("/")
    if not rel or ":" in rel or any(p in ("", ".", "..") for p in parts):
        raise Refused("feature_root %s: expected a folder relative to the project root, like Assets/_Project/Scripts/Shop" % shown(value, 200))
    target = (ctx.root / rel).resolve()
    if target != ctx.root.resolve() and ctx.root.resolve() not in target.parents:
        raise Refused("feature_root %s resolves outside the project root" % shown(value, 200))
    return rel


def feature_root_rel(ctx, slug: str) -> str:
    row = registry_row(ctx, slug)
    if row is None:
        raise Refused("feature %s is not in the registry, so its feature root is unknown: register it with records.py --root %s "
                      "feature add, stdin {\"slug\": \"%s\", \"feature_root\": \"<folder>\"}" % (slug, ctx.root, slug))
    if not row["feature_root"]:
        raise Refused("feature %s has no feature_root: set it with records.py --root %s feature update %s, stdin "
                      "{\"feature_root\": \"<folder relative to the project root>\"}" % (slug, ctx.root, slug))
    return safe_root(ctx, row["feature_root"])


def table_rel(ctx, table: Table, slug: str) -> str:
    slug = parse_slug(slug)
    if table.scope == "root":
        return "%s/%s" % (feature_root_rel(ctx, slug), table.file)
    return ".workflow/features/%s/%s" % (slug, table.file)


def open_table(ctx, table: Table, slug: str, check_feature=True) -> CsvFile:
    rel = table_rel(ctx, table, slug)
    if check_feature and table.scope == "feature" and registry_row(ctx, slug) is None and not ctx.exists(".workflow/features/%s.md" % slug):
        raise Refused("feature %s: no registry row and no .workflow/features/%s.md: check the slug" % (slug, slug))
    return CsvFile(table, ctx.file(rel), rel)


def prepare_decision(ctx, slug: str, kind: str, text: str) -> Pending:
    """The decisions.csv row of a journal-backed decision, staged beside the file before the journal write."""
    table = TABLES["decisions"]
    f = open_table(ctx, table, slug, check_feature=False)
    row = csv_row(table, {"kind": kind, "decision": text}, csv_cleaner(ctx), internal=True)
    _, data = f.with_row(row)
    return Pending(f.path, data)


@contextlib.contextmanager
def journal_then(pending: Pending | None, what: str, slug: str):
    """The journal write runs inside; the staged CSV row is moved in only after it committed."""
    try:
        yield
    except BaseException:
        if pending:
            pending.discard()
        raise
    if pending:
        try:
            pending.commit()
        except OSError as ex:
            raise Refused("%s is in the journal, so the counters are right, but the decisions.csv row was not written (%s): "
                          "add it with records.py csv add decisions --feature %s, kind decision" % (what, ex, slug)) from None


def md_cells(table: Table, row: dict) -> str:
    return "| %s |" % " | ".join(md_cell(row.get(c, "")) for c in table.columns)


def csv_render_lines(table: Table, rows) -> list:
    return (["| %s |" % " | ".join(table.labels), "|%s|" % "|".join("---" for _ in table.labels)]
            + [md_cells(table, r) for r in rows])


def cmd_csv_add(ctx, a):
    ctx.require_writable()
    table = TABLES[a.table]
    cleaner = csv_cleaner(ctx)
    data = journal.read_stdin_json(True)
    row = csv_row(table, data, cleaner)
    f = open_table(ctx, table, a.feature)
    rid = f.append(row)
    cleaner.report()
    print(rid)
    return 0


def cmd_csv_update(ctx, a):
    ctx.require_writable()
    table = TABLES[a.table]
    cleaner = csv_cleaner(ctx)
    data = journal.read_stdin_json(True)
    if "id" in data:
        raise Refused("id: never updated")
    unknown = sorted(set(data) - set(table.fields))
    if unknown:
        raise Refused("unknown field: %s (columns: %s)" % (shown_all(unknown), ", ".join(table.fields)))
    for f in table.internal:
        if f in data:
            raise Refused("%s: set by csv mirror, never by hand" % f)
    f = open_table(ctx, table, a.feature)
    f.refuse_blocking()
    rows = f.rows()
    hits = [r for r in rows if r["id"] == a.id]
    if not hits:
        raise Refused("%s not found in %s" % (shown(a.id), f.rel))
    if len(hits) > 1:
        raise Refused("duplicate id %s in %s: run records.py csv doctor %s --feature %s --fix" % (a.id, f.rel, table.name, a.feature))
    row = hits[0]
    if table.name == "decisions" and "kind" in data and data["kind"] != row["kind"]:
        for kind in (data["kind"], row["kind"]):  # into or out of a journal-backed kind: the journal would disagree
            if kind in JOURNAL_KINDS:
                raise journal_kind_refusal(kind)
    changes = {}
    for field, value in data.items():
        v = csv_value(cleaner, table, field, value, field in table.required)
        if v != row[field]:
            changes[field] = v
    if changes:
        row.update(changes)
        write_atomic(f.path, csv_bytes(table, rows))
    cleaner.report()
    print("%s updated: %s" % (a.id, ", ".join(sorted(changes))) if changes else "%s: no change" % a.id)
    return 0


def cmd_csv_list(ctx, a):
    table = TABLES[a.table]
    f = open_table(ctx, table, a.feature)
    f.refuse_blocking()
    rows = f.rows()
    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return 0
    if not rows:
        print("no rows")
        return 0
    print(" | ".join(table.labels))
    for r in rows:
        print(" | ".join(r[c] or "-" for c in table.columns))
    return 0


def cmd_csv_render(ctx, a):
    table = TABLES[a.table]
    f = open_table(ctx, table, a.feature)
    f.refuse_blocking()
    print("\n".join(csv_render_lines(table, f.rows())))
    return 0


def value_problems(f: CsvFile, cleaner) -> list:
    """Each stored value against the write rules: one that a write would refuse, redact or trim is a problem."""
    out = []
    n = len(f.table.columns)
    for line, cells in f.records:
        if len(cells) != n:
            continue
        for col, v in zip(f.table.columns[1:], cells[1:]):
            try:
                stored = csv_value(cleaner, f.table, col, v, col in f.table.required)
            except Refused as ex:
                out.append("%s: line %d: %s" % (f.rel, line, ex))
                continue
            if stored != v:
                out.append("%s: line %d: %s is not in its stored form (a write would redact or trim it)" % (f.rel, line, col))
    return out


def repaired_csv(f: CsvFile) -> tuple[bytes | None, list]:
    """The file with later duplicates renumbered past the high water, merge-left header rows and blank lines dropped,
    BOM and CRLF gone. Malformed rows are written back as they are: reported, never guessed at."""
    top, seen, done, out = f.top(), set(), [], []
    for line, cells in f.records:
        cells = list(cells)
        if cells and f.table.rx_id.fullmatch(cells[0]):
            if cells[0] in seen:
                top += 1
                done.append("%s: line %d: renumbered %s to %s" % (f.rel, line, cells[0], f.table.fmt_id(top)))
                cells[0] = f.table.fmt_id(top)
            seen.add(cells[0])
        out.append(cells)
    return (csv_bytes(f.table, out) if out else None), done


def feature_tables(ctx, slug: str, name: str | None) -> tuple[list, list]:
    """(the tables doctor checks, info lines). A root table with no feature_root is skipped unless asked for by name."""
    if name:
        return [TABLES[name]], []
    tables, info = [], []
    for t in TABLES.values():
        if t.scope == "root":
            try:
                feature_root_rel(ctx, slug)
            except Refused:
                info.append("%s: skipped, feature %s has no feature root in the registry" % (t.file, slug))
                continue
        tables.append(t)
    return tables, info


def cmd_csv_doctor(ctx, a):
    slug = parse_slug(a.feature)
    if a.fix:
        ctx.require_writable()
    try:
        cleaner = csv_cleaner(ctx)
    except Refused as ex:
        raise Refused("csv doctor: values cannot be checked: %s" % ex) from None
    tables, info = feature_tables(ctx, slug, a.table)
    problems = []
    for t in tables:
        f = open_table(ctx, t, slug, check_feature=False)
        if a.fix and f.exists and f.readable and any(k in ("fix", "dup") for k, _ in f.problems):
            data, done = repaired_csv(f)
            if data is None:
                f.path.unlink()
                done = ["%s: deleted, it held no rows" % f.rel]
            else:
                write_atomic(f.path, data)
            for line in done:
                print(line)
            f = CsvFile(t, f.path, f.rel)
        problems += [text for _, text in f.problems] + (value_problems(f, cleaner) if f.readable else [])
    for line in info:
        print(line)
    if problems:
        raise Refused("\n".join(problems))
    print("csv doctor: clean (%s)" % ", ".join(t.name for t in tables))
    return 0


def cmd_csv_mirror(ctx, a):
    print(mirror_limitations(ctx, parse_slug(a.feature)))
    return 0


def mirror_limitations(ctx, slug: str) -> str:
    """Each limitations.csv row with `mirrored` empty becomes an accepted-gap row of the feature root's DEBT.csv. A row
    already in DEBT.csv (same source and text, from a run cut short) is reused, never copied twice."""
    ctx.require_writable()
    cleaner = csv_cleaner(ctx)
    lim = open_table(ctx, TABLES["limitations"], slug)
    debt = open_table(ctx, TABLES["debt"], slug)
    lim.refuse_blocking()
    debt.refuse_blocking()
    todo = [r for r in lim.rows() if not r["mirrored"]]
    if not todo:
        return "nothing to mirror: every limitation of %s is mirrored" % slug
    rows = debt.rows()
    top = debt.top()
    done = []
    for r in todo:
        hit = [d["id"] for d in rows if d["source"] == slug and d["kind"] == "accepted-gap" and d["text"] == r["text"]]
        if hit:
            r["mirrored"] = hit[0]
        else:
            top += 1
            new = csv_row(TABLES["debt"], {"date": r["date"], "kind": "accepted-gap", "text": r["text"], "source": slug,
                                           "accepted_by": r["accepted_by"], "state": "Open"}, cleaner, internal=True)
            new["id"] = TABLES["debt"].fmt_id(top)
            rows.append(new)
            r["mirrored"] = new["id"]
        done.append("%s -> %s" % (r["id"], r["mirrored"]))
    write_atomic(debt.path, csv_bytes(TABLES["debt"], rows))
    all_lim = lim.rows()
    for row in all_lim:
        for r in todo:
            if row["id"] == r["id"]:
                row["mirrored"] = r["mirrored"]
    write_atomic(lim.path, csv_bytes(TABLES["limitations"], all_lim))
    return "mirrored %d limitation(s) into %s: %s" % (len(done), debt.rel, ", ".join(done))


# ---------------------------------------------------------------- bug -> debt mirror

MIRRORED_STATUSES = ("Won't fix", "Accepted")


def mirror_bug(ctx, bug_id: str, title: str, feature, by: str, note, date: str) -> str:
    """A bug moved to Won't fix or Accepted becomes debt: a DEBT.csv row in its feature's root when the registry names one,
    else a `debt` record. Idempotent by the bug id: a second terminal-accepted move adds nothing."""
    ctx.require_writable()
    cleaner = csv_cleaner(ctx)
    root = None
    if isinstance(feature, str) and RX_SLUG.fullmatch(feature) and len(feature) <= 100:
        row = registry_row(ctx, feature)
        if row is not None and row["feature_root"]:
            root = safe_root(ctx, row["feature_root"])
    if root:
        table = TABLES["debt"]
        rel = "%s/%s" % (root, table.file)
        f = CsvFile(table, ctx.file(rel), rel)
        f.refuse_blocking()
        hit = [r["id"] for r in f.rows() if r["source"] == bug_id]
        if hit:
            return "debt mirror: %s is already %s in %s" % (bug_id, hit[0], rel)
        rid = f.append(csv_row(table, {"date": date, "kind": "accepted-gap", "text": title, "source": bug_id, "accepted_by": by,
                                       "next_step": note or "", "state": "Open"}, cleaner, internal=True))
        return "debt mirror: %s added as %s in %s" % (bug_id, rid, rel)
    store = STORES["debt"]
    found = []

    def already(w):  # inside the write transaction: two mirrors of one bug cannot both add
        hit = w.db.execute("SELECT id FROM debt WHERE source=? ORDER BY %s LIMIT 1" % order_by(store), (bug_id,)).fetchone()
        if hit:
            found.append(hit[0])
        return hit[0] if hit else None

    rid = create_record(ctx, store, {"text": title, "source": bug_id, "accepted_by": by, "next_step": note or None, "date": date},
                        by, cleaner_for(ctx, store), guard=already)
    if found:
        return "debt mirror: %s is already %s" % (bug_id, rid)
    return "debt mirror: %s added as %s (.workflow/debt.jsonl)" % (bug_id, rid)


def load_bugs():
    """bugs.py beside this skill, by path, for bug-mirror's repair run. -I removes the script dir from sys.path."""
    path = Path(__file__).resolve().parents[2] / "bugs" / "scripts" / "bugs.py"
    if not path.exists():
        raise Refused("%s is missing, so the bug cannot be read" % path)
    spec = importlib.util.spec_from_file_location("records_bugs", path)
    module = importlib.util.module_from_spec(spec)
    keep, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = keep
    return module


def cmd_bug_mirror(ctx, a):
    """The repair path bugs.py names when its own mirror failed after the move committed."""
    bugs = load_bugs()
    bctx = bugs.Ctx(str(ctx.root))
    db = bugs.open_read(bctx)
    row = bugs.live_bug(db, a.id)
    if row["status"] not in MIRRORED_STATUSES:
        raise Refused("%s is %s: only a bug in Won't fix or Accepted is mirrored into debt" % (row["id"], row["status"]))
    by, note, ts = "main GD", None, row["updated_at"]
    for ev in db.execute("SELECT * FROM bug_event WHERE bug_uid=? AND type='status' ORDER BY ts DESC, event_uid DESC", (row["uid"],)):
        if json.loads(ev["data"]).get("to") == row["status"]:
            by, note, ts = ev["by_who"] or by, ev["note"], ev["ts"]
            break
    print(mirror_bug(ctx, row["id"], row["title"], row["feature"], by, note, ts[:10]))
    return 0


# ---------------------------------------------------------------- migrate --from-md

RX_MD_SEP = re.compile(r"\|(\s*:?-{3,}:?\s*\|)+")
RX_FW_STATE = re.compile(r"(Open|Done|Recorded \((?:main )?GD decision\)|Recorded|Deferred)(?:\s*:\s*(.*))?")
RX_HEADER = re.compile(r"- (Status|CP|Session|Size|Rounds|Profile|Feature root|Branch|Assemblies|Build mode|Worktrees):\s*(.*)")
RX_EXTRA = re.compile(r"(?i)extra round:\s*(review|qa|rework)\s*\+(\d+)")
RX_LEAD_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})\s+(.*)")
RX_ANY_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
DECISION_HEADINGS = ("## main gd decisions", "## gd decisions")
MIGRATED_SECTIONS = {"## log": "log", "## tests": "tests", "## known limitations": "limitations",
                     "## main gd decisions": "decisions", "## gd decisions": "decisions"}
LOG_HEADS = {"agent": "agent", "lane": "lane", "changed": "changed", "verified": "verified"}
TEST_HEADS = {"criterion": "criterion", "test id": "test_id", "mode": "mode", "owner": "owner", "last result": "last_result"}
MIGRATE_BY = "migrate"
MIGRATE_ERRORS = 50  # problem lines listed per run


def at(rel: str, line: int, ex) -> Refused:
    return Refused("%s:%d: %s" % (rel, line, ex))


@contextlib.contextmanager
def located(rel: str, line: int):
    try:
        yield
    except Refused as ex:
        raise at(rel, line, ex) from None


def md_split(line: str, rendered=False) -> list:
    """A markdown table row's cells. `\\|` is a pipe inside a cell; with `rendered`, `\\\\` is one backslash too
    (the inverse of md_cell, for reading back this CLI's own render)."""
    s = line.strip()
    cells, cur, i, ended = [], [], 0, False
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s) and (s[i + 1] == "|" or (rendered and s[i + 1] == "\\")):
            cur.append(s[i + 1])
            i += 2
            ended = False
            continue
        if c == "|":
            cells.append("".join(cur).strip())
            cur, ended = [], True
        else:
            cur.append(c)
            ended = False
        i += 1
    if not ended:
        cells.append("".join(cur).strip())
    if s.startswith("|"):
        cells = cells[1:]
    return cells


def md_lines(raw: bytes, rel: str) -> tuple[list, str, bool]:
    """(lines without their ends, the line end the file uses, whether it had a BOM)."""
    bom = raw.startswith(BOM)
    try:
        text = raw[len(BOM):].decode("utf-8") if bom else raw.decode("utf-8")
    except UnicodeDecodeError as ex:
        raise at(rel, raw[:ex.start].count(b"\n") + 1, "not UTF-8 (byte %d)" % ex.start) from None
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.replace("\r\n", "\n").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines, nl, bom


def md_sections(lines) -> list:
    """(heading line index or None, body start, body end) per `## ` section; the part before the first one has None."""
    heads = [i for i, line in enumerate(lines) if line.startswith("## ")]
    out = [(None, 0, heads[0] if heads else len(lines))]
    for k, h in enumerate(heads):
        out.append((h, h + 1, heads[k + 1] if k + 1 < len(heads) else len(lines)))
    return out


def md_tables(lines, start, end) -> list:
    """[(header line index, header cells, [(line index, cells)])] in lines[start:end]. Blank lines between row groups
    stay inside the table (hand-written logs use them); a row line followed by a separator starts a new table."""

    def starts_table(k):
        return lines[k].lstrip().startswith("|") and k + 1 < end and RX_MD_SEP.fullmatch(lines[k + 1].strip()) is not None

    out, i = [], start
    while i < end:
        if starts_table(i):
            rows, j = [], i + 2
            while j < end:
                if lines[j].lstrip().startswith("|") and not starts_table(j):
                    rows.append((j, md_split(lines[j])))
                    j += 1
                    continue
                k = j
                while k < end and not lines[k].strip():
                    k += 1
                if k > j and k < end and lines[k].lstrip().startswith("|") and not starts_table(k):
                    j = k
                    continue
                break
            out.append((i, md_split(lines[i]), rows))
            i = j
            continue
        i += 1
    return out


def md_bullets(lines, start, end, tables=()) -> tuple[list, list]:
    """([(line index, text)], [kept line indexes]): a bullet with its indented continuation lines joined by one space;
    blank lines and the lines of `tables` (already migrated) dropped; every other line kept."""
    skip = set()
    for h, _, rows in tables:
        skip |= {h, h + 1} | {j for j, _ in rows}
    bullets, kept, cur = [], [], None
    for i in range(start, end):
        line = lines[i]
        if i in skip:
            cur = None
            continue
        if line.startswith("- ") or line.startswith("* "):
            cur = [i, line[2:].strip()]
            bullets.append(cur)
        elif not line.strip():
            cur = None
        elif cur is not None and line[:1] in (" ", "\t"):
            cur[1] = (cur[1] + " " + line.strip()).strip()
        else:
            cur = None
            kept.append(i)
    return [(i, t) for i, t in bullets], kept


class Migration:
    """Every write lands in a staging copy first (StagedCtx); verify() reads each target back; swap() moves the staged
    files over the root and renames the sources. Any refusal before the swap leaves the root as it was."""

    def __init__(self, real: Ctx, dry_run: bool):
        self.real, self.dry_run = real, dry_run
        self.stage = Path(tempfile.mkdtemp(prefix="records-migrate-"))
        self.ctx = StagedCtx(real, self.stage, dry_run)
        self.stamp = utc_stamp()
        self.renames = []  # (source rel, migrated rel)
        self.report = []
        self.checks = []  # (label, [expected rows], rendered lines fn, columns)
        self.counter_checks = []  # (rel, line, slug, legacy counters)
        self.ledger_events = None
        self.errors = []

    # ------------------------------------------------------------ helpers
    def source(self, rel: str) -> bytes | None:
        path = self.real.root / rel
        raw = path.read_bytes() if path.is_file() else None
        if raw is not None:
            self.ctx.copied[rel] = sha(raw)
        return raw

    def unchanged(self):
        """Every root file read or copied in still holds the bytes read: a session writing meanwhile is never overwritten."""
        for rel, h in sorted(self.ctx.copied.items()):
            path = self.real.root / rel
            if not path.is_file() or sha(path.read_bytes()) != h:
                raise Refused("%s changed while the migration ran: rerun it" % rel)

    def rename_later(self, rel: str):
        p = Path(rel)
        self.renames.append((rel, (p.parent / ("%s.migrated-%s%s" % (p.stem, self.stamp, p.suffix))).as_posix()))

    @contextlib.contextmanager
    def soft(self, rel: str, line: int):
        """A row's refusal is collected and the next row is read: one run lists every line to fix by hand."""
        try:
            yield
        except Refused as ex:
            self.errors.append(str(at(rel, line, ex)))

    def step(self, fn, *args):
        """A source's refusal is collected and the next source is read."""
        try:
            fn(*args)
        except (Refused, Corrupt) as ex:
            self.errors.append(str(ex))

    def expect_csv(self, label, table, rel, rows):
        self.checks.append((label, "csv", (table, rel), 0, rows))

    # ------------------------------------------------------------ framework backlog
    def fwbacklog(self):
        rel = ".workflow/framework-backlog.md"
        raw = self.source(rel)
        if raw is None:
            self.report.append("%s: absent" % rel)
            return
        lines, _, _ = md_lines(raw, rel)
        rows, skipped = [], 0
        for h, start, end in md_sections(lines):
            wanted = h is None or lines[h].strip().lower() == "## deferred and recorded"
            for hi, header, trs in md_tables(lines, start, end):
                if not (wanted and [c.lower() for c in header] == ["item", "state"]):
                    skipped += len(trs)
                    continue
                for j, cells in trs:
                    with self.soft(rel, j + 1):
                        if len(cells) != 2:
                            raise Refused("%d cells, the table has 2" % len(cells))
                        m = RX_FW_STATE.fullmatch(cells[1])
                        if not m:
                            raise Refused("state %s: expected Open, Done: <ref>, Recorded, Recorded (main GD decision) or Deferred" % shown(cells[1], 60))
                        state = "Recorded (main GD decision)" if m.group(1).startswith("Recorded (") else m.group(1)
                        ref = (m.group(2) or "").strip() or None
                        if state == "Done" and not ref:
                            raise Refused("Done needs its ref: Done: <commit sha or path>")
                        rows.append((j, cells[0], state, ref))
        store = STORES["fwbacklog"]
        cleaner = cleaner_for(self.ctx, store)
        expected = []
        with StoreWriter(self.ctx, store, create=True) as w:
            for j, item, state, ref in rows:
                with self.soft(rel, j + 1):
                    record = {"item": clean_field(cleaner, store, "item", item, True), "state": state}
                    r = clean_field(cleaner, store, "ref", ref, False) if ref else None
                    if r:
                        record["ref"] = r
                    num = w.top + 1
                    w.emit("create", str(uuid.uuid4()), dict(record, id=num), by=MIGRATE_BY, note="migrated from %s:%d" % (rel, j + 1))
                    expected.append((rel, j, {"ID": store.fmt_id(num), "Item": record["item"], "State": state, "Ref": record.get("ref") or ""}))
        self.checks.append(("fwbacklog", "store", store, None, expected))
        self.rename_later(rel)
        self.report.append("%s: %d rows -> fwbacklog; %d table rows in other sections kept in the renamed file" % (rel, len(rows), skipped))

    # ------------------------------------------------------------ game backlog
    def backlog(self):
        rel = ".workflow/backlog.md"
        raw = self.source(rel)
        if raw is None:
            self.report.append("%s: absent" % rel)
            return
        lines, _, _ = md_lines(raw, rel)
        want = ["#", "feature", "milestone", "size", "risk", "depends on", "status"]
        tables = [t for t in md_tables(lines, 0, len(lines)) if [c.lower() for c in t[1]] == want]
        if not tables:
            raise at(rel, 1, "no table with the columns | # | Feature | Milestone | Size | Risk | Depends on | Status |")
        store = STORES["backlog"]
        cleaner = cleaner_for(self.ctx, store)
        expected, suffixes = [], 0
        with StoreWriter(self.ctx, store, create=True) as w:
            if w.db.execute("SELECT COUNT(*) FROM backlog").fetchone()[0]:
                raise Refused("%s: .workflow/backlog.jsonl already holds records: their numbers could collide, move the md rows by hand" % rel)
            seen = set()
            for j, cells in tables[0][2]:
                with self.soft(rel, j + 1):
                    if len(cells) != 7:
                        raise Refused("%d cells, the table has 7" % len(cells))
                    num_text = cells[0].lstrip("#").strip()
                    if not num_text.isdigit() or int(num_text) < 1 or int(num_text) in seen:
                        raise Refused("# %s: expected a new positive number" % shown(cells[0]))
                    num = int(num_text)
                    seen.add(num)
                    m = re.match(r"(?i)(todo|in progress|done|dropped)\b\s*(.*)", cells[6])
                    if not m:
                        raise Refused("status %s: expected todo, in progress, done or dropped" % shown(cells[6], 60))
                    suffixes += bool(m.group(2).strip())
                    record = {"status": m.group(1).lower()}
                    for col, value in (("feature", cells[1]), ("milestone", cells[2]), ("size", cells[3]), ("risk", cells[4])):
                        v = clean_field(cleaner, store, col, value, store.fields[col].required)
                        if v is not None:
                            record[col] = v
                    deps = cells[5].replace("#", "").strip()
                    if deps not in ("", "-", "—", "none"):
                        record["depends_on"] = clean_field(cleaner, store, "depends_on", deps, False)
                    w.emit("create", str(uuid.uuid4()), dict(record, id=num), by=MIGRATE_BY, note="migrated from %s:%d" % (rel, j + 1))
                    expected.append((rel, j, {"#": str(num), "Feature": record["feature"], "Milestone": record["milestone"], "Size": record["size"],
                                              "Risk": record.get("risk") or "", "Depends on": record.get("depends_on") or "", "Status": record["status"]}))
        expected.sort(key=lambda e: int(e[2]["#"]))
        self.checks.append(("backlog", "store", store, None, expected))
        self.rename_later(rel)
        self.report.append("%s: %d rows -> backlog%s" % (rel, len(expected), "; %d status suffix(es) like (`/feature <slug>`) dropped" % suffixes if suffixes else ""))

    # ------------------------------------------------------------ project debt
    def project_debt(self):
        rel = ".workflow/DEBT.md"
        raw = self.source(rel)
        if raw is None:
            self.report.append("%s: absent" % rel)
            return
        lines, _, _ = md_lines(raw, rel)
        bullets, kept = md_bullets(lines, 0, len(lines))
        store = STORES["debt"]
        cleaner = cleaner_for(self.ctx, store)
        expected = []
        with StoreWriter(self.ctx, store, create=True) as w:
            for j, text in bullets:
                with self.soft(rel, j + 1):
                    record = debt_bullet(text)
                    for col in ("text", "source", "next_step", "accepted_by", "date"):
                        v = clean_field(cleaner, store, col, record.get(col), store.fields[col].required)
                        if v is None:
                            record.pop(col, None)
                        else:
                            record[col] = v
                    record["state"] = "Open"
                    num = w.top + 1
                    w.emit("create", str(uuid.uuid4()), dict(record, id=num), by=MIGRATE_BY, note="migrated from %s:%d" % (rel, j + 1))
                    expected.append((rel, j, {"ID": store.fmt_id(num), "Date": record["date"], "Source": record["source"], "Text": record["text"],
                                              "Next step": record.get("next_step") or "", "Accepted by": record["accepted_by"], "State": "Open"}))
        self.checks.append(("debt", "store", store, None, expected))
        self.rename_later(rel)
        self.report.append("%s: %d bullets -> debt; %d other lines kept in the renamed file" % (rel, len(bullets), len(kept)))

    # ------------------------------------------------------------ feature files
    def features(self):
        folder = self.real.root / ".workflow" / "features"
        files = sorted(p for p in folder.glob("*.md") if not p.name.endswith(".spec.md") and ".migrated-" not in p.name) if folder.is_dir() else []
        if not files:
            self.report.append(".workflow/features/: no feature files")
        for p in files:
            self.step(self.feature, p)

    def feature(self, path: Path):
        rel = ".workflow/features/%s" % path.name
        slug = path.stem
        lines, nl, bom = md_lines(self.source(rel), rel)
        if any(line.startswith("- State: records.py feature show") for line in lines):
            self.report.append("%s: already migrated, skipped" % rel)
            return
        with located(rel, 1):
            parse_slug(slug)
        sections = md_sections(lines)
        # -- the header lines
        header_end = sections[0][2]
        fields, header_lines, rounds, field_line = {}, [], {}, {}
        status, rounds_line, size_line = None, None, None
        for i in range(0, header_end):
            m = RX_HEADER.fullmatch(lines[i].rstrip())
            if not m:
                continue
            header_lines.append(i)
            key, value = m.group(1), m.group(2).strip()
            before = set(fields)
            with located(rel, i + 1):
                header_value(fields, key, value)
            field_line.update({f: i for f in set(fields) - before})
            if key == "Status":
                status = value
            elif key == "Rounds":
                rounds_line, rounds = i, {c: re.search(r"(?i)\b%s\s*:?\s*(\d+)\s*/\s*(\d+)" % c, value) for c in COUNTERS}
            elif key == "Size":
                size_line = i
        if status is None:
            raise at(rel, 1, "no - Status: line: the registry needs Open, Closed or Abandoned")
        # -- sections
        decisions, log_rows, test_rows, limitations, stops = [], [], [], [], []
        rewrite = {}  # heading index -> (table name, kept line indexes)
        for h, start, end in sections:
            if h is None:
                continue
            name = MIGRATED_SECTIONS.get(lines[h].strip().lower())
            tables = md_tables(lines, start, end)
            if name in ("log", "tests"):
                migrated = tables[:1]
                skip = set()
                if migrated:
                    rows = table_rows(rel, lines, migrated[0], LOG_HEADS if name == "log" else TEST_HEADS, name)
                    (log_rows if name == "log" else test_rows).extend(rows)
                    skip = {migrated[0][0], migrated[0][0] + 1} | {j for j, _ in migrated[0][2]}
                rewrite[h] = (name, [i for i in range(start, end) if i not in skip and lines[i].strip()])
            elif name in ("decisions", "limitations"):
                bullets, kept = md_bullets(lines, start, end)
                for j, text in bullets:
                    if text.startswith("Stop rule:"):
                        stops.append((j, text))
                    elif name == "decisions":
                        decisions.append((j, text))
                    else:
                        limitations.append((j, text))
                rewrite[h] = (name, kept)
            else:
                for j, text in md_bullets(lines, start, end)[0]:
                    if text.startswith("Stop rule:"):  # the hook matched it anywhere: its counter effect moves to the journal
                        stops.append((j, text))
                        self.report.append("%s:%d: a stop rule line outside the migrated sections: migrated, and left in place" % (rel, j + 1))
        open_feature = fields.get("status") == "Open"
        legacy = legacy_counters(lines, [s for s in sections if s[0] is not None and lines[s[0]].strip().lower() in DECISION_HEADINGS])
        # -- the registry record and its journal events
        store = STORES["feature"]
        cleaner = cleaner_for(self.ctx, store)
        record = {"slug": slug}
        for key, value in fields.items():
            if key == "status":
                continue
            with located(rel, field_line[key] + 1):
                v = clean_field(cleaner, store, key, value, False)
            if v is not None:
                record[key] = v
        record["status"] = fields["status"]
        events = {"round": 0, "extra_round": 0, "stop_rule": 0}
        with StoreWriter(self.ctx, store, create=True) as w:
            if w.db.execute("SELECT 1 FROM feature WHERE slug=?", (slug,)).fetchone():
                raise at(rel, 1, "feature %s is already in the registry: the header is migrated once; remove its header lines by hand" % slug)
            uid = feature_uid(slug)
            w.emit("create", uid, record, by=MIGRATE_BY, note="migrated from %s" % rel, event_uid=journal.stable_uid("feature/%s/create" % slug))
            for c in COUNTERS:
                m = rounds.get(c)
                if m and int(m.group(1)):
                    with located(rel, rounds_line + 1):
                        n = int(m.group(1))
                        if n > journal.MAX_COUNT:
                            raise Refused("%s used %d: more than %d" % (c, n, journal.MAX_COUNT))
                    w.emit("round", uid, {"counter": c, "n": n}, by=MIGRATE_BY, note="Rounds line of %s" % rel)
                    events["round"] += 1
            for j, text in decisions:
                for m in RX_EXTRA.finditer(text):
                    with self.soft(rel, j + 1):
                        n = int(m.group(2))
                        if not 1 <= n <= journal.MAX_COUNT:
                            raise Refused("extra round +%d: expected 1 to %d" % (n, journal.MAX_COUNT))
                    w.emit("extra_round", uid, {"counter": m.group(1).lower(), "n": n}, by=MIGRATE_BY, note="main GD decision at %s:%d" % (rel, j + 1))
                    events["extra_round"] += 1
            for j, text in stops:
                for c in COUNTERS:
                    if re.search(r"(?i)\b%s\b" % c, text):
                        m = re.search(r"(?i)extra dispatch:\s*(unused|used)\b", text)
                        d = RX_ANY_DATE.search(text)
                        data = {"counter": c, "extra_dispatch": m.group(1).lower() if m else "unused"}
                        if d:
                            data["date"] = d.group(0)
                        w.emit("stop_rule", uid, data, by=MIGRATE_BY, note="stop rule at %s:%d" % (rel, j + 1))
                        events["stop_rule"] += 1
        # -- the CSV tables
        csv_rows = {"decisions": [], "log": log_rows, "tests": test_rows, "limitations": []}
        for j, text in decisions:
            m = RX_LEAD_DATE.fullmatch(text)
            date, body = (m.group(1), m.group(2)) if m else ("", text)
            csv_rows["decisions"].append((j, {"date": date, "kind": "extra-round" if RX_EXTRA.search(body) else "decision", "decision": body}))
        for j, text in stops:
            d = RX_ANY_DATE.search(text)
            csv_rows["decisions"].append((j, {"date": d.group(0) if d else "", "kind": "stop-rule", "decision": text}))
        for j, text in limitations:
            m = RX_LEAD_DATE.fullmatch(text)
            date, body = (m.group(1), m.group(2)) if m else ("", text)
            csv_rows["limitations"].append((j, {"date": date, "text": body, "accepted_by": "main GD", "mirrored": "" if open_feature else "pre-migration"}))
        counts = {}
        csv_cleaner_ = csv_cleaner(self.ctx)
        for name, rows in csv_rows.items():
            counts[name] = len(rows)
            if not rows:
                continue
            table = TABLES[name]
            trel = ".workflow/features/%s/%s" % (slug, table.file)
            if self.ctx.exists(trel):
                raise at(rel, 1, "%s already exists: this feature's %s rows were migrated before" % (trel, name))
            out, expected = [], []
            for j, data in rows:
                with self.soft(rel, j + 1):
                    row = csv_row(table, data, csv_cleaner_, internal=True, fill_date=False)
                    row["id"] = table.fmt_id(len(out) + 1)
                    out.append(row)
                    expected.append((rel, j, row))
            write_atomic(self.ctx.file(trel), csv_bytes(table, out))
            self.expect_csv("%s %s" % (slug, name), table, trel, expected)
        # -- the md rewrite
        new = rewrite_feature(lines, slug, header_lines, rewrite)
        data = (BOM if bom else b"") + (nl.join(new) + nl).encode("utf-8")
        target = self.stage / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        self.checks.append(("%s registry" % slug, "registry", slug, None, [(rel, header_lines[0] if header_lines else 0, record)]))
        if legacy["open"]:
            self.counter_checks.append((rel, (rounds_line if rounds_line is not None else size_line or 0), slug, legacy))
        self.report.append("%s: registry 1 (%s) · decisions %d · log %d · tests %d · limitations %d · journal round %d, extra_round %d, stop_rule %d%s"
                           % (rel, record["status"], counts["decisions"], counts["log"], counts["tests"], counts["limitations"], events["round"],
                              events["extra_round"], events["stop_rule"], "" if not any(k for _, k in rewrite.values())
                              else " · %d other lines kept" % sum(len(k) for _, k in rewrite.values())))

    # ------------------------------------------------------------ feature-root DEBT.md and NOTES.md
    def feature_roots(self):
        db = open_read(self.ctx, [STORES["feature"]])
        roots = []
        for row in db.execute("SELECT slug, feature_root FROM feature WHERE feature_root IS NOT NULL ORDER BY created_at, slug"):
            try:
                rel = safe_root(self.real, row["feature_root"])
            except Refused as ex:
                self.report.append("feature %s: feature root not checked for DEBT.md/NOTES.md: %s" % (row["slug"], ex))
                continue
            if rel not in roots:
                roots.append(rel)
        found = 0
        for root in roots:
            for name, table in (("DEBT.md", TABLES["debt"]), ("NOTES.md", TABLES["notes"])):
                rel = "%s/%s" % (root, name)
                raw = self.source(rel)
                if raw is None:
                    continue
                found += 1
                lines, _, _ = md_lines(raw, rel)
                bullets, kept = md_bullets(lines, 0, len(lines))
                trel = "%s/%s" % (root, table.file)
                f = CsvFile(table, self.ctx.file(trel), trel)
                with located(trel, 1):
                    f.refuse_blocking()
                rows, top, expected = f.rows(), f.top(), []
                cleaner = csv_cleaner(self.ctx)
                for j, text in bullets:
                    with self.soft(rel, j + 1):
                        row = csv_row(table, (root_debt_bullet if table.name == "debt" else root_note_bullet)(text), cleaner, internal=True, fill_date=False)
                        top += 1
                        row["id"] = table.fmt_id(top)
                        rows.append(row)
                        expected.append((rel, j, row))
                if rows:
                    write_atomic(f.path, csv_bytes(table, rows))
                    self.expect_csv(trel, table, trel, expected)
                self.rename_later(rel)
                self.report.append("%s: %d bullets -> %s; %d other lines kept in the renamed file" % (rel, len(bullets), trel, len(kept)))
        if not found:
            self.report.append("feature roots: no DEBT.md or NOTES.md")

    # ------------------------------------------------------------ the round ledger
    def ledger(self):
        raw = self.source(".workflow/rounds.json")
        if raw is None:
            self.report.append(".workflow/rounds.json: absent")
            return
        try:
            self.ledger_events = parse_rounds_json(raw)
        except ValueError as ex:
            raise at(".workflow/rounds.json", 1, "unparsable (%s): fix it by hand, then rerun" % type(ex).__name__) from None
        self.report.append(".workflow/rounds.json: %d events -> .workflow/ledger.db (ledger migrate)" % len(self.ledger_events))

    # ------------------------------------------------------------ verification
    def verify(self):
        for label, kind, what, _, rows in self.checks:
            if kind == "store":
                got = [dict(zip(md_split(render_lines(self.ctx, what)[0], True), md_split(line, True))) for line in render_lines(self.ctx, what)[2:]]
                key = "#" if what.name == "backlog" else "ID"
                by_id = {g[key]: g for g in got}
                for rel, j, want in rows:
                    have = by_id.get(want[key])
                    if have is None or any(have.get(k) != v for k, v in want.items()):
                        raise at(rel, j + 1, "verification: the %s render does not hold this row (%s)" % (what.name, want[key]))
            elif kind == "csv":
                table, trel = what
                f = CsvFile(table, self.ctx.file(trel), trel)
                if f.problems:
                    raise at(trel, 1, "verification: %s" % "; ".join(t for _, t in f.problems))
                got = {}
                for line in csv_render_lines(table, f.rows())[2:]:
                    cells = md_split(line, True)
                    got.setdefault(cells[0], []).append(cells)
                for rel, j, want in rows:
                    cells = got.get(want["id"], [])
                    if len(cells) != 1 or cells[0] != [want.get(c, "") for c in table.columns]:
                        raise at(rel, j + 1, "verification: the %s render does not hold this row (%s)" % (trel, want["id"]))
            elif kind == "registry":
                row = registry_row(self.ctx, what)
                for rel, j, want in rows:
                    if row is None or any(row[k] != v for k, v in want.items()):
                        raise at(rel, j + 1, "verification: the registry record of %s differs from the header" % what)
        db = open_read(self.ctx, [STORES["feature"]])
        for rel, j, slug, legacy in self.counter_checks:
            new = feature_counters(self.ctx, db, slug)
            for c in COUNTERS:
                stopped = re.search(r"(?im)^- Stop rule:.*\b%s\b" % c, new["record"]) is not None
                have = (new[c]["used"], new[c]["cap"], stopped)
                if not new["open"] or have != legacy[c]:
                    raise at(rel, j + 1, "verification: %s counter would change from used %d, cap %d, stopped %s to used %d, cap %d, stopped %s: "
                             "make the Rounds line and the extra round lines agree by hand, then rerun" % ((c,) + legacy[c] + have))
        self.report.append("verified: every render holds its source rows; counters equal for %d open feature(s)" % len(self.counter_checks))

    # ------------------------------------------------------------ the swap
    def swap(self):
        """The ledger first: its migrate is one transaction, so a busy or broken ledger stops here with the root unchanged."""
        self.unchanged()
        if self.ledger_events is not None:
            try:
                self.report.append(ledger_migrate(self.real))
                view = ledger_view(ledger_rows(self.real.workflow / LEDGER_NAME))
            except LedgerBusy:
                raise Refused("ledger busy past %d ms: rerun migrate" % LEDGER_BUSY_MS) from None
            except LedgerBroken as ex:
                raise Refused("ledger: %s" % ex) from None
            missing = [e for e in self.ledger_events if e[2] not in view.get(e[0], {}).get(e[1], [])]
            if missing:
                raise SwapFailed("ledger migrate ran, but %d event(s) of rounds.json are not in ledger.db: nothing else was swapped" % len(missing))
        moves = []
        for p in sorted(self.stage.rglob("*")):
            rel = p.relative_to(self.stage).as_posix()
            if not p.is_file() or rel.startswith(".workflow/%s" % DB_NAME) or p.name.endswith(".tmp"):
                continue
            dest = self.real.root / rel
            if dest.is_file() and dest.read_bytes() == p.read_bytes():
                continue
            moves.append((p, dest))
        staged = []
        try:
            for src, dest in moves:
                staged.append(Pending(dest, src.read_bytes()))
        except BaseException:
            for s in staged:
                s.discard()
            raise
        for k, s in enumerate(staged):
            try:
                s.commit()
            except OSError as ex:
                for rest in staged[k + 1:]:
                    rest.discard()
                self.keep_stage = True
                raise SwapFailed("swap stopped after %d of %d files (%s): the staged copies are kept in %s; the sources are not renamed"
                                 % (k, len(staged), ex, self.stage)) from None
        for src, dst in self.renames:
            try:
                (self.real.root / src).rename(self.real.root / dst)
            except OSError as ex:
                raise SwapFailed("every target was written, but %s was not renamed (%s): rename it to %s by hand" % (src, ex, Path(dst).name)) from None
            self.report.append("renamed %s to %s" % (src, Path(dst).name))
        self.report.append("wrote %d file(s)" % len(staged))

    def run(self) -> list:
        self.keep_stage = False
        try:
            for fn in (self.fwbacklog, self.backlog, self.project_debt, self.features, self.feature_roots, self.ledger):
                self.step(fn)
            if self.errors:
                shown_errors = self.errors[:MIGRATE_ERRORS]
                more = len(self.errors) - len(shown_errors)
                raise Refused("%d line(s) to fix by hand, then rerun:\n%s%s" % (len(self.errors), "\n".join(shown_errors),
                                                                            "\n(%d more)" % more if more else ""))
            self.verify()
            journal.close_all()
            if self.dry_run:
                self.report.append("dry run: nothing written")
            else:
                self.swap()
        finally:
            journal.close_all()
            if not self.keep_stage:
                shutil.rmtree(self.stage, ignore_errors=True)
        return self.report


class SwapFailed(Refused):
    """A failure after the swap began: part of the root may have changed, so the message says what did."""


def header_value(fields: dict, key: str, value: str):
    """One `- Key: value` header line into registry fields."""
    if key == "Status":
        word = value.split()[0] if value.split() else ""
        if word not in STORES["feature"].states:
            raise Refused("Status %s: expected Open, Closed or Abandoned" % shown(value, 60))
        fields["status"] = word
    elif key == "CP":
        word = re.match(r"\S*", value).group(0).rstrip(";,.:")
        choices = STORES["feature"].fields["cp"].choices
        if word in choices:
            fields["cp"] = word
            value = value[len(re.match(r"\S*", value).group(0)):].strip().lstrip("—–-;:,").strip()
        m = re.fullmatch(r"(?i)next step:\s*(.*)", value)
        if m:
            value = m.group(1)
        if value:
            fields["next_step"] = value
    elif key == "Size":
        m = re.fullmatch(r"(S|M|L)\b\s*(?:·\s*Risk flag:\s*(.*))?", value)
        if not m:
            raise Refused("Size %s: expected S, M or L, then · Risk flag: <...>" % shown(value, 60))
        fields["size"] = m.group(1)
        if m.group(2):
            fields["risk"] = m.group(2).strip()
    elif key == "Rounds":
        pass  # used counts become round events; caps come from the size and the extra rounds
    elif key == "Feature root":
        fields["feature_root"] = value.strip().strip("`").strip()
    elif key == "Branch":
        m = re.fullmatch(r"(.*?)\s*·\s*Base:\s*(.*)", value)
        fields["branch"], base = (m.group(1), m.group(2)) if m else (value, None)
        if base:
            fields["base"] = base
    elif key == "Build mode":
        if value not in ("serial", "lanes"):
            raise Refused("Build mode %s: expected serial or lanes" % shown(value, 60))
        fields["build_mode"] = value
    else:
        fields[{"Session": "session", "Profile": "profile", "Assemblies": "assemblies", "Worktrees": "worktrees"}[key]] = value


def table_rows(rel, lines, table, heads: dict, name: str) -> list:
    """A Log or Tests table's rows as CSV values, mapped by header text; `#` is dropped (the CSV id replaces it)."""
    h, header, rows = table
    cols = []
    for cell in header:
        key = cell.strip().lower()
        if key == "#":
            cols.append(None)
        elif name == "log" and key.startswith("attempts"):
            cols.append("attempts")
        elif name == "log" and key.startswith("limitations"):
            cols.append("limitations")
        elif key in heads:
            cols.append(heads[key])
        else:
            raise at(rel, h + 1, "column %s: not a %s column (%s)" % (shown(cell), name, ", ".join(TABLES[name].fields)))
    named = [c for c in cols if c]
    if len(named) != len(set(named)):
        raise at(rel, h + 1, "two columns map to one %s field" % name)
    out = []
    for j, cells in rows:
        if len(cells) != len(cols):
            raise at(rel, j + 1, "%d cells, the header has %d" % (len(cells), len(cols)))
        out.append((j, {c: v for c, v in zip(cols, cells) if c}))
    return out


def legacy_counters(lines, decision_sections) -> dict:
    """What round-cap.ps1 read from the md before the migration: Get-FeatureCounters and New-Counter, file part only."""
    text = "\n".join(lines)
    out = {"open": re.search(r"(?im)^- Status:\s*Open", text) is not None}
    m = re.search(r"(?im)^- Rounds:(.*)$", text)  # PowerShell's -match ignores case
    line = m.group(1) if m else ""
    size = (re.search(r"(?im)^- Size:\s*(S|M|L)\b", text) or [None, "M"])[1].upper()
    gd = "\n".join("\n".join(lines[s:e]) for _, s, e in decision_sections)
    stop = "\n".join(line_ for line_ in lines if line_.startswith("- Stop rule:"))
    record = gd + "\n" + stop
    for c in COUNTERS:
        default = (REWORK_CAPS["L"] if size == "L" else REWORK_CAPS["M"]) if c == "rework" else BASE_CAPS[c]
        used, cap = 0, default
        m = re.search(r"(?i)\b%s\s*:?\s*(\d+)\s*/\s*(\d+)" % c, line)
        if m:
            used, cap = int(m.group(1)), int(m.group(2))
        if cap > default and not re.search(r"(?i)extra round", record):
            cap = default
        out[c] = (used, cap, re.search(r"(?im)^- Stop rule:.*\b%s\b" % c, record) is not None)
    return out


def rewrite_feature(lines, slug, header_lines, rewrite) -> list:
    """The header lines become one State line; each migrated section keeps its heading, gets one pointer line, and keeps
    the lines that were not migrated. Every other line stays as it was."""
    out, i, n = [], 0, len(lines)
    heads = sorted(rewrite)
    first_header = header_lines[0] if header_lines else None
    while i < n:
        if i in header_lines:
            if i == first_header:
                out.append("- State: records.py feature show %s" % slug)
            i += 1
            continue
        if i in rewrite:
            name, kept = rewrite[i]
            end = next((k for k in range(i + 1, n) if lines[k].startswith("## ")), n)
            out += [lines[i], "", "- Rows: records.py csv render %s --feature %s" % (name, slug)]
            if kept:
                out += [""] + [lines[k] for k in kept]
            if end < n:
                out.append("")
            i = end
            continue
        out.append(lines[i])
        i += 1
    while out and not out[-1].strip():
        out.pop()
    return out


def debt_bullet(text: str) -> dict:
    """A .workflow/DEBT.md bullet: `BUG-####: ...`, `<slug> (...): ...`, `<slug>: ...`, or framework debt; ` Next: ...` ends it."""
    record = {"accepted_by": "main GD"}
    m = re.match(r"(BUG-\d{4,})\s*:\s*(.*)", text)
    m2 = re.match(r"([a-z0-9]+(?:-[a-z0-9]+)+|framework)\s*(\([^)]*\))?\s*:\s*(.*)", text)
    if m:
        record["source"], body = m.group(1), m.group(2)
    elif m2:
        record["source"] = m2.group(1)
        body = ("%s %s" % (m2.group(2), m2.group(3))) if m2.group(2) else m2.group(3)
    else:
        record["source"], body = "framework", text
    parts = re.split(r"\s+Next:\s+", body)
    if len(parts) > 1:
        body, record["next_step"] = " Next: ".join(parts[:-1]), parts[-1]
    record["text"] = body.strip()
    d = RX_ANY_DATE.search(text)
    record["date"] = d.group(0) if d else today()
    return record


def root_debt_bullet(text: str) -> dict:
    row = {"state": "Open"}
    m = re.match(r"(\d{4}-\d{2}-\d{2})\s+(.*)", text)
    if m:
        row["date"], text = m.group(1), m.group(2)
    m = re.match(r"(?i)(workaround|limitation|accepted[ -]gap)\s*[:—–-]\s*(.*)", text)
    row["kind"] = m.group(1).lower().replace(" ", "-") if m else "limitation"
    text = m.group(2) if m else text
    m = re.match(r"(BUG-\d{4,})\s*:\s*(.*)", text)
    if m:
        row["source"], text = m.group(1), m.group(2)
    parts = re.split(r"\s+Next:\s+", text)
    if len(parts) > 1:
        text, row["next_step"] = " Next: ".join(parts[:-1]), parts[-1]
    row["text"] = text
    if row["kind"] == "accepted-gap":
        row["accepted_by"] = "main GD"
    return row


def root_note_bullet(text: str) -> dict:
    row = {"state": "Open"}
    m = re.match(r"(\d{4}-\d{2}-\d{2})\s+(.*)", text)
    if m:
        row["date"], text = m.group(1), m.group(2)
    m = re.match(r"\*\*(.+?)\*\*\s*[:—–-]?\s*(.*)", text)
    if m:
        row["topic"], text = m.group(1), m.group(2)
    row["text"] = text
    return row


def cmd_migrate(ctx, a):
    if not a.from_md:
        raise UsageError("bad arguments: migrate needs --from-md")
    if not a.dry_run:
        ctx.require_writable()
    journal.Cleaner(ctx)  # fail closed before anything is read: every migrated value goes through the content rules
    try:
        report = Migration(ctx, a.dry_run).run()
    except SwapFailed as ex:
        raise Refused("migrate failed during the swap: %s" % ex) from None
    except (Refused, Corrupt) as ex:
        raise Refused("migrate refused, nothing was changed: %s" % ex) from None
    print("\n".join(report))
    return 0


# ---------------------------------------------------------------- parser and main

STORE_HANDLERS = {"add": cmd_add, "update": cmd_update, "set-state": cmd_set_state, "list": cmd_list, "show": cmd_show,
                  "search": cmd_search, "render": cmd_render, "stats": cmd_store_stats, "round": cmd_round,
                  "extra-round": cmd_extra_round, "stop-rule": cmd_stop_rule, "counters": cmd_counters}
GLOBAL_HANDLERS = {"rebuild": cmd_rebuild, "doctor": cmd_doctor, "sql": cmd_sql, "stats": cmd_stats, "bug-mirror": cmd_bug_mirror,
                   "migrate": cmd_migrate}
LEDGER_HANDLERS = {"get": cmd_ledger_get, "add": cmd_ledger_add, "migrate": cmd_ledger_migrate}
CSV_HANDLERS = {"add": cmd_csv_add, "update": cmd_csv_update, "list": cmd_csv_list, "render": cmd_csv_render, "doctor": cmd_csv_doctor,
                "mirror": cmd_csv_mirror}


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
    top.add_parser("stats", help="one line: Records: ... open per store").add_argument("--json", action="store_true", help="{line, open_features}")
    sp = top.add_parser("ledger", help="the local round ledger .workflow/ledger.db")
    sub = sp.add_subparsers(dest="cmd", required=True)
    sub.add_parser("get", help="the ledger as {key: {counter: [ids]}}").add_argument("--json", action="store_true", help="always JSON")
    sub.add_parser("add", help="stdin: [{key, counter, id}]").add_argument("--json", action="store_true", help="stdin is JSON")
    sub.add_parser("migrate", help="import .workflow/rounds.json and parked files")
    sp = top.add_parser("csv", help="a feature's CSV tables: %s" % ", ".join(TABLES))
    sub = sp.add_subparsers(dest="cmd", required=True)
    for name, text in (("add", "a new row: JSON fields on stdin; prints its id"), ("update", "change a row: JSON on stdin"),
                       ("list", "the rows"), ("render", "GitHub markdown table"), ("doctor", "report a broken file")):
        s = sub.add_parser(name, help=text)
        s.add_argument("table", choices=list(TABLES), nargs="?" if name == "doctor" else None)
        if name == "update":
            s.add_argument("id")
        s.add_argument("--feature", required=True, help="the feature's slug")
        if name == "list":
            s.add_argument("--json", action="store_true")
        if name == "doctor":
            s.add_argument("--fix", action="store_true", help="renumber duplicate ids, drop merge-left headers, normalize BOM and CRLF")
    sub.add_parser("mirror", help="copy unmirrored limitations into the feature root's DEBT.csv").add_argument("--feature", required=True)
    top.add_parser("bug-mirror", help="mirror a Won't fix or Accepted bug into debt (the repair bugs.py names)").add_argument("id", help="BUG-####")
    s = top.add_parser("migrate", help="convert the markdown stores to journals and CSV tables")
    s.add_argument("--from-md", dest="from_md", action="store_true", required=True)
    s.add_argument("--dry-run", dest="dry_run", action="store_true", help="stage, verify and report; write nothing")
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
        if a.area == "csv":
            return CSV_HANDLERS[a.cmd](ctx, a)
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
