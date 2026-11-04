"""Tests for bugs.py. Run: python -I .claude/skills/bugs/scripts/test_bugs.py"""
import contextlib
import datetime as dt
import io
import json
import os
import random
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unicodedata
import _thread
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bugs  # noqa: E402

SKILL_DIR = HERE.parent
FAKE_KEY = "AK" + "IA" + "Q" * 16  # built at runtime so this file holds no secret-shaped literal
PEM_HEADER = "-----BEGIN RSA PRIVATE" + " KEY-----"
T0 = "2026-01-01T00:00:00.000Z"
TERMINAL = ["Complete", "Won't fix", "Accepted", "As designed", "Duplicate"]
OPEN = ["Request", "Processing", "Resolved", "Review", "Reopen", "Backlog"]
STATUSES = OPEN + TERMINAL
PRIORITIES = ["Low", "Medium", "High", "Highest"]
VI_LOWER = "àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ"

# The spec's state machine, written out here rather than imported: a typo in bugs.py must fail against it.
PLAIN_MOVES = {("Request", "Processing"), ("Reopen", "Processing"), ("Processing", "Request"), ("Processing", "Resolved"),
               ("Resolved", "Review"), ("Review", "Complete"), ("Review", "Reopen"), ("Review", "Resolved")}
PLAIN_MOVES |= {(t, "Reopen") for t in TERMINAL}
PLAIN_MOVES |= {(o, t) for o in OPEN for t in ("As designed", "Duplicate")}
GD_MOVES = {("Backlog", "Request")}
GD_MOVES |= {(o, "Backlog") for o in OPEN if o != "Backlog"}
GD_MOVES |= {(o, t) for o in OPEN for t in ("Won't fix", "Accepted")}

# Copied from .workflow/bugs.md on 2026-11-03: the import has to take today's real file.
REAL_BUGS_MD = r"""# Bugs

Next ID: BUG-0006

| ID | Title | Severity | Status | Feature | Owner | Regression test |
|---|---|---|---|---|---|---|
| BUG-0001 | Consent skill allows Firebase bootstrap before consent without GD acceptance | Medium | Closed | engineer-skill-gaps | consent-att-init-order (sdk author) | Written repro (docs, no seam) |
| BUG-0002 | google-ump.md caveat omits Firebase re-apply on privacy-options close | Medium | Closed | engineer-skill-gaps | consent-att-init-order (main session R3-1 text) | Written repro (docs, no seam) |
| BUG-0003 | mobile-safe-area defaults gate placed after the per-device verify step | Low | Closed | engineer-skill-gaps | mobile-safe-area (ui author) | Written repro (docs, no seam) |
| BUG-0004 | Apple Family-Shared refund fallback can reverse or tombstone the purchaser's grant | High | Closed | engineer-skill-gaps | iap-server-receipt-ledger (backend author) | Written repro (docs, no seam) |
| BUG-0005 | Consent caveat claims Crashlytics stops in-session on withdrawal | Medium | Closed | engineer-skill-gaps | consent-att-init-order (sdk author) | Written repro (docs, no seam) |

## BUG-0001 — Consent skill allows Firebase bootstrap before consent without GD acceptance
- Repro: read `.claude/skills/consent-att-init-order/SKILL.md:21`, step 3 clause "Firebase bootstrap may move before (b) only when … off keys ship".
- Expected: spec 4 "no ad/analytics SDK starts before consent resolves" · Actual: an optional path lets Firebase Installations and Remote Config/Auth traffic precede consent; no GD acceptance recorded.
- Evidence: `.workflow/evidence/engineer-skill-gaps/attempt-1/qa-report.md` DEF-1.
- History: 2026-10-29 Open — QA executor. 2026-10-29 Fixed — sdk author (consent SKILL:21); security re-check: nothing starts before consent. 2026-10-29 Closed — qa-lead re-read the fixed lines (sign-off read-through).

## BUG-0002 — google-ump.md caveat omits Firebase re-apply on privacy-options close
- Repro: compare `consent-att-init-order/SKILL.md:26` (re-apply 3(d) Firebase consent and 3(e) ad signals on close) with `references/google-ump.md:73` (Firebase re-applied only "every launch").
- Expected: both re-applied on close · Actual: a reader following the reference leaves Firebase collecting until the next launch after a withdrawal.
- Evidence: qa-report.md DEF-2.
- Root cause: R3-1 fix text written by the main session named only `ApplyAdConsentSignals` for on-close.
- History: 2026-10-29 Open — QA executor. 2026-10-29 Fixed — sdk author (google-ump.md:70-89); security re-check: analytics stops in-session (Crashlytics → BUG-0005). 2026-10-29 Closed — qa-lead re-read the fixed lines (sign-off read-through).

## BUG-0003 — mobile-safe-area defaults gate placed after the per-device verify step
- Repro: read `mobile-safe-area/SKILL.md:25-26`: step 10 "target devices unstated → defaults" follows step 9 verification per target device.
- Expected: decision-ordered steps (skill template) · Actual: the gate that sets the device list comes after its use.
- Evidence: qa-report.md DEF-3.
- History: 2026-10-29 Open — QA executor. 2026-10-29 Fixed — ui author (mobile-safe-area SKILL:25-26; localization SKILL:27 ref). 2026-10-29 Closed — qa-lead re-read the fixed lines (sign-off read-through).

## BUG-0004 — Apple Family-Shared refund fallback can reverse or tombstone the purchaser's grant
- Repro: read `iap-server-receipt-ledger/references/app-store-server-api.md:65` and `SKILL.md:28`: FAMILY_SHARED refund/REVOKE with no entry → match by appAccountToken+productId; void with no entry → orphan + tombstone.
- Expected: a family REVOKE never reverses or blocks the purchaser's PURCHASED grant · Actual: fallback can land on the purchaser's entry; a tombstone can block their later grant.
- Evidence: security re-check after QA fixes, F-1.
- History: 2026-10-29 Open — security-reviewer. 2026-10-29 Fixed — backend author (ownership per entry; family events never touch PURCHASED; tombstones only from PURCHASED); security re-check Clear. 2026-10-29 Closed — qa-lead re-read the fixed lines (sign-off read-through).

## BUG-0005 — Consent caveat claims Crashlytics stops in-session on withdrawal
- Repro: `consent-att-init-order/references/google-ump.md:89` says withdrawal stops Firebase collection in the same session; `firebase-unity-sdk/references/crashlytics.md:29` says the Crashlytics flag takes effect next launch.
- Expected: caveat limited to Analytics, Crashlytics gap stated · Actual: overclaims.
- Evidence: security re-check, F-2.
- History: 2026-10-29 Open — security-reviewer. 2026-10-29 Fixed — sdk author (same-session stop limited to Analytics + ads; Crashlytics next launch in Known limitations); security re-check Clear. 2026-10-29 Closed — qa-lead re-read the fixed lines (sign-off read-through).
"""

MD_HEADER = "# Bugs\n\nNext ID: %s\n\n| ID | Title | Severity | Status | Feature | Owner | Regression test |\n|---|---|---|---|---|---|---|\n"


def md_record(bug_id="BUG-0001", title="Save slot overwrite drops coins", severity="Medium", status="Open",
              repro="1. load slot", expected="coins kept (spec 3)", actual="coins zero", evidence="log.md",
              history="2026-10-29 Open — QA executor.", extra=""):
    row = "| %s | %s | %s | %s | feat | owner | none |\n" % (bug_id, title, severity, status)
    rec = "\n## %s — %s\n- Repro: %s\n- Expected: %s · Actual: %s\n- Evidence: %s\n%s- History: %s\n" % (
        bug_id, title, repro, expected, actual, evidence, extra, history)
    return row, rec


def md_file(*records, next_id="BUG-0099"):
    return MD_HEADER % next_id + "".join(r[0] for r in records) + "".join(r[1] for r in records)


def fields(**over):
    d = dict(title="Save slot overwrite drops coins", description="Overwriting a save slot zeroes coins for the player.",
             priority="Medium", repro="not yet", expected="Coins kept (spec 3.2)", actual="Coins read zero",
             evidence=".workflow/evidence/save/log.md")
    d.update(over)
    return d


def stamp(days=0, ms=0):
    d = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc) + dt.timedelta(days=days, milliseconds=ms)
    return d.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (d.microsecond // 1000)


def event(etype, uid, data, ts=T0, event_uid=None, by="main session", note=None):
    ev = {"event_uid": event_uid or "%s-%s-%s" % (uid, etype, ts), "bug_uid": uid, "ts": ts, "type": etype, "data": data}
    if etype != "tombstone":
        ev["by"] = by
    if note is not None:
        ev["note"] = note
    return ev


def create(uid, num, ts=T0, **over):
    data = fields(id=num, status="Request")
    data.update(over)
    return event("create", uid, data, ts)


def fmt_future(days):
    """The real clock plus some days: a purge clock for bugs just closed on the real clock."""
    d = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=days)
    return d.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (d.microsecond // 1000)


def git(cwd, *args, check=True):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(cwd)] + list(args),
                          check=check, capture_output=True, text=True, encoding="utf-8")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bugs-test-")
        self.root = Path(self.tmp) / "p"
        self.root.mkdir()
        self.env_patch = mock.patch.dict(os.environ)
        self.env_patch.start()
        os.environ.pop("BUGS_NOW", None)

    def tearDown(self):
        self.env_patch.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    @property
    def journal(self):
        return self.root / ".workflow" / "bugs.jsonl"

    @property
    def db_path(self):
        return self.root / ".workflow" / "bugs.db"

    def run_cli(self, *argv, stdin=None, now=None, root=None):
        data = b"" if stdin is None else (stdin if isinstance(stdin, bytes) else json.dumps(stdin, ensure_ascii=False).encode("utf-8"))
        out, err = io.StringIO(), io.StringIO()
        old_stdin = sys.stdin
        sys.stdin = io.TextIOWrapper(io.BytesIO(data), encoding="utf-8")
        if now is not None:
            os.environ["BUGS_NOW"] = now
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                try:
                    code = bugs.main(["--root", str(root or self.root)] + list(argv))
                except SystemExit as ex:
                    code = ex.code
        finally:
            sys.stdin = old_stdin
            os.environ.pop("BUGS_NOW", None)
        return code, out.getvalue(), err.getvalue()

    def ok(self, *argv, **kw):
        code, out, err = self.run_cli(*argv, **kw)
        self.assertEqual(code, 0, "stdout: %s\nstderr: %s" % (out, err))
        return out

    def no(self, *argv, **kw):
        code, out, err = self.run_cli(*argv, **kw)
        self.assertNotEqual(code, 0, "expected a refusal, got stdout: %s" % out)
        self.assertTrue(err.strip(), "a refusal must say why on stderr")
        return err

    def add(self, **over):
        return self.ok("add", stdin=fields(**over)).strip()

    def show(self, bug_id):
        return json.loads(self.ok("show", bug_id, "--json"))

    def counters(self, bug_id):
        return json.loads(self.ok("counters", bug_id, "--json"))

    def status(self, bug_id, to, by=None, now=None, **kw):
        args = ["set-status", bug_id, to, "--note", "main session: test move"]
        if by:
            args += ["--by", by]
        if to == "Duplicate":
            args += ["--duplicate-of", kw.get("dup", "BUG-0001")]
        return self.ok(*args, now=now)

    def isolated_copy(self, with_mem=True, with_patterns=False):
        base = Path(self.tmp) / "framework"
        scripts = base / ".claude" / "skills" / "bugs" / "scripts"
        scripts.mkdir(parents=True)
        shutil.copy(HERE / "bugs.py", scripts / "bugs.py")
        if with_mem:
            m = base / ".claude" / "skills" / "mem" / "scripts"
            m.mkdir(parents=True)
            shutil.copy(SKILL_DIR.parent / "mem" / "scripts" / "mem.py", m / "mem.py")
        if with_patterns:
            h = base / ".claude" / "hooks"
            h.mkdir(parents=True)
            shutil.copy(SKILL_DIR.parents[1] / "hooks" / "secret-patterns.txt", h / "secret-patterns.txt")
        return scripts / "bugs.py"

    def cli(self, script, *argv, stdin=b""):
        return subprocess.run([sys.executable, "-I", str(script), "--root", str(self.root)] + list(argv),
                              input=stdin, capture_output=True)

    def seed(self, *events):
        self.journal.parent.mkdir(parents=True, exist_ok=True)
        with open(self.journal, "ab") as f:
            for e in events:
                f.write((json.dumps(e, ensure_ascii=False) if isinstance(e, dict) else e).encode("utf-8") + b"\n")

    def lines(self):
        return [json.loads(x) for x in self.journal.read_bytes().split(b"\n") if x.strip()]

    def dump_tables(self):
        self.ok("rebuild")
        db = sqlite3.connect(str(self.db_path))
        try:
            return (db.execute("SELECT * FROM bug ORDER BY uid").fetchall(),
                    db.execute("SELECT * FROM bug_event ORDER BY event_uid").fetchall(),
                    db.execute("SELECT value FROM meta WHERE key='high_water'").fetchall())
        finally:
            db.close()


class TestCrud(Base):
    def test_add_files_a_request_with_default_caps(self):
        self.assertEqual(self.add(), "BUG-0001")
        b = self.show("BUG-0001")
        self.assertEqual(b["status"], "Request")
        self.assertEqual((b["fix_used"], b["fix_cap"], b["review_used"], b["review_cap"]), (0, 2, 0, 3))
        self.assertIsNone(b["closed_at"])
        self.assertEqual(b["title"], fields()["title"])

    def test_ids_are_sequential(self):
        self.assertEqual([self.add(), self.add(), self.add()], ["BUG-0001", "BUG-0002", "BUG-0003"])

    def test_add_stores_optional_fields(self):
        self.add(feature="save-system", owner="backend-engineer", regression_test="SaveTests.Overwrite", root_cause="Bad index")
        b = self.show("BUG-0001")
        self.assertEqual((b["feature"], b["owner"], b["regression_test"], b["root_cause"]),
                         ("save-system", "backend-engineer", "SaveTests.Overwrite", "Bad index"))

    def test_add_refuses_status_and_unknown_keys(self):
        self.assertIn("status", self.no("add", stdin=fields(status="Complete")))
        self.assertIn("severity", self.no("add", stdin=fields(severity="High")))
        self.assertFalse(self.journal.exists())

    def test_add_refuses_bad_stdin(self):
        self.assertIn("JSON", self.no("add", stdin=b"not json"))
        self.assertIn("JSON", self.no("add", stdin=b"[1,2]"))
        self.assertIn("JSON", self.no("add"))

    def test_stdin_with_a_bom_is_accepted(self):
        self.ok("add", stdin=b"\xef\xbb\xbf" + json.dumps(fields()).encode("utf-8"))
        self.assertEqual(self.show("BUG-0001")["title"], fields()["title"])

    def test_dollar_signs_survive_stdin(self):
        self.add(actual="Cost shows $PRICE and $(x) literally")
        self.assertEqual(self.show("BUG-0001")["actual"], "Cost shows $PRICE and $(x) literally")

    def test_update_changes_a_field_and_records_an_event(self):
        self.add()
        self.ok("update", "BUG-0001", stdin={"root_cause": "Bad slot index", "priority": "High", "note": "main session: triage"})
        b = self.show("BUG-0001")
        self.assertEqual((b["root_cause"], b["priority"]), ("Bad slot index", "High"))
        e = b["events"][-1]
        self.assertEqual((e["type"], e["note"]), ("update", "main session: triage"))

    def test_update_without_a_change_writes_nothing(self):
        self.add()
        before = self.journal.read_bytes()
        self.assertIn("no change", self.ok("update", "BUG-0001", stdin={"priority": "Medium"}))
        self.assertEqual(self.journal.read_bytes(), before)

    def test_note_only_update_records_the_note(self):
        self.add()
        out = self.ok("update", "BUG-0001", stdin={"note": "qa: second hit in log2.md"})
        self.assertIn("BUG-0001 updated", out)
        self.assertNotIn("no change", out)
        e = self.show("BUG-0001")["events"][-1]
        self.assertEqual((e["type"], e["note"], e["data"]), ("update", "qa: second hit in log2.md", "{}"))
        self.assertEqual(len(self.lines()), 2)
        self.assertIn("BUG-0001", self.ok("search", "log2"))
        self.db_path.unlink()
        self.assertEqual(self.show("BUG-0001")["events"][-1]["note"], "qa: second hit in log2.md")

    def test_note_with_an_unchanged_field_keeps_the_note(self):
        self.add()
        self.ok("update", "BUG-0001", stdin={"priority": "Medium", "note": "qa: same priority, new evidence"})
        e = self.show("BUG-0001")["events"][-1]
        self.assertEqual((e["note"], e["data"]), ("qa: same priority, new evidence", "{}"))

    def test_truly_empty_update_says_no_change(self):
        self.add()
        before = self.journal.read_bytes()
        self.assertIn("no change", self.ok("update", "BUG-0001", stdin={}))
        self.assertIn("no change", self.ok("update", "BUG-0001", stdin={"note": "   "}))
        self.assertEqual(self.journal.read_bytes(), before)

    def test_update_refuses_status_id_and_counters(self):
        self.add()
        for key, val in (("status", "Complete"), ("id", "BUG-0009"), ("fix_cap", 9), ("closed_at", T0), ("duplicate_of", "BUG-0001")):
            self.assertIn(key, self.no("update", "BUG-0001", stdin={key: val}))

    def test_update_refuses_clearing_a_required_field_but_clears_an_optional_one(self):
        self.add(root_cause="Known")
        for key in ("title", "description", "repro", "expected", "actual", "evidence"):
            self.assertIn(key, self.no("update", "BUG-0001", stdin={key: ""}))
        self.ok("update", "BUG-0001", stdin={"root_cause": ""})
        self.assertIsNone(self.show("BUG-0001")["root_cause"])

    def test_update_unknown_bug_refused(self):
        self.assertIn("BUG-0042", self.no("update", "BUG-0042", stdin={"priority": "Low"}))
        self.assertFalse(self.db_path.exists())

    def test_show_text_form_holds_the_record(self):
        self.add(root_cause="Bad slot index")
        self.status("BUG-0001", "Processing")
        out = self.ok("show", "BUG-0001")
        for piece in ("BUG-0001", fields()["title"], fields()["description"], "Bad slot index", "Processing", "main session: test move"):
            self.assertIn(piece, out)

    def test_show_unknown_is_an_error_and_a_gap_reads_purged(self):
        self.assertIn("not found", self.no("show", "BUG-0007"))
        self.add()
        self.add()
        self.ok("delete", "BUG-0001", "--by", "GD")
        self.assertIn("purged", self.ok("show", "BUG-0001"))

    def test_bad_id_format_refused(self):
        self.assertIn("BUG-", self.no("show", "BUG-12"))
        self.assertIn("BUG-", self.no("counters", "7", "--json"))

    def test_list_filters(self):
        self.add(title="alpha", priority="Low", feature="f1")
        self.add(title="beta", priority="High", feature="f2")
        self.add(title="gamma", priority="High", feature="f1")
        self.status("BUG-0002", "Processing")
        self.status("BUG-0003", "As designed")
        ids = lambda *a: [b["id"] for b in json.loads(self.ok("list", "--json", *a))]
        self.assertEqual(ids(), ["BUG-0001", "BUG-0002", "BUG-0003"])
        self.assertEqual(ids("--status", "Processing"), ["BUG-0002"])
        self.assertEqual(ids("--priority", "High"), ["BUG-0002", "BUG-0003"])
        self.assertEqual(ids("--feature", "f1"), ["BUG-0001", "BUG-0003"])
        self.assertEqual(ids("--open"), ["BUG-0001", "BUG-0002"])
        self.assertEqual(ids("--open", "--priority", "High", "--feature", "f2"), ["BUG-0002"])

    def test_list_refuses_unknown_filter_values(self):
        self.assertNotEqual(self.run_cli("list", "--status", "Open")[0], 0)
        self.assertNotEqual(self.run_cli("list", "--priority", "Critical")[0], 0)

    def test_list_text_shows_closed_at(self):
        self.add()
        self.status("BUG-0001", "As designed", now="2030-03-04T05:06:07Z")
        self.assertIn("2030-03-04", self.ok("list"))

    def test_search_finds_text_and_survives_query_syntax(self):
        self.add(title="Crash in inventory panel", description="Tapping the panel crashes the client.")
        self.add(title="Audio pops on pause")
        self.assertIn("BUG-0001", self.ok("search", "inventory"))
        self.assertNotIn("BUG-0002", self.ok("search", "inventory"))
        self.assertIn("BUG-0001", self.ok("search", 'NEAR( "inventory" * : ^'))
        self.assertIn("BUG-0001", self.ok("search", "crashing"))  # porter stem
        self.assertIn("words", self.no("search", "***"))

    def test_search_covers_notes_and_closed_bugs(self):
        self.add()
        self.ok("set-status", "BUG-0001", "As designed", "--note", "qa-lead: matches telemetry dashboard")
        self.assertIn("BUG-0001", self.ok("search", "telemetry"))

    def test_search_stays_current_after_update(self):
        self.add()
        self.ok("update", "BUG-0001", stdin={"root_cause": "Marshalling fault"})
        self.assertIn("BUG-0001", self.ok("search", "marshalling"))

    def test_delete_needs_the_gd(self):
        self.add()
        self.assertIn("GD", self.no("delete", "BUG-0001"))
        self.assertIn("GD", self.no("delete", "BUG-0001", "--by", "main session"))
        self.assertEqual(self.show("BUG-0001")["id"], "BUG-0001")

    def test_delete_leaves_only_a_text_free_tombstone_and_never_reuses_the_id(self):
        self.add(title="Sensitive words here")
        self.ok("delete", "BUG-0001", "--by", "GD")
        raw = self.journal.read_text(encoding="utf-8")
        self.assertNotIn("Sensitive", raw)
        self.assertEqual([e["type"] for e in self.lines()], ["tombstone"])
        self.assertEqual(self.add(), "BUG-0002")

    def test_no_journal_reads_are_empty_and_create_nothing(self):
        self.assertEqual(json.loads(self.ok("list", "--json")), [])
        self.assertIn("Bugs: 0 open (0 High+)", self.ok("stats"))
        self.assertFalse(self.counters("BUG-0001")["found"])
        self.assertIn("no bugs", self.ok("list"))
        self.assertEqual(self.ok("sql", "SELECT 1 AS x").split(), ["x", "1"])
        self.ok("search", "anything")
        self.ok("purge", "--dry-run")
        self.ok("rebuild")
        self.ok("doctor")
        self.assertFalse((self.root / ".workflow").exists())

    def test_first_write_creates_db_and_journal(self):
        self.add()
        self.assertTrue(self.db_path.exists())
        self.assertTrue(self.journal.exists())

    def test_journal_is_lf_utf8_without_bom(self):
        self.add(actual="Dash — and ellipsis … stay readable")
        raw = self.journal.read_bytes()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\r", raw)
        self.assertTrue(raw.endswith(b"\n"))
        self.assertIn("Dash —".encode("utf-8"), raw)

    def test_journal_line_carries_the_required_keys(self):
        self.add()
        e = self.lines()[0]
        for key in ("event_uid", "bug_uid", "ts", "type", "data"):
            self.assertIn(key, e)
        self.assertEqual(e["type"], "create")
        self.assertRegex(e["ts"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$")

    def test_priority_scale(self):
        for p in PRIORITIES:
            self.add(priority=p)
        for bad in ("Critical", "low", "P1", ""):
            self.no("add", stdin=fields(priority=bad))
        self.assertIn("priority", self.no("update", "BUG-0001", stdin={"priority": "Critical"}))

    def test_add_needs_a_priority(self):
        d = fields()
        del d["priority"]
        self.assertIn("priority", self.no("add", stdin=d))

    def test_schema_has_the_spec_columns_checks_and_indexes(self):
        self.add()
        db = sqlite3.connect(str(self.db_path))
        try:
            cols = {r[1] for r in db.execute("PRAGMA table_info(bug)")}
            self.assertEqual(cols, {"id", "uid", "title", "description", "priority", "status", "feature", "owner", "regression_test",
                                    "repro", "expected", "actual", "evidence", "root_cause", "duplicate_of", "fix_used", "fix_cap",
                                    "review_used", "review_cap", "created_at", "updated_at", "closed_at"})
            self.assertNotIn("severity", cols)
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE bug SET status='Open'")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE bug SET priority='Critical'")
            sql = " ".join(r[0] for r in db.execute("SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL AND tbl_name='bug'"))
            for col in ("status", "priority", "feature", "closed_at"):
                self.assertIn("(%s)" % col, sql)
            self.assertTrue(db.execute("SELECT 1 FROM sqlite_master WHERE name='bug_fts'").fetchone())
        finally:
            db.close()


class TestTransitions(Base):
    def seed_all_pairs(self):
        """One bug in each from-state for each (from, to) pair, seeded through the journal."""
        evs, cases, n = [], {}, 0
        evs.append(create("target", 1))
        n = 1
        for frm in STATUSES:
            for to in STATUSES:
                n += 1
                uid = "u%d" % n
                evs.append(create(uid, n))
                if frm != "Request":
                    evs.append(event("status", uid, {"to": frm, "from": "Request"}, stamp(ms=n)))
                cases[(frm, to)] = "BUG-%04d" % n
        self.seed(*evs)
        return cases

    def attempt(self, bug_id, to, *extra):
        args = ["set-status", bug_id, to, "--note", "qa: matrix"] + list(extra)
        if to == "Duplicate":
            args += ["--duplicate-of", "BUG-0001"]
        return self.run_cli(*args)

    def test_exact_status_and_priority_names(self):
        self.assertEqual(list(bugs.STATUSES), ["Request", "Processing", "Resolved", "Review", "Complete", "Reopen", "Backlog",
                                               "Won't fix", "Accepted", "As designed", "Duplicate"])
        self.assertEqual(list(bugs.PRIORITIES), PRIORITIES)
        self.assertEqual(sorted(bugs.TERMINAL), sorted(TERMINAL))
        self.assertEqual(len(bugs.STATUSES), 11)

    def test_every_allowed_and_refused_move(self):
        cases = self.seed_all_pairs()
        self.assertEqual(len(cases), 121)
        for (frm, to), bug_id in cases.items():
            with self.subTest(frm=frm, to=to):
                before = self.journal.read_bytes()
                code, out, err = self.attempt(bug_id, to)
                if (frm, to) in PLAIN_MOVES:
                    self.assertEqual(code, 0, err)
                    self.assertEqual(self.show(bug_id)["status"], to)
                    continue
                self.assertNotEqual(code, 0, "%s -> %s must be refused without the GD" % (frm, to))
                self.assertEqual(self.journal.read_bytes(), before)
                self.assertEqual(self.show(bug_id)["status"], frm)
                if (frm, to) in GD_MOVES:
                    self.assertIn("GD only", err)
                    self.assertIn("state machine", err)
                    code, _, err = self.attempt(bug_id, to, "--by", "GD")
                    self.assertEqual(code, 0, err)
                    self.assertEqual(self.show(bug_id)["status"], to)
                else:
                    code, _, _ = self.attempt(bug_id, to, "--by", "GD")
                    self.assertNotEqual(code, 0, "the GD cannot force an illegal move %s -> %s" % (frm, to))
                    self.assertEqual(self.show(bug_id)["status"], frm)

    def test_gd_attribution_is_exact(self):
        self.add()
        for by in ("gd", "G.D.", "GD please", "main session"):
            self.assertIn("GD only", self.no("set-status", "BUG-0001", "Backlog", "--note", "x", "--by", by))
        self.ok("set-status", "BUG-0001", "Backlog", "--note", "x", "--by", "GD")

    def test_unknown_status_refused(self):
        self.add()
        self.assertIn("status", self.no("set-status", "BUG-0001", "Closed", "--note", "x"))

    def test_note_is_required_and_comes_from_stdin_too(self):
        self.add()
        self.assertIn("note", self.no("set-status", "BUG-0001", "Processing"))
        self.ok("set-status", "BUG-0001", "Processing", stdin={"note": "main session: dispatched $owner"})
        self.assertEqual(self.show("BUG-0001")["events"][-1]["note"], "main session: dispatched $owner")

    def test_set_status_stdin_refuses_unknown_keys(self):
        self.add()
        self.assertIn("bogus", self.no("set-status", "BUG-0001", "Processing", stdin={"note": "n", "bogus": "x"}))

    def test_duplicate_needs_a_real_target(self):
        self.add()
        self.add()
        self.assertIn("duplicate_of", self.no("set-status", "BUG-0002", "Duplicate", "--note", "x"))
        self.assertIn("duplicate_of", self.no("set-status", "BUG-0002", "Duplicate", "--note", "x", "--duplicate-of", "BUG-0002"))
        self.assertIn("BUG-0009", self.no("set-status", "BUG-0002", "Duplicate", "--note", "x", "--duplicate-of", "BUG-0009"))
        self.no("set-status", "BUG-0002", "Duplicate", "--note", "x", "--duplicate-of", "nope")
        self.no("set-status", "BUG-0002", "Duplicate", stdin={"note": "x", "duplicate_of": 7})
        self.assertIn("duplicate_of", self.no("set-status", "BUG-0002", "Processing", "--note", "x", "--duplicate-of", "BUG-0001"))
        self.ok("set-status", "BUG-0002", "Duplicate", "--note", "x", "--duplicate-of", "BUG-0001")
        self.assertEqual(self.show("BUG-0002")["duplicate_of"], "BUG-0001")

    def test_every_terminal_status_sets_closed_at_and_reopen_clears_it(self):
        self.add()  # the Duplicate target
        for status in TERMINAL[1:]:
            bug_id = self.add()
            self.status(bug_id, status, by="GD", now="2030-02-02T02:02:02Z")
            b = self.show(bug_id)
            self.assertTrue(b["closed_at"].startswith("2030-02-02"), status)
            self.status(bug_id, "Reopen")
            b = self.show(bug_id)
            self.assertIsNone(b["closed_at"], status)
            self.assertIsNone(b["duplicate_of"])

    def test_full_happy_path_with_complete(self):
        bug_id = self.add()
        for to in ("Processing", "Resolved", "Review", "Complete"):
            self.status(bug_id, to)
        self.assertIsNotNone(self.show(bug_id)["closed_at"])
        self.status(bug_id, "Reopen")
        self.assertIsNone(self.show(bug_id)["closed_at"])

    def test_events_replace_history(self):
        bug_id = self.add()
        self.status(bug_id, "Processing")
        e = self.show(bug_id)["events"]
        self.assertEqual([x["type"] for x in e], ["create", "status"])
        self.assertEqual(json.loads(e[1]["data"])["from"], "Request")
        self.assertEqual(json.loads(e[1]["data"])["to"], "Processing")


class TestCounters(Base):
    def test_shape(self):
        self.add()
        c = self.counters("BUG-0001")
        self.assertEqual(set(c), {"id", "found", "settled", "status", "fix", "review", "record"})
        self.assertEqual(c, {"id": "BUG-0001", "found": True, "settled": False, "status": "Request",
                             "fix": {"used": 0, "cap": 2}, "review": {"used": 0, "cap": 3}, "record": ""})

    def test_unknown_id_is_found_false_exit_zero(self):
        c = self.counters("BUG-0042")
        self.assertEqual(c["found"], False)
        self.assertEqual(c["id"], "BUG-0042")
        self.assertEqual(set(c), {"id", "found", "settled", "status", "fix", "review", "record"})

    def test_purged_id_is_found_false_exit_zero(self):
        self.add()
        self.ok("delete", "BUG-0001", "--by", "GD")
        self.assertFalse(self.counters("BUG-0001")["found"])

    def test_settled_covers_backlog_and_the_terminal_five(self):
        self.add()
        for status in OPEN:
            self.assertEqual(status == "Backlog", bugs.is_settled(status), status)
        for status in TERMINAL:
            self.assertTrue(bugs.is_settled(status), status)
        bug_id = self.add()
        self.assertFalse(self.counters(bug_id)["settled"])
        self.status(bug_id, "Backlog", by="GD")
        c = self.counters(bug_id)
        self.assertTrue(c["settled"])
        self.assertEqual(c["status"], "Backlog")
        self.status(bug_id, "As designed")
        self.assertTrue(self.counters(bug_id)["settled"])

    def test_round_adds_used_without_enforcing_the_cap(self):
        self.add()
        for _ in range(3):
            self.ok("round", "BUG-0001", "fix", "+1", "--note", "main session: verify reproduced")
        self.ok("round", "BUG-0001", "review", "+1", "--note", "review round")
        c = self.counters("BUG-0001")
        self.assertEqual(c["fix"], {"used": 3, "cap": 2})
        self.assertEqual(c["review"], {"used": 1, "cap": 3})

    def test_round_refuses_bad_input(self):
        self.add()
        self.no("round", "BUG-0001", "fix", "+0", "--note", "x")
        self.no("round", "BUG-0001", "fix", "-1", "--note", "x")
        self.no("round", "BUG-0001", "fix", "abc", "--note", "x")
        self.assertNotEqual(self.run_cli("round", "BUG-0001", "qa", "+1", "--note", "x")[0], 0)
        self.assertIn("note", self.no("round", "BUG-0001", "fix", "+1"))
        self.assertIn("note", self.no("extra-round", "BUG-0001", "fix", "+1"))

    def test_extra_round_raises_the_cap_and_writes_the_old_line_shape(self):
        self.add()
        self.ok("extra-round", "BUG-0001", "fix", "+2", "--note", "GD ordered more rounds")
        self.ok("extra-round", "BUG-0001", "review", "+1", "--note", "GD ordered more")
        c = self.counters("BUG-0001")
        self.assertEqual(c["fix"]["cap"], 4)
        self.assertEqual(c["review"]["cap"], 4)
        self.assertIn("extra round: fix +2", c["record"].splitlines())
        self.assertIn("extra round: review +1", c["record"].splitlines())
        self.assertRegex(c["record"], r"(?i)extra round")  # New-Counter in round-cap.ps1

    def test_stop_rule_line_matches_the_hook_regex(self):
        self.add()
        self.ok("stop-rule", "BUG-0001", "review", "--extra-dispatch", "unused", now="2030-11-03T10:00:00Z")
        rec = self.counters("BUG-0001")["record"]
        self.assertIn("- Stop rule: review root-caused 2030-11-03 - extra dispatch: unused", rec.splitlines())
        self.assertRegex(rec, r"(?im)^- Stop rule:.*\breview\b")
        self.assertNotRegex(rec, r"(?im)^- Stop rule:.*\bfix\b")

    def test_stop_rule_updates_to_used_with_one_line_per_counter(self):
        self.add()
        self.ok("stop-rule", "BUG-0001", "fix", "--extra-dispatch", "unused")
        self.ok("stop-rule", "BUG-0001", "fix", "--extra-dispatch", "used")
        lines = [x for x in self.counters("BUG-0001")["record"].splitlines() if x.startswith("- Stop rule:")]
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].endswith("extra dispatch: used"))

    def test_stop_rule_refuses_bad_values(self):
        self.add()
        self.assertNotEqual(self.run_cli("stop-rule", "BUG-0001", "fix", "--extra-dispatch", "maybe")[0], 0)
        self.assertNotEqual(self.run_cli("stop-rule", "BUG-0001", "fix")[0], 0)
        self.assertNotEqual(self.run_cli("stop-rule", "BUG-0001", "qa", "--extra-dispatch", "used")[0], 0)

    def test_python_never_reads_the_rounds_ledger(self):
        self.assertNotIn("rounds.json", (HERE / "bugs.py").read_text(encoding="utf-8"))

    def test_corrupt_journal_fails_closed_on_stderr(self):
        self.add()
        with open(self.journal, "ab") as f:
            f.write(b"{broken\n")
        code, out, err = self.run_cli("counters", "BUG-0001", "--json")
        self.assertNotEqual(code, 0)
        self.assertEqual(out, "")
        self.assertIn("corrupt journal", err)

    def test_stats_counts_open_and_high(self):
        self.add(priority="High")
        self.add(priority="Highest")
        self.add(priority="Low")
        bid = self.add(priority="High")
        done = self.add(priority="Highest")
        self.status(bid, "Backlog", by="GD")
        self.status(done, "As designed")
        self.assertEqual(self.ok("stats").strip(), "Bugs: 4 open (3 High+)")


class TestPurge(Base):
    def closed_at_t0(self, uid="c1", num=1, status="Complete"):
        self.seed(create(uid, num, stamp(days=-5)),
                  event("status", uid, {"to": status, "from": "Review"}, T0, event_uid=uid + "-close"))

    def test_window_boundaries(self):
        for days, ms, purged in ((89, 0, False), (90, 0, False), (90, 1, True), (91, 0, True)):
            with self.subTest(days=days, ms=ms):
                if self.journal.exists():
                    self.journal.unlink()
                self.closed_at_t0()
                out = self.ok("purge", now=stamp(days, ms))
                self.assertEqual(self.show_or_none("BUG-0001") is None, purged, out)
                self.assertEqual(out.strip().startswith("purged 1"), purged, out)

    def show_or_none(self, bug_id):
        c = self.counters(bug_id)
        return c if c["found"] else None

    def test_every_terminal_status_is_purged(self):
        for i, status in enumerate(TERMINAL, 1):
            self.closed_at_t0("c%d" % i, i, status)
        self.assertEqual(self.ok("purge", now=stamp(91)).strip(), "purged 5, journal uncommitted")
        self.assertEqual(json.loads(self.ok("list", "--json")), [])

    def test_open_and_backlog_are_never_purged(self):
        evs = []
        for i, status in enumerate(OPEN, 1):
            evs += [create("o%d" % i, i), event("status", "o%d" % i, {"to": status}, stamp(ms=i))]
        self.seed(*evs)
        self.assertEqual(self.ok("purge", now=stamp(5000)).strip(), "purged 0")
        self.assertEqual(len(json.loads(self.ok("list", "--json"))), 6)

    def test_reopen_clears_the_clock(self):
        self.closed_at_t0()
        self.seed(event("status", "c1", {"to": "Reopen"}, stamp(1)))
        self.assertEqual(self.ok("purge", now=stamp(500)).strip(), "purged 0")
        self.assertIsNone(self.show("BUG-0001")["closed_at"])

    def test_clock_runs_from_terminal_not_from_creation(self):
        self.seed(create("c1", 1, stamp(days=-500)), event("status", "c1", {"to": "Complete"}, stamp(0)))
        self.assertEqual(self.ok("purge", now=stamp(10)).strip(), "purged 0")

    def test_dry_run_lists_without_writing(self):
        self.closed_at_t0()
        before = self.journal.read_bytes()
        out = self.ok("purge", "--dry-run", now=stamp(91))
        self.assertIn("BUG-0001", out)
        self.assertIn("would purge 1", out)
        self.assertEqual(self.journal.read_bytes(), before)
        self.assertTrue(self.counters("BUG-0001")["found"])

    def test_purge_drops_only_that_bug_and_appends_one_text_free_tombstone(self):
        self.closed_at_t0()
        keep = create("k1", 2, stamp(days=1), title="Keeper bug")
        self.seed(keep)
        self.ok("purge", now=stamp(91))
        self.assertFalse((self.root / ".workflow" / "bugs.db.jsonl.tmp").exists())
        left = self.lines()
        self.assertEqual([e["type"] for e in left], ["create", "tombstone"])
        self.assertEqual(left[0]["bug_uid"], "k1")
        tomb = left[1]
        self.assertEqual((tomb["bug_uid"], tomb["data"]), ("c1", {"id": 1}))
        self.assertNotIn("note", tomb)
        self.assertNotIn(fields()["title"], self.journal.read_text(encoding="utf-8"))
        self.assertEqual(self.show("BUG-0002")["title"], "Keeper bug")

    def test_id_is_not_reused_and_a_gap_reads_purged(self):
        self.closed_at_t0()
        self.ok("purge", now=stamp(91))
        self.assertIn("purged", self.ok("show", "BUG-0001"))
        self.assertIn("purged", self.no("update", "BUG-0001", stdin={"priority": "Low"}))
        self.assertEqual(self.add(), "BUG-0002")

    def test_tombstone_beats_a_resurrected_line(self):
        c = create("c1", 1, stamp(days=-5), title="Old bug text")
        late = event("update", "c1", {"root_cause": "Late branch line"}, stamp(days=120))
        tomb = event("tombstone", "c1", {"id": 1}, stamp(91))
        self.seed(tomb, c, late, create("k1", 2, stamp(1)))
        rows = json.loads(self.ok("list", "--json"))
        self.assertEqual([r["id"] for r in rows], ["BUG-0002"])
        self.assertEqual(self.add(), "BUG-0003")
        self.assertFalse(self.counters("BUG-0001")["found"])

    def test_the_test_clock_warns_on_every_purge_form(self):
        self.closed_at_t0()
        for args in (["purge", "--dry-run"], ["purge", "--auto"], ["purge"]):
            with self.subTest(args):
                code, out, err = self.run_cli(*args, now=stamp(10))
                self.assertEqual(code, 0, err)
                self.assertEqual(len(err.strip().splitlines()), 1, err)
                self.assertIn("BUGS_NOW", err)
                self.assertIn("reads as the test clock", err)
                self.assertNotIn("purge runs", err)  # --auto can skip: the line must not claim a run
                self.assertNotIn("BUGS_NOW", out)

    def test_no_clock_override_no_warning(self):
        self.closed_at_t0()
        self.assertEqual(self.run_cli("purge", "--dry-run")[2], "")

    def test_auto_without_git_does_nothing_and_says_why(self):
        self.closed_at_t0()
        before = self.journal.read_bytes()
        out = self.ok("purge", "--auto", now=stamp(91))
        self.assertIn("skipped", out)
        self.assertIn("git", out)
        self.assertEqual(self.journal.read_bytes(), before)
        self.assertEqual(len(out.strip().splitlines()), 1)


class TestReplay(Base):
    def build_history(self):
        evs = []
        for i in range(1, 7):
            uid = "b%d" % i
            evs.append(create(uid, i, stamp(i)))
            evs.append(event("update", uid, {"root_cause": "Cause %d" % i}, stamp(i, 1)))
            evs.append(event("status", uid, {"to": "Processing"}, stamp(i, 2)))
            evs.append(event("round", uid, {"counter": "fix", "n": 1}, stamp(i, 3), note="round"))
            evs.append(event("status", uid, {"to": "Request"}, stamp(i, 4)))
        evs.append(event("extra_round", "b1", {"counter": "fix", "n": 2}, stamp(9), note="GD"))
        evs.append(event("status", "b2", {"to": "Complete"}, stamp(9, 1)))
        evs.append(event("status", "b2", {"to": "Reopen"}, stamp(9, 2)))
        evs.append(event("status", "b3", {"to": "Complete"}, stamp(9, 3)))
        return evs

    def test_shuffled_lines_replay_to_the_same_tables(self):
        evs = self.build_history()
        self.seed(*evs)
        want = self.dump_tables()
        for seed in range(5):
            shuffled = evs[:]
            random.Random(seed).shuffle(shuffled)
            self.journal.unlink()
            self.seed(*shuffled)
            self.assertEqual(self.dump_tables(), want, seed)

    def test_same_ts_breaks_ties_by_event_uid(self):
        self.seed(create("a", 1), event("status", "a", {"to": "Processing"}, stamp(1), event_uid="z"),
                  event("status", "a", {"to": "Resolved"}, stamp(1), event_uid="y"))
        self.assertEqual(self.show("BUG-0001")["status"], "Processing")

    def test_duplicate_event_uid_applies_once(self):
        r = event("round", "a", {"counter": "fix", "n": 1}, stamp(1), event_uid="same")
        self.seed(create("a", 1), r, r)
        self.assertEqual(self.counters("BUG-0001")["fix"]["used"], 1)

    def test_replay_does_not_enforce_transitions(self):
        self.seed(create("a", 1), event("status", "a", {"to": "Complete"}, stamp(1)))
        self.assertEqual(self.show("BUG-0001")["status"], "Complete")

    def test_replay_refuses_malformed_lines(self):
        good = create("a", 1)
        bad_lines = {
            "not json": "{nope",
            "not an object": "[1]",
            "no event_uid": {k: v for k, v in good.items() if k != "event_uid"},
            "no bug_uid": {k: v for k, v in good.items() if k != "bug_uid"},
            "bad ts": dict(good, ts="yesterday"),
            "impossible ts": dict(good, ts="2026-13-45T00:00:00.000Z"),
            "unknown type": dict(good, type="sneak"),
            "unknown field": event("update", "a", {"bug; DROP TABLE bug": "x"}, stamp(1)),
            "bad status": event("status", "a", {"to": "Open"}, stamp(1)),
            "bad priority": event("update", "a", {"priority": "Critical"}, stamp(1)),
            "non-text field": event("update", "a", {"title": 7}, stamp(1)),
            "bad counter": event("round", "a", {"counter": "qa", "n": 1}, stamp(1)),
            "unhashable counter": event("round", "a", {"counter": ["fix"], "n": 1}, stamp(1)),
            "bad n": event("round", "a", {"counter": "fix", "n": "x"}, stamp(1)),
            "bad tombstone": event("tombstone", "a", {"id": "one"}, stamp(1)),
            "orphan": event("update", "ghost", {"title": "x"}, stamp(1)),
        }
        for name, bad in bad_lines.items():
            with self.subTest(name):
                if self.journal.exists():
                    self.journal.unlink()
                self.seed(good, bad, event("update", "a", {"title": "After the bad line"}, stamp(2)))
                err = self.no("list")
                self.assertIn("corrupt journal", err)
                self.no("add", stdin=fields())

    def test_two_creates_for_one_uid_refused(self):
        self.seed(create("a", 1), dict(create("a", 2), event_uid="other"))
        self.assertIn("corrupt journal", self.no("list"))

    def test_journal_alone_rebuilds_the_db(self):
        self.add()
        self.status("BUG-0001", "Processing")
        want = self.show("BUG-0001")
        self.db_path.unlink()
        self.assertEqual(self.show("BUG-0001"), want)

    def test_external_change_is_seen_by_every_command(self):
        self.add()
        self.seed(create("ext", 2, "2030-01-01T00:00:00.000Z", title="From a pull"))
        self.assertIn("From a pull", self.ok("list"))
        self.seed(create("ext2", 3, "2030-01-02T00:00:00.000Z", title="Second pull"))
        self.assertIn("Second pull", self.ok("show", "BUG-0003"))
        self.seed(create("ext3", 4, "2030-01-03T00:00:00.000Z"))
        self.assertTrue(self.counters("BUG-0004")["found"])
        self.seed(create("ext4", 5, "2030-01-04T00:00:00.000Z", priority="Highest"))
        self.assertIn("5 open", self.ok("stats"))
        self.seed(create("ext5", 6, "2030-01-05T00:00:00.000Z", title="Findable elephant"))
        self.assertIn("BUG-0006", self.ok("search", "elephant"))
        self.seed(create("ext6", 7, "2030-01-06T00:00:00.000Z"))
        self.assertIn("7", self.ok("sql", "SELECT COUNT(*) AS n FROM bug"))
        self.seed(create("ext7", 8, "2030-01-07T00:00:00.000Z"))
        self.assertEqual(self.add(), "BUG-0009")  # the write path rebuilds before it picks an id

    def test_journal_removed_reads_empty(self):
        self.add()
        self.journal.unlink()
        self.assertEqual(json.loads(self.ok("list", "--json")), [])

    def test_ts_is_monotonic_under_clock_skew(self):
        self.seed(create("a", 1, "2030-01-01T00:00:00.000Z"))
        self.ok("update", "BUG-0001", stdin={"priority": "Low"}, now="2026-01-01T00:00:00Z")
        self.ok("update", "BUG-0001", stdin={"priority": "High"}, now="2026-01-01T00:00:00Z")
        ts = [e["ts"] for e in self.lines()]
        self.assertEqual(ts, ["2030-01-01T00:00:00.000Z", "2030-01-01T00:00:00.001Z", "2030-01-01T00:00:00.002Z"])
        self.assertEqual(self.show("BUG-0001")["priority"], "High")

    def test_ts_uses_now_when_the_clock_is_ahead(self):
        self.ok("add", stdin=fields(), now="2026-05-05T05:05:05.123Z")
        self.assertEqual(self.lines()[0]["ts"], "2026-05-05T05:05:05.123Z")

    def test_corrupt_db_file_heals(self):
        self.add()
        self.db_path.write_bytes(b"this is not a database at all" * 100)
        self.assertEqual(self.show("BUG-0001")["id"], "BUG-0001")

    def test_old_schema_version_heals(self):
        self.add()
        db = sqlite3.connect(str(self.db_path))
        db.execute("PRAGMA user_version=999")
        db.commit()
        db.close()
        self.assertEqual(self.show("BUG-0001")["id"], "BUG-0001")

    def test_rebuild_reports_counts(self):
        self.add()
        self.add()
        self.assertIn("2 bugs", self.ok("rebuild"))


class TestCrashAndTorn(Base):
    def crash_run(self, argv, stdin=None, hook="_after_append"):
        code = ("import os, sys; sys.path.insert(0, %r); import bugs; bugs.%s = lambda: os._exit(9); "
                "sys.exit(bugs.main(%r))") % (str(HERE), hook, ["--root", str(self.root)] + argv)
        return subprocess.run([sys.executable, "-I", "-c", code], input=stdin, capture_output=True).returncode

    def test_crash_between_append_and_commit_is_healed(self):
        self.add()
        self.assertEqual(self.crash_run(["add"], json.dumps(fields(title="Written then crashed")).encode("utf-8")), 9)
        self.assertIn(b"Written then crashed", self.journal.read_bytes())
        self.assertEqual(self.show("BUG-0002")["title"], "Written then crashed")
        self.assertEqual(self.add(), "BUG-0003")

    def test_crash_on_the_very_first_write_is_healed(self):
        self.assertEqual(self.crash_run(["add"], json.dumps(fields()).encode("utf-8")), 9)
        self.assertEqual(self.show("BUG-0001")["id"], "BUG-0001")

    def test_crash_during_purge_is_healed(self):
        self.seed(create("c1", 1, stamp(-5)), event("status", "c1", {"to": "Complete"}, T0))
        self.ok("rebuild")
        code = ("import os, sys; sys.path.insert(0, %r); import bugs; bugs._after_append = lambda: os._exit(9); "
                "os.environ['BUGS_NOW'] = %r; sys.exit(bugs.main(%r))") % (str(HERE), stamp(91), ["--root", str(self.root), "purge"])
        self.assertEqual(subprocess.run([sys.executable, "-I", "-c", code], capture_output=True).returncode, 9)
        self.assertFalse(self.counters("BUG-0001")["found"])
        self.assertEqual(self.add(), "BUG-0002")

    def test_failed_write_rolls_back_the_db(self):
        self.add()
        with mock.patch.object(bugs, "append_lines", side_effect=OSError("disk full")):
            self.assertIn("disk full", self.no("update", "BUG-0001", stdin={"priority": "High"}))
        self.assertEqual(self.show("BUG-0001")["priority"], "Medium")

    def test_valid_final_line_without_newline_gets_repaired_on_append(self):
        self.add()
        raw = self.journal.read_bytes()
        self.journal.write_bytes(raw[:-1])
        self.assertTrue(self.counters("BUG-0001")["found"])
        self.assertEqual(self.add(), "BUG-0002")
        self.assertEqual(len(self.lines()), 2)
        self.assertTrue(self.journal.read_bytes().endswith(b"\n"))

    def test_torn_fragment_reads_past_it_and_the_next_write_removes_it(self):
        self.add()
        whole = self.journal.read_bytes()
        with open(self.journal, "ab") as f:
            f.write(whole[:40])
        self.assertTrue(self.counters("BUG-0001")["found"])
        self.assertEqual(len(json.loads(self.ok("list", "--json"))), 1)
        self.assertIn("torn", self.no("doctor"))
        self.assertEqual(self.add(), "BUG-0002")
        self.assertEqual(len(self.lines()), 2)
        self.ok("doctor")

    def test_torn_fragment_with_a_cut_multibyte_char_is_torn_not_corrupt(self):
        self.add(actual="Dash — here")
        whole = self.journal.read_bytes()
        cut = whole.index("—".encode("utf-8")) + 1
        with open(self.journal, "ab") as f:
            f.write(whole[:cut])
        self.assertTrue(self.counters("BUG-0001")["found"])

    def test_doctor_fix_removes_the_fragment(self):
        self.add()
        with open(self.journal, "ab") as f:
            f.write(b'{"event_uid":"x')
        self.ok("doctor", "--fix")
        self.assertEqual(len(self.lines()), 1)
        self.ok("doctor")

    def test_malformed_terminated_line_stays_a_refusal(self):
        self.add()
        with open(self.journal, "ab") as f:
            f.write(b'{"event_uid":"x\n')
        self.assertIn("corrupt journal", self.no("list"))
        self.assertIn("line 2", self.no("doctor"))
        self.assertIn("line 2", self.no("doctor", "--fix"))

    def test_repairing_a_fragment_never_rewrites_the_good_lines(self):
        self.add()
        whole = self.journal.read_bytes()
        with open(self.journal, "ab") as f:
            f.write(b'{"event_uid":"x')
        self.add()
        self.assertTrue(self.journal.read_bytes().startswith(whole))
        self.assertEqual(len(self.lines()), 2)

    def test_reads_do_not_wait_for_a_writer(self):
        self.add()
        self.ok("rebuild")
        held = sqlite3.connect(str(self.db_path), isolation_level=None)
        held.execute("BEGIN IMMEDIATE")
        try:
            self.assertTrue(self.counters("BUG-0001")["found"])
            self.assertIn("1 open", self.ok("stats"))
        finally:
            held.execute("ROLLBACK")
            held.close()

    def test_crlf_journal_still_replays(self):
        self.add()
        self.journal.write_bytes(self.journal.read_bytes().replace(b"\n", b"\r\n"))
        self.assertEqual(self.show("BUG-0001")["id"], "BUG-0001")
        self.assertEqual(self.add(), "BUG-0002")
        self.assertEqual(len(self.lines()), 2)

    def test_parallel_writers_do_not_lose_lines(self):
        self.add()
        cmd = [sys.executable, "-I", str(HERE / "bugs.py"), "--root", str(self.root), "add"]
        procs = [subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(6)]
        results = [p.communicate(json.dumps(fields()).encode("utf-8")) for p in procs]
        self.assertTrue(all(p.returncode == 0 for p in procs), results)
        ids = sorted(r[0].decode().strip() for r in results)
        self.assertEqual(ids, ["BUG-%04d" % i for i in range(2, 8)])
        self.assertEqual(len(self.lines()), 7)


class TestDuplicateIds(Base):
    def seed_dup(self):
        self.seed(create("first", 1, stamp(1), title="First holder"), create("second", 1, stamp(2), title="Second holder"),
                  create("other", 2, stamp(3), title="Unrelated"))

    def test_counters_and_writes_fail_closed(self):
        self.seed_dup()
        err = self.no("counters", "BUG-0001", "--json")
        self.assertIn("duplicate", err)
        self.assertIn("doctor --fix", err)
        for args, stdin in ((["update", "BUG-0001"], {"priority": "Low"}),
                            (["set-status", "BUG-0001", "Processing", "--note", "x"], None),
                            (["round", "BUG-0001", "fix", "+1", "--note", "x"], None),
                            (["extra-round", "BUG-0001", "fix", "+1", "--note", "x"], None),
                            (["stop-rule", "BUG-0001", "fix", "--extra-dispatch", "used"], None),
                            (["delete", "BUG-0001", "--by", "GD"], None)):
            self.assertIn("duplicate", self.no(*args, stdin=stdin))

    def test_other_ids_stay_writable_and_new_ids_clear_the_high_water(self):
        self.seed_dup()
        self.ok("update", "BUG-0002", stdin={"priority": "Low"})
        self.assertEqual(self.add(), "BUG-0003")

    def test_reads_report_it(self):
        self.seed_dup()
        code, out, err = self.run_cli("list")
        self.assertEqual(code, 0)
        self.assertIn("duplicate", err)
        self.assertIn("First holder", out)
        self.assertIn("Second holder", out)
        self.assertIn("duplicate", self.run_cli("show", "BUG-0001")[2])
        self.assertIn("duplicate", self.run_cli("rebuild")[2])
        self.assertIn("BUG-0001", self.no("doctor"))

    def test_doctor_fix_renumbers_the_later_create_durably(self):
        self.seed_dup()
        out = self.ok("doctor", "--fix")
        self.assertIn("BUG-0003", out)
        self.assertEqual(self.show("BUG-0001")["title"], "First holder")
        self.assertEqual(self.show("BUG-0003")["title"], "Second holder")
        last = self.lines()[-1]
        self.assertEqual((last["type"], last["bug_uid"], last["data"]), ("renumber", "second", {"from": 1, "to": 3}))
        self.ok("doctor")
        self.db_path.unlink()
        self.assertEqual(self.show("BUG-0003")["title"], "Second holder")
        self.assertEqual(self.add(), "BUG-0004")

    def test_later_lines_attach_by_uid_after_a_renumber(self):
        self.seed_dup()
        self.ok("doctor", "--fix")
        self.ok("update", "BUG-0003", stdin={"root_cause": "Attached by uid"})
        self.assertEqual(self.lines()[-1]["bug_uid"], "second")
        self.assertIsNone(self.show("BUG-0001")["root_cause"])
        self.assertEqual(self.show("BUG-0003")["root_cause"], "Attached by uid")

    def test_same_renumber_from_two_machines_dedupes(self):
        self.seed_dup()
        self.ok("doctor", "--fix")
        last = self.lines()[-1]
        self.seed(dict(last, ts=stamp(50)))
        self.assertEqual(self.show("BUG-0003")["title"], "Second holder")
        self.ok("doctor")

    def test_three_holders(self):
        self.seed(create("a", 1, stamp(1)), create("b", 1, stamp(2)), create("c", 1, stamp(3)))
        self.ok("doctor", "--fix")
        self.assertEqual([b["id"] for b in json.loads(self.ok("list", "--json"))], ["BUG-0001", "BUG-0002", "BUG-0003"])
        self.ok("doctor")

    def test_high_water_counts_renumbers_and_tombstones(self):
        self.seed(create("a", 1, stamp(1)), event("renumber", "a", {"from": 1, "to": 7}, stamp(2)))
        self.assertEqual(self.add(), "BUG-0008")
        self.journal.unlink()
        self.seed(event("tombstone", "gone", {"id": 12}, stamp(1)))
        self.assertEqual(self.add(), "BUG-0013")


class TestContentRules(Base):
    LIMITS = {"title": 100, "description": 280, "repro": 500, "expected": 300, "actual": 300, "evidence": 300, "root_cause": 300}

    def test_each_field_at_its_limit_accepted_one_over_refused_never_truncated(self):
        for field, limit in self.LIMITS.items():
            with self.subTest(field):
                bug_id = self.ok("add", stdin=fields(**{field: "x" * limit})).strip()
                self.assertEqual(self.show(bug_id)[field], "x" * limit)
                before = self.journal.read_bytes()
                err = self.no("add", stdin=fields(**{field: "x" * (limit + 1)}))
                self.assertIn(field, err)
                self.assertIn(str(limit + 1), err)
                self.assertEqual(self.journal.read_bytes(), before)
                err = self.no("update", bug_id, stdin={field: "y" * (limit + 1)})
                self.assertIn(field, err)
                self.assertIn(str(limit + 1), err)
                self.assertEqual(self.show(bug_id)[field], "x" * limit)

    def test_note_limit_on_every_command_that_takes_one(self):
        self.add()
        at, over = "n" * 200, "n" * 201
        for args in (["set-status", "BUG-0001", "Processing"], ["round", "BUG-0001", "fix", "+1"], ["extra-round", "BUG-0001", "fix", "+1"]):
            err = self.no(*args, "--note", over)
            self.assertIn("note", err)
            self.assertIn("201", err)
            self.ok(*args, "--note", at)
        self.assertIn("note", self.no("update", "BUG-0001", stdin={"priority": "Low", "note": over}))
        self.assertIn("note", self.no("stop-rule", "BUG-0001", "fix", "--extra-dispatch", "used", "--note", over))

    def test_missing_or_blank_required_fields_refused(self):
        for field in ("title", "description", "repro", "expected", "actual", "evidence"):
            with self.subTest(field):
                d = fields()
                del d[field]
                self.assertIn(field, self.no("add", stdin=d))
                self.assertIn(field, self.no("add", stdin=fields(**{field: "   "})))
        self.assertFalse(self.journal.exists())
        self.assertFalse(self.db_path.exists())

    def test_repro_accepts_not_yet(self):
        self.add(repro="not yet")
        self.assertEqual(self.show("BUG-0001")["repro"], "not yet")

    def test_newline_refused_in_one_line_fields(self):
        for field in ("title", "description", "feature", "owner", "regression_test"):
            for nl in ("\n", "\r\n", "\r", "\u2028", "\x0b"):
                with self.subTest(field=field, nl=repr(nl)):
                    self.assertIn(field, self.no("add", stdin=fields(**{field: "one" + nl + "two"})))

    def test_newline_refused_in_note_and_by(self):
        self.add()
        self.assertIn("note", self.no("set-status", "BUG-0001", "Processing", stdin={"note": "a\nb"}))
        self.assertIn("note", self.no("set-status", "BUG-0001", "Processing", "--note", "a\nb"))
        self.assertIn("by", self.no("set-status", "BUG-0001", "Processing", "--note", "n", "--by", "a\nb"))

    def test_multi_line_allowed_where_the_spec_does_not_say_one_line(self):
        self.add(repro="1. Load slot\n2. Overwrite")
        self.assertEqual(self.show("BUG-0001")["repro"], "1. Load slot\n2. Overwrite")
        self.assertEqual(len(self.lines()), 1)  # the newline stays escaped: one journal line per event

    def test_non_string_refused(self):
        for bad in (7, None, ["a"], {"a": 1}, True):
            self.assertIn("title", self.no("add", stdin=fields(title=bad)))

    def test_control_characters_refused(self):
        self.assertIn("title", self.no("add", stdin=fields(title="bell\x07")))

    def test_over_limit_message_never_echoes_the_value(self):
        err = self.no("add", stdin=fields(title="secretish" * 20))
        self.assertNotIn("secretish", err)


class TestEnglish(Base):
    TEXT = ("title", "description", "repro", "expected", "actual", "evidence", "root_cause", "feature", "owner", "regression_test")

    def test_every_vietnamese_letter_refused_lower_upper_and_decomposed(self):
        self.assertEqual(len(VI_LOWER), 67)
        for ch in VI_LOWER + VI_LOWER.upper():
            for form in ("NFC", "NFD"):
                with self.subTest(ch=ch, form=form):
                    with self.assertRaises(bugs.Refused):
                        bugs.check_english("title", unicodedata.normalize(form, "ab" + ch + "cd"))

    def test_ascii_and_english_punctuation_pass(self):
        bugs.check_english("title", "Plain text - with dash — ellipsis … arrows → and dot · and $vars \"quoted\"")

    def test_refused_in_every_text_field(self):
        for field in self.TEXT:
            with self.subTest(field):
                self.assertIn(field, self.no("add", stdin=fields(**{field: "Lỗi màn hình"})))
        self.assertFalse(self.journal.exists())

    def test_refused_on_update_note_and_by(self):
        self.add()
        for field in self.TEXT:
            self.assertIn(field, self.no("update", "BUG-0001", stdin={field: "Không chạy"}))
        self.assertIn("note", self.no("update", "BUG-0001", stdin={"priority": "Low", "note": "đã sửa"}))
        self.assertIn("note", self.no("set-status", "BUG-0001", "Processing", "--note", "đã sửa"))
        self.assertIn("note", self.no("set-status", "BUG-0001", "Processing", stdin={"note": "đã sửa"}))
        self.assertIn("note", self.no("round", "BUG-0001", "fix", "+1", "--note", "đã sửa"))
        self.assertIn("note", self.no("extra-round", "BUG-0001", "fix", "+1", "--note", "đã sửa"))
        self.assertIn("note", self.no("stop-rule", "BUG-0001", "fix", "--extra-dispatch", "used", "--note", "đã sửa"))
        self.assertIn("by", self.no("set-status", "BUG-0001", "Processing", "--note", "n", "--by", "Quản lý"))
        self.assertIn("by", self.no("add", "--by", "Quản lý", stdin=fields()))
        self.assertIn("by", self.no("round", "BUG-0001", "fix", "+1", "--note", "n", "--by", "Quản lý"))

    def test_refused_decomposed_through_the_cli(self):
        self.assertIn("title", self.no("add", stdin=fields(title=unicodedata.normalize("NFD", "Lỗi"))))


class TestSecurity(Base):
    TEXT = TestEnglish.TEXT

    def test_secret_refused_in_every_field_and_nothing_written(self):
        for field in self.TEXT:
            with self.subTest(field):
                err = self.no("add", stdin=fields(**{field: "key " + FAKE_KEY}))
                self.assertIn("secret-shaped", err)
                self.assertIn(field, err)
                self.assertIn("AWS access key", err)
                self.assertNotIn(FAKE_KEY, err)
        self.assertFalse(self.journal.exists())

    def test_secret_refused_on_update_note_and_by(self):
        self.add()
        self.assertIn("secret-shaped", self.no("update", "BUG-0001", stdin={"actual": FAKE_KEY}))
        self.assertIn("secret-shaped", self.no("set-status", "BUG-0001", "Processing", "--note", FAKE_KEY))
        self.assertIn("secret-shaped", self.no("set-status", "BUG-0001", "Processing", stdin={"note": FAKE_KEY}))
        self.assertIn("secret-shaped", self.no("round", "BUG-0001", "fix", "+1", "--note", FAKE_KEY))
        self.assertIn("secret-shaped", self.no("set-status", "BUG-0001", "Processing", "--note", "n", "--by", FAKE_KEY))
        self.assertNotIn(FAKE_KEY.encode(), self.journal.read_bytes())

    def test_private_key_block_refused_header_only_forms_too(self):
        self.assertIn("secret-shaped", self.no("add", stdin=fields(repro=PEM_HEADER + "\nabc")))
        self.assertIn("secret-shaped", self.no("add", stdin=fields(repro="-----BEGIN ODD PRIVATE" + " KEY-----\nabc")))

    def test_pii_redacted_in_store_and_journal(self):
        email, ip, phone, idfa = "qa.tester@example.com", "203.0.113.7", "+1 555 010 9999", "AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA"
        code, out, err = self.run_cli("add", stdin=fields(
            actual="Contact %s from %s" % (email, ip), evidence="phone %s" % phone, repro="idfa: %s" % idfa))
        self.assertEqual(code, 0, err)
        b = self.show("BUG-0001")
        self.assertEqual(b["actual"], "Contact [REDACTED:email] from [REDACTED:ip]")
        self.assertEqual(b["evidence"], "phone [REDACTED:phone]")
        self.assertIn("[REDACTED:device id]", b["repro"])
        self.assertTrue(bugs.mem_module().RX_DEVICE_ID.search("idfa: " + idfa))
        raw = self.journal.read_text(encoding="utf-8")
        for value in (email, ip, phone, idfa):
            self.assertNotIn(value, raw)
        self.assertIn("redacted", err)
        self.assertNotIn(email, err)

    def test_pii_redacted_in_notes_too(self):
        self.add()
        self.ok("set-status", "BUG-0001", "Processing", "--note", "told qa.tester@example.com")
        self.assertEqual(self.show("BUG-0001")["events"][-1]["note"], "told [REDACTED:email]")

    def test_redaction_counts_against_the_limit_it_stores(self):
        self.add(title="Short")
        self.assertIn("title", self.no("update", "BUG-0001", stdin={"title": "x" * 90 + " a@ex.io"}))

    def test_missing_pattern_file_refuses_the_write(self):
        script = self.isolated_copy(with_mem=True, with_patterns=False)
        r = self.cli(script, "add", stdin=json.dumps(fields()).encode("utf-8"))
        self.assertNotEqual(r.returncode, 0)
        self.assertTrue(r.stderr.strip())
        self.assertFalse(self.journal.exists())

    def test_missing_mem_module_refuses_the_write_but_reads_work(self):
        script = self.isolated_copy(with_mem=False, with_patterns=True)
        r = self.cli(script, "add", stdin=json.dumps(fields()).encode("utf-8"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(b"mem.py", r.stderr)
        self.assertFalse(self.journal.exists())
        self.assertEqual(self.cli(script, "list").returncode, 0)

    def test_broken_pattern_file_refuses_the_write(self):
        script = self.isolated_copy(with_mem=True, with_patterns=True)
        patterns = script.parents[3] / "hooks" / "secret-patterns.txt"
        patterns.write_text("# only comments\n", encoding="utf-8")
        r = self.cli(script, "add", stdin=json.dumps(fields()).encode("utf-8"))
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(self.journal.exists())

    def test_project_pattern_file_wins(self):
        pat = self.root / ".claude" / "hooks"
        pat.mkdir(parents=True)
        (pat / "secret-patterns.txt").write_text("house key\tHOUSEKEY[0-9]+\n", encoding="utf-8")
        self.assertIn("house key", self.no("add", stdin=fields(actual="HOUSEKEY123")))

    def test_source_builds_no_sql_from_journal_values(self):
        self.add()
        self.seed(event("update", "x", {"title; DROP TABLE bug; --": "x"}, stamp(1)))
        self.no("list")
        db = sqlite3.connect(str(self.db_path))
        try:
            self.assertTrue(db.execute("SELECT COUNT(*) FROM bug").fetchone()[0])
        finally:
            db.close()


class TestSql(Base):
    WRITES = [
        "INSERT INTO bug(uid, id, title, description, priority, status) VALUES('x','BUG-9','t','d','Low','Request')",
        "REPLACE INTO meta(key, value) VALUES('a','b')",
        "UPDATE bug SET title='hacked'",
        "DELETE FROM bug",
        "DROP TABLE bug",
        "DROP INDEX bug_status",
        "CREATE TABLE evil(a)",
        "CREATE TEMP TABLE evil(a)",
        "CREATE INDEX evil ON bug(title)",
        "CREATE VIEW evil AS SELECT 1",
        "CREATE TRIGGER evil AFTER UPDATE ON bug BEGIN SELECT 1; END",
        "ALTER TABLE bug ADD COLUMN evil TEXT",
        "ALTER TABLE bug RENAME TO evil",
        "REINDEX",
        "ANALYZE",
        "VACUUM",
        "VACUUM INTO '%(out)s'",
        "ATTACH DATABASE '%(out)s' AS evil",
        "DETACH DATABASE main",
        "PRAGMA writable_schema=1",
        "PRAGMA journal_mode=WAL",
        "PRAGMA user_version=99",
        "PRAGMA query_only=OFF",
        "BEGIN",
        "COMMIT",
        "ROLLBACK",
        "SAVEPOINT s",
        "RELEASE s",
        "WITH x AS (SELECT 1) DELETE FROM bug",
        "WITH x AS (SELECT 1) INSERT INTO meta SELECT 'a','b' FROM x",
        "WITH x AS (SELECT 1) UPDATE bug SET title='h'",
        "SELECT 1; DROP TABLE bug",
        "SELECT 1; DELETE FROM bug;",
        "/* comment */ DELETE FROM bug",
        "-- comment\nDELETE FROM bug",
        "  delete from bug",
        "INSERT INTO bug_fts(bug_fts) VALUES('delete-all')",
        "SELECT load_extension('x')",
    ]

    def test_rejects_every_write_form(self):
        self.add()
        out = Path(self.tmp) / "stolen.db"
        before = self.ok("sql", "SELECT id, title, status FROM bug")
        schema = self.ok("sql", "SELECT name FROM sqlite_master ORDER BY name")
        for stmt in self.WRITES:
            with self.subTest(stmt):
                code, stdout, err = self.run_cli("sql", stmt % {"out": out.as_posix()} if "%(" in stmt else stmt)
                self.assertNotEqual(code, 0, stdout)
                self.assertTrue(err.strip())
                self.assertFalse(out.exists())
        self.assertEqual(self.ok("sql", "SELECT id, title, status FROM bug"), before)
        self.assertEqual(self.ok("sql", "SELECT name FROM sqlite_master ORDER BY name"), schema)
        self.assertEqual(len(self.lines()), 1)

    def test_rejects_writes_on_the_empty_store_too(self):
        for stmt in ("CREATE TABLE evil(a)", "DROP TABLE bug", "DELETE FROM bug"):
            self.no("sql", stmt)
        self.assertFalse((self.root / ".workflow").exists())

    def test_connection_is_opened_read_only(self):
        self.add()
        seen = []
        real = sqlite3.connect

        def spy(database, *a, **k):
            seen.append(str(database))
            return real(database, *a, **k)

        with mock.patch.object(bugs.sqlite3, "connect", spy):
            self.ok("sql", "SELECT 1")
        self.assertTrue(any("mode=ro" in s for s in seen), seen)

    def test_reads_work_including_fts_cte_and_the_views_of_the_store(self):
        self.add(title="Elephant in the inventory")
        self.assertIn("Elephant", self.ok("sql", "SELECT title FROM bug WHERE id='BUG-0001'"))
        self.assertIn("create", self.ok("sql", "SELECT type FROM bug_event"))
        self.assertIn("BUG-0001", self.ok("sql", "WITH x AS (SELECT id FROM bug) SELECT * FROM x"))
        self.assertIn("Elephant", self.ok("sql", "SELECT title FROM bug_fts WHERE bug_fts MATCH 'elephant'"))
        self.assertIn("3", self.ok("sql", "WITH RECURSIVE c(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM c WHERE n<3) SELECT MAX(n) FROM c"))
        self.assertEqual(json.loads(self.ok("sql", "SELECT id, priority FROM bug", "--json")), [{"id": "BUG-0001", "priority": "Medium"}])

    def test_runaway_query_is_stopped(self):
        self.add()
        with mock.patch.object(bugs, "SQL_SECONDS", 0.05):
            self.assertIn("interrupted", self.no("sql", "WITH RECURSIVE c(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM c) SELECT MAX(n) FROM c"))

    def test_a_real_interrupt_during_a_query_exits_130(self):
        timer = threading.Timer(0.5, _thread.interrupt_main)
        timer.start()
        try:
            code, out, err = self.run_cli("sql", "WITH RECURSIVE c(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM c) SELECT MAX(n) FROM c")
        finally:
            timer.cancel()
        self.assertEqual((code, out), (130, ""))
        self.assertIn("bugs: interrupted", err)
        self.assertNotIn("sql refused", err)

    def test_a_blob_result_is_hex_in_json_and_text(self):
        code, out, err = self.run_cli("sql", "SELECT x'00ff' AS b, 'plain' AS t, 1 AS n, NULL AS z", "--json")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out), [{"b": "x'00ff'", "t": "plain", "n": 1, "z": None}])
        self.assertEqual(self.ok("sql", "SELECT x'00ff' AS b").split(), ["b", "x'00ff'"])

    def test_text_that_is_not_utf8_is_a_clean_refusal(self):
        self.assertIn("sql refused", self.no("sql", "SELECT CAST(x'ff' AS TEXT) AS bad", "--json"))

    def test_bad_sql_is_an_error(self):
        self.add()
        self.no("sql", "SELECT nope FROM nothing")
        self.no("sql", "")


class TestBugsMdRefusal(Base):
    def test_every_command_but_import_md_refuses(self):
        self.add()
        (self.root / ".workflow" / "bugs.md").write_text("# Bugs\n", encoding="utf-8")
        calls = [["add"], ["update", "BUG-0001"], ["set-status", "BUG-0001", "Processing", "--note", "n"],
                 ["round", "BUG-0001", "fix", "+1", "--note", "n"], ["extra-round", "BUG-0001", "fix", "+1", "--note", "n"],
                 ["stop-rule", "BUG-0001", "fix", "--extra-dispatch", "used"], ["show", "BUG-0001"], ["list"], ["search", "x"],
                 ["sql", "SELECT 1"], ["delete", "BUG-0001", "--by", "GD"], ["counters", "BUG-0001", "--json"], ["purge"],
                 ["purge", "--auto"], ["purge", "--dry-run"], ["rebuild"], ["doctor"], ["doctor", "--fix"], ["stats"]]
        for argv in calls:
            with self.subTest(argv):
                self.assertIn("bugs.md", self.no(*argv, stdin=fields() if argv[0] == "add" else None))


# develop:.claude/skills/fix/references/bugs-template.md, the file an adopted project with no bugs holds.
ZERO_ROW_BUGS_MD = """# Bugs

Next ID: BUG-0001

| ID | Title | Severity | Status | Feature | Owner | Regression test |
|---|---|---|---|---|---|---|

<!-- One record per bug, below the table. Delete this comment and the sample heading. -->
## BUG-#### \u2014 <title>
- Repro: <steps from a known state; attempts / hits>
- Expected: <and its source> \u00b7 Actual: <observed>
- Evidence: <log, screenshot, failing test>
- Root cause: <when known>
- Fix rounds: 0/2
- Review rounds: 0/3
- Stop rule: <counter> root-caused <date> - extra dispatch: unused|used (only when it fires)
- History: <date status \u2014 by whom, evidence>
"""


class TestZeroRowImport(Base):
    """E3-15: after the ordered delete, a project with no bugs has the empty journal /release asks for."""

    def test_the_real_template_leaves_an_empty_journal(self):
        md = self.root / ".workflow" / "bugs.md"
        md.parent.mkdir()
        md.write_text(ZERO_ROW_BUGS_MD, encoding="utf-8")
        self.assertIn("imported 0 bugs", self.ok("import-md"))
        md.unlink()
        self.assertEqual(self.journal.read_bytes(), b"")
        self.assertEqual(self.ok("stats").split(" open")[0], "Bugs: 0")
        self.assertEqual(self.ok("doctor"), "doctor: clean\n")
        self.assertEqual(self.add(), "BUG-0001")

    def test_a_journal_already_there_is_left_alone(self):
        self.add()
        before = self.journal.read_bytes()
        (self.root / ".workflow" / "bugs.md").write_text(ZERO_ROW_BUGS_MD, encoding="utf-8")
        self.ok("import-md")
        self.assertEqual(self.journal.read_bytes(), before)


class TestImport(Base):
    def write_md(self, text, root=None):
        p = (root or self.root) / ".workflow"
        p.mkdir(parents=True, exist_ok=True)
        with open(p / "bugs.md", "w", encoding="utf-8", newline="") as f:
            f.write(text)
        return p / "bugs.md"

    def imported(self, text=REAL_BUGS_MD):
        md = self.write_md(text)
        out = self.ok("import-md")
        md.unlink()
        return out

    def test_real_file_imports_five_complete_bugs(self):
        out = self.imported()
        self.assertIn("5 bugs", out)
        rows = json.loads(self.ok("list", "--json"))
        self.assertEqual([r["id"] for r in rows], ["BUG-%04d" % i for i in range(1, 6)])
        for r in rows:
            self.assertEqual(r["status"], "Complete")
            self.assertTrue(r["closed_at"].startswith("2026-10-29"), r)
            self.assertEqual(r["feature"], "engineer-skill-gaps")
            self.assertEqual(r["regression_test"], "Written repro (docs, no seam)")
        self.assertEqual([r["priority"] for r in rows], ["Medium", "Medium", "Low", "High", "Medium"])
        self.assertEqual(self.ok("stats").strip(), "Bugs: 0 open (0 High+)")

    def test_real_file_keeps_each_field(self):
        self.imported()
        b = self.show("BUG-0004")
        self.assertEqual(b["title"], "Apple Family-Shared refund fallback can reverse or tombstone the purchaser's grant")
        self.assertEqual(b["owner"], "iap-server-receipt-ledger (backend author)")
        self.assertEqual(b["expected"], "a family REVOKE never reverses or blocks the purchaser's PURCHASED grant")
        self.assertEqual(b["actual"], "fallback can land on the purchaser's entry; a tombstone can block their later grant.")
        self.assertEqual(b["description"], b["actual"])
        self.assertIn("appAccountToken+productId", b["repro"])
        self.assertEqual(b["evidence"], "security re-check after QA fixes, F-1.")
        self.assertIsNone(b["root_cause"])
        self.assertEqual(self.show("BUG-0002")["root_cause"], "R3-1 fix text written by the main session named only `ApplyAdConsentSignals` for on-close.")

    def test_real_file_history_becomes_events(self):
        self.imported()
        for i in range(1, 6):
            e = self.show("BUG-%04d" % i)["events"]
            self.assertEqual([x["type"] for x in e], ["create", "status", "status"])
            self.assertEqual([json.loads(x["data"]).get("to") for x in e[1:]], ["Resolved", "Complete"])
            self.assertTrue(all(x["ts"].startswith("2026-10-29") for x in e))
            self.assertEqual(e[0]["by"], "import-md")
        e = self.show("BUG-0004")["events"]
        self.assertEqual(e[0]["note"], "security-reviewer.")
        self.assertIn("tombstones only from PURCHASED", e[1]["note"])
        self.assertIn("qa-lead re-read", e[2]["note"])

    def test_next_id_follows_the_file(self):
        self.imported()
        self.assertEqual(self.add(), "BUG-0006")

    def test_crlf_copy_imports_the_same(self):
        self.imported(REAL_BUGS_MD.replace("\n", "\r\n"))
        want = self.journal.read_bytes()
        other = Path(self.tmp) / "other"
        other.mkdir()
        self.write_md(REAL_BUGS_MD, root=other)
        self.ok("import-md", root=other)
        self.assertEqual((other / ".workflow" / "bugs.jsonl").read_bytes(), want)

    def test_uids_are_deterministic_and_rerun_cannot_duplicate(self):
        md = self.write_md(REAL_BUGS_MD)
        self.ok("import-md")
        first = self.journal.read_bytes()
        self.assertIn("0 bugs", self.ok("import-md"))
        self.assertEqual(self.journal.read_bytes(), first)
        self.assertTrue(md.exists(), "deleting the file is the caller's job")
        uids = {e["bug_uid"] for e in self.lines()}
        self.assertEqual(len(uids), 5)
        for u in uids:
            self.assertRegex(u, r"^[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-")

    def test_import_keeps_working_with_the_file_present_and_nothing_else_does(self):
        self.write_md(REAL_BUGS_MD)
        self.ok("import-md")
        self.assertIn("bugs.md", self.no("list"))

    def test_missing_file_is_an_error(self):
        self.assertIn("bugs.md", self.no("import-md"))

    def test_journal_is_lf_after_import(self):
        self.imported(REAL_BUGS_MD.replace("\n", "\r\n"))
        self.assertNotIn(b"\r", self.journal.read_bytes())

    def test_over_limit_stops_the_whole_import_with_a_report(self):
        good = md_record()
        bad = md_record("BUG-0002", actual="x" * 281)
        self.write_md(md_file(good, bad))
        err = self.no("import-md")
        self.assertIn("BUG-0002", err)
        self.assertIn("description", err)
        self.assertIn("281", err)
        self.assertFalse(self.journal.exists())
        self.assertFalse(self.db_path.exists())

    def test_every_problem_is_reported_at_once(self):
        self.write_md(md_file(md_record("BUG-0001", title="t" * 101), md_record("BUG-0002", evidence="e" * 301),
                              md_record("BUG-0003", history="2026-10-29 Open — " + "n" * 201)))
        err = self.no("import-md")
        for piece in ("BUG-0001 title: 101", "BUG-0002 evidence: 301", "BUG-0003 note: 201"):
            self.assertIn(piece, err)

    def test_vietnamese_and_secret_stop_the_import(self):
        self.write_md(md_file(md_record(actual="không chạy")))
        self.assertIn("actual", self.no("import-md"))
        self.write_md(md_file(md_record(evidence=FAKE_KEY)))
        err = self.no("import-md")
        self.assertIn("secret-shaped", err)
        self.assertNotIn(FAKE_KEY, err)
        self.assertFalse(self.journal.exists())

    def test_pii_is_redacted_on_import(self):
        self.imported(md_file(md_record(actual="seen by qa.tester@example.com")))
        self.assertEqual(self.show("BUG-0001")["actual"], "seen by [REDACTED:email]")

    def test_severity_map(self):
        self.imported(md_file(md_record("BUG-0001", severity="Critical"), md_record("BUG-0002", severity="High"),
                              md_record("BUG-0003", severity="Medium"), md_record("BUG-0004", severity="Low")))
        self.assertEqual([r["priority"] for r in json.loads(self.ok("list", "--json"))], ["Highest", "High", "Medium", "Low"])

    def test_unknown_severity_stops(self):
        self.write_md(md_file(md_record(severity="Blocker")))
        self.assertIn("Blocker", self.no("import-md"))

    def test_status_map_and_final_status_must_match_the_table(self):
        h = "2026-10-29 Open — a. 2026-10-30 Fixed — b. 2026-10-31 Closed — c. 2026-11-01 Reopened — d."
        self.imported(md_file(md_record(status="Reopened", history=h)))
        b = self.show("BUG-0001")
        self.assertEqual(b["status"], "Reopen")
        self.assertIsNone(b["closed_at"])
        self.write_md(md_file(md_record(status="Closed", history="2026-10-29 Open — a.")))
        self.assertIn("History", self.no("import-md", root=self.root))

    def test_kept_statuses(self):
        for i, (old, h) in enumerate((("Won't fix", "Won't fix — GD."), ("Accepted", "Accepted — GD."), ("As designed", "As designed — QA."),
                                      ("Duplicate", "Duplicate — of BUG-0001.")), 2):
            self.write_md(md_file(md_record("BUG-0001"), md_record("BUG-%04d" % i, status=old, history="2026-10-29 Open — a. 2026-10-30 " + h)))
            self.ok("import-md")
        (self.root / ".workflow" / "bugs.md").unlink()
        self.assertEqual([self.show("BUG-%04d" % i)["status"] for i in range(2, 6)], ["Won't fix", "Accepted", "As designed", "Duplicate"])
        self.assertEqual(self.show("BUG-0005")["duplicate_of"], "BUG-0001")
        self.assertTrue(self.show("BUG-0002")["closed_at"].startswith("2026-10-30"))

    def test_duplicate_of_status_cell_is_the_documented_form(self):
        first = md_record("BUG-0001")
        self.imported(md_file(first, md_record("BUG-0002", status="Duplicate of BUG-0001",
                                               history="2026-10-29 Open — a. 2026-10-30 Duplicate of BUG-0001 — QA executor.")))
        b = self.show("BUG-0002")
        self.assertEqual((b["status"], b["duplicate_of"]), ("Duplicate", "BUG-0001"))
        self.assertTrue(b["closed_at"].startswith("2026-10-30"))
        self.assertEqual(json.loads(b["events"][-1]["data"])["to"], "Duplicate")

    def test_duplicate_target_comes_from_the_cell_over_any_note(self):
        self.imported(md_file(md_record("BUG-0001"), md_record(
            "BUG-0002", status="Duplicate of BUG-0001",
            history="2026-10-29 Open — seen beside BUG-0077. 2026-10-30 Duplicate — QA executor.")))
        self.assertEqual(self.show("BUG-0002")["duplicate_of"], "BUG-0001")

    def test_duplicate_target_without_a_cell_comes_from_the_duplicate_event(self):
        self.imported(md_file(md_record("BUG-0001"), md_record(
            "BUG-0002", status="Duplicate",
            history="2026-10-29 Open — seen beside BUG-0077. 2026-10-30 Duplicate — of BUG-0001.")))
        self.assertEqual(self.show("BUG-0002")["duplicate_of"], "BUG-0001")

    def test_duplicate_cell_with_no_real_target_stops(self):
        self.write_md(md_file(md_record("BUG-0002", status="Duplicate of nothing",
                                        history="2026-10-29 Open — a. 2026-10-30 Duplicate — b.")))
        self.assertIn("status", self.no("import-md"))
        self.assertFalse(self.journal.exists())

    def test_duplicate_cell_with_trailing_text_stops(self):
        self.write_md(md_file(md_record("BUG-0001"), md_record(
            "BUG-0002", status="Duplicate of BUG-0001 see notes",
            history="2026-10-29 Open — a. 2026-10-30 Duplicate — b.")))
        err = self.no("import-md")
        self.assertIn("BUG-0002 status", err)
        self.assertIn("see notes", err)
        self.assertFalse(self.journal.exists())

    def test_duplicate_of_itself_stops_in_either_form(self):
        h_cell = "2026-10-29 Open — a. 2026-10-30 Duplicate — b."
        h_note = "2026-10-29 Open — a. 2026-10-30 Duplicate — of BUG-0002."
        for status, history in (("Duplicate of BUG-0002", h_cell), ("Duplicate", h_note)):
            with self.subTest(status):
                self.write_md(md_file(md_record("BUG-0001"), md_record("BUG-0002", status=status, history=history)))
                err = self.no("import-md")
                self.assertIn("BUG-0002 duplicate_of", err)
                self.assertIn("itself", err)
                self.assertFalse(self.journal.exists())

    def test_duplicate_of_a_missing_row_stops_in_either_form(self):
        h_cell = "2026-10-29 Open — a. 2026-10-30 Duplicate — b."
        h_note = "2026-10-29 Open — a. 2026-10-30 Duplicate — of BUG-0077."
        for status, history in (("Duplicate of BUG-0077", h_cell), ("Duplicate", h_note)):
            with self.subTest(status):
                self.write_md(md_file(md_record("BUG-0001"), md_record("BUG-0002", status=status, history=history)))
                err = self.no("import-md")
                self.assertIn("BUG-0002 duplicate_of", err)
                self.assertIn("BUG-0077", err)
                self.assertFalse(self.journal.exists())

    def test_duplicate_target_problems_join_the_rest_of_the_report(self):
        self.write_md(md_file(md_record("BUG-0001", title="t" * 101), md_record("BUG-0002", status="Duplicate of BUG-0077",
                                                                                history="2026-10-29 Open — a. 2026-10-30 Duplicate — b.")))
        err = self.no("import-md")
        self.assertIn("BUG-0001 title: 101", err)
        self.assertIn("BUG-0002 duplicate_of", err)

    def test_one_bug_breaking_two_rules_reports_both(self):
        h = "2026-10-29 Open — a. 2026-10-30 Duplicate — b."
        for status, needle in (("Duplicate of BUG-0077", "BUG-0077"), ("Duplicate of BUG-0002", "itself")):
            with self.subTest(status):
                self.write_md(md_file(md_record("BUG-0001"), md_record("BUG-0002", title="t" * 101, status=status, history=h)))
                err = self.no("import-md")
                self.assertIn("BUG-0002 title: 101", err)
                self.assertIn("BUG-0002 duplicate_of", err)
                self.assertIn(needle, err)
                self.assertFalse(self.journal.exists())

    def test_unknown_history_status_and_label_stop(self):
        self.write_md(md_file(md_record(history="2026-10-29 Open — a. 2026-10-30 Parked — b.")))
        self.assertIn("History", self.no("import-md"))
        self.write_md(md_file(md_record(history="nothing parsable")))
        self.assertIn("History", self.no("import-md"))
        self.write_md(md_file(md_record(extra="- Mystery: dropped text\n")))
        self.assertIn("Mystery", self.no("import-md"))
        self.assertFalse(self.journal.exists())

    def test_record_and_row_must_pair_up(self):
        r = md_record()
        self.write_md(MD_HEADER % "BUG-0002" + r[0])
        self.assertIn("BUG-0001", self.no("import-md"))
        self.write_md(MD_HEADER % "BUG-0002" + r[1])
        self.assertIn("BUG-0001", self.no("import-md"))

    def test_missing_required_field_stops(self):
        rec = md_record()
        self.write_md(md_file((rec[0], rec[1].replace("- Evidence: log.md\n", ""))))
        err = self.no("import-md")
        self.assertIn("BUG-0001", err)
        self.assertIn("evidence", err)

    def test_counters_stop_rule_and_extra_rounds_carry_over(self):
        extra = ("- Fix rounds: 3/4\n- Review rounds: 1/3\n- Stop rule: fix root-caused 2026-10-30 - extra dispatch: used\n"
                 "- extra round: fix +2\n")
        self.imported(md_file(md_record(extra=extra)))
        c = self.counters("BUG-0001")
        self.assertEqual(c["fix"], {"used": 3, "cap": 4})
        self.assertEqual(c["review"], {"used": 1, "cap": 3})
        self.assertIn("- Stop rule: fix root-caused 2026-10-30 - extra dispatch: used", c["record"].splitlines())
        self.assertIn("extra round: fix +2", c["record"].splitlines())

    def test_cap_above_default_without_a_record_stays_default(self):
        self.imported(md_file(md_record(extra="- Fix rounds: 1/9\n")))
        self.assertEqual(self.counters("BUG-0001")["fix"], {"used": 1, "cap": 2})

    def test_next_id_above_the_records_keeps_the_high_water(self):
        self.imported(md_file(md_record(), next_id="BUG-0040"))
        self.assertEqual(self.add(), "BUG-0040")

    def test_next_id_above_one_with_no_records_leaves_a_working_store(self):
        self.imported(MD_HEADER % "BUG-0006")
        self.assertEqual(self.add(), "BUG-0006")
        self.assertEqual(self.add(), "BUG-0007")
        self.ok("list")
        self.ok("doctor")
        self.db_path.unlink()
        self.assertEqual(self.add(), "BUG-0008")

    def test_empty_template_imports_nothing_but_keeps_the_next_id(self):
        self.imported("# Bugs\n\nNext ID: BUG-0001\n\n| ID | Title | Severity | Status | Feature | Owner | Regression test |\n|---|---|---|---|---|---|---|\n\n"
                      "<!-- One record per bug. -->\n## BUG-#### — <title>\n- Repro: <steps>\n")
        self.assertEqual(self.add(), "BUG-0001")

    def test_id_held_by_another_bug_stops(self):
        self.add()
        self.write_md(md_file(md_record()))
        self.assertIn("BUG-0001", self.no("import-md"))
        self.assertEqual(len(self.lines()), 1)


class GitBase(Base):
    def setUp(self):
        super().setUp()
        git(self.root, "init", "-q", "-b", "main")
        (self.root / ".gitattributes").write_text(".workflow/bugs.jsonl text eol=lf merge=union\n", encoding="utf-8")
        (self.root / ".gitignore").write_text(".workflow/bugs.db*\n", encoding="utf-8")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "base")

    def commit(self, msg="work"):
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", msg)


class TestRealGit(GitBase):
    def test_db_is_ignored_and_the_journal_is_union_merged(self):
        self.add()
        self.assertNotIn("bugs.db", git(self.root, "status", "--porcelain", "--untracked-files=all").stdout)
        self.assertIn("merge: union", git(self.root, "check-attr", "merge", "--", ".workflow/bugs.jsonl").stdout)

    def test_two_branches_merge_through_union_both_survive_and_rebuild(self):
        self.add(title="Base bug")
        self.commit()
        git(self.root, "switch", "-q", "-c", "a")
        self.assertEqual(self.add(title="Bug from branch a"), "BUG-0002")
        self.commit("a")
        git(self.root, "switch", "-q", "main")
        git(self.root, "switch", "-q", "-c", "b")
        self.assertEqual(self.add(title="Bug from branch b"), "BUG-0002")
        self.commit("b")
        git(self.root, "switch", "-q", "main")
        git(self.root, "merge", "-q", "--no-edit", "a")
        r = git(self.root, "merge", "--no-edit", "b", check=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn(b"<<<<", self.journal.read_bytes())
        titles = [b["title"] for b in json.loads(self.ok("list", "--json"))]
        self.assertEqual(sorted(titles), ["Base bug", "Bug from branch a", "Bug from branch b"])
        # Both took BUG-0002: fail closed until doctor --fix makes the renumber durable.
        self.assertIn("duplicate", self.no("counters", "BUG-0002", "--json"))
        self.ok("doctor", "--fix")
        self.commit("renumber")
        rows = json.loads(self.ok("list", "--json"))
        self.assertEqual([r["id"] for r in rows], ["BUG-0001", "BUG-0002", "BUG-0003"])
        self.assertEqual(sorted(r["title"] for r in rows), sorted(titles))
        self.assertTrue(self.counters("BUG-0003")["found"])
        self.db_path.unlink()
        self.assertEqual(json.loads(self.ok("list", "--json")), rows)

    def test_merge_without_id_clash_needs_no_doctor(self):
        self.add(title="Base bug")
        self.commit()
        git(self.root, "switch", "-q", "-c", "a")
        self.add(title="On a")
        self.commit("a")
        git(self.root, "switch", "-q", "main")
        self.ok("update", "BUG-0001", stdin={"root_cause": "Found on main"})
        self.commit("main")
        r = git(self.root, "merge", "--no-edit", "a", check=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.show("BUG-0001")["root_cause"], "Found on main")
        self.assertEqual(self.show("BUG-0002")["title"], "On a")
        self.ok("doctor")

    def test_git_switch_refreshes_the_db(self):
        self.add(title="On main")
        self.commit()
        git(self.root, "switch", "-q", "-c", "a")
        self.add(title="Only on a")
        self.status("BUG-0001", "Processing")
        self.commit("a")
        self.assertEqual(self.show("BUG-0001")["status"], "Processing")
        git(self.root, "switch", "-q", "main")
        self.assertEqual([b["title"] for b in json.loads(self.ok("list", "--json"))], ["On main"])
        self.assertEqual(self.show("BUG-0001")["status"], "Request")
        git(self.root, "switch", "-q", "a")
        self.assertEqual(len(json.loads(self.ok("list", "--json"))), 2)
        self.assertEqual(self.show("BUG-0001")["status"], "Processing")

    def test_switch_to_a_branch_without_the_journal(self):
        git(self.root, "switch", "-q", "-c", "a")
        self.add()
        self.commit("a")
        git(self.root, "switch", "-q", "main")
        self.assertFalse(self.journal.exists())
        self.assertEqual(json.loads(self.ok("list", "--json")), [])

    def test_purge_on_one_branch_then_merging_a_pre_purge_branch_keeps_it_gone(self):
        self.seed(create("old", 1, stamp(-5), title="Purged text"), event("status", "old", {"to": "Complete"}, T0))
        self.add(title="Keeper")
        self.commit("base bugs")
        git(self.root, "switch", "-q", "-c", "pre")
        self.ok("update", "BUG-0001", stdin={"root_cause": "Late finding on the old branch"}, now=stamp(1))
        self.add(title="Other work on pre")
        self.commit("pre")
        git(self.root, "switch", "-q", "main")
        self.assertIn("purged 1", self.ok("purge", now=stamp(91)))
        self.commit("purge")
        r = git(self.root, "merge", "--no-edit", "pre", check=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(self.counters("BUG-0001")["found"])
        self.assertIn("purged", self.ok("show", "BUG-0001"))
        rows = json.loads(self.ok("list", "--json"))
        self.assertNotIn("BUG-0001", [b["id"] for b in rows])
        self.assertNotIn("Purged text", json.dumps(rows))
        self.assertEqual(sorted(b["title"] for b in rows), ["Keeper", "Other work on pre"])
        self.assertEqual(self.add(title="After the merge"), "BUG-0004")

    def test_merge_back_of_full_old_lines_stays_gone_and_doctor_sweeps_them(self):
        evs = [create("old", 1, stamp(-5), title="Purged text"), event("status", "old", {"to": "Complete"}, T0)]
        self.seed(*evs)
        self.commit("base")
        self.ok("purge", now=stamp(91))
        self.seed(*evs)  # what a bad merge resolution would leave
        self.assertFalse(self.counters("BUG-0001")["found"])
        self.assertIn("inert", self.no("doctor"))
        self.ok("doctor", "--fix")
        self.assertNotIn("Purged text", self.journal.read_text(encoding="utf-8"))
        self.assertFalse(self.counters("BUG-0001")["found"])
        self.ok("doctor")

    def test_doctor_warns_when_the_union_attribute_is_missing(self):
        self.add()
        (self.root / ".gitattributes").write_text("", encoding="utf-8")
        self.assertIn("merge=union", self.run_cli("doctor")[2])


class TestAutoPurge(GitBase):
    def setUp(self):
        super().setUp()
        self.seed(create("old", 1, stamp(-5)), event("status", "old", {"to": "Complete"}, T0))
        self.commit("bugs")

    def skipped(self, needle, now=None):
        before = self.journal.read_bytes()
        out = self.ok("purge", "--auto", now=now or stamp(91))
        self.assertTrue(out.startswith("purge skipped:"), out)
        self.assertIn(needle, out)
        self.assertEqual(len(out.strip().splitlines()), 1)
        self.assertEqual(self.journal.read_bytes(), before)
        return out

    def test_all_conditions_met_purges_and_prints_one_line(self):
        out = self.ok("purge", "--auto", now=stamp(91))
        self.assertEqual(out, "purged 1, journal uncommitted\n")
        self.assertFalse(self.counters("BUG-0001")["found"])
        self.assertIn("bugs.jsonl", git(self.root, "status", "--porcelain").stdout)

    def test_nothing_to_do_says_purged_zero(self):
        self.assertEqual(self.ok("purge", "--auto", now=stamp(10)), "purged 0\n")

    def test_feature_branch_skips(self):
        git(self.root, "switch", "-q", "-c", "feature/x")
        self.skipped("feature/x")

    def test_other_branches_run(self):
        git(self.root, "switch", "-q", "-c", "develop")
        self.assertIn("purged 1", self.ok("purge", "--auto", now=stamp(91)))

    def test_dirty_journal_skips(self):
        self.ok("update", "BUG-0001", stdin={"priority": "Low"})
        self.skipped("journal")

    def test_untracked_journal_skips(self):
        git(self.root, "rm", "-q", "--cached", ".workflow/bugs.jsonl")
        git(self.root, "commit", "-q", "-m", "untrack")
        self.skipped("journal")

    def test_merge_in_progress_skips(self):
        (self.root / "f.txt").write_text("base\n", encoding="utf-8")
        self.commit("f")
        git(self.root, "switch", "-q", "-c", "other")
        (self.root / "f.txt").write_text("other\n", encoding="utf-8")
        self.commit("other")
        git(self.root, "switch", "-q", "main")
        (self.root / "f.txt").write_text("main\n", encoding="utf-8")
        self.commit("main")
        self.assertNotEqual(git(self.root, "merge", "--no-edit", "other", check=False).returncode, 0)
        self.skipped("merge")

    def test_rebase_in_progress_skips(self):
        for marker in ("rebase-merge", "rebase-apply"):
            d = self.root / ".git" / marker
            d.mkdir()
            self.skipped("rebase")
            d.rmdir()

    def test_detached_head_skips(self):
        git(self.root, "switch", "-q", "--detach")
        self.skipped("detached")

    def test_linked_worktree_skips(self):
        wt = Path(self.tmp) / "wt"
        git(self.root, "worktree", "add", "-q", str(wt), "-b", "wt-branch")
        code, out, _ = self.run_cli("purge", "--auto", now=stamp(91), root=wt)
        self.assertEqual(code, 0)
        self.assertIn("worktree", out)
        self.assertTrue(out.startswith("purge skipped:"))
        self.assertTrue(self.counters("BUG-0001")["found"])

    def test_explicit_purge_ignores_branch_and_dirt_but_not_worktrees(self):
        git(self.root, "switch", "-q", "-c", "feature/x")
        self.ok("update", "BUG-0001", stdin={"priority": "Low"}, now=stamp(0))
        self.assertIn("purged 1", self.ok("purge", now=stamp(91)))


class TestWorktree(GitBase):
    def setUp(self):
        super().setUp()
        self.add(title="On the main checkout")
        self.commit("bugs")
        self.wt = Path(self.tmp) / "wt"
        git(self.root, "worktree", "add", "-q", str(self.wt), "-b", "wt-branch")

    def test_every_write_refused_with_nothing_written(self):
        before = self.journal.read_bytes()
        wt_journal = self.wt / ".workflow" / "bugs.jsonl"
        wt_before = wt_journal.read_bytes()
        calls = [(["add"], fields()), (["update", "BUG-0001"], {"priority": "Low"}),
                 (["set-status", "BUG-0001", "Processing", "--note", "n"], None), (["round", "BUG-0001", "fix", "+1", "--note", "n"], None),
                 (["extra-round", "BUG-0001", "fix", "+1", "--note", "n"], None), (["stop-rule", "BUG-0001", "fix", "--extra-dispatch", "used"], None),
                 (["delete", "BUG-0001", "--by", "GD"], None), (["purge"], None), (["doctor", "--fix"], None)]
        for argv, stdin in calls:
            with self.subTest(argv):
                self.assertIn("worktree", self.no(*argv, stdin=stdin, root=self.wt))
        self.assertEqual(self.journal.read_bytes(), before)
        self.assertEqual(wt_journal.read_bytes(), wt_before)

    def test_import_md_refused(self):
        (self.root / ".workflow" / "bugs.md").write_text(REAL_BUGS_MD, encoding="utf-8")
        self.assertIn("worktree", self.no("import-md", root=self.wt))

    def test_reads_use_the_main_checkout(self):
        self.add(title="Uncommitted on main")
        rows = json.loads(self.ok("list", "--json", root=self.wt))
        self.assertEqual([r["title"] for r in rows], ["On the main checkout", "Uncommitted on main"])
        self.assertTrue(json.loads(self.ok("counters", "BUG-0002", "--json", root=self.wt))["found"])
        self.assertIn("2 open", self.ok("stats", root=self.wt))
        self.assertIn("BUG-0002", self.ok("sql", "SELECT id FROM bug", root=self.wt))
        self.assertFalse((self.wt / ".workflow" / "bugs.db").exists())

    def test_dry_run_is_a_read(self):
        self.assertIn("would purge 0", self.ok("purge", "--dry-run", root=self.wt))

    def test_bugs_md_in_the_main_checkout_blocks_the_worktree(self):
        (self.root / ".workflow" / "bugs.md").write_text("# Bugs\n", encoding="utf-8")
        self.assertIn("bugs.md", self.no("list", root=self.wt))


class TestCli(Base):
    """The real process: -I, a pipe for stdin, the exit code."""

    def cli(self, *argv, stdin=b"", env=None):
        e = dict(os.environ)
        e.update(env or {})
        return subprocess.run([sys.executable, "-I", str(HERE / "bugs.py"), "--root", str(self.root)] + list(argv),
                              input=stdin, capture_output=True, env=e, cwd=self.tmp)

    def test_isolated_mode_loads_mem_and_round_trips(self):
        r = self.cli("add", stdin=json.dumps(fields(actual="Costs $5 — $(oops)"), ensure_ascii=False).encode("utf-8"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), b"BUG-0001")
        r = self.cli("show", "BUG-0001", "--json")
        self.assertEqual(json.loads(r.stdout.decode("utf-8"))["actual"], "Costs $5 — $(oops)")

    def test_counters_contract_exit_codes(self):
        self.cli("add", stdin=json.dumps(fields()).encode("utf-8"))
        ok = self.cli("counters", "BUG-0001", "--json")
        self.assertEqual(ok.returncode, 0)
        self.assertTrue(json.loads(ok.stdout)["found"])
        unknown = self.cli("counters", "BUG-0099", "--json")
        self.assertEqual(unknown.returncode, 0)
        self.assertFalse(json.loads(unknown.stdout)["found"])
        with open(self.journal, "ab") as f:
            f.write(b"junk\n")
        bad = self.cli("counters", "BUG-0001", "--json")
        self.assertNotEqual(bad.returncode, 0)
        self.assertTrue(bad.stderr.strip())

    def test_clock_override(self):
        self.cli("add", stdin=json.dumps(fields()).encode("utf-8"), env={"BUGS_NOW": "2026-05-05T05:05:05Z"})
        self.assertEqual(self.lines()[0]["ts"], "2026-05-05T05:05:05.000Z")

    def test_bad_clock_override_is_an_error(self):
        r = self.cli("add", stdin=json.dumps(fields()).encode("utf-8"), env={"BUGS_NOW": "tomorrow"})
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(self.journal.exists())

    def test_invalid_utf8_stdin_refused(self):
        r = self.cli("add", stdin=b'{"title": "\xff\xfe"}')
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(self.journal.exists())

    def test_stats_is_one_line(self):
        self.assertEqual(self.cli("stats").stdout.decode().strip(), "Bugs: 0 open (0 High+)")

    def test_missing_root_refused(self):
        r = subprocess.run([sys.executable, "-I", str(HERE / "bugs.py"), "--root", str(Path(self.tmp) / "nope"), "stats"], capture_output=True)
        self.assertNotEqual(r.returncode, 0)


class TestSkillContract(unittest.TestCase):
    """verify.ps1 cannot read .py: these hold the contract the layer check used to carry."""

    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.schema = (SKILL_DIR / "references" / "schema.md").read_text(encoding="utf-8")
        cls.source = (HERE / "bugs.py").read_text(encoding="utf-8")

    def test_frontmatter(self):
        self.assertRegex(self.skill, r"(?m)^name: bugs$")
        self.assertRegex(self.skill, r"(?m)^user-invocable: false$")

    def test_schema_reference_lists_all_statuses_and_priorities(self):
        for s in STATUSES + PRIORITIES:
            self.assertIn("`%s`" % s, self.schema, s)

    def test_skill_points_to_the_state_machine(self):
        self.assertIn("(references/schema.md)", self.skill)

    def test_marker_strings(self):
        for marker in ("Bug: BUG-####", "Verify: BUG-####"):
            self.assertIn(marker, self.skill)

    def test_commands_named_in_the_skill(self):
        for cmd in ("add", "update", "set-status", "round", "extra-round", "stop-rule", "show", "list", "search", "sql", "delete",
                    "counters", "purge", "rebuild", "doctor", "import-md", "stats"):
            self.assertIn("`%s" % cmd, self.skill, cmd)

    def test_skill_names_its_script_without_a_hardcoded_path(self):
        self.assertIn("bugs.py", self.skill)
        self.assertNotIn(".claude/skills/bugs/scripts/", self.skill)

    def test_no_long_fence_in_the_reference(self):
        fence, n = False, 0
        for line in self.schema.splitlines():
            if line.lstrip().startswith("```"):
                fence, n = not fence, 0
            elif fence:
                n += 1
                self.assertLess(n, 15)

    def test_the_test_clock_is_documented_as_test_only(self):
        line = next(x for x in self.schema.splitlines() if "BUGS_NOW" in x)
        self.assertIn("test-only", line.lower())

    def test_stdlib_only(self):
        imports = set(re.findall(r"(?m)^\s*(?:import|from)\s+([A-Za-z_][A-Za-z0-9_]*)", self.source))
        self.assertLessEqual(imports, {"__future__", "argparse", "datetime", "hashlib", "importlib", "json", "os", "re", "sqlite3",
                                       "subprocess", "sys", "unicodedata", "uuid", "pathlib"})


def secret_shapes():
    """Synthetic values, built at runtime so this file holds no secret-shaped literal. One per pattern family."""
    return {"aws": FAKE_KEY, "github": "gh" + "p_" + "a" * 36, "pem": PEM_HEADER, "long": "s" + "k-" + "ant-" + "x" * 95,
            "jwt": ".".join(("ey" + "J" + "a" * 12, "ey" + "J" + "b" * 12, "c" * 12)), "credential": "api" + "_key=" + "q" * 16}


class TestRefusalsAreRedacted(Base):
    """No value the caller passed reaches stderr unredacted: DEF-E1-01."""

    def forms(self, value):
        yield ["show", value], None
        yield ["counters", value], None
        yield ["update", value], {"note": "n"}
        yield ["set-status", value, "Request", "--note", "n"], None
        yield ["set-status", "BUG-0001", value, "--note", "n"], None
        yield ["set-status", "BUG-0001", "Duplicate", "--note", "n", "--duplicate-of", value], None
        yield ["set-status", "BUG-0001", "Duplicate"], {"note": "n", "duplicate_of": value}
        yield ["round", "BUG-0001", "fix", value, "--note", "n"], None
        yield ["extra-round", "BUG-0001", "fix", value, "--note", "n"], None
        yield ["delete", value, "--by", "GD"], None
        yield ["add"], dict(fields(), **{value: "x"})
        yield ["update", "BUG-0001"], {value: "x"}
        yield ["set-status", "BUG-0001", "Processing"], {"note": "n", value: "x"}
        yield ["round", "BUG-0001", "fix", "+1"], {"note": "n", value: "x"}
        yield ["list", "--status", value], None
        yield ["list", "--priority", value], None
        yield ["round", "BUG-0001", value, "+1", "--note", "n"], None
        yield ["show", "BUG-0001", value], None
        yield [value], None
        yield ["sql", "SELECT %s" % value], None
        yield ["sql", "SELECT 1 FROM [%s]" % value], None

    def test_no_shape_reaches_stderr_or_stdout_in_any_form(self):
        self.add()
        before = self.journal.read_bytes()
        for name, value in secret_shapes().items():
            for argv, stdin in self.forms(value):
                with self.subTest(shape=name, argv=argv[:2]):
                    code, out, err = self.run_cli(*argv, stdin=stdin)
                    self.assertNotEqual(code, 0, out)
                    self.assertTrue(err.strip())
                    self.assertNotIn(value, err)
                    self.assertNotIn(value, out)
        self.assertEqual(self.journal.read_bytes(), before)

    def test_pii_shape_as_a_value_is_redacted_too(self):
        self.add()
        err = self.no("show", "qa.tester@example.com")
        self.assertNotIn("qa.tester@example.com", err)
        self.assertIn("REDACTED", err)

    def test_a_refusal_still_names_what_is_wrong(self):
        self.add()
        self.assertIn("expected BUG-####", self.no("show", FAKE_KEY))
        self.assertIn("REDACTED", self.no("show", FAKE_KEY))
        self.assertIn("unknown status", self.no("set-status", "BUG-0001", FAKE_KEY, "--note", "n"))
        self.assertIn("unknown or read-only field", self.no("update", "BUG-0001", stdin={FAKE_KEY: "x"}))
        self.assertIn("garbage", self.no("show", "garbage"))

    def test_a_long_value_is_not_echoed(self):
        self.add()
        for argv, stdin in (
                (["show", "z" * 500], None), (["set-status", "BUG-0001", "z" * 500, "--note", "n"], None),
                (["update", "BUG-0001"], {"z" * 500: "x"}), (["round", "BUG-0001", "fix", "z" * 500, "--note", "n"], None)):
            with self.subTest(argv[:2]):
                err = self.no(*argv, stdin=stdin)
                self.assertNotIn("z" * 41, err)
                self.assertLess(len(err), 400)

    def test_argparse_usage_errors_keep_their_exit_code(self):
        code, _, err = self.run_cli("list", "--status", FAKE_KEY)
        self.assertEqual(code, 2)
        self.assertIn("usage", err)
        self.assertNotIn(FAKE_KEY, err)

    def test_values_are_hidden_when_nothing_can_scan_them(self):
        for kw in (dict(with_mem=True, with_patterns=False), dict(with_mem=False, with_patterns=True)):
            with self.subTest(**kw):
                shutil.rmtree(Path(self.tmp) / "framework", ignore_errors=True)
                script = self.isolated_copy(**kw)
                for argv in (["show", FAKE_KEY], ["list", "--status", FAKE_KEY], ["sql", "SELECT %s" % FAKE_KEY]):
                    r = self.cli(script, *argv)
                    self.assertNotEqual(r.returncode, 0)
                    self.assertTrue(r.stderr.strip())
                    self.assertNotIn(FAKE_KEY.encode(), r.stderr + r.stdout)

    def test_a_table_cell_or_label_in_import_md_is_redacted(self):
        self.root.joinpath(".workflow").mkdir()
        md = self.root / ".workflow" / "bugs.md"
        long_value = secret_shapes()["long"]
        for text in (md_file(md_record(status=FAKE_KEY)), md_file(md_record(severity=FAKE_KEY)),
                     md_file(md_record(extra="- %s: x\n" % long_value)),
                     md_file(md_record(history="2026-10-29 Open — 2026-10-29 Bogus %s" % long_value))):
            md.write_text(text, encoding="utf-8")
            err = self.no("import-md")
            self.assertIn("import stopped", err)
            self.assertNotIn(FAKE_KEY, err)
            self.assertNotIn(long_value[:20], err)
        self.assertFalse(self.journal.exists())

    def test_a_cut_journal_value_cannot_slip_past_the_scan(self):
        long_value = secret_shapes()["long"]
        self.seed(create("a", 1), event("update", "a", {long_value: "x"}, stamp(1)))
        for argv in (["list"], ["doctor"]):
            err = self.no(*argv)
            self.assertIn("corrupt journal", err)
            self.assertNotIn(long_value[:20], err)


class TestEveryWriteNeedsThePatterns(Base):
    """DEF-E1-02: delete, purge and doctor --fix refuse like every other write."""

    def broken_states(self):
        def missing(script):
            (script.parents[3] / "hooks" / "secret-patterns.txt").unlink()

        def comments_only(script):
            (script.parents[3] / "hooks" / "secret-patterns.txt").write_text("# only comments\n", encoding="utf-8")

        def bad_regex(script):
            (script.parents[3] / "hooks" / "secret-patterns.txt").write_text("name\t([unclosed\n", encoding="utf-8")

        def no_tab(script):
            (script.parents[3] / "hooks" / "secret-patterns.txt").write_text("no tab here\n", encoding="utf-8")

        def mem_missing(script):
            (script.parents[2] / "mem" / "scripts" / "mem.py").unlink()

        def mem_raises(script):
            (script.parents[2] / "mem" / "scripts" / "mem.py").write_text("raise RuntimeError('broken')\n", encoding="utf-8")

        def mem_syntax_error(script):
            (script.parents[2] / "mem" / "scripts" / "mem.py").write_text("def broken(:\n", encoding="utf-8")

        def mem_import_error(script):
            (script.parents[2] / "mem" / "scripts" / "mem.py").write_text("import no_such_module_anywhere\n", encoding="utf-8")

        def mem_lacks_the_api(script):
            (script.parents[2] / "mem" / "scripts" / "mem.py").write_text("x = 1\n", encoding="utf-8")

        def mem_api_raises(script):
            (script.parents[2] / "mem" / "scripts" / "mem.py").write_text(
                "RX_PEM_BLOCK = None\nredact = redact_pii = None\ndef load_secret_patterns(root):\n    return undefined_name\n", encoding="utf-8")

        return (missing, comments_only, bad_regex, no_tab, mem_missing, mem_raises, mem_syntax_error, mem_import_error, mem_lacks_the_api, mem_api_raises)

    def assert_refused(self, *argv, env=None):
        for state in self.broken_states():
            with self.subTest(state=state.__name__, argv=argv):
                shutil.rmtree(Path(self.tmp) / "framework", ignore_errors=True)
                script = self.isolated_copy(with_mem=True, with_patterns=True)
                state(script)
                before = self.journal.read_bytes()
                e = dict(os.environ)
                e.update(env or {})
                r = subprocess.run([sys.executable, "-I", str(script), "--root", str(self.root)] + list(argv),
                                   input=b"", capture_output=True, env=e)
                self.assertNotEqual(r.returncode, 0, r.stdout)
                self.assertTrue(r.stderr.strip())
                self.assertNotIn(b"Traceback", r.stderr)
                self.assertIn(b"bugs: ", r.stderr)
                self.assertEqual(self.journal.read_bytes(), before)

    def test_delete(self):
        self.add()
        self.assert_refused("delete", "BUG-0001", "--by", "GD")

    def test_every_other_write_gives_a_clean_refusal_too(self):
        self.add()
        self.assert_refused("set-status", "BUG-0001", "Processing", "--note", "n")
        self.assert_refused("round", "BUG-0001", "fix", "+1", "--note", "n")

    def test_a_refusal_on_a_read_stays_clean_with_mem_broken(self):
        self.add()
        script = self.isolated_copy(with_mem=True, with_patterns=True)
        (script.parents[2] / "mem" / "scripts" / "mem.py").write_text("def broken(:\n", encoding="utf-8")
        r = self.cli(script, "show", FAKE_KEY)
        self.assertEqual(r.returncode, 1)
        self.assertNotIn(b"Traceback", r.stderr)
        self.assertNotIn(FAKE_KEY.encode(), r.stderr)
        self.assertEqual(self.cli(script, "show", "BUG-0001").returncode, 0)

    def test_purge_with_a_bug_due(self):
        self.seed(create("old", 1, stamp(-5)), event("status", "old", {"to": "Complete"}, T0))
        self.assert_refused("purge", env={"BUGS_NOW": stamp(91)})

    def test_doctor_fix_with_a_duplicate_to_renumber(self):
        self.seed(create("a", 2), create("b", 2, stamp(1)))
        self.assert_refused("doctor", "--fix")

    def test_doctor_without_fix_and_a_dry_run_are_reads(self):
        self.add()
        script = self.isolated_copy(with_mem=True, with_patterns=False)
        self.assertEqual(self.cli(script, "doctor").returncode, 0)
        self.assertEqual(self.cli(script, "purge", "--dry-run").returncode, 0)


class TestAFaultInsideMemStaysClean(Base):
    """mem.py and the patterns load, then a call into mem.py faults: no Traceback and no raw value, refusal or write."""

    EMAIL = "qa.tester@example.com"
    # Appended to a copy of the real mem.py: each overrides one name and the rest stays real. The exception text holds the
    # value, as a fault in real redaction code could.
    REDACT_FAULTS = {"redact raises": 'def redact(text, patterns):\n    raise TypeError("fault on " + text)\n',
                     "redact returns nothing": "def redact(text, patterns):\n    return None\n",
                     "redact raises BaseException": 'def redact(text, patterns):\n    raise BaseException("fault on " + text)\n',
                     "redact exits 0": "def redact(text, patterns):\n    raise SystemExit(0)\n"}
    WRITE_FAULTS = {"redact_pii raises": 'def redact_pii(text):\n    raise AttributeError("fault on " + text)\n',
                    "redact_pii returns nothing": "def redact_pii(text):\n    return None\n",
                    "redact_pii raises BaseException": 'def redact_pii(text):\n    raise BaseException("fault on " + text)\n',
                    "redact_pii exits 0": "def redact_pii(text):\n    raise SystemExit(0)\n",
                    "the PEM regex is not one": "RX_PEM_BLOCK = object()\n",
                    "a compiled pattern is not one": "def load_secret_patterns(root):\n    return [('x', object())]\n",
                    "no patterns": "def load_secret_patterns(root):\n    return []\n",
                    "an empty generator": "def load_secret_patterns(root):\n    return (x for x in [])\n",
                    "an empty iterator": "def load_secret_patterns(root):\n    return iter(())\n",
                    "a string": "def load_secret_patterns(root):\n    return 'abc'\n",
                    "pairs of strings": "def load_secret_patterns(root):\n    return [('x', 'y')]\n",
                    "a generator that faults": "def load_secret_patterns(root):\n    yield ('x', RX_PEM_BLOCK)\n    raise RuntimeError('mid-way')\n",
                    "no patterns at all": "def load_secret_patterns(root):\n    return None\n",
                    "the pattern loader exits 0": "def load_secret_patterns(root):\n    raise SystemExit(0)\n",
                    "the pattern loader raises BaseException": 'def load_secret_patterns(root):\n    raise BaseException("base")\n',
                    "exit 0 at import": "raise SystemExit(0)\n",
                    "exit 3 at import": "raise SystemExit(3)\n",
                    "BaseException at import": 'raise BaseException("base")\n'}
    # A real SIGINT through Python's own handler, at the points the fault tests fault.
    SIGINT = ("import signal, time", "signal.signal(signal.SIGINT, signal.default_int_handler)", "signal.raise_signal(signal.SIGINT)", "time.sleep(30)")
    INTERRUPTS = {"in redact": ("def redact(text, patterns):\n    " + "\n    ".join(SIGINT) + "\n", ("show", FAKE_KEY)),
                  "in the pattern loader": ("def load_secret_patterns(root):\n    " + "\n    ".join(SIGINT) + "\n", ("show", FAKE_KEY)),
                  "at import": ("\n".join(SIGINT) + "\n", ("show", FAKE_KEY)),
                  "in redact_pii": ("def redact_pii(text):\n    " + "\n    ".join(SIGINT) + "\n", ("round", "BUG-0001", "fix", "+1", "--note", "Mail qa.tester@example.com"))}

    def faulty_copy(self, fault):
        shutil.rmtree(Path(self.tmp) / "framework", ignore_errors=True)
        script = self.isolated_copy(with_mem=True, with_patterns=True)
        with open(script.parents[2] / "mem" / "scripts" / "mem.py", "a", encoding="utf-8") as f:
            f.write("\n" + fault)
        return script

    def assert_clean(self, r, *raw):
        for value in raw:
            self.assertNotIn(value.encode(), r.stderr + r.stdout)
        self.assertNotIn(b"Traceback", r.stderr)

    def test_a_refusal_hides_the_value_when_redaction_faults(self):
        self.add()
        before = self.journal.read_bytes()
        for name, fault in {**self.REDACT_FAULTS, **self.WRITE_FAULTS}.items():
            script = self.faulty_copy(fault)
            for value in (FAKE_KEY, self.EMAIL):
                for argv in (["show", value], ["list", "--status", value], ["sql", "SELECT %s" % value]):
                    with self.subTest(fault=name, argv=argv[0], value=value[:4]):
                        r = self.cli(script, *argv)
                        self.assertNotEqual(r.returncode, 0, r.stdout)
                        self.assertIn(b"bugs: ", r.stderr)
                        self.assert_clean(r, value)
            with self.subTest(fault=name, argv="add with a secret"):
                r = self.cli(script, "add", stdin=json.dumps(fields(actual="Key %s here" % FAKE_KEY)).encode("utf-8"))
                self.assertNotEqual(r.returncode, 0, r.stdout)
                self.assert_clean(r, FAKE_KEY)
        self.assertEqual(self.journal.read_bytes(), before)

    def test_an_interrupt_exits_130_and_prints_no_value(self):
        self.add()
        before = self.journal.read_bytes()
        for name, (fault, argv) in self.INTERRUPTS.items():
            with self.subTest(interrupt=name):
                r = self.cli(self.faulty_copy(fault), *argv)
                self.assertEqual(r.returncode, 130, r.stderr)
                self.assert_clean(r, FAKE_KEY, self.EMAIL)
                self.assertEqual(self.journal.read_bytes(), before)

    def test_an_interrupt_outside_mem_exits_130(self):
        self.add()
        with mock.patch.object(bugs, "open_read", side_effect=KeyboardInterrupt):
            try:
                code, out, err = self.run_cli("list")
            except KeyboardInterrupt:
                self.fail("main let the interrupt through")
        self.assertEqual((code, out), (130, ""))
        self.assertNotIn("Traceback", err)

    def test_a_refused_read_still_names_what_is_wrong(self):
        self.add()
        r = self.cli(self.faulty_copy(self.REDACT_FAULTS["redact raises"]), "show", FAKE_KEY)
        self.assertIn(b"expected BUG-####", r.stderr)
        self.assertIn(b"<hidden: secret patterns unavailable>", r.stderr)

    def test_a_write_is_refused_when_the_write_rules_fault(self):
        self.add()
        before = self.journal.read_bytes()
        for name, fault in self.WRITE_FAULTS.items():
            script = self.faulty_copy(fault)
            for argv, stdin in ((["add"], fields(actual="Mail %s here" % self.EMAIL)), (["update", "BUG-0001"], {"actual": "Mail %s here" % self.EMAIL}),
                                (["round", "BUG-0001", "fix", "+1", "--note", "Mail %s" % self.EMAIL], None)):
                with self.subTest(fault=name, argv=argv[0]):
                    r = self.cli(script, *argv, stdin=b"" if stdin is None else json.dumps(stdin).encode("utf-8"))
                    self.assertEqual(r.returncode, 1, r.stdout)
                    self.assertIn(b"write refused", r.stderr)
                    self.assert_clean(r, self.EMAIL)
                    self.assertEqual(self.journal.read_bytes(), before)

    def test_a_one_shot_iterator_scans_every_field(self):
        script = self.faulty_copy("_real_load = load_secret_patterns\ndef load_secret_patterns(root):\n    return iter(_real_load(root))\n")
        for field in ("title", "actual", "evidence"):
            with self.subTest(field):
                r = self.cli(script, "add", stdin=json.dumps(fields(**{field: "Key %s here" % FAKE_KEY})).encode("utf-8"))
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn(("secret-shaped value in %s" % field).encode(), r.stderr)
                self.assert_clean(r, FAKE_KEY)
                self.assertFalse(self.journal.exists() and FAKE_KEY.encode() in self.journal.read_bytes())
        r = self.cli(script, "show", FAKE_KEY)
        self.assert_clean(r, FAKE_KEY)
        self.assertIn(b"REDACTED", r.stderr)
        self.assertEqual(self.cli(script, "add", stdin=json.dumps(fields()).encode("utf-8")).returncode, 0)

    def test_unrecognized_arguments_are_counted_never_echoed(self):
        self.add()
        flag = "--" + "s" + "k-" + "a" * 24
        for argv, count in ((["list", flag], 1), ([flag, "list"], 1), (["show", "BUG-0001", flag, "stray"], 2), (["list", "stray"], 1)):
            with self.subTest(argv=argv[0]):
                code, out, err = self.run_cli(*argv)
                self.assertEqual(code, 2, out)
                self.assertIn("%d unrecognized argument" % count, err)
                self.assertNotIn(flag, err + out)
                self.assertNotIn("stray", err + out)

    def test_a_write_needing_only_the_write_rules_survives_a_redact_fault(self):
        for name, fault in self.REDACT_FAULTS.items():
            with self.subTest(fault=name):
                r = self.cli(self.faulty_copy(fault), "add", stdin=json.dumps(fields(actual="Mail %s here" % self.EMAIL)).encode("utf-8"))
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assert_clean(r, self.EMAIL)
                self.assertNotIn(self.EMAIL.encode(), self.journal.read_bytes())


class TestRootRule(GitBase):
    """N1: only the root's own .git counts, as in Get-BugsRoot. hooks/tests/run.ps1 drives the two over the same layouts."""

    def worktree(self):
        self.add(title="Other repo first")
        self.add(title="Other repo second")
        self.commit()
        wt = Path(self.tmp) / "wt"
        git(self.root, "worktree", "add", "-q", str(wt), "-b", "wt-branch")
        return wt, self.root / ".git" / "worktrees" / "wt"

    def planted(self):
        """A project with no .git and its own bug, below a .git file naming this repo's real worktree, which has two bugs."""
        _, admin = self.worktree()
        above = Path(self.tmp) / "above"
        project = above / "proj"
        project.mkdir(parents=True)
        (above / ".git").write_text("gitdir: %s\n" % admin, encoding="utf-8")
        self.ok("add", stdin=fields(title="Own bug"), root=project)
        return project

    def bug_count(self, root):
        return self.ok("stats", root=root).split(" open")[0]

    def test_a_git_file_above_a_project_with_none_is_not_followed(self):
        project = self.planted()
        before = self.journal.read_bytes()
        self.assertEqual(self.bug_count(project), "Bugs: 1")
        self.assertEqual(json.loads(self.ok("show", "BUG-0001", "--json", root=project))["title"], "Own bug")
        self.assertFalse(json.loads(self.ok("counters", "BUG-0002", "--json", root=project))["found"])
        self.assertEqual(self.journal.read_bytes(), before)

    def test_a_project_there_has_no_git_context(self):
        project = self.planted()
        code, out, _ = self.run_cli("purge", "--auto", root=project)
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "purge skipped: not a git repository")
        self.assertEqual(self.ok("doctor", root=project), "doctor: clean\n")
        self.assertIn("BUG-0002", self.ok("add", stdin=fields(), root=project))

    def test_a_subfolder_of_a_repo_is_its_own_root(self):
        self.add()
        self.commit()
        sub = self.root / "Sub"
        sub.mkdir()
        self.assertEqual(self.bug_count(sub), "Bugs: 0")
        self.assertEqual(self.ok("add", stdin=fields(), root=sub).strip(), "BUG-0001")
        self.assertTrue((sub / ".workflow" / "bugs.jsonl").exists())

    def test_a_subfolder_of_a_linked_worktree_is_its_own_root(self):
        wt, _ = self.worktree()
        sub = wt / "Sub"
        sub.mkdir()
        self.ok("add", stdin=fields(title="Own bug"), root=sub)
        self.assertEqual(self.bug_count(sub), "Bugs: 1")

    def test_a_linked_worktree_still_reads_main_and_refuses_writes(self):
        wt, _ = self.worktree()
        self.assertEqual(self.bug_count(wt), "Bugs: 2")
        self.assertIn("worktree", self.no("add", stdin=fields(), root=wt))
        code, out, _ = self.run_cli("purge", "--auto", root=wt)
        self.assertEqual(code, 0)
        self.assertIn("linked worktree", out)

    def test_a_damaged_link_at_the_root_refuses_a_read_too(self):
        wt, admin = self.worktree()
        link, commondir = wt / ".git", admin / "commondir"
        if os.name == "nt":
            subprocess.run(["attrib", "-h", str(link)], check=True, capture_output=True)  # a hidden file refuses a write
        good_link, good_common = link.read_text(encoding="utf-8"), commondir.read_text(encoding="utf-8")
        for name, damage in {"no gitdir": lambda: link.write_text("not a link\n", encoding="utf-8"),
                             "missing gitdir": lambda: link.write_text("gitdir: %s\n" % (Path(self.tmp) / "nowhere"), encoding="utf-8"),
                             "commondir lost": commondir.unlink,
                             "commondir not .git": lambda: commondir.write_text("..\n", encoding="utf-8"),
                             "commondir missing": lambda: commondir.write_text("../../../no-such/.git\n", encoding="utf-8")}.items():
            with self.subTest(name):
                damage()
                self.no("stats", root=wt)
                link.write_text(good_link, encoding="utf-8")
                commondir.write_text(good_common, encoding="utf-8")

    def test_git_failing_at_a_real_git_folder_reads_and_refuses_writes(self):
        self.add()
        with mock.patch.object(bugs, "run_git", side_effect=OSError("no git")):
            self.assertEqual(self.bug_count(self.root), "Bugs: 1")
            self.assertIn("git failed", self.no("add", stdin=fields()))
            code, out, _ = self.run_cli("purge", "--auto")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "purge skipped: git failed")

    def test_a_git_folder_git_will_not_read_is_never_read_as_the_repo_above(self):
        self.add()
        self.commit()
        project = self.root / "Inner"
        (project / ".git").mkdir(parents=True)
        self.assertEqual(self.bug_count(project), "Bugs: 0")
        self.assertIn("git failed", self.no("add", stdin=fields(), root=project))
        code, out, _ = self.run_cli("purge", "--auto", root=project)
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "purge skipped: git failed")

    def test_no_root_argument_means_the_project_holding_the_script(self):
        wt, admin = self.worktree()
        plain = Path(self.tmp) / "above" / "proj"
        plain.mkdir(parents=True)
        (Path(self.tmp) / "above" / ".git").write_text("gitdir: %s\n" % admin, encoding="utf-8")
        for folder, want in ((wt, "Bugs: 2"), (plain, "Bugs: 0"), (self.root, "Bugs: 2")):
            scripts = folder / ".claude" / "skills" / "bugs" / "scripts"
            scripts.mkdir(parents=True)
            shutil.copy(HERE / "bugs.py", scripts / "bugs.py")
            with self.subTest(folder.name):
                r = subprocess.run([sys.executable, "-I", str(scripts / "bugs.py"), "stats"], input=b"", capture_output=True, cwd=self.tmp)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(r.stdout.decode("utf-8").split(" open")[0], want)


class TestTombstoneHoldsItsId(GitBase):
    """DEF-E1-03: a purged ID coming back through a merge is a duplicate, not a silent reuse."""

    def test_merge_returning_a_purged_id_fails_closed_until_doctor_fix(self):
        self.add(title="Bug A")
        self.status("BUG-0001", "As designed")
        self.commit("a")
        git(self.root, "switch", "-q", "-c", "b")
        self.assertEqual(self.add(title="B second"), "BUG-0002")
        self.commit("b")
        git(self.root, "switch", "-q", "main")
        self.assertEqual(self.add(title="main second"), "BUG-0002")
        self.status("BUG-0002", "As designed")
        self.commit("main")
        self.assertIn("purged", self.ok("purge", now=fmt_future(100)))
        self.commit("purge")
        r = git(self.root, "merge", "--no-edit", "b", check=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

        self.assertIn("duplicate", self.no("counters", "BUG-0002", "--json"))
        self.assertIn("duplicate", self.no("update", "BUG-0002", stdin={"note": "n"}))
        self.assertIn("duplicate", self.no("set-status", "BUG-0002", "Processing", "--note", "n"))
        self.assertIn("duplicate", self.no("doctor"))
        self.assertIn("doctor --fix", self.run_cli("show", "BUG-0002")[2])

        fixed = self.ok("doctor", "--fix")
        self.assertEqual(fixed.splitlines()[0], "renumbered BUG-0002 to BUG-0003")
        self.assertNotIn("uid", fixed)
        self.ok("doctor")
        self.assertIn("purged", self.ok("show", "BUG-0002"))
        self.assertFalse(self.counters("BUG-0002")["found"])
        rows = {r["title"]: r["id"] for r in json.loads(self.ok("list", "--json"))}
        self.assertEqual(rows["B second"], "BUG-0003")
        self.assertEqual(self.add(title="After"), "BUG-0004")
        lines = self.lines()
        self.db_path.unlink()
        self.assertEqual({r["title"]: r["id"] for r in json.loads(self.ok("list", "--json"))}["B second"], "BUG-0003")
        self.assertEqual(self.lines(), lines)


class TestNonAsciiPaths(Base):
    """git's output is bytes decoded as UTF-8 here, whatever the console code page: the hook's bug class cannot occur."""

    def test_a_non_ascii_main_checkout_and_worktree_resolve(self):
        name = "\u0110\u1ec7"
        main = Path(self.tmp) / ("main " + name)
        main.mkdir()
        git(main, "init", "-q", "-b", "main")
        (main / ".gitattributes").write_text(".workflow/bugs.jsonl text eol=lf merge=union\n", encoding="utf-8")
        (main / ".gitignore").write_text(".workflow/bugs.db*\n", encoding="utf-8")
        git(main, "add", "-A")
        git(main, "commit", "-q", "-m", "base")
        wt = Path(self.tmp) / ("wt " + name)
        git(main, "worktree", "add", "-q", str(wt), "-b", "wt-branch")
        self.assertEqual(self.ok("add", stdin=fields(), root=main).strip(), "BUG-0001")
        self.assertEqual(self.counters_at(wt, "BUG-0001")["status"], "Request")
        self.assertIn("worktree", self.no("add", stdin=fields(), root=wt))
        self.assertFalse((wt / ".workflow" / "bugs.jsonl").exists())
        self.assertEqual(self.ok("doctor", root=wt), "doctor: clean\n")

    def counters_at(self, root, bug_id):
        return json.loads(self.ok("counters", bug_id, "--json", root=root))


class TestTombstoneReplay(Base):
    def test_a_create_on_a_tombstoned_id_from_another_uid_is_a_duplicate(self):
        self.seed(create("live", 2, stamp(1)), event("tombstone", "gone", {"id": 2}, stamp(2)))
        self.assertIn("duplicate", self.no("counters", "BUG-0002", "--json"))
        self.assertIn("duplicate", self.no("round", "BUG-0002", "fix", "+1", "--note", "n"))
        self.assertIn("duplicate", self.no("doctor"))
        self.ok("doctor", "--fix")
        self.assertEqual(self.counters("BUG-0003")["status"], "Request")
        self.assertIn("purged", self.ok("show", "BUG-0002"))

    def test_the_same_uid_resurrected_stays_gone_with_no_duplicate(self):
        self.seed(create("gone", 2, stamp(1)), event("tombstone", "gone", {"id": 2}, stamp(2)))
        self.assertFalse(self.counters("BUG-0002")["found"])
        self.assertIn("purged", self.ok("show", "BUG-0002"))
        self.assertNotIn("duplicate", self.no("doctor"))
        self.assertEqual(json.loads(self.ok("list", "--json")), [])

    def test_a_renumbered_bug_that_left_the_id_is_not_a_duplicate(self):
        self.seed(create("live", 2, stamp(1)), event("renumber", "live", {"from": 2, "to": 3}, stamp(2)),
                  event("tombstone", "gone", {"id": 2}, stamp(3)))
        self.assertEqual(self.counters("BUG-0003")["found"], True)
        self.assertFalse(self.counters("BUG-0002")["found"])
        self.ok("doctor")

    def test_replay_is_the_same_in_any_line_order(self):
        evs = [create("live", 2, stamp(1)), event("tombstone", "gone", {"id": 2}, stamp(2))]
        self.seed(*reversed(evs))
        self.assertIn("duplicate", self.no("counters", "BUG-0002", "--json"))

    def test_delete_then_add_is_no_duplicate(self):
        self.add()
        self.ok("delete", "BUG-0001", "--by", "GD")
        self.assertEqual(self.add(), "BUG-0002")
        self.ok("doctor")


class TestRoundCount(Base):
    """DEF-E1-04, DEF-E1-06: +n only, 1 to 100 per call, an integer total."""

    TOO_BIG = ("+101", "+1000", "+99999999999999", "+9223372036854775807", "+9223372036854775808", "+" + "9" * 5000)
    NO_PLUS = ("1", "100", "0", "007")

    def test_limits_on_both_commands(self):
        self.add()
        before = self.counters("BUG-0001")
        for cmd in ("round", "extra-round"):
            for bad in self.TOO_BIG + self.NO_PLUS + ("+0", "+00", "abc", "+", "+1.5", "+1e3"):
                with self.subTest(cmd=cmd, n=bad[:24]):
                    code, _, err = self.run_cli(cmd, "BUG-0001", "fix", bad, "--note", "n")
                    self.assertNotEqual(code, 0)
                    self.assertIn("bad count", err)
                    self.assertNotIn("Traceback", err)
        self.assertEqual(self.counters("BUG-0001"), before)
        self.ok("round", "BUG-0001", "fix", "+100", "--note", "n")
        self.ok("extra-round", "BUG-0001", "fix", "+100", "--note", "n")
        c = self.counters("BUG-0001")
        self.assertEqual(c["fix"], {"used": 100, "cap": 102})
        self.assertIsInstance(c["fix"]["used"], int)

    def test_out_of_range_journal_values_refuse_with_no_float_or_traceback(self):
        for bad in (101, 2 ** 63, 2 ** 64, 1000.0, 1e30):
            for etype in ("round", "extra_round"):
                with self.subTest(etype=etype, n=bad):
                    shutil.rmtree(self.root / ".workflow", ignore_errors=True)
                    self.seed(create("a", 1), event(etype, "a", {"counter": "fix", "n": bad}, stamp(1)))
                    for argv in (["counters", "BUG-0001", "--json"], ["list"], ["doctor"]):
                        code, out, err = self.run_cli(*argv)
                        self.assertNotEqual(code, 0, out)
                        self.assertIn("corrupt journal", err)
                        self.assertNotIn("Traceback", err)

    def test_import_refuses_a_count_replay_would_refuse(self):
        self.root.joinpath(".workflow").mkdir()
        md = self.root / ".workflow" / "bugs.md"
        for extra in ("- Fix rounds: 101/2\n", "- Fix rounds: 1/900\n- Extra round: fix +898\n"):
            md.write_text(md_file(md_record(extra=extra)), encoding="utf-8")
            self.assertIn("import stopped", self.no("import-md"))
            self.assertFalse(self.journal.exists())


class TestGdAttribution(Base):
    """DEF-E1-05: exactly GD on every path; whitespace variants are refused, as delete does."""

    VARIANTS = ("GD ", " GD", "\tGD", "GD\t", " GD ", "GD ")

    def test_set_status_refuses_a_padded_gd(self):
        self.add()
        before = self.journal.read_bytes()
        for by in self.VARIANTS:
            with self.subTest(by=by):
                self.assertIn("exactly GD", self.no("set-status", "BUG-0001", "Backlog", "--note", "n", "--by", by))
                self.assertEqual(self.show("BUG-0001")["status"], "Request")
        self.assertEqual(self.journal.read_bytes(), before)
        self.ok("set-status", "BUG-0001", "Backlog", "--note", "n", "--by", "GD")

    def test_every_other_path_refuses_it_too(self):
        self.add()
        before = self.journal.read_bytes()
        calls = ((["add"], fields()), (["update", "BUG-0001"], {"note": "n"}), (["round", "BUG-0001", "fix", "+1", "--note", "n"], None),
                 (["extra-round", "BUG-0001", "fix", "+1", "--note", "n"], None), (["stop-rule", "BUG-0001", "fix", "--extra-dispatch", "used"], None),
                 (["set-status", "BUG-0001", "Processing", "--note", "n"], None), (["delete", "BUG-0001"], None))
        for argv, stdin in calls:
            for by in self.VARIANTS:
                with self.subTest(argv=argv[0], by=by):
                    self.no(*argv, "--by", by, stdin=stdin)
        self.assertEqual(self.journal.read_bytes(), before)

    def test_other_writers_keep_their_trim(self):
        self.add()
        self.ok("update", "BUG-0001", "--by", " QA executor ", stdin={"note": "n"})
        self.assertEqual(self.show("BUG-0001")["events"][-1]["by"], "QA executor")


class TestEmptyJournal(Base):
    """E3-01: bootstrap creates an empty tracked journal; every command takes it."""

    def setUp(self):
        super().setUp()
        (self.root / ".workflow").mkdir()
        self.journal.write_bytes(b"")

    def test_reads_are_empty(self):
        self.assertEqual(self.ok("list"), "no bugs\n")
        self.assertEqual(json.loads(self.ok("list", "--json")), [])
        self.assertEqual(self.ok("stats"), "Bugs: 0 open (0 High+)\n")
        self.assertEqual(self.ok("search", "coins"), "no matches\n")
        self.assertEqual(self.ok("sql", "SELECT COUNT(*) AS n FROM bug"), "n\n0\n")
        self.assertFalse(self.counters("BUG-0001")["found"])
        self.assertIn("not found", self.no("show", "BUG-0001"))
        self.assertEqual(self.journal.read_bytes(), b"")

    def test_first_write_works_and_starts_at_one(self):
        self.assertEqual(self.add(), "BUG-0001")
        self.assertEqual(len(self.lines()), 1)
        self.assertTrue(self.journal.read_bytes().endswith(b"\n"))
        self.assertFalse(self.journal.read_bytes().startswith(b"\n"))

    def test_purge_and_doctor_are_clean_and_write_nothing(self):
        self.assertEqual(self.ok("purge"), "purged 0\n")
        self.assertEqual(self.ok("purge", "--dry-run"), "would purge 0\n")
        self.assertEqual(self.ok("doctor"), "doctor: clean\n")
        self.assertEqual(self.ok("doctor", "--fix"), "doctor: clean\n")
        self.assertEqual(self.ok("rebuild"), "rebuilt: 0 bugs, 0 events\n")
        self.assertEqual(self.journal.read_bytes(), b"")

    def test_import_md_works_with_it(self):
        (self.root / ".workflow" / "bugs.md").write_text(REAL_BUGS_MD, encoding="utf-8")
        self.assertIn("imported 5 bugs", self.ok("import-md"))
        (self.root / ".workflow" / "bugs.md").unlink()
        self.assertEqual(len(json.loads(self.ok("list", "--json"))), 5)

    def test_bugs_md_refuse_rule_is_unchanged(self):
        (self.root / ".workflow" / "bugs.md").write_text("# Bugs\n", encoding="utf-8")
        for argv in (["list"], ["stats"], ["doctor"], ["purge"], ["add"]):
            with self.subTest(argv):
                self.assertIn("bugs.md", self.no(*argv, stdin=fields() if argv[0] == "add" else None))
        self.assertEqual(self.journal.read_bytes(), b"")


class TestDoctorGitChecks(GitBase):
    """E3-03, E3-04: a project rule that defeats the journal's attributes or ignores it is a problem, not a clean bill."""

    def assert_problem(self, needle, *argv):
        code, out, err = self.run_cli("doctor", *argv)
        self.assertEqual(code, 1, out + err)
        self.assertNotIn("doctor: clean", out)
        self.assertIn(needle, err)

    def test_clean_when_merge_is_union_and_tracked(self):
        self.add()
        self.commit()
        self.assertEqual(self.ok("doctor"), "doctor: clean\n")

    def test_no_line_at_all_is_a_problem(self):
        self.add()
        (self.root / ".gitattributes").write_text("", encoding="utf-8")
        self.assert_problem("merge=union")
        self.assert_problem("merge=union", "--fix")

    def test_a_later_rule_defeating_union_is_a_problem(self):
        self.add()
        with open(self.root / ".gitattributes", "a", encoding="utf-8") as f:
            f.write(".workflow/** -text merge=binary\n")
        self.assert_problem("binary")
        self.assert_problem("binary", "--fix")

    def test_an_ignored_journal_is_a_problem(self):
        with open(self.root / ".gitignore", "a", encoding="utf-8") as f:
            f.write(".workflow/\n")
        self.add()
        self.assert_problem("ignored")
        self.assert_problem("ignored", "--fix")

    def test_a_tracked_journal_under_an_ignore_rule_is_not(self):
        self.add()
        self.commit()
        with open(self.root / ".gitignore", "a", encoding="utf-8") as f:
            f.write(".workflow/\n")
        self.assertEqual(self.ok("doctor"), "doctor: clean\n")

    def test_no_journal_yet_is_checked_too(self):
        with open(self.root / ".gitignore", "a", encoding="utf-8") as f:
            f.write(".workflow/\n")
        self.assert_problem("ignored")

    def test_a_tracked_journal_deleted_by_hand_is_a_problem(self):
        self.add()
        self.commit()
        self.journal.unlink()
        self.assert_problem("journal deleted")

    def test_a_tracked_journal_deleted_in_the_index_too_is_a_problem(self):
        self.add()
        self.commit()
        git(self.root, "rm", "-q", "--", ".workflow/bugs.jsonl")
        self.assert_problem("journal deleted")

    def test_a_journal_git_never_tracked_reads_clean_when_missing(self):
        self.assertEqual(self.ok("doctor"), "doctor: clean\n")

    def test_a_later_rule_making_the_journal_crlf_is_a_problem(self):
        self.add()
        self.commit()
        with open(self.root / ".gitattributes", "a", encoding="utf-8") as f:
            f.write(".workflow/** eol=crlf\n")
        self.assert_problem("eol resolves to crlf")
        self.assert_problem("eol resolves to crlf", "--fix")

    def test_a_rule_unsetting_eol_is_a_problem(self):
        self.add()
        self.commit()
        with open(self.root / ".gitattributes", "a", encoding="utf-8") as f:
            f.write(".workflow/** !eol\n")
        self.assert_problem("eol resolves to")

    def test_a_linked_worktree_reads_the_main_checkout(self):
        self.add()
        self.commit()
        wt = Path(self.tmp) / "wt"
        git(self.root, "worktree", "add", "-q", str(wt), "-b", "wt-branch")
        self.assertEqual(self.ok("doctor", root=wt), "doctor: clean\n")


class TestDocContracts(unittest.TestCase):
    """Text the QA findings turned on. verify.ps1 cannot express these, and a real session only reads the words."""

    @classmethod
    def setUpClass(cls):
        layer = SKILL_DIR.parents[1]
        read = lambda rel: (layer / rel).read_text(encoding="utf-8").replace("\r\n", "\n")
        cls.skill = read("skills/bugs/SKILL.md")
        cls.schema = read("skills/bugs/references/schema.md")
        cls.fix = read("skills/fix/SKILL.md")
        cls.release = read("skills/release/SKILL.md")
        cls.qa = read("skills/qa/SKILL.md")
        cls.feature = read("skills/feature/SKILL.md")
        cls.new_project = read("skills/new-project/SKILL.md")
        cls.lifecycle = read("skills/qa-standards/references/bug-lifecycle.md")
        cls.routing = read("rules/routing.md")
        cls.feature_docs = read("skills/feature-docs/SKILL.md")

    def test_abandon_reports_a_dirty_journal_with_or_without_moves(self):
        line = next(x for x in self.feature.split("\n") if x.startswith("- **Journal:**") and "journal uncommitted" in x)
        self.assertNotIn("those moves", line)
        self.assertIn("dirty or untracked", line)
        self.assertIn("no bugs moved", line)

    def test_the_device_marker_says_how_to_read_it_and_when_it_counts(self):
        for name, text in (("release", self.release), ("fix", self.fix)):
            line = next(x for x in text.split("\n") if "awaits device verification" in x)
            with self.subTest(name):
                self.assertIn("`show`", line)
                self.assertIn("latest move to `Resolved`", line)

    def test_uncommitted_reports_name_the_no_feature_debt_file(self):
        for name, text in (("fix", self.fix), ("qa", self.qa), ("release", self.release)):
            line = next(x for x in text.split("\n") if "journal uncommitted" in x and "`.workflow/bugs.jsonl`" in x)
            with self.subTest(name):
                self.assertIn("`.workflow/DEBT.md`", line)

    def test_known_debt_is_read_from_the_no_feature_file_too(self):
        line = next(x for x in self.feature_docs.split("\n") if x.startswith("- **Before filing a bug"))
        self.assertIn("`.workflow/DEBT.md`", line)

    def test_the_eol_check_is_documented(self):
        line = next(x for x in self.schema.split("\n") if x.startswith("- **Attributes:**"))
        self.assertIn("`eol`", line)
        self.assertIn("`lf`", line)

    def test_the_root_rule_is_one_rule_in_the_schema(self):
        self.assertIn("`Ctx` in `bugs.py` and `Get-BugsRoot` in `common.ps1`", self.schema)
        self.assertNotIn("root comes from comparing", self.schema)

    def test_an_empty_journal_lists_import_md_as_a_source(self):
        line = next(x for x in self.schema.split("\n") if x.startswith("- **Empty journal:**"))
        self.assertIn("zero-row `import-md`", line)

    def test_a_failed_git_names_its_purge_skip(self):
        line = next(x for x in self.schema.split("\n") if x.startswith("- **Git failing:**"))
        self.assertIn("`purge skipped: git failed`", line)

    def test_a_missing_journal_says_what_doctor_can_see(self):
        line = next(x for x in self.schema.split("\n") if x.startswith("- **Empty journal:**"))
        self.assertIn("only when git shows the tracked file deleted", line)

    def test_refusal_text_documents_the_unrecognized_count(self):
        line = next(x for x in self.schema.split("\n") if x.startswith("- **Refusal text:**"))
        self.assertIn("Unrecognized arguments are counted", line)

    def line(self, text, needle):
        hits = [x for x in text.splitlines() if needle in x]
        self.assertTrue(hits, needle)
        return hits[0]

    def test_f1_stdin_rule_names_the_form_that_works_on_both_shells(self):
        form = "$OutputEncoding = [Text.UTF8Encoding]::new($false)"
        self.assertIn(form, self.line(self.skill, "**Stdin:**"))
        self.assertIn(form, self.schema)
        self.assertRegex(self.line(self.schema, form), r"(?i)cannot (?:detect|tell)")

    def test_def_e1_07_a_match_moves_only_a_terminal_bug_to_reopen(self):
        check = self.line(self.skill, "**Check first:**")
        self.assertNotIn("settled bug moves", check)
        self.assertIn("terminal", check)
        for text in (check, self.line(self.fix, "**Match by status:**"), self.line(self.lifecycle, "Check existing bugs first")):
            self.assertIn("Backlog", text)
            self.assertIn("update", text)
            self.assertIn("Reopen", text)

    def test_def_e1_08_e3_08_the_note_is_written_as_required(self):
        row = self.line(self.skill, "`set-status <id>")
        self.assertIn('`set-status <id> "<status>" --note N', row)
        self.assertNotIn("[--note N]", self.skill)

    def test_counts_are_documented(self):
        for text in (self.skill, self.schema):
            self.assertRegex(text, r"1 to 100")

    def test_e3_01_bootstrap_creates_the_empty_journal(self):
        state = self.line(self.new_project, "**Workflow state:**")
        self.assertIn("empty `.workflow/bugs.jsonl`", state)
        self.assertNotIn("first `bugs.py add` starts", self.new_project)
        step_0 = self.feature[self.feature.index("## 0. Open"):self.feature.index("## 4. Build")]
        step_4 = self.feature[self.feature.index("## 4. Build"):]
        self.assertNotIn("bugs.jsonl", step_0)  # the S exit leaves step 1: an empty file there would stay untracked
        self.assertIn("no `.workflow/bugs.jsonl` → create it empty", step_4.split("\n- **Start:**")[0])
        self.assertIn("not a pass", self.line(self.release, "**Bug queries:**"))

    def test_e3_02_a_dry_run_brief_has_no_verify_line(self):
        line = self.line(self.release, "**Dry-run brief:**")
        self.assertIn("repro steps in plain words", line)
        self.assertIn("no `Verify:` line", line)
        self.assertIn("not a `Repro:` line", line)

    def test_e3_05_release_and_standalone_qa_report_the_uncommitted_journal(self):
        self.assertIn("journal uncommitted", self.release)
        self.assertIn("journal uncommitted", self.qa)
        self.assertIn(".workflow/bugs.jsonl", self.line(self.release, "journal uncommitted"))
        self.assertIn(".workflow/bugs.jsonl", self.line(self.qa, "journal uncommitted"))

    def test_e3_06_fix_names_the_safe_evidence_form(self):
        line = self.line(self.fix, "**Existing bug:**")
        self.assertIn("a `note` alone", line)
        self.assertIn("`evidence` field is replaced", line)

    def test_e3_07_a_no_feature_mirror_has_a_home_and_row_0b_reads_it(self):
        self.assertIn(".workflow/DEBT.md", self.line(self.skill, "**Mirror:**"))
        self.assertIn(".workflow/DEBT.md", self.line(self.release, "| 0b |"))
        self.assertIn(".workflow/DEBT.md", self.line(self.lifecycle, "**Won't fix**"))
        self.assertIn(".workflow/DEBT.md", self.line(self.fix, "**No feature:** `AskUserQuestion`"))
        self.assertIn(".workflow/DEBT.md", self.line(self.fix, "**Cannot reproduce:**"))

    def test_e3_09_qa_plan_command_has_its_filters(self):
        self.assertIn("`bugs.py list --feature <slug> --open`", self.line(self.qa, "**Brief:** `Feature:"))

    def test_e3_10_the_interpreter_line_is_named(self):
        self.assertIn("`Memory:`", self.line(self.skill, "**Python:**"))

    def test_e3_11_routing_names_the_bug_record_beside_the_state_file(self):
        line = self.line(self.routing, "The state file")
        self.assertIn("bug record", line)
        self.assertIn("used = file or database + hook", line)

    def test_e3_12_the_device_exception_has_a_marker(self):
        marker = "awaits device verification"
        self.assertIn(marker, self.line(self.release, "| 1 | Open bugs |"))
        self.assertIn(marker, self.line(self.fix, "**Its marker:**"))

    def test_e3_13_a_duplicate_hit_follows_its_target(self):
        for text in (self.line(self.skill, "**Check first:**"), self.line(self.fix, "**Match by status:**"), self.line(self.lifecycle, "Check existing bugs first")):
            self.assertIn("duplicate_of", text)

    def test_abandon_reports_the_uncommitted_journal(self):
        abandon = self.feature[self.feature.index("## Abandon"):]
        self.assertIn("journal uncommitted", abandon)
        self.assertIn(".workflow/bugs.jsonl", abandon)

    def test_the_echo_limits_are_the_codes(self):
        line = self.line(self.schema, "**Refusal text:**")
        self.assertNotIn("over 40 chars is not echoed", line)
        self.assertIn("redaction always runs", line)
        source = (HERE / "bugs.py").read_text(encoding="utf-8")
        self.assertIn("def shown(value, limit=40)", source)
        for limit, call in ((60, "shown(note, 60)"), (200, "shown(ex, 200)"), (200, "shown(given, 200)"), (300, "shown(message, 300)")):
            self.assertIn(call, source)
            self.assertIn(str(limit), line)
        self.assertIn("500", line)
        self.assertIn("REFUSAL_LINE = 500", source)

    def test_a_broken_mem_is_named_in_the_fail_closed_rule(self):
        self.assertIn("syntax error", self.line(self.schema, "**Fail closed:**"))

    def test_the_purge_clock_is_documented(self):
        self.assertIn("last terminal status reached", self.schema)


CSC = Path(os.environ.get("WINDIR", "")) / "Microsoft.NET" / "Framework64" / "v4.0.30319" / "csc.exe"


@unittest.skipUnless(os.name == "nt" and CSC.exists(), "needs Windows and its csc.exe to build a stub git.exe")
class TestPlantedGit(unittest.TestCase):
    """A git in the working folder never runs: CreateProcess and shutil.which both try that folder before PATH.
    Unless NoDefaultCurrentDirectoryInExePath is set, as a Claude Code session sets it: nothing promises a hook that, so it is cleared."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        env = mock.patch.dict(os.environ)
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop("NoDefaultCurrentDirectoryInExePath", None)
        self.root = self.tmp / "repo"
        self.root.mkdir()
        git(self.root, "init", "-q")
        self.planted = self.tmp / "planted"
        self.planted.mkdir()
        self.marker = self.tmp / "ran.txt"

    def stub_exe(self):
        src = self.tmp / "stub.cs"
        src.write_text('class P { static int Main() { System.IO.File.WriteAllText(@"%s", "ran"); return 0; } }' % self.marker, encoding="utf-8")
        subprocess.run([str(CSC), "/nologo", "/out:" + str(self.planted / "git.exe"), str(src)], check=True, capture_output=True)

    def run_cli(self, *argv):
        return subprocess.run([sys.executable, "-I", str(HERE / "bugs.py"), "--root", str(self.root)] + list(argv),
                              input=b"", capture_output=True, cwd=self.planted)

    def test_a_git_exe_in_the_working_folder_never_runs(self):
        self.stub_exe()
        r = self.run_cli("stats")
        self.assertFalse(self.marker.exists(), "the planted git.exe ran")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_git_cmd_in_the_working_folder_never_runs(self):
        (self.planted / "git.cmd").write_text('@echo ran> "%s"' % self.marker, encoding="ascii")
        r = self.run_cli("stats")
        self.assertFalse(self.marker.exists(), "the planted git.cmd ran")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_relative_path_entry_is_not_searched(self):
        self.stub_exe()
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.planted)
        with mock.patch.dict(os.environ, {"PATH": "." + os.pathsep + os.environ["PATH"]}):
            self.assertNotEqual(Path(bugs.git_exe()).parent, self.planted)

    def test_no_git_on_path_is_the_error_a_missing_program_raises(self):
        with mock.patch.dict(os.environ, {"PATH": str(self.tmp)}):
            with self.assertRaises(FileNotFoundError):
                bugs.git_exe()


if __name__ == "__main__":
    unittest.main(verbosity=1)
