"""Zero-Mem store: deterministic capture, indexing and retrieval of traces, notes and knowledge. No LLM, stdlib only.

Run with `python -I mem.py <command>`. Files under .memory/ and the docs in sources.txt are the source of truth;
.memory/.index/mem.db is a derived SQLite FTS5 index, refreshed incrementally before every command.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import textwrap
import time
from pathlib import Path

SCHEMA_VERSION = 1
NOTE_TYPES = ("feedback", "lesson", "project", "reference")
LAYER_PRIOR = {"M": 1.3, "K": 1.0, "T": 0.8}
TRACE_HALF_LIFE_DAYS = 90.0
MAX_TURN_CHARS = 20000
MAX_CHUNK_CHARS = 6000
GET_CAP = 4000  # chars `get` prints without --full
ENT_CAP = 3  # entity cards `ent` prints
DEFAULT_SOURCES = """\
# Knowledge (layer K): docs indexed in place. One glob per line; ! excludes; ** spans folders.
CLAUDE.md
README.md
docs/**/*.md
.workflow/**/*.md
.claude/rules/*.md
.claude/agents/*.md
.claude/skills/**/*.md
framework-docs/**/*.md
**/{README,CONTRACTS,INTEGRATION,ARCHITECTURE,DECISIONS,DEBT,NOTES,WORKMEMORY}.md
!Assets/Plugins/**
!Packages/**
!**/ThirdParty/**
"""
FEATURE_DOCS = {"readme", "contracts", "integration", "architecture", "decisions", "debt", "notes", "workmemory"}
# Basenames too common to identify a file on their own: the entity keeps the parent folder.
GENERIC_STEMS = FEATURE_DOCS | {"skill", "claude", "index", "changelog", "main", "run", "test", "tests", "common", "template"}
STOPWORDS = set("a an and are as at be by do does for from how i in is it of on or the this to was what when where which who why with".split())
SKIP_DIRS = {".git", "library", "temp", "logs", "usersettings", "obj", "build", "builds", "node_modules", ".index", ".state"}

RX_HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*#*\s*$")
RX_FENCE = re.compile(r"^\s*(```|~~~)")
RX_PATH = re.compile(r"(?<![\w.-])((?:[\w.-]+/)*[\w-][\w.-]*\.(?:cs|md|ps1|py|js|ts|json|asset|prefab|unity|asmdef|shader|hlsl|uxml|uss|txt|ya?ml|xml|csv))\b", re.I)
RX_IDS = re.compile(r"\b(BUG-\d{4}|ADR-\d+|CP[1-4])\b")
RX_PKG = re.compile(r"\b(com\.[a-z0-9-]+(?:\.[a-z0-9-]+)+)\b")
RX_TYPE = re.compile(r"\b(Game\.(?:Core|Client|Server)(?:\.[A-Z]\w*)*|[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+)\b")
RX_WORD = re.compile(r"\w+", re.UNICODE)
RX_HARNESS = re.compile(r"<(system-reminder|ide_\w+|local-command-\w+|command-message|browser_instruction|user-prompt-submit-hook|bash-stdout|bash-stderr)>.*?</\1>", re.S)
RX_TAG_KEEP = re.compile(r"</?(command-name|command-args|bash-input|pasted_content[^>]*)>")


# ---------------------------------------------------------------- paths and helpers

def find_root(arg: str | None) -> Path:
    if arg:
        return Path(arg).resolve()
    return Path(__file__).resolve().parents[4]


def rel(root: Path, p: Path) -> str:
    return p.relative_to(root).as_posix()


def load_secret_patterns(root: Path) -> list[tuple[str, re.Pattern]]:
    f = root / ".claude" / "hooks" / "secret-patterns.txt"
    if not f.exists():
        f = Path(__file__).resolve().parents[3] / "hooks" / "secret-patterns.txt"
    out = []
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        name, rx = line.split("\t", 1)
        out.append((name, re.compile(rx)))
    if not out:
        raise RuntimeError("no secret patterns in %s" % f)  # fail closed: never capture or lint unscanned
    return out


# The pattern list detects a key by its header; redaction must remove the whole block, body included.
RX_PEM_BLOCK = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?(?:-----END [A-Z ]*PRIVATE KEY-----|$)")
RX_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b")  # not package@1.2.3


def redact(text: str, patterns) -> str:
    text = RX_PEM_BLOCK.sub("[REDACTED:private key]", text)
    for name, rx in patterns:
        text = rx.sub("[REDACTED:%s]" % name, text)
    return text


def write_lf(path: Path, text: str):
    with open(path, "w", encoding="utf-8", newline="\n") as f:  # Path.write_text(newline=) needs 3.10
        f.write(text)


def glob_regex(g: str) -> re.Pattern:
    out, i = "", 0
    while i < len(g):
        if g.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
            continue
        if g.startswith("**", i):
            out, i = out + ".*", i + 2
            continue
        c = g[i]
        if c == "*":
            out += "[^/]*"
        elif c == "?":
            out += "[^/]"
        elif c == "{" and "}" in g[i:]:
            j = g.index("}", i)
            out += "(?:" + "|".join(re.escape(x) for x in g[i + 1:j].split(",")) + ")"
            i = j
        else:
            out += re.escape(c)
        i += 1
    return re.compile(out + "$", re.I)


def read_sources(mem: Path):
    f = mem / "sources.txt"
    text = f.read_text(encoding="utf-8") if f.exists() else DEFAULT_SOURCES
    inc, exc = [], []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        (exc if line.startswith("!") else inc).append(glob_regex(line.lstrip("!")))
    return inc, exc


def list_files(root: Path) -> list[str]:
    """Tracked + untracked-not-ignored files (git respects .gitignore, so Library/Temp never appear)."""
    try:
        r = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                           capture_output=True, timeout=30)
        if r.returncode == 0:
            return sorted({p for p in r.stdout.decode("utf-8", "replace").split("\0") if p})
    except (OSError, subprocess.SubprocessError):
        pass
    out = []
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x.lower() not in SKIP_DIRS]
        out += [rel(root, Path(d) / f) for f in files]
    return out


def file_entity(path: str) -> tuple[str, str]:
    parts = path.replace("\\", "/").lower().strip("./").split("/")
    base = parts[-1]
    stem = base.rsplit(".", 1)[0]
    name = "/".join(parts[-2:]) if stem in GENERIC_STEMS and len(parts) > 1 else base
    return name, stem


def parse_frontmatter(text: str) -> tuple[dict, str, int]:
    """Minimal YAML subset: key: value, [a, b] lists, '- item' lists, one level of nesting flattened."""
    if not text.startswith("---"):
        return {}, text, 0
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return {}, text, 0
    meta, key = {}, None
    for line in lines[1:end]:
        m = re.match(r"^\s*-\s+(.*)$", line)
        if m:
            if key and (meta.get(key) == "" or isinstance(meta.get(key), list)):
                meta[key] = (meta[key] or []) + [m.group(1).strip().strip("\"'")]
            continue
        m = re.match(r"^\s*([\w-]+):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val.startswith("[") and val.endswith("]"):
            meta[key] = [x.strip().strip("\"'") for x in val[1:-1].split(",") if x.strip()]
        elif val:
            meta[key] = val.strip("\"'")
        else:
            meta.setdefault(key, "")
    return meta, "\n".join(lines[end + 1:]), end + 1


def slugify(s: str) -> str:
    return re.sub(r"[^\w]+", "-", s.lower()).strip("-")[:60]


# ---------------------------------------------------------------- entities (deterministic NER)

class Vocab:
    def __init__(self, root: Path):
        names = set()
        for d, kind in ((root / ".claude" / "agents", "agent"), (root / ".workflow" / "features", "feature")):
            if d.exists():
                names |= {(p.stem.lower(), kind) for p in d.glob("*.md")}
        sk = root / ".claude" / "skills"
        if sk.exists():
            names |= {(p.name.lower(), "skill") for p in sk.iterdir() if p.is_dir()}
        self.kind = {n: k for n, k in names}
        multi = sorted((n for n in self.kind if "-" in n), key=len, reverse=True)
        single = sorted(n for n in self.kind if "-" not in n)
        self.rx_multi = re.compile(r"(?<![\w-])(" + "|".join(map(re.escape, multi)) + r")(?![\w-])") if multi else None
        # One-word names ("fix", "qa") are common words: only a slash command or a backticked name counts.
        self.rx_single = re.compile(r"(?:/|`)(" + "|".join(map(re.escape, single)) + r")\b") if single else None


def extract_entities(text: str, vocab: Vocab, files=()) -> set[tuple[str, str, str]]:
    """Returns {(name, kind, stem)}; names are lowercase."""
    out = set()
    for f in files:
        n, s = file_entity(f)
        out.add((n, "file", s))
    flat = text.replace("\\", "/")
    for m in RX_PATH.finditer(flat):
        n, s = file_entity(m.group(1))
        out.add((n, "file", s))
    for m in RX_IDS.finditer(text):
        out.add((m.group(1).lower(), "id", m.group(1).lower()))
    for m in RX_PKG.finditer(text):
        out.add((m.group(1), "package", m.group(1)))
    for m in RX_TYPE.finditer(text):
        n = m.group(1).lower()
        out.add((n, "type", n))
    low = text.lower()
    for rx in (vocab.rx_multi, vocab.rx_single):
        if rx:
            for m in rx.finditer(low):
                out.add((m.group(1), vocab.kind[m.group(1)], m.group(1)))
    return out


# ---------------------------------------------------------------- database

_connections = []  # closed by main()


def open_db(mem: Path) -> sqlite3.Connection:
    db = _open_db(mem)
    _connections.append(db)
    return db


def _open_db(mem: Path) -> sqlite3.Connection:
    idx = mem / ".index"
    idx.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(idx / "mem.db"), timeout=10)
    if db.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
        db.close()
        for f in idx.glob("mem.db*"):
            f.unlink()
        db = sqlite3.connect(str(idx / "mem.db"), timeout=10)
        db.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE doc(rid INTEGER PRIMARY KEY, id TEXT UNIQUE, layer TEXT, type TEXT, path TEXT, line INT,
                             title TEXT, status TEXT, ts TEXT, session TEXT, turn INT, hash TEXT, src TEXT);
            CREATE INDEX doc_src ON doc(src);
            CREATE INDEX doc_session ON doc(session, turn);
            CREATE VIRTUAL TABLE fts USING fts5(title, tags, body, tokenize="porter unicode61 remove_diacritics 2");
            CREATE TABLE entity(eid INTEGER PRIMARY KEY, name TEXT UNIQUE, kind TEXT, stem TEXT);
            CREATE INDEX entity_stem ON entity(stem);
            CREATE TABLE mention(eid INT, rid INT, PRIMARY KEY(eid, rid)) WITHOUT ROWID;
            CREATE INDEX mention_rid ON mention(rid);
            CREATE TABLE file(path TEXT PRIMARY KEY, mtime INT, size INT);
        """)
        db.execute("PRAGMA user_version=%d" % SCHEMA_VERSION)
        db.commit()
    return db


def drop_src(db, src: str):
    rids = [r[0] for r in db.execute("SELECT rid FROM doc WHERE src=?", (src,))]
    for i in range(0, len(rids), 500):
        part = rids[i:i + 500]
        q = ",".join("?" * len(part))
        db.execute("DELETE FROM fts WHERE rowid IN (%s)" % q, part)
        db.execute("DELETE FROM mention WHERE rid IN (%s)" % q, part)
    db.execute("DELETE FROM doc WHERE src=?", (src,))
    db.execute("DELETE FROM file WHERE path=?", (src,))


def add_doc(db, vocab, d: dict, files=()):
    body = d["body"]
    h = hashlib.sha1((d["title"] + "\n" + body).encode("utf-8")).hexdigest()[:16]
    cur = db.execute("INSERT OR REPLACE INTO doc(id,layer,type,path,line,title,status,ts,session,turn,hash,src) "
                     "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                     (d["id"], d["layer"], d["type"], d["path"], d.get("line", 1), d["title"], d.get("status", "active"),
                      d.get("ts", ""), d.get("session"), d.get("turn"), h, d["src"]))
    rid = cur.lastrowid
    db.execute("INSERT INTO fts(rowid,title,tags,body) VALUES(?,?,?,?)", (rid, d["title"], d.get("tags", ""), body))
    for name, kind, stem in extract_entities(d["title"] + "\n" + body, vocab, files):
        db.execute("INSERT OR IGNORE INTO entity(name,kind,stem) VALUES(?,?,?)", (name, kind, stem))
        db.execute("INSERT OR IGNORE INTO mention(eid,rid) SELECT eid,? FROM entity WHERE name=?", (rid, name))


def chunk_markdown(text: str):
    """Yields (line, heading, body) per heading section of level 1-3, outside code fences."""
    lines = text.splitlines()
    start, heading, fenced, out = 0, "", False, []
    for i, line in enumerate(lines):
        if RX_FENCE.match(line):
            fenced = not fenced
        m = None if fenced else RX_HEADING.match(line)
        if m:
            out.append((start, heading, lines[start:i]))
            start, heading = i, m.group(2)
    out.append((start, heading, lines[start:]))
    for start, heading, body in out:
        body_text = "\n".join(body).strip()
        if not body_text:
            continue
        if len(body_text) <= MAX_CHUNK_CHARS:
            yield start + 1, heading, body_text
            continue
        piece, piece_line = "", start + 1
        for para in re.split(r"\n\s*\n", body_text):
            if piece and len(piece) + len(para) > MAX_CHUNK_CHARS:
                yield piece_line, heading, piece
                piece_line, piece = piece_line + piece.count("\n") + 2, ""
            piece = (piece + "\n\n" + para) if piece else para
        if piece:
            yield piece_line, heading, piece


def knowledge_type(path: str) -> str:
    p = path.lower()
    stem = p.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    if p.startswith("docs/adr/"):
        return "adr"
    if p.startswith(".workflow/"):
        return "workflow"
    if p.startswith(".claude/skills/"):
        return "skill"
    if p.startswith(".claude/agents/"):
        return "agent"
    if p.startswith(".claude/rules/"):
        return "rule"
    if stem in FEATURE_DOCS and not p.count("/") == 0:
        return "feature-doc"
    return "doc"


def index_knowledge(db, vocab, root: Path, path: str):
    text = (root / path).read_text(encoding="utf-8", errors="replace")
    meta, body, offset = parse_frontmatter(text)
    ktype = knowledge_type(path)
    superseded = False
    seen = set()
    doc_title = meta.get("name") if isinstance(meta.get("name"), str) and meta.get("name") else path.rsplit("/", 1)[-1]
    if not isinstance(meta.get("description"), str):
        meta["description"] = ""
    first = True
    for line, heading, chunk in chunk_markdown(body):
        if first:
            # Only the doc's own header can supersede it, not a status line quoted further down.
            superseded = bool(re.search(r"(?im)^[-*\s]*status:\s*superseded", chunk))
        base = slug = slugify(heading) if heading else ""
        n = 1
        while slug in seen:
            n += 1
            slug = "%s-%d" % (base, n)
        seen.add(slug)
        if first and meta.get("description"):
            chunk = meta["description"] + "\n\n" + chunk
        first = False
        add_doc(db, vocab, {
            "id": "k:" + path + ("#" + slug if slug else ""), "layer": "K", "type": ktype, "path": path,
            "line": line + offset, "title": doc_title + (" > " + heading if heading else ""),
            "tags": " ".join(meta.get("tags", []) if isinstance(meta.get("tags"), list) else [ktype]),
            "body": chunk, "status": "superseded" if superseded else "active", "src": path,
        }, files=[path])
    if not seen and meta.get("description"):
        add_doc(db, vocab, {"id": "k:" + path, "layer": "K", "type": ktype, "path": path, "line": 1,
                            "title": doc_title, "body": meta["description"], "src": path})


def index_note(db, vocab, root: Path, path: str):
    text = (root / path).read_text(encoding="utf-8", errors="replace")
    meta, body, _ = parse_frontmatter(text)
    ntype = path.split("/")[2] if path.count("/") >= 3 else meta.get("type", "note")
    stem = path.rsplit("/", 1)[-1][:-3]
    tags = meta.get("tags") if isinstance(meta.get("tags"), list) else []
    paths = meta.get("paths") if isinstance(meta.get("paths"), list) else []
    add_doc(db, vocab, {
        "id": "m:%s/%s" % (ntype, stem), "layer": "M", "type": ntype, "path": path, "line": 1,
        "title": meta.get("name", stem), "tags": " ".join(tags),
        "body": (meta.get("description", "") + "\n\n" + body.strip()).strip(),
        "status": meta.get("status", "active") or "active", "ts": str(meta.get("updated", "")), "src": path,
    }, files=paths)


def index_trace(db, vocab, root: Path, path: str):
    session = path.rsplit("/", 1)[-1][:-6]
    with open(root / path, encoding="utf-8", errors="replace") as f:
        for n, line in enumerate(f, 1):
            try:
                t = json.loads(line)
            except ValueError:
                continue
            if not isinstance(t, dict):
                continue
            role = t.get("role", "?")
            body = t.get("text", "")
            if t.get("files"):
                body += "\nfiles: " + " ".join(t["files"])
            if t.get("tools"):
                body += "\ntools: " + " ".join(t["tools"])
            add_doc(db, vocab, {
                "id": "t:%s#%d" % (session, n), "layer": "T", "type": role, "path": path, "line": n,
                "title": role + (" " + t["agent"] if t.get("agent") else ""), "body": body,
                "ts": t.get("ts", ""), "session": session, "turn": n, "src": path,
            }, files=t.get("files") or ())


def refresh(root: Path, full=False, seconds: float = 0) -> sqlite3.Connection:
    """Brings the index up to date. seconds > 0 stops early; progress is committed in batches and resumes next call."""
    deadline = time.monotonic() + seconds if seconds > 0 else None
    mem = root / ".memory"
    db = open_db(mem)
    if full:
        for t in ("doc", "fts", "entity", "mention", "file"):
            db.execute("DELETE FROM %s" % t)
    inc, exc = read_sources(mem)
    wanted = {}
    # Traces and notes are read from disk too: a repo may gitignore its traces and still query them locally.
    own = []
    for sub in ("traces", "notes"):
        d = mem / sub
        if d.is_dir():
            own += [rel(root, Path(dp) / f) for dp, _, files in os.walk(d) for f in files]
    for p in sorted(set(list_files(root)) | set(own)):
        low = p.lower()
        if low.startswith(".memory/"):
            if low.startswith(".memory/traces/") and low.endswith(".jsonl"):
                wanted[p] = index_trace
            elif low.startswith(".memory/notes/") and low.endswith(".md"):
                wanted[p] = index_note
        elif low.endswith(".md") and any(r.match(p) for r in inc) and not any(r.match(p) for r in exc):
            wanted[p] = index_knowledge
    known = {r[0]: (r[1], r[2]) for r in db.execute("SELECT path,mtime,size FROM file")}
    vocab = None
    changed = False
    for p in set(known) - set(wanted):
        drop_src(db, p)
        changed = True
    done = 0
    for p, fn in wanted.items():
        try:
            st = os.stat(root / p)
        except OSError:  # tracked but deleted in the working tree
            if p in known:
                drop_src(db, p)
                changed = True
            continue
        sig = (st.st_mtime_ns, st.st_size)
        if known.get(p) == sig:
            continue
        if deadline and time.monotonic() > deadline:
            refresh.partial = True
            break
        vocab = vocab or Vocab(root)
        drop_src(db, p)
        fn(db, vocab, root, p)
        db.execute("INSERT OR REPLACE INTO file(path,mtime,size) VALUES(?,?,?)", (p, sig[0], sig[1]))
        changed = True
        done += 1
        if done % 200 == 0:
            db.commit()
    if changed:
        db.execute("DELETE FROM entity WHERE eid NOT IN (SELECT eid FROM mention)")
    db.commit()
    return db


# ---------------------------------------------------------------- retrieval

def fts_query(text: str) -> str | None:
    phrases = re.findall(r'"([^"]+)"', text)
    rest = re.sub(r'"[^"]*"', " ", text)
    terms = ['"%s"' % " ".join(RX_WORD.findall(p)) for p in phrases if RX_WORD.findall(p)]
    words = [w for w in RX_WORD.findall(rest.lower()) if len(w) > 1 and w not in STOPWORDS]
    terms += ['"%s"*' % w for w in dict.fromkeys(words)]
    return " OR ".join(terms[:16]) or None


def link_entities(db, text: str, vocab: Vocab) -> set[int]:
    cands = {n for n, _, _ in extract_entities(text, vocab)}
    words = [w.lower() for w in RX_WORD.findall(text)]
    for n in (1, 2, 3):
        for i in range(len(words) - n + 1):
            gram = words[i:i + n]
            if n == 1 and (len(gram[0]) < 3 or gram[0] in STOPWORDS):
                continue
            for sep in ("-", "", "_", "."):
                cands.add(sep.join(gram))
    if not cands:
        return set()
    cands = sorted(cands)[:400]  # sorted: set order changes per process under -I
    q = ",".join("?" * len(cands))
    rows = db.execute("SELECT e.eid, e.name, e.stem, (SELECT COUNT(*) FROM mention m WHERE m.eid=e.eid) FROM entity e "
                      "WHERE e.name IN (%s) OR e.stem IN (%s)" % (q, q), cands + cands).fetchall()
    names = set(cands)
    per_stem = {}
    for _, name, stem, _ in rows:
        if name not in names:
            per_stem[stem] = per_stem.get(stem, 0) + 1
    # A stem shared by many files (every SKILL.md) identifies nothing; an entity in >200 docs is noise.
    return {eid for eid, name, stem, c in rows if c <= 200 and (name in names or per_stem.get(stem, 0) <= 3)}


def resolve_entity(db, name: str, vocab: Vocab) -> set[int]:
    exact = {r[0] for r in db.execute("SELECT eid FROM entity WHERE name=?", (name.lower(),))}
    return exact or link_entities(db, name, vocab)


def where_clause(a) -> tuple[str, list]:
    w, p = [], []
    if a.layer:
        w.append("d.layer IN (%s)" % ",".join("?" * len(a.layer)))
        p += list(a.layer.upper())
    if a.type:
        w.append("d.type=?")
        p.append(a.type)
    if a.since:
        w.append("d.ts>=?")
        p.append(a.since)
    if not a.all:
        w.append("d.status!='superseded'")
    return (" AND " + " AND ".join(w)) if w else "", p


def age_days(ts: str) -> float:
    """Traces are UTC ("2026-10-28T07:58:32.786Z"); notes may carry a date only."""
    for fmt, n in (("%Y-%m-%dT%H:%M:%S", 19), ("%Y-%m-%d", 10)):
        try:
            t = dt.datetime.strptime(ts[:n], fmt).replace(tzinfo=dt.timezone.utc)
            return max(0.0, (dt.datetime.now(dt.timezone.utc) - t).total_seconds() / 86400)
        except ValueError:
            continue
    return 0.0


def search(db, root: Path, a) -> list[sqlite3.Row]:
    vocab = Vocab(root)
    wsql, wp = where_clause(a)
    lists = []
    fq = fts_query(a.text)
    if fq:
        rows = db.execute("SELECT d.rid FROM fts JOIN doc d ON d.rid=fts.rowid WHERE fts MATCH ?%s "
                          "ORDER BY bm25(fts, 8.0, 4.0, 1.0) LIMIT 60" % wsql, [fq] + wp).fetchall()
        lists.append((1.0, [r[0] for r in rows]))
    linked = link_entities(db, a.text, vocab)
    if a.entity:
        forced = resolve_entity(db, a.entity, vocab)
        if not forced:
            return []
        linked |= forced
    if linked:
        q = ",".join("?" * len(linked))
        rows = db.execute("SELECT m.rid FROM mention m JOIN doc d ON d.rid=m.rid WHERE m.eid IN (%s)%s "
                          "GROUP BY m.rid ORDER BY COUNT(*) DESC, d.ts DESC LIMIT 60" % (q, wsql), list(linked) + wp).fetchall()
        lists.append((1.0, [r[0] for r in rows]))
        hop = [r[0] for r in db.execute(
            "SELECT m2.eid FROM mention m1 JOIN mention m2 ON m1.rid=m2.rid JOIN entity e ON e.eid=m2.eid "
            "WHERE m1.eid IN (%s) AND m2.eid NOT IN (%s) AND e.kind!='id' "
            "AND (SELECT COUNT(*) FROM mention m3 WHERE m3.eid=m2.eid) <= 200 GROUP BY m2.eid ORDER BY COUNT(*) DESC LIMIT 5"
            % (q, q), list(linked) * 2)]
        if hop:
            hq = ",".join("?" * len(hop))
            rows = db.execute("SELECT m.rid FROM mention m JOIN doc d ON d.rid=m.rid WHERE m.eid IN (%s)%s "
                              "GROUP BY m.rid ORDER BY COUNT(*) DESC, d.ts DESC LIMIT 30" % (hq, wsql), hop + wp).fetchall()
            lists.append((0.4, [r[0] for r in rows]))
    score = {}
    for weight, rids in lists:
        for rank, rid in enumerate(rids):
            score[rid] = score.get(rid, 0.0) + weight / (60 + rank)
    if a.entity:
        q = ",".join("?" * len(forced))
        allowed = {r[0] for r in db.execute("SELECT rid FROM mention WHERE eid IN (%s)" % q, list(forced))}
        score = {k: v for k, v in score.items() if k in allowed} if score else {k: 1.0 for k in allowed}
    if not score:
        return []
    db.row_factory = sqlite3.Row
    ids = list(score)
    docs = {}
    for i in range(0, len(ids), 500):
        part = ids[i:i + 500]
        for r in db.execute("SELECT d.*, f.body FROM doc d JOIN fts f ON f.rowid=d.rid WHERE d.rid IN (%s)%s"
                            % (",".join("?" * len(part)), wsql), part + wp):
            docs[r["rid"]] = r
    for rid, r in docs.items():
        s = score[rid] * LAYER_PRIOR.get(r["layer"], 1.0)
        if r["layer"] == "T":
            s *= 0.5 ** (age_days(r["ts"]) / TRACE_HALF_LIFE_DAYS)
        score[rid] = s
    # Deterministic calibration: one copy per content hash, at most 2 turns per session and 3 chunks per file.
    out, hashes, per = [], set(), {}
    for rid in sorted(docs, key=lambda k: -score[k]):
        r = docs[rid]
        key = r["session"] or r["path"]
        cap = 2 if r["layer"] == "T" else 3
        if r["hash"] in hashes or per.get(key, 0) >= cap:
            continue
        hashes.add(r["hash"])
        per[key] = per.get(key, 0) + 1
        out.append(r)
    return out


def snippet(body: str, text: str, width=160) -> str:
    flat = re.sub(r"\s+", " ", body).strip()
    low = flat.lower()
    pos = -1
    for w in sorted(RX_WORD.findall(text.lower()), key=len, reverse=True):
        if len(w) > 2 and w not in STOPWORDS:
            pos = low.find(w)
            if pos >= 0:
                break
    start = max(0, pos - width // 3) if pos > width // 2 else 0
    s = flat[start:start + width]
    return ("..." if start else "") + s + ("..." if start + width < len(flat) else "")


def line_of(r, text: str) -> str:
    """Only what the id does not say: a T role, a K line and kind. `get` prints the path."""
    head = {"T": "%s %s" % (r["id"], r["type"]), "K": "%s :%s %s" % (r["id"], r["line"], r["type"])}.get(r["layer"], r["id"])
    return "%s | %s" % (head, snippet(r["body"], text))


def capped(text: str, cap: int) -> str:
    return text if len(text) <= cap else text[:cap] + "\n[+%d chars; --full]" % (len(text) - cap)


def print_budgeted(lines: list[str], budget: int, n: int):
    used, shown = 0, 0
    for line in lines[:n]:
        if shown and used + len(line) > budget:
            break
        print(line)
        used += len(line) + 1
        shown += 1
    if len(lines) > shown:
        print("(+%d more)" % (len(lines) - shown))


# ---------------------------------------------------------------- capture (Stop hook)

def clean_prompt(text: str) -> str:
    text = RX_HARNESS.sub("", text)
    text = RX_TAG_KEEP.sub("", text)
    return text.strip()


RX_HANDBACK = re.compile(r"\[Subagent hand-back\].*?The report follows:[ \t]*\n", re.S)


def unwrap_agent(text: str) -> str:
    """An agent's own report, without the harness's hand-back preamble, notes and indentation."""
    text = re.sub(r"<tools-used-before-summary>.*?</tools-used-before-summary>", "", text, flags=re.S)
    text = re.sub(r"(?m)^[ \t]*\[harness:[^\n]*\][ \t]*\n?", "", text)  # before dedent: an unindented note blocks it
    m = RX_HANDBACK.search(text)
    if m:
        text = textwrap.dedent(text[m.end():])
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def block_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def repo_path(root: Path, p: str) -> str | None:
    if not p:
        return None
    q = p.replace("\\", "/")
    r = root.as_posix().rstrip("/")
    if q.lower().startswith(r.lower() + "/"):
        return q[len(r) + 1:]
    q = re.sub(r"^(\./)+", "", q)
    # A relative path counts only when its first folder exists in the repo (never ~/..., ../..., C:...).
    if q and not re.match(r"^([a-zA-Z]:|/|~|\.\.)", q) and (root / q.split("/")[0]).exists():
        return q
    return None


def parse_transcript(root: Path, transcript: Path) -> list[dict]:
    turns, pending = [], {"text": [], "tools": [], "files": [], "ts": ""}
    special = {}  # tool_use id -> ("agent", name) | ("answer", None)

    def flush():
        if pending["text"] or pending["files"]:
            turns.append({"role": "assistant", "ts": pending.get("ts", ""), "text": "\n\n".join(pending["text"]),
                          "tools": sorted(set(pending["tools"])), "files": sorted(set(pending["files"]))})
        pending.update(text=[], tools=[], files=[], ts="")

    queued = set()  # queued commands not yet seen delivered
    agent_ids = {}  # agentId from a launch receipt -> agent type

    def user_text(raw: str, ts: str, is_queued=False):
        agent = None
        if "<agent-message" in raw:  # a subagent's report handed back into the main session
            m = re.search(r'<agent-message from="([^"]*)">(.*?)</agent-message>', raw, re.S)
            if not m:
                return
            role, text, agent = "agent", unwrap_agent(m.group(2)), agent_ids.get(m.group(1))
        elif "<task-notification>" in raw:
            summ = re.search(r"<summary>(.*?)</summary>", raw, re.S)
            res = re.search(r"<result>(.*?)</result>", raw, re.S)
            if not res or "was delivered to you as a message from" in res.group(1):
                return  # no result, or only a pointer to the agent-message captured above
            use = re.search(r"<tool-use-id>(.*?)</tool-use-id>", raw)
            kind = special.get(use.group(1).strip()) if use else None
            agent = kind[1] if kind and kind[0] == "agent" else None
            role, text = "agent", ((summ.group(1).strip() + "\n\n") if summ else "") + unwrap_agent(res.group(1))
        else:
            role, text = "user", clean_prompt(raw)
            if not text or text.startswith("[Request interrupted"):
                return
        # A queued command is logged again when delivered: skip only that second copy; repeated prompts stay.
        key = (role, hashlib.sha1(text.encode("utf-8")).hexdigest())
        if is_queued:
            queued.add(key)
        elif key in queued:
            queued.discard(key)
            return
        else:
            queued.clear()  # a queued command never delivered must not swallow a later identical prompt
        flush()
        turn = {"role": role, "ts": ts, "text": text}
        if agent:
            turn["agent"] = agent
        turns.append(turn)

    with open(transcript, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if not isinstance(e, dict):
                continue
            # A subagent's report arrives as a meta "peer" message: keep it, but only ever as an agent turn.
            peer = isinstance(e.get("origin"), dict) and e["origin"].get("kind") == "peer"
            if e.get("isSidechain") or (e.get("isMeta") and not peer) or e.get("isCompactSummary"):
                continue
            if peer:
                raw = block_text(e["message"].get("content")) if isinstance(e.get("message"), dict) else ""
                if "<agent-message" in raw:
                    user_text(raw, e.get("timestamp", ""))
                continue
            msg = e.get("message") if isinstance(e.get("message"), dict) else {}
            ts = e.get("timestamp", "")
            content = msg.get("content")
            if e.get("type") == "assistant" and isinstance(content, list):
                for b in content:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "text" and b.get("text", "").strip():
                        if pending["tools"]:
                            flush()  # one assistant turn per message, with the tools used since the last one
                        pending["ts"] = pending["ts"] or ts
                        pending["text"].append(b["text"].strip())
                    elif b.get("type") == "tool_use":
                        name, inp = b.get("name", ""), b.get("input") or {}
                        pending["tools"].append(name)
                        pending["ts"] = pending["ts"] or ts
                        for k in ("file_path", "notebook_path"):
                            rp = repo_path(root, str(inp.get(k, "")))
                            if rp:
                                pending["files"].append(rp)
                        if name in ("Agent", "Task"):
                            flush()
                            agent = inp.get("subagent_type") or "general-purpose"
                            special[b.get("id")] = ("agent", agent)
                            turns.append({"role": "brief", "ts": ts, "agent": agent,
                                          "text": (inp.get("description", "") + "\n\n" + inp.get("prompt", "")).strip()})
                        elif name == "AskUserQuestion":
                            special[b.get("id")] = ("answer", None)
            elif e.get("type") == "user":
                if isinstance(content, str):
                    blocks = [{"type": "text", "text": content}]
                else:
                    blocks = content if isinstance(content, list) else []
                for b in blocks:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "tool_result":
                        kind = special.get(b.get("tool_use_id"))
                        if not kind:
                            continue
                        text = block_text(b.get("content")).strip()
                        if kind[0] == "agent" and text.startswith("Async agent launched"):
                            rid = re.search(r"agentId:\s*([\w-]+)", text)
                            if rid:
                                agent_ids[rid.group(1)] = kind[1]
                            continue  # launch receipt; the result arrives later as a message or notification
                        if kind[0] == "agent":
                            text = unwrap_agent(text)
                        flush()
                        turns.append({"role": "agent" if kind[0] == "agent" else "answer", "ts": ts,
                                      "agent": kind[1], "text": text})
                    elif b.get("type") == "text":
                        user_text(b.get("text", ""), ts)
            elif e.get("type") == "attachment" and isinstance(e.get("attachment"), dict):
                # Background agent results and prompts typed while busy arrive as queued commands.
                a = e["attachment"]
                if a.get("type") == "queued_command" and isinstance(a.get("prompt"), str):
                    user_text(a["prompt"], ts, is_queued=True)
    flush()
    return turns


def capture(root: Path, transcript: str, session: str) -> int:
    if os.environ.get("MEM_CAPTURE") == "0" or not transcript or not os.path.exists(transcript):
        return 0
    mem = root / ".memory"
    sid8 = re.sub(r"[^\w-]", "", session)[:8] or "unknown"
    state_f = mem / ".state" / "capture" / (sid8 + ".json")
    st = os.stat(transcript)
    state = {}
    if state_f.exists():
        try:
            state = json.loads(state_f.read_text(encoding="utf-8"))
        except ValueError:
            state = {}
    if state.get("sig") == [st.st_mtime_ns, st.st_size]:
        return 0
    turns = parse_transcript(root, Path(transcript))
    if not turns:
        return 0
    pats = load_secret_patterns(root)
    existing = sorted((mem / "traces").glob("**/*-%s.jsonl" % sid8)) if (mem / "traces").exists() else []
    if existing:
        out = existing[0]
    else:
        day = (turns[0].get("ts") or "")[:10]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            day = dt.datetime.now(dt.timezone.utc).date().isoformat()
        out = mem / "traces" / day[:4] / day[5:7] / ("%s-%s.jsonl" % (day, sid8))
    # Append-only past a high-water mark: a line edited or deleted by hand never comes back. The mark is kept
    # in state; without state (another machine, cleared .state) it is the highest turn index "n" in the file.
    written = state.get("turns") if state.get("out") == rel(root, out) else None
    if not isinstance(written, int):
        written = high_water(out)
    new = []
    last = state.get("last") if isinstance(state.get("last"), dict) else None
    if last and 0 < written <= len(turns):
        grown = continuation(turns[written - 1], last)  # a turn that kept growing after the previous Stop
        if grown:
            new.append((written - 1, grown))
    new += list(enumerate(turns))[written:]
    lines = [json.dumps(trace_record(root, t, pats, n), ensure_ascii=False) for n, t in new]
    if lines:
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "a", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
    tail = turns[-1]
    state_f.parent.mkdir(parents=True, exist_ok=True)
    write_lf(state_f, json.dumps({"sig": [st.st_mtime_ns, st.st_size], "out": rel(root, out),
                                  "turns": max(written, len(turns)),
                                  "last": {"len": len(tail["text"]), "tools": tail.get("tools", []), "files": tail.get("files", [])}}))
    return len(lines)


def high_water(out: Path) -> int:
    if not out.exists():
        return 0
    marks, count = [], 0
    with open(out, encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.strip():
                continue
            count += 1
            try:
                rec = json.loads(line)
                if isinstance(rec, dict) and isinstance(rec.get("n"), int):
                    marks.append(rec["n"])
            except ValueError:
                pass
    return max(marks) + 1 if marks else count


def continuation(t: dict, last: dict) -> dict | None:
    if t["role"] != "assistant":
        return None
    text = t["text"][last.get("len", 0):].strip() if len(t["text"]) > last.get("len", 0) else ""
    tools = sorted(set(t.get("tools", [])) - set(last.get("tools", [])))
    files = sorted(set(t.get("files", [])) - set(last.get("files", [])))
    if not (text or files):
        return None
    return {"role": "assistant", "ts": t.get("ts", ""), "text": text, "tools": tools, "files": files}


def trace_record(root: Path, t: dict, pats, n: int = 0) -> dict:
    """Absolute paths shrink to <root>/ and ~/ (no OS user name in git), then emails and secrets are redacted."""
    text = t["text"]
    for prefix, short in ((str(root), "<root>"), (str(Path.home()), "~")):
        fwd = prefix.replace("\\", "/")
        variants = {prefix, fwd, prefix.replace("\\", "\\\\")}
        if re.match(r"^[A-Za-z]:/", fwd):
            variants.add("/" + fwd[0].lower() + fwd[2:])  # Git Bash form: /c/Users/...
        for variant in sorted(variants, key=len, reverse=True):
            text = re.sub(re.escape(variant), lambda m: short, text, flags=re.I)
    # Any other path through the user's profile folder still names the OS user, including Claude Code's
    # folder-name form of a path (c--Users-<u>-...).
    leaf = Path.home().name
    if leaf:
        text = re.sub(r"(?i)(?<![A-Za-z0-9])users([\\/]+)" + re.escape(leaf) + r"(?![A-Za-z0-9])", lambda m: "Users" + m.group(1) + "<user>", text)
        # The folder-name form turns every non-alphanumeric into '-', so "first.last" appears as "first-last".
        slug_leaf = "[^A-Za-z0-9]+".join(re.escape(p) for p in re.split(r"[^A-Za-z0-9]+", leaf) if p)
        if slug_leaf:
            text = re.sub(r"(?i)(?<![A-Za-z0-9])([A-Za-z]--)?users-" + slug_leaf + r"(?![A-Za-z0-9])",
                          lambda m: (m.group(1) or "") + "Users-<user>", text)
    text = RX_EMAIL.sub("[REDACTED:email]", redact(text, pats))
    if len(text) > MAX_TURN_CHARS:
        text = text[:MAX_TURN_CHARS] + "\n...[truncated %d chars]" % (len(text) - MAX_TURN_CHARS)
    rec = {"n": n, "ts": t.get("ts", ""), "role": t["role"]}  # n: transcript turn index, the append mark
    if t.get("agent"):
        rec["agent"] = t["agent"]
    rec["text"] = text
    for k in ("tools", "files"):
        if t.get(k):
            rec[k] = t[k]
    return rec


# ---------------------------------------------------------------- commands

def cmd_q(root, a):
    db = refresh(root)
    rows = search(db, root, a)
    if not rows:
        print("no hits")
        return 0
    print_budgeted([line_of(r, a.text) for r in rows], a.budget, a.n)
    return 0


def cmd_get(root, a):
    db = refresh(root)
    db.row_factory = sqlite3.Row
    sel = "SELECT d.*, f.body FROM doc d JOIN fts f ON f.rowid=d.rid "
    r = db.execute(sel + "WHERE d.id=?", (a.id,)).fetchone() or \
        db.execute(sel + "WHERE d.id LIKE ? ORDER BY length(d.id) LIMIT 1", (a.id + "%",)).fetchone()
    if not r:
        print("not found: " + a.id)
        return 1
    if r["layer"] == "T" and a.ctx:
        for n in db.execute(sel + "WHERE d.session=? AND d.turn BETWEEN ? AND ? ORDER BY d.turn",
                            (r["session"], r["turn"] - a.ctx, r["turn"] + a.ctx)):
            body = body_of(n["body"], a) if n["rid"] == r["rid"] else n["body"][:600] + ("..." if len(n["body"]) > 600 else "")
            where = " %s:%s" % (n["path"], n["line"]) if n["rid"] == r["rid"] else ""
            print("## %s%s (%s %s)\n%s\n" % (n["id"], where, n["title"], (n["ts"] or "")[:19], body))
        return 0
    title = "" if r["layer"] == "M" else r["title"] + "\n"  # a note's title is its slug
    print("## %s %s:%s\n%s%s" % (r["id"], r["path"], r["line"], title, body_of(r["body"], a)))
    return 0


def body_of(body: str, a) -> str:
    return body if a.full else capped(body, GET_CAP)


def cmd_ent(root, a):
    db = refresh(root)
    eids = resolve_entity(db, a.name, Vocab(root)) or {r[0] for r in db.execute(
        "SELECT eid FROM entity WHERE name LIKE ?", ("%" + a.name.lower() + "%",))}
    if not eids:
        print("no entity: " + a.name)
        return 1
    q = ",".join("?" * len(eids))
    ents = db.execute("SELECT e.eid, e.name, e.kind, (SELECT COUNT(*) FROM mention m WHERE m.eid=e.eid) c FROM entity e "
                      "WHERE e.eid IN (%s) ORDER BY c DESC, e.name" % q, sorted(eids)).fetchall()
    for eid, name, kind, count in ents[:ENT_CAP]:
        co = db.execute("SELECT e.name, COUNT(*) c FROM mention m1 JOIN mention m2 ON m1.rid=m2.rid JOIN entity e "
                        "ON e.eid=m2.eid WHERE m1.eid=? AND m2.eid!=? GROUP BY e.eid ORDER BY c DESC LIMIT 8", (eid, eid)).fetchall()
        latest = db.execute("SELECT d.id FROM mention m JOIN doc d ON d.rid=m.rid WHERE m.eid=? AND d.status!='superseded' "
                            "ORDER BY CASE d.layer WHEN 'M' THEN 0 WHEN 'K' THEN 1 ELSE 2 END, d.ts DESC LIMIT 6", (eid,)).fetchall()
        print("%s [%s] %d mentions" % (name, kind, count))
        print("  with: " + ", ".join("%s(%d)" % c for c in co))
        print("  see:  " + " . ".join(r[0] for r in latest))
    if len(ents) > ENT_CAP:
        print("(+%d more)" % (len(ents) - ENT_CAP))
    return 0


def cmd_for(root, a):
    db = refresh(root)
    a.text, a.entity = "", file_entity(a.path)[0]
    rows = search(db, root, a)
    if not rows:
        print("no hits")
        return 0
    print_budgeted([line_of(r, "") for r in rows], a.budget, a.n)
    return 0


def cmd_sessions(root, a):
    db = refresh(root)
    rows = db.execute("SELECT session, MIN(ts), COUNT(*) FROM doc WHERE layer='T' AND ts>=? GROUP BY session "
                      "ORDER BY MIN(ts) DESC LIMIT ?", (a.since or "", a.n)).fetchall()
    for session, ts, count in rows:
        first = db.execute("SELECT f.body FROM doc d JOIN fts f ON f.rowid=d.rid WHERE d.session=? AND d.type='user' "
                           "ORDER BY d.turn LIMIT 1", (session,)).fetchone()
        print("%s %s %d turns | %s" % (session, (ts or "")[:16], count, snippet(first[0] if first else "", "", 120)))
    return 0


def cmd_add(root, a):
    if a.type not in NOTE_TYPES:
        print("type must be one of: " + ", ".join(NOTE_TYPES))
        return 1
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", a.slug):
        print("slug must be kebab-case")
        return 1
    f = root / ".memory" / "notes" / a.type / (a.slug + ".md")
    if f.exists():
        print("exists: " + rel(root, f))
        return 1
    items = (a.tags or []) + (a.paths or [])
    if any(re.search(r"[\r\n,\[\]]", x) for x in items):
        print("tags and paths may not contain newlines, commas or brackets")
        return 1
    body = (a.body or "").strip()
    text = "---\nname: %s\ndescription: %s\ntype: %s\ntags: [%s]\npaths: [%s]\nstatus: active\nupdated: %s\n---\n\n%s\n" % (
        a.slug, re.sub(r"[\r\n]+", " ", a.desc), a.type, ", ".join(a.tags or []), ", ".join(a.paths or []),
        dt.date.today().isoformat(), body)
    hits = [n for n, rx in load_secret_patterns(root) if rx.search(text)]
    if hits:
        print("refused: secret-shaped value (%s)" % ", ".join(hits))
        return 1
    f.parent.mkdir(parents=True, exist_ok=True)
    write_lf(f, text)
    print(rel(root, f))
    return 0


def cmd_lint(root, a):
    mem = root / ".memory"
    pats = load_secret_patterns(root)
    errors, names = [], {}
    for f in sorted((mem / "notes").glob("*/*.md")) if (mem / "notes").exists() else []:
        r = rel(root, f)
        meta, _, _ = parse_frontmatter(f.read_text(encoding="utf-8", errors="replace"))
        if f.parent.name not in NOTE_TYPES:
            errors.append("%s: folder must be one of %s" % (r, "|".join(NOTE_TYPES)))
        if meta.get("name") != f.stem:
            errors.append("%s: name must equal the file name" % r)
        if not meta.get("description"):
            errors.append("%s: missing description" % r)
        if meta.get("type") and meta.get("type") != f.parent.name:
            errors.append("%s: type must equal its folder" % r)
        status = meta.get("status", "active")
        if status not in ("active", "superseded"):
            errors.append("%s: status must be active|superseded" % r)
        if status == "superseded" and meta.get("superseded_by"):
            target = mem / "notes" / (meta["superseded_by"] + ".md")
            if not target.exists():
                errors.append("%s: superseded_by points to a missing note" % r)
        names.setdefault(f.stem, []).append(r)
    errors += ["duplicate note name %s: %s" % (n, ", ".join(p)) for n, p in names.items() if len(p) > 1]
    for f in sorted(mem.rglob("*")) if mem.exists() else []:
        if f.is_file() and not ({".index", ".state"} & set(f.relative_to(mem).parts)):
            text = f.read_text(encoding="utf-8", errors="replace")
            if f.suffix == ".jsonl":  # JSON escapes quotes, which hides quoted-value patterns: scan decoded text too
                for line in text.splitlines():
                    try:
                        text += "\n" + str(json.loads(line).get("text", ""))
                    except (ValueError, AttributeError):
                        pass
            for name, rx in pats:
                if rx.search(text):
                    errors.append("%s: secret-shaped value (%s)" % (rel(root, f), name))
    for e in errors:
        print(e)
    print("lint: %d problem(s)" % len(errors) if errors else "lint: clean")
    return 1 if errors else 0


def cmd_stats(root, a):
    refresh.partial = False
    db = refresh(root, seconds=getattr(a, "seconds", 0) or 0)
    c = dict(db.execute("SELECT layer, COUNT(*) FROM doc GROUP BY layer").fetchall())
    s = db.execute("SELECT COUNT(DISTINCT session) FROM doc WHERE layer='T'").fetchone()[0]
    print("T %d turns/%d sessions . M %d notes . K %d chunks%s" % (
        c.get("T", 0), s, c.get("M", 0), c.get("K", 0), " (indexing, continues on next query)" if refresh.partial else ""))
    return 0


def cmd_reindex(root, a):
    refresh(root, full=a.full)
    return cmd_stats(root, a)


def cmd_capture(root, a):
    try:
        n = capture(root, a.transcript, a.session)
    except Exception as ex:  # A hook must never break the session; capture is best effort.
        print("mem capture skipped: %s" % ex, file=sys.stderr)
        return 0
    if n and a.verbose:
        print("captured %d turns" % n)
    return 0


def main(argv=None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    p = argparse.ArgumentParser(prog="mem", description="Zero-Mem store: traces (T), notes (M), knowledge (K).")
    p.add_argument("--root", help="project root (default: derived from this script's location)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def filters(sp, text=True):
        if text:
            sp.add_argument("text")
        sp.add_argument("-l", "--layer", help="any of T, M, K, e.g. MK")
        sp.add_argument("-t", "--type")
        sp.add_argument("-e", "--entity")
        sp.add_argument("--since", help="YYYY-MM-DD")
        sp.add_argument("-n", type=int, default=8)
        sp.add_argument("--budget", type=int, default=1200, help="max output characters")
        sp.add_argument("--all", action="store_true", help="include superseded entries")

    filters(sub.add_parser("q", help="ranked search"))
    g = sub.add_parser("get", help="entry with its file path; --ctx N adds neighbouring turns")
    g.add_argument("id")
    g.add_argument("--ctx", type=int, default=0)
    g.add_argument("--full", action="store_true", help="no %d-char cap" % GET_CAP)
    sub.add_parser("ent", help="entity card").add_argument("name")
    f = sub.add_parser("for", help="entries mentioning a file")
    f.add_argument("path")
    filters(f, text=False)
    s = sub.add_parser("sessions", help="captured sessions, newest first")
    s.add_argument("--since")
    s.add_argument("-n", type=int, default=8)
    ad = sub.add_parser("add", help="scaffold a note")
    ad.add_argument("type")
    ad.add_argument("slug")
    ad.add_argument("--desc", required=True)
    ad.add_argument("--tags", nargs="*")
    ad.add_argument("--paths", nargs="*")
    ad.add_argument("--body")
    sub.add_parser("lint", help="validate notes and scan .memory for secrets")
    sub.add_parser("stats", help="entry counts per layer").add_argument(
        "--seconds", type=float, default=0, help="stop indexing after this long (session start)")
    sub.add_parser("reindex", help="refresh the index, then stats").add_argument(
        "--full", action="store_true", help="rebuild from scratch")
    c = sub.add_parser("capture", help="Stop hook: transcript -> .memory/traces")
    c.add_argument("--transcript", required=True)
    c.add_argument("--session", required=True)
    c.add_argument("--verbose", action="store_true")
    a = p.parse_args(argv)
    root = find_root(a.root)
    try:
        return _dispatch(root, a)
    except (RuntimeError, re.error, ValueError, OSError) as ex:  # e.g. a broken or missing secret-patterns.txt
        print("mem: %s" % ex, file=sys.stderr)
        return 1
    finally:
        while _connections:
            _connections.pop().close()


def _dispatch(root, a) -> int:
    return {"q": cmd_q, "get": cmd_get, "ent": cmd_ent, "for": cmd_for, "sessions": cmd_sessions, "add": cmd_add,
            "lint": cmd_lint, "stats": cmd_stats, "reindex": cmd_reindex, "capture": cmd_capture}[a.cmd](root, a)


if __name__ == "__main__":
    sys.exit(main())
