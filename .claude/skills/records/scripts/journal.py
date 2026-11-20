"""Shared journal engine: a tracked JSONL journal as the truth, a gitignored SQLite cache rebuilt from it. No LLM, stdlib only.

Loaded by path (importlib) from bugs.py and records.py: `-I` drops the script dir from sys.path. Store-agnostic parts only;
each store keeps its schema, event types, replay and commands. Contract: ../references/schema.md.
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

SQL_SECONDS = 10
SQL_ROWS = 1000
MAX_COUNT = 100  # one round or extra-round call; replay refuses more, so a counter's total stays a small integer
REFUSAL_LINE = 500
VALUE_MARK = ""  # brackets a caller's value inside refusal text; refusal_text() is the only reader
RX_SHOWN = re.compile("%s.*?%s" % (VALUE_MARK, VALUE_MARK), re.S)
DEFAULT_BY = "main session"

RX_TS = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z")
RX_BREAK = re.compile("[\r\n\v\f\x85  ]")
RX_CONTROL = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f  ]")
VI_LETTERS = "àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ"
RX_VIETNAMESE = re.compile("[%s%s]" % (VI_LETTERS, VI_LETTERS.upper()))
UID_NAMESPACE = uuid.UUID("6f1f3b52-8a44-5c0e-9b7d-2e0c4a7d1b90")
GIT_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_PREFIX", "GIT_OBJECT_DIRECTORY")
MEM_API = ("load_secret_patterns", "redact", "redact_pii", "RX_PEM_BLOCK")


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


# ---------------------------------------------------------------- time and ids

def fmt_ts(d: dt.datetime) -> str:
    return d.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (d.microsecond // 1000)


def parse_ts(s: str) -> dt.datetime:
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=dt.timezone.utc)


def now_utc(env: str = "BUGS_NOW") -> dt.datetime:
    override = os.environ.get(env)  # test-only clock
    if not override:
        return dt.datetime.now(dt.timezone.utc)
    return parse_ts(override if "." in override else override[:-1] + ".000Z")


def next_ts(last: str | None, env: str = "BUGS_NOW") -> str:
    now = now_utc(env)
    if last:
        now = max(now, parse_ts(last) + dt.timedelta(milliseconds=1))
    return fmt_ts(now)


def shown(value, limit=40) -> str:
    """A caller's or a file's value inside refusal text. A long one is never echoed, not cut: the scan at the exit
    could miss a secret cut in half."""
    text = str(value).replace(VALUE_MARK, "")
    return VALUE_MARK + (text if len(text) <= limit else "<%d chars>" % len(text)) + VALUE_MARK


def shown_all(values) -> str:
    return ", ".join(shown(v) for v in values)


def stable_uid(name: str) -> str:
    return str(uuid.uuid5(UID_NAMESPACE, name))


# ---------------------------------------------------------------- content rules

def check_english(field: str, text: str):
    m = RX_VIETNAMESE.search(unicodedata.normalize("NFC", text))
    if m:
        raise Refused("%s: Vietnamese diacritics ('%s'): the database is English only, translate first" % (field, m.group(0)))


def load_by_path(name: str, path, missing: str = ""):
    """Another framework script as a module, by path: -I removes the script dir from sys.path, hence importlib. Cached in
    sys.modules under `name` only while that entry came from this same file; a file that fails to run is never cached.
    Writes no .pyc beside the framework. A missing file refuses, naming it; `missing` says what that costs the caller.
    The two bootstrap loaders that fetch this file keep their own copy: they run before this function exists."""
    path = Path(path).resolve()
    module = sys.modules.get(name)
    file = getattr(module, "__file__", None)
    if file and Path(file).resolve() == path:
        return module
    if not path.is_file():
        raise Refused("%s is missing%s" % (path, missing))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    keep, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = keep
    sys.modules[name] = module
    return module


_mem = None


def mem_module(name: str = "journal_mem"):
    """mem.py owns the secret patterns and PII rules. Any fault in loading it refuses the write, never a traceback."""
    global _mem
    if _mem is None:
        path = Path(__file__).resolve().parents[2] / "mem" / "scripts" / "mem.py"
        if not path.exists():
            raise Refused("write refused: %s is missing, so secret shapes cannot be checked" % path)
        try:
            module = load_by_path(name, path)
            for attr in MEM_API:
                getattr(module, attr)
        except KeyboardInterrupt:
            raise
        except BaseException as ex:  # whatever the fault in that file, a SyntaxError or a sys.exit too: it leaves through main()
            raise Refused("write refused: %s cannot be loaded (%s), so secret shapes cannot be checked" % (path, type(ex).__name__)) from None
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
    """Applies every content rule to text about to be written. A missing pattern file refuses here, before any write.
    `limits` maps each field to its stored-length limit; `one_line` names the fields that hold no line break."""

    def __init__(self, ctx, limits=None, one_line=()):
        self.limits, self.one_line = dict(limits or {}), set(one_line)
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
        if field in self.one_line:
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
        limit = self.limits[field]
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

    def report(self):
        if self.redacted:
            print("redacted PII in: %s" % ", ".join(sorted(set(self.redacted))), file=sys.stderr)


def read_stdin_json(required: bool, kind=dict):
    """A JSON value of `kind` on stdin (dict, or list for the ledger). Empty stdin: {} unless required."""
    stream = getattr(sys.stdin, "buffer", None)
    if sys.stdin is None or stream is None or sys.stdin.isatty():
        raw = b""
    else:
        raw = stream.read()
    what = "a JSON object" if kind is dict else "a JSON list"
    if not raw.strip():
        if required:
            raise Refused("expected %s on stdin" % what)
        return kind()
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except UnicodeDecodeError as ex:
        raise Refused("stdin is not UTF-8 JSON: %s" % ex) from None
    except ValueError as ex:
        raise Refused("stdin is not valid JSON: %s" % ex) from None
    if not isinstance(data, kind):
        raise Refused("expected %s on stdin" % what)
    return data


def by_of(cleaner: Cleaner, a, default: str = DEFAULT_BY) -> str:
    if a.by is None:
        return default
    if a.by != "main GD" and a.by.strip() == "main GD":  # clean() trims, which would store a padded form as the main GD's attribution
        raise Refused("by: must be exactly main GD, with no padding")
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

def git_exe() -> str:
    """git's full path from PATH alone. On Windows CreateProcess tries the current folder before PATH, and so does shutil.which,
    so a bare "git" would run a git.exe in the folder a session starts in. A relative PATH entry names that folder too. None: the
    FileNotFoundError subprocess raises for a missing program."""
    names = ("git.exe", "git.cmd", "git.bat") if os.name == "nt" else ("git",)
    for folder in os.environ.get("PATH", "").split(os.pathsep):
        folder = folder.strip().strip('"')
        if not os.path.isabs(folder):
            continue
        for name in names:
            path = os.path.join(folder, name)
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
    raise FileNotFoundError("git is not on PATH")


def run_git(cwd: Path, *args) -> tuple[int, str]:
    env = {k: v for k, v in os.environ.items() if k not in GIT_ENV}
    r = subprocess.run([git_exe(), "-C", str(cwd)] + list(args), capture_output=True, env=env, timeout=30)
    return r.returncode, r.stdout.decode("utf-8", "replace").strip()


def main_checkout(root: Path, label: str = "journal") -> tuple[Path, Path | None, bool]:
    """(the checkout holding the journal, its git dir, whether root is a linked worktree). The rule of Get-BugsRoot in
    hooks/common.ps1, kept the same in effect: hooks/tests/run.ps1 drives both over the same layouts. Only the root's own .git
    counts, since git itself walks up to any link planted above. A link that leads nowhere refuses, read or write."""
    link = root / ".git"
    if not link.is_file():
        return root, link if link.is_dir() else None, False
    m = re.search(r"(?m)^gitdir:\s*(.+?)\s*$", link.read_text(encoding="utf-8-sig", errors="replace"))
    if not m:
        raise Refused("%s names no gitdir, so the main checkout's %s cannot be found" % (shown(link, 200), label))
    git_dir = Path(os.path.normpath(root / m.group(1)))
    if not git_dir.is_dir():
        raise Refused("%s, named by %s, does not exist" % (shown(git_dir, 200), shown(link, 200)))
    common_file = git_dir / "commondir"
    if not common_file.is_file():
        if (git_dir / "objects").is_dir():  # a full git dir: a submodule or --separate-git-dir
            return root, git_dir, False
        raise Refused("%s is missing and %s holds no objects, so the main checkout's %s cannot be found" % (shown(common_file, 200), shown(git_dir, 200), label))
    common = Path(os.path.normpath(git_dir / common_file.read_text(encoding="utf-8-sig", errors="replace").strip()))
    if common.name != ".git":
        raise Refused("%s is no checkout's .git, so the %s cannot be found" % (shown(common, 200), label))
    if not common.is_dir():
        raise Refused("%s, named by %s, does not exist" % (shown(common, 200), shown(common_file, 200)))
    return common.parent.resolve(), common, True


class Ctx:
    """The root per main_checkout: a linked worktree reads the main checkout's data, a root with no .git has no git context.
    `journal_name` and `db_name` live under .workflow/; `use_git=False` skips the git cross-check (the ledger needs no git)."""

    def __init__(self, arg: str | None, journal_name: str, db_name: str, default_root: Path, label: str = "journal",
                 clock_env: str = "BUGS_NOW", use_git: bool = True):
        self.journal_name, self.db_name, self.clock_env = journal_name, db_name, clock_env
        given = Path(arg).resolve() if arg else Path(default_root)
        if not given.is_dir():
            raise Refused("root %s is not a directory" % shown(given, 200))
        self.root, self.git_dir, self.linked = main_checkout(given, label)
        self.git_failed = False
        if self.git_dir is None or not use_git:
            return
        try:
            code, out = self.run_git(given, "rev-parse", "--git-common-dir")
        except (OSError, subprocess.SubprocessError):
            code, out = 1, ""
        # Git is missing, refuses, or walked past a .git it will not read to a repo above: cannot rule out a linked worktree.
        if code or (given / out).resolve() != self.git_dir.resolve():
            self.git_failed, self.git_dir = True, None

    def run_git(self, cwd: Path, *args) -> tuple[int, str]:
        """A store overrides this to route through its own module, so a test patch there reaches the check."""
        return run_git(cwd, *args)

    @property
    def workflow(self) -> Path:
        return self.root / ".workflow"

    @property
    def journal(self) -> Path:
        return self.workflow / self.journal_name

    @property
    def db_path(self) -> Path:
        return self.workflow / self.db_name

    def require_writable(self):
        if self.linked:
            raise Refused("writes from a linked worktree are refused: run from the main checkout %s" % self.root)
        if self.git_failed:
            raise Refused("git failed in %s: cannot rule out a linked worktree, write refused" % self.root)


# ---------------------------------------------------------------- journal I/O

def read_journal(path: Path) -> bytes:
    try:
        return Path(path).read_bytes()
    except FileNotFoundError:
        return b""


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def need(cond: bool, msg: str):
    if not cond:
        raise ValueError(msg)


def is_count(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 1


def check_ts(ev: dict):
    need(RX_TS.fullmatch(ev["ts"]) is not None, "bad ts")
    try:
        parse_ts(ev["ts"])
    except ValueError:
        need(False, "bad ts")


class Parsed:
    def __init__(self):
        self.events, self.errors, self.torn = [], [], False


def parse_journal(raw: bytes, check_event) -> Parsed:
    """A final line with no newline that is not JSON is a torn write: skipped here, removed by the next write.
    `check_event` raises ValueError or TypeError on a line of the wrong shape."""
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


def replay_order(events, uid_key: str = "uid") -> list:
    """Sort by (ts, event_uid), one copy per event_uid, tombstoned uids dropped, creates first."""
    best = {}
    for ev in events:
        key = (ev["ts"], canon(ev))
        if ev["event_uid"] not in best or key < best[ev["event_uid"]][0]:
            best[ev["event_uid"]] = (key, ev)
    unique = [v[1] for v in best.values()]
    dead = {ev[uid_key] for ev in unique if ev["type"] == "tombstone"}
    live = [ev for ev in unique if ev["type"] != "tombstone" and ev[uid_key] not in dead]
    live.sort(key=lambda ev: (ev["ts"], ev["event_uid"]))
    creates = [ev for ev in live if ev["type"] == "create"]
    uids = [ev[uid_key] for ev in creates]
    if len(set(uids)) != len(uids):
        raise Corrupt("corrupt journal: two create lines for one %s" % uid_key)
    known = set(uids)
    for ev in live:
        if ev[uid_key] not in known:
            raise Corrupt("corrupt journal: %s line for a %s with no create: %s" % (ev["type"], uid_key, shown(ev["event_uid"])))
    return creates + [ev for ev in live if ev["type"] != "create"]


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


def append_lines(path: Path, lines: list) -> bytes:
    """LF only, UTF-8, no BOM, whatever the platform. Returns the journal's new bytes."""
    raw = read_journal(path)
    fixed = repaired(raw)
    if len(fixed) < len(raw):  # never rewrite the good lines: only the fragment goes
        with open(path, "r+b") as f:
            f.truncate(len(fixed))
    blob = (b"\n" if len(fixed) > len(raw) else b"") + b"".join(lines)
    with open(path, "ab") as f:
        f.write(blob)
        f.flush()
        os.fsync(f.fileno())
    return (raw if len(fixed) > len(raw) else fixed) + blob


def replace_journal(path: Path, tmp: Path, raw: bytes):
    """Atomic: written to `tmp` (a name the DB's ignore rule covers), then moved over the journal."""
    with open(tmp, "wb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


# ---------------------------------------------------------------- database

_connections = []  # closed by each CLI's main()
BUSY_SECONDS = 10  # a lock wait on the cache; a Ctx with busy_seconds (a hook's read) waits that long instead


def connect(target: str, timeout: float = BUSY_SECONDS, **kw) -> sqlite3.Connection:
    db = sqlite3.connect(target, timeout=timeout, isolation_level=None, **kw)
    db.row_factory = sqlite3.Row
    _connections.append(db)
    return db


def close_all():
    while _connections:
        _connections.pop().close()


def create_schema(db, schema, version: int):
    db.execute("BEGIN IMMEDIATE")
    try:
        if db.execute("PRAGMA user_version").fetchone()[0] == 0:
            for stmt in schema:
                db.execute(stmt)
            db.execute("PRAGMA user_version=%d" % version)
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise


def remove_db(ctx: Ctx):
    for db in list(_connections):
        db.close()
        _connections.remove(db)
    for f in ctx.workflow.glob(ctx.db_path.name + "*"):
        f.unlink()


def open_db(ctx: Ctx, schema, version: int, create=False, journals=None) -> sqlite3.Connection:
    """No journal, no DB, not a create: an empty in-memory store, so reads return nothing and create nothing."""
    journals = [ctx.journal] if journals is None else journals
    if not create and not ctx.db_path.exists() and not any(Path(j).exists() for j in journals):
        db = connect(":memory:")
        create_schema(db, schema, version)
        return db
    ctx.workflow.mkdir(parents=True, exist_ok=True)
    for _ in range(2):
        try:
            db = connect(str(ctx.db_path), getattr(ctx, "busy_seconds", BUSY_SECONDS))
            got = db.execute("PRAGMA user_version").fetchone()[0]
            if got not in (0, version):
                raise sqlite3.DatabaseError("schema version %d" % got)
            if got == 0:  # a read must not take the write lock when the schema is already there
                create_schema(db, schema, version)
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


# ---------------------------------------------------------------- the write path

class Writer:
    """BEGIN IMMEDIATE, hash check, rebuild if different, the command validates, apply, append, commit.
    A crash after the append is healed by the next command's hash mismatch. A store subclasses it and fills the hooks."""

    uid_key = "uid"

    def __init__(self, ctx: Ctx, create=False):
        self.ctx, self.create, self.lines = ctx, create, []
        self.rewritten = None

    # -- store hooks
    def check_writable(self):
        self.ctx.require_writable()
        Cleaner(self.ctx)  # every write, text-free ones too: a missing pattern file refuses here (fail closed)

    def open_db(self):
        raise NotImplementedError

    def read(self) -> bytes:
        return read_journal(self.ctx.journal)

    def append(self, lines) -> bytes:
        return append_lines(self.ctx.journal, lines)

    def after_append(self):
        """Between the journal append and the DB commit. Tests replace it to crash exactly there."""

    def stored_hash(self) -> str | None:
        return get_meta(self.db, "journal_hash")

    def rebuild(self, raw: bytes):
        raise NotImplementedError

    def load_state(self):
        """Sets self.last_ts and self.top (the id high water) from the DB."""
        raise NotImplementedError

    def save_state(self, new: bytes):
        raise NotImplementedError

    def apply(self, ev: dict):
        raise NotImplementedError

    def high_water_of(self, events) -> int:
        return 0

    # -- the engine
    def __enter__(self):
        self.check_writable()
        self.db = self.open_db()
        self.db.execute("BEGIN IMMEDIATE")
        try:
            raw = self.read()
            if self.stored_hash() != sha(raw):
                self.rebuild(raw)
            self.load_state()
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        return self

    def emit(self, etype: str, uid: str, data: dict, by=None, note=None, event_uid=None) -> dict:
        ev = {"event_uid": event_uid or str(uuid.uuid4()), self.uid_key: uid, "ts": next_ts(self.last_ts, self.ctx.clock_env), "type": etype, "data": data}
        if by is not None:
            ev["by"] = by
        if note is not None:
            ev["note"] = note
        self.apply(ev)
        self.lines.append(encode_line(ev))
        self.last_ts = max(self.last_ts or "", ev["ts"])
        self.top = max(self.top, self.high_water_of([ev]))
        return ev

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.db.execute("ROLLBACK")
            return False
        try:
            if self.lines:
                new = self.append(self.lines)
                self.after_append()
                self.save_state(new)
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        return False


# ---------------------------------------------------------------- the read-only sql gate

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


def run_sql(query_text: str, as_json: bool, open_read, db_path: Path, seconds=SQL_SECONDS) -> int:
    """One read-only statement: a leading-keyword gate, then `open_read()` (the store's hash check), then a mode=ro
    connection with query_only and the authorizer. 1000 rows, `seconds` of run time."""
    query = strip_sql_comments(query_text)
    first = re.match(r"[A-Za-z]+", query)
    if not first or first.group(0).upper() not in ("SELECT", "WITH", "VALUES"):
        raise Refused("sql is read-only: only SELECT, WITH and VALUES")
    db = open_read()
    if db_path.exists():
        db.close()
        db = connect(db_path.resolve().as_uri() + "?mode=ro", uri=True)
    db.execute("PRAGMA query_only=ON")
    db.set_authorizer(sql_authorizer)
    deadline = dt.datetime.now() + dt.timedelta(seconds=seconds)
    expired = []

    def past_deadline():
        if dt.datetime.now() > deadline:
            expired.append(True)
        return bool(expired)

    db.set_progress_handler(past_deadline, 100000)
    try:
        cur = db.execute(query_text)
        rows = cur.fetchmany(SQL_ROWS + 1)
    except (sqlite3.Error, sqlite3.Warning) as ex:
        # A Ctrl+C lands in the handler, and SQLite reports it as this error with the deadline not reached.
        if not expired and isinstance(ex, sqlite3.OperationalError) and str(ex) == "interrupted":
            raise KeyboardInterrupt from None
        raise Refused("sql refused: %s" % shown(ex, 200)) from None  # SQLite quotes the query
    names = [c[0] for c in cur.description or ()]
    more = len(rows) > SQL_ROWS
    rows = rows[:SQL_ROWS]
    if as_json:
        print(json.dumps([dict(zip(names, map(sql_cell, tuple(r)))) for r in rows], ensure_ascii=False, indent=1))
    else:
        print("\t".join(names))
        for r in rows:
            print("\t".join("" if v is None else str(sql_cell(v)).replace("\n", "\\n") for v in tuple(r)))
    if more:
        print("(first %d rows)" % SQL_ROWS, file=sys.stderr)
    return 0


# ---------------------------------------------------------------- refusal text

def refusal_text(text: str, root: Path) -> str:
    """The only way refusal text reaches stderr. Everything passes the same secret and PII redaction as a write, because
    an ID, a status or a JSON key can be a pasted secret. Nothing to scan with: the values stay out."""
    try:
        mem = mem_module()
        patterns = loaded_patterns(mem, root)
        lines = mem.redact_pii(mem.redact(text.replace(VALUE_MARK, ""), patterns)).split("\n")
    except KeyboardInterrupt:
        raise
    except BaseException:  # it is already reporting an error, whatever broke the module, the file or a redaction: it must not raise
        lines = RX_SHOWN.sub("<hidden: secret patterns unavailable>", text).split("\n")
    return "\n".join(line[:REFUSAL_LINE] for line in lines)


def given_root(argv, default_root: Path) -> Path:
    """--root as typed, for the pattern lookup when the arguments themselves did not parse."""
    words = sys.argv[1:] if argv is None else list(argv)
    for i, word in enumerate(words):
        if word == "--root" and i + 1 < len(words):
            return Path(words[i + 1])
        if word.startswith("--root="):
            return Path(word[len("--root="):])
    return Path(default_root)


def reconfigure_streams():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
