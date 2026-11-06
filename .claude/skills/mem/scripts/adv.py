"""Advisory store: adviser returns and their findings in SQLite, off git. Deterministic, stdlib only, no LLM.

The database is the record (unlike mem.py's index, nothing rebuilds it), so it lives outside .memory/.index/.
Every write first proves the path is git-ignored: advice carries observed revenue and retention figures.
Run: python -I adv.py --root <project root> <cmd>. Tests: python -I test_adv.py.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

DB_REL = ".memory/advisory/advisory.db"
DECISIONS = ("accepted", "rejected", "deferred")
MAIN_GD = "main GD"
SCHEMA = """
CREATE TABLE advice(
    id INTEGER PRIMARY KEY, ts TEXT NOT NULL, session TEXT, agent TEXT NOT NULL, agent_id TEXT, workflow TEXT,
    thread TEXT, target TEXT, data_period TEXT, brief TEXT, body TEXT NOT NULL, digest TEXT NOT NULL);
CREATE UNIQUE INDEX advice_once ON advice(agent, COALESCE(agent_id, ''), digest);
CREATE TABLE finding(
    id INTEGER PRIMARY KEY, advice INTEGER NOT NULL REFERENCES advice(id), k INTEGER NOT NULL, severity TEXT,
    title TEXT NOT NULL, body TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open', decided_by TEXT, decided_at TEXT,
    note TEXT, useful INTEGER, UNIQUE(advice, k));
CREATE INDEX finding_status ON finding(status);
CREATE INDEX advice_thread ON advice(thread);
CREATE VIRTUAL TABLE fts USING fts5(ref UNINDEXED, agent, title, body, tokenize="porter unicode61 remove_diacritics 2");
"""
RX_FINDING = re.compile(r"(?m)^### F(\d+)(?:[ \t]+\[([A-Za-z]+)\])?[ \t]*(.*)$")
RX_MARKER = {name: re.compile(r"(?im)^[\s*_>-]*%s[*_]*:[*_`\s]*([^\r\n`]+)" % re.escape(label))
             for name, label in (("workflow", "Workflow"), ("thread", "Advisory-Thread"), ("target", "Target"),
                                 ("data_period", "Data-Period"), ("feature", "Feature"))}
# Copied from mem.py: this script runs with -I, which keeps a sibling import off sys.path.
RX_PEM_BLOCK = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?(?:-----END [A-Z ]*PRIVATE KEY-----|$)")
RX_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b")
RX_DEVICE_ID = re.compile(r"(?i)(\b(?:adid|idfa|idfv|gaid|aaid|advertising[ _-]?id|device[ _-]?id|android[ _-]?id|installation[ _-]?id)\b[^0-9A-Za-z\n]{0,20})[0-9A-Fa-f][0-9A-Fa-f-]{15,35}\b")
RX_IPV4 = re.compile(r"(?<![\d.])(?!127\.|0\.0\.0\.0)(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)(?![\d.])")
RX_PHONE = re.compile(r"(?<![\w+])\+\d[\d ()-]{8,}\d\b")


class Refused(Exception):
    pass


def git_exe() -> str:
    """git's full path from PATH alone: a bare "git" on Windows would run a git.exe in the current folder first."""
    names = ("git.exe", "git.cmd", "git.bat") if os.name == "nt" else ("git",)
    for folder in os.environ.get("PATH", "").split(os.pathsep):
        folder = folder.strip().strip('"')
        if os.path.isabs(folder):
            for name in names:
                path = os.path.join(folder, name)
                if os.path.isfile(path) and os.access(path, os.X_OK):
                    return path
    raise Refused("git not found on PATH, so the store cannot prove it is ignored")


def find_root(arg):
    return Path(arg).resolve() if arg else Path(__file__).resolve().parents[4]


def require_ignored(root: Path, rel: str):
    """Fail closed: not ignored, not a repository or no git all refuse the write."""
    r = subprocess.run([git_exe(), "-C", str(root), "check-ignore", "-q", "--", rel], capture_output=True)
    if r.returncode == 1:
        raise Refused("%s is not git-ignored: add .memory/advisory/ to .gitignore first" % rel)
    if r.returncode != 0:
        raise Refused("cannot prove %s is git-ignored: %s" % (rel, r.stderr.decode("utf-8", "replace").strip()))


def secret_patterns(root: Path):
    f = root / ".claude" / "hooks" / "secret-patterns.txt"
    if not f.exists():
        f = Path(__file__).resolve().parents[3] / "hooks" / "secret-patterns.txt"
    out = []
    for line in f.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            name, rx = line.split("\t", 1)
            out.append((name, re.compile(rx)))
    if not out:
        raise Refused("no secret patterns in %s" % f)
    return out


def refuse_secrets(root: Path, text: str):
    hits = [name for name, rx in secret_patterns(root) if rx.search(text)]
    if RX_PEM_BLOCK.search(text):
        hits.append("private key")
    if hits:
        raise Refused("secret-shaped value (%s); nothing stored" % ", ".join(sorted(set(hits))))


def redact_pii(text: str) -> str:
    text = RX_EMAIL.sub("[REDACTED:email]", text)
    text = RX_DEVICE_ID.sub(lambda m: m.group(1) + "[REDACTED:device id]", text)
    text = RX_IPV4.sub("[REDACTED:ip]", text)
    return RX_PHONE.sub("[REDACTED:phone]", text)


def clean(root: Path, text: str) -> str:
    refuse_secrets(root, text)
    return redact_pii(text)


def open_db(root: Path, write: bool):
    path = root / DB_REL
    if write:
        require_ignored(root, DB_REL)
        path.parent.mkdir(parents=True, exist_ok=True)
    elif not path.exists():
        return None
    db = sqlite3.connect(str(path), timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='advice'").fetchone():
        db.executescript(SCHEMA)
    return db


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def marker(brief: str, name: str):
    m = RX_MARKER[name].search(brief or "")
    return m.group(1).strip() if m else None


def split_findings(body: str):
    """Findings by the fixed `### F<n> [Severity] title` heading of skill advisory-protocol. A repeated number keeps the first."""
    heads = list(RX_FINDING.finditer(body))
    seen, out = set(), []
    for i, m in enumerate(heads):
        k = int(m.group(1))
        if k in seen:
            continue
        seen.add(k)
        end = heads[i + 1].start() if i + 1 < len(heads) else len(body)
        out.append({"k": k, "severity": m.group(2), "title": m.group(3).strip() or "F%d" % k, "body": body[m.end():end].strip()})
    return out


def parse_ref(ref: str):
    """adv:12 is a return, adv:12.3 its finding 3."""
    m = re.fullmatch(r"(?:adv:)?(\d+)(?:\.(\d+))?", ref.strip())
    if not m:
        raise Refused("bad id %r: use adv:<n> or adv:<n>.<k>" % ref)
    return int(m.group(1)), int(m.group(2)) if m.group(2) else None


def cmd_ingest(root, a):
    if a.file:
        data = json.loads(Path(a.file).read_text(encoding="utf-8-sig"))
    else:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    agent = data.get("agent")
    body = (data.get("return") or "").strip()
    if not agent or not body:
        raise Refused("ingest needs agent and return")
    brief = data.get("brief") or ""
    body_clean, brief_clean = clean(root, body), clean(root, brief)
    db = open_db(root, True)
    # SubagentStop can fire more than once for one return, and a duplicate would inflate the follow-up count.
    digest = hashlib.sha256(body_clean.encode("utf-8")).hexdigest()
    seen = db.execute("SELECT id FROM advice WHERE agent=? AND COALESCE(agent_id,'')=? AND digest=?", (agent, data.get("agent_id") or "", digest)).fetchone()
    if seen:
        print("adv:%d (already stored)" % seen["id"])
        return 0
    with db:
        cur = db.execute("INSERT INTO advice(ts,session,agent,agent_id,workflow,thread,target,data_period,brief,body,digest) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                         (now(), data.get("session"), agent, data.get("agent_id"), marker(brief_clean, "workflow"), marker(brief_clean, "thread"),
                          marker(brief_clean, "target") or marker(brief_clean, "feature"), marker(brief_clean, "data_period"), brief_clean, body_clean, digest))
        rid = cur.lastrowid
        findings = split_findings(body_clean)
        for f in findings:
            db.execute("INSERT INTO finding(advice,k,severity,title,body) VALUES(?,?,?,?,?)", (rid, f["k"], f["severity"], f["title"], f["body"]))
            db.execute("INSERT INTO fts(ref,agent,title,body) VALUES(?,?,?,?)", ("adv:%d.%d" % (rid, f["k"]), agent, f["title"], f["body"]))
        if not findings:
            db.execute("INSERT INTO fts(ref,agent,title,body) VALUES(?,?,?,?)", ("adv:%d" % rid, agent, marker(brief_clean, "thread") or "", body_clean))
    print("adv:%d (%d findings)" % (rid, len(findings)))
    return 0


def fts_query(words: str) -> str:
    terms = re.findall(r"[^\W_]+", words, re.UNICODE)
    if not terms:
        raise Refused("query has no words")
    return " OR ".join('"%s"' % t for t in terms)


def cmd_q(root, a):
    db = open_db(root, False)
    if not db:
        print("no advisory store yet")
        return 0
    sql = "SELECT ref, agent, title, snippet(fts, 3, '', '', '...', 24) AS snip FROM fts WHERE fts MATCH ?"
    args = [fts_query(a.words)]
    if a.agent:
        sql += " AND agent = ?"
        args.append(a.agent)
    for r in db.execute(sql + " ORDER BY rank LIMIT ?", args + [a.n]):
        print("%s %s | %s | %s" % (r["ref"], r["agent"], r["title"], r["snip"].replace("\n", " ")))
    return 0


def cmd_get(root, a):
    rid, k = parse_ref(a.id)
    db = open_db(root, False)
    row = db.execute("SELECT * FROM advice WHERE id=?", (rid,)).fetchone() if db else None
    if not row:
        raise Refused("adv:%d not found" % rid)
    if k is None:
        print("## adv:%d %s %s workflow=%s thread=%s target=%s data=%s\n\n%s" % (
            rid, row["ts"], row["agent"], row["workflow"], row["thread"], row["target"], row["data_period"], row["body"]))
        return 0
    f = db.execute("SELECT * FROM finding WHERE advice=? AND k=?", (rid, k)).fetchone()
    if not f:
        raise Refused("adv:%d.%d not found" % (rid, k))
    print("## adv:%d.%d %s [%s] %s\nstatus: %s by=%s at=%s useful=%s\nnote: %s\n\n%s" % (
        rid, k, row["agent"], f["severity"], f["title"], f["status"], f["decided_by"], f["decided_at"], f["useful"], f["note"], f["body"]))
    return 0


def cmd_list(root, a):
    db = open_db(root, False)
    if not db:
        print("no advisory store yet")
        return 0
    sql = ("SELECT a.id AS rid, f.k, a.ts, a.agent, a.workflow, a.thread, f.severity, f.title, f.status, f.useful "
           "FROM advice a LEFT JOIN finding f ON f.advice = a.id WHERE 1=1")
    args = []
    for col, val in (("a.agent", a.agent), ("a.workflow", a.workflow), ("a.thread", a.thread), ("f.status", a.status)):
        if val:
            sql += " AND %s = ?" % col
            args.append(val)
    for r in db.execute(sql + " ORDER BY a.id DESC, f.k LIMIT ?", args + [a.n]):
        ref = "adv:%d" % r["rid"] + (".%d" % r["k"] if r["k"] is not None else "")
        print("%s %s %s %s [%s] %s | %s useful=%s" % (ref, r["ts"][:10], r["agent"], r["thread"] or "-", r["severity"] or "-", r["title"] or "-", r["status"] or "-", r["useful"]))
    return 0


def one_finding(db, ref):
    rid, k = parse_ref(ref)
    if k is None:
        raise Refused("%s names a return: use adv:<n>.<k>" % ref)
    row = db.execute("SELECT id FROM finding WHERE advice=? AND k=?", (rid, k)).fetchone()
    if not row:
        raise Refused("adv:%d.%d not found" % (rid, k))
    return row["id"]


def cmd_decide(root, a):
    if a.by != MAIN_GD:
        raise Refused("decide is main GD only: pass --by 'main GD' on the main GD's order")
    note = clean(root, a.note or "")
    db = open_db(root, True)
    fid = one_finding(db, a.id)
    with db:
        db.execute("UPDATE finding SET status=?, decided_by=?, decided_at=?, note=? WHERE id=?", (a.decision, a.by, now(), note, fid))
    print("%s %s" % (a.id, a.decision))
    return 0


def cmd_useful(root, a):
    db = open_db(root, True)
    fid = one_finding(db, a.id)
    with db:
        db.execute("UPDATE finding SET useful=? WHERE id=?", (1 if a.value == "yes" else 0, fid))
    print("%s useful=%s" % (a.id, a.value))
    return 0


def cmd_rounds(root, a):
    """Follow-up rounds in a thread: its returns per agent, minus the first read."""
    db = open_db(root, False)
    rows = db.execute("SELECT agent, COUNT(*) AS n FROM advice WHERE thread=? GROUP BY agent ORDER BY agent", (a.thread,)).fetchall() if db else []
    for r in rows:
        print("%s %d" % (r["agent"], r["n"] - 1))
    return 0


GIT_LOCATION_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_CEILING_DIRECTORIES")


def enclosing_repo(folder: Path):
    """The work tree holding this folder, or None only when no folder from here to the root holds a .git entry.
    Git's message is never read: it is locale-dependent, and "not a git repository" also names a .git file whose
    gitdir is missing. Any git failure under a .git entry refuses: an export into a repository must land on an ignored path."""
    probe = folder
    while not probe.exists() and probe.parent != probe:
        probe = probe.parent
    env = {k: v for k, v in os.environ.items() if k not in GIT_LOCATION_ENV}  # discovery from the folder, not the caller's env
    r = subprocess.run([git_exe(), "-C", str(probe), "rev-parse", "--show-toplevel"], capture_output=True, env=env)
    if r.returncode == 0:
        return Path(r.stdout.decode("utf-8", "replace").strip()).resolve()
    if not any(os.path.lexists(p / ".git") for p in (probe, *probe.parents)):
        return None
    raise Refused("cannot tell whether %s is inside a repository: %s" % (folder, r.stderr.decode("utf-8", "replace").strip()))


def cmd_export(root, a):
    target = Path(a.path).resolve()
    db = open_db(root, False)
    if not db:
        raise Refused("no advisory store yet")
    repo = enclosing_repo(target.parent)
    if repo:
        require_ignored(repo, target.relative_to(repo).as_posix())
    target.parent.mkdir(parents=True, exist_ok=True)  # only after the checks: a refusal leaves no folders behind
    out = sqlite3.connect(str(target))
    with out:
        db.backup(out)
    out.close()
    print("exported to %s" % target)
    return 0


def cmd_lint(root, a):
    db = open_db(root, False)
    if not db:
        print("no advisory store yet")
        return 0
    problems = []
    if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        problems.append("integrity_check failed")
    pats = secret_patterns(root)
    for table, col in (("advice", "body"), ("advice", "brief"), ("finding", "body"), ("finding", "note")):
        for r in db.execute("SELECT id, %s AS t FROM %s" % (col, table)):
            if r["t"] and any(rx.search(r["t"]) for _, rx in pats):
                problems.append("secret shape in %s.%s row %d" % (table, col, r["id"]))
    try:
        require_ignored(root, DB_REL)
    except Refused as ex:
        problems.append(str(ex))
    for p in problems:
        print("FAIL " + p)
    print("adv lint: %s" % ("%d problem(s)" % len(problems) if problems else "OK"))
    return 1 if problems else 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="adv", description="Advisory store: adviser returns and findings in SQLite, off git.")
    p.add_argument("--root")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("ingest", help="store one return from JSON {agent, return, brief?, session?, agent_id?}")
    c.add_argument("--file", help="JSON file; default stdin")
    c.set_defaults(fn=cmd_ingest)
    c = sub.add_parser("q", help="search findings and returns")
    c.add_argument("words")
    c.add_argument("--agent")
    c.add_argument("-n", type=int, default=10)
    c.set_defaults(fn=cmd_q)
    c = sub.add_parser("get", help="one return adv:<n> or finding adv:<n>.<k>")
    c.add_argument("id")
    c.set_defaults(fn=cmd_get)
    c = sub.add_parser("list", help="newest first")
    for name in ("agent", "workflow", "thread", "status"):
        c.add_argument("--" + name)
    c.add_argument("-n", type=int, default=30)
    c.set_defaults(fn=cmd_list)
    c = sub.add_parser("decide", help="record the main GD's decision on a finding")
    c.add_argument("id")
    c.add_argument("decision", choices=DECISIONS)
    c.add_argument("--by", required=True)
    c.add_argument("--note")
    c.set_defaults(fn=cmd_decide)
    c = sub.add_parser("useful", help="the main GD's usefulness mark on a finding")
    c.add_argument("id")
    c.add_argument("value", choices=("yes", "no"))
    c.set_defaults(fn=cmd_useful)
    c = sub.add_parser("rounds", help="follow-up rounds per agent in a thread")
    c.add_argument("thread")
    c.set_defaults(fn=cmd_rounds)
    c = sub.add_parser("export", help="back up the database to a path outside git")
    c.add_argument("path")
    c.set_defaults(fn=cmd_export)
    c = sub.add_parser("lint", help="integrity, secret shapes, ignore rule")
    c.set_defaults(fn=cmd_lint)
    a = p.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        return a.fn(find_root(a.root), a)
    except (Refused, ValueError, OSError, sqlite3.Error) as ex:
        print("refused: %s" % ex, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
