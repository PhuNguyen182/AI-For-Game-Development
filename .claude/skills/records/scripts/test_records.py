"""Tests for records.py and the shared journal engine. Run: python -I .claude/skills/records/scripts/test_records.py"""
import contextlib
import io
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import records  # noqa: E402

SKILLS = HERE.parents[1]
FAKE_KEY = "AK" + "IA" + "Q" * 16  # built at runtime so this file holds no secret-shaped literal
EMAIL = "player" + "@" + "example.com"
T0 = "2026-01-01T00:00:00Z"


def git(cwd, *args, check=True):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "init.defaultBranch=main", "-C", str(cwd)] + list(args),
                          check=check, capture_output=True, text=True, encoding="utf-8")


def bl(**over):
    d = {"feature": "Core loop", "milestone": "M1", "size": "M"}
    d.update(over)
    return d


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="records-test-")
        self.root = Path(self.tmp) / "p"
        self.root.mkdir()
        self.env_patch = mock.patch.dict(os.environ)
        self.env_patch.start()
        os.environ.pop("RECORDS_NOW", None)

    def tearDown(self):
        self.env_patch.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    @property
    def wf(self):
        return self.root / ".workflow"

    def run_cli(self, *argv, stdin=None, now=T0, root=None):
        data = b"" if stdin is None else (stdin if isinstance(stdin, bytes) else json.dumps(stdin, ensure_ascii=False).encode("utf-8"))
        out, err = io.StringIO(), io.StringIO()
        old_stdin = sys.stdin
        sys.stdin = io.TextIOWrapper(io.BytesIO(data), encoding="utf-8")
        if now is not None:
            os.environ["RECORDS_NOW"] = now
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                try:
                    code = records.main(["--root", str(root or self.root)] + list(argv))
                except SystemExit as ex:
                    code = ex.code
        finally:
            sys.stdin = old_stdin
            os.environ.pop("RECORDS_NOW", None)
        return code, out.getvalue(), err.getvalue()

    def ok(self, *argv, **kw):
        code, out, err = self.run_cli(*argv, **kw)
        self.assertEqual(code, 0, "stdout: %s\nstderr: %s" % (out, err))
        return out

    def no(self, *argv, code=None, **kw):
        got, out, err = self.run_cli(*argv, **kw)
        self.assertNotEqual(got, 0, "expected a refusal, got stdout: %s" % out)
        if code is not None:
            self.assertEqual(got, code, err)
        self.assertTrue(err.strip(), "a refusal must say why on stderr")
        return err

    def show(self, store, rid):
        return json.loads(self.ok(store, "show", rid, "--json"))

    def lines(self, name):
        return [json.loads(x) for x in (self.wf / name).read_bytes().split(b"\n") if x.strip()]


class GitBase(Base):
    def setUp(self):
        super().setUp()
        git(self.root, "init", "-q")
        (self.root / ".gitattributes").write_text(".workflow/*.jsonl text eol=lf merge=union\n", encoding="utf-8")
        (self.root / ".gitignore").write_text(".workflow/records.db*\n.workflow/ledger.db*\n", encoding="utf-8")
        self.commit("init")

    def commit(self, msg="c"):
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "--allow-empty", "-m", msg)


# ---------------------------------------------------------------- per store

class TestBacklog(Base):
    def test_add_update_state_list_show_search_render(self):
        self.assertEqual(self.ok("backlog", "add", stdin=bl()).strip(), "BL-0001")
        self.assertEqual(self.ok("backlog", "add", stdin=bl(feature="Shop | store", size="S", depends_on="1 ,1")).strip(), "BL-0002")
        r = self.show("backlog", "BL-0002")
        self.assertEqual((r["num"], r["status"], r["depends_on"]), (2, "todo", "1, 1"))
        self.assertIn("risk", self.ok("backlog", "update", "BL-0001", stdin={"risk": "save-data migration"}))
        self.assertIn("no change", self.ok("backlog", "update", "BL-0001", stdin={"risk": "save-data migration"}))
        self.assertIn("todo -> in progress", self.ok("backlog", "set-state", "BL-0001", "in progress", "--note", "main session: /feature core-loop"))
        self.assertEqual([x["id"] for x in json.loads(self.ok("backlog", "list", "--open", "--json"))], ["BL-0001", "BL-0002"])
        self.assertEqual([x["id"] for x in json.loads(self.ok("backlog", "list", "--state", "in progress", "--json"))], ["BL-0001"])
        self.ok("backlog", "set-state", "BL-0001", "done", "--note", "closed")
        self.assertEqual([x["id"] for x in json.loads(self.ok("backlog", "list", "--open", "--json"))], ["BL-0002"])
        self.assertIn("BL-0002 | todo | M1 | S | Shop | store", self.ok("backlog", "list"))
        self.assertIn("BL-0001", self.ok("backlog", "search", "migration"))
        self.assertIn("BL-0001", self.ok("backlog", "search", "feature core"))  # notes are searched too
        self.assertEqual(self.ok("backlog", "render").splitlines(), [
            "| # | Feature | Milestone | Size | Risk | Depends on | Status |",
            "|---|---|---|---|---|---|---|",
            "| 1 | Core loop | M1 | M | save-data migration |  | done |",
            "| 2 | Shop \\| store | M1 | S |  | 1, 1 | todo |"])
        self.assertIn("Backlog: 1 open of 2", self.ok("backlog", "stats"))

    def test_field_rules(self):
        self.assertIn("size: required", self.no("backlog", "add", stdin=bl(size=None)))
        self.assertIn("size: must be one of S, M, L", self.no("backlog", "add", stdin=bl(size="XL")))
        self.assertIn("depends_on", self.no("backlog", "add", stdin=bl(depends_on="BL-0001")))
        self.assertIn("num is assigned", self.no("backlog", "add", stdin=bl(num=4)))
        self.assertIn("unknown status", self.no("backlog", "set-state", "BL-0001", "blocked", "--note", "n"))
        self.assertIn("note: required", self.no("backlog", "set-state", "BL-0001", "done"))
        self.assertIn("bad id", self.no("backlog", "show", "BUG-0001"))

    def test_status_words_match_plan_game(self):
        text = (SKILLS / "plan-game" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("todo | in progress (`/feature <slug>`) | done | dropped", text)
        self.assertEqual(records.STORES["backlog"].states, ("todo", "in progress", "done", "dropped"))


class TestFwBacklog(Base):
    def test_done_needs_a_ref_and_the_main_gd_state_needs_the_main_gd(self):
        self.assertEqual(self.ok("fwbacklog", "add", stdin={"item": "**Hook misfires** on a `-C` path"}).strip(), "FW-0001")
        self.assertIn("ref: required for Done", self.no("fwbacklog", "set-state", "FW-0001", "Done", "--note", "fixed"))
        self.ok("fwbacklog", "set-state", "FW-0001", "Done", "--note", "fixed", "--ref", "862cd2c")
        self.assertEqual(self.show("fwbacklog", "FW-0001")["ref"], "862cd2c")
        self.ok("fwbacklog", "add", stdin={"item": "Pilot v2"})
        err = self.no("fwbacklog", "set-state", "FW-0002", "Recorded (main GD decision)", "--note", "accepted")
        self.assertIn("main GD only", err)
        self.assertIn("no padding", self.no("fwbacklog", "set-state", "FW-0002", "Recorded (main GD decision)", "--note", "a", "--by", " main GD"))
        self.ok("fwbacklog", "set-state", "FW-0002", "Recorded (main GD decision)", "--note", "accepted", "--by", "main GD")
        self.assertIn("main GD only", self.no("fwbacklog", "set-state", "FW-0002", "Open", "--note", "undo"))
        self.assertIn("main GD only", self.no("fwbacklog", "add", stdin={"item": "x", "state": "Recorded (main GD decision)"}))
        self.assertIn("ref: required", self.no("fwbacklog", "add", stdin={"item": "x", "state": "Done"}))
        self.assertEqual(self.ok("fwbacklog", "add", stdin={"item": "y", "state": "Done", "ref": ".claude/hooks/x.ps1"}).strip(), "FW-0003")
        self.assertEqual([x["id"] for x in json.loads(self.ok("fwbacklog", "list", "--open", "--json"))], [])
        self.assertIn("FW-0001", self.ok("fwbacklog", "search", "misfires"))
        self.assertEqual(self.ok("fwbacklog", "render").splitlines()[2], "| FW-0001 | **Hook misfires** on a `-C` path | Done | 862cd2c |")
        self.assertIn("--ref: only for fwbacklog", self.no("debt", "set-state", "DEBT-0001", "Paid", "--note", "n", "--ref", "x"))

    def test_item_limit(self):
        self.ok("fwbacklog", "add", stdin={"item": "x" * 1000})
        self.assertIn("item: 1001 chars, limit 1000", self.no("fwbacklog", "add", stdin={"item": "x" * 1001}))
        self.assertIn("item: must be one line", self.no("fwbacklog", "add", stdin={"item": "a\nb"}))


class TestDebt(Base):
    def test_add_defaults_the_date_and_checks_the_source(self):
        self.assertEqual(self.ok("debt", "add", stdin={"text": "Gates miss commit messages", "source": "BUG-0007", "accepted_by": "main GD",
                                                       "next_step": "native git hooks"}).strip(), "DEBT-0001")
        r = self.show("debt", "DEBT-0001")
        self.assertEqual((r["date"], r["state"], r["source"]), ("2026-01-01", "Open", "BUG-0007"))
        for source in ("framework", "game-production-agent"):
            self.ok("debt", "add", stdin={"text": "t", "source": source, "accepted_by": "main GD", "date": "2026-11-06"})
        self.assertIn("source: expected", self.no("debt", "add", stdin={"text": "t", "source": "Some Feature", "accepted_by": "main GD"}))
        self.assertIn("date: expected", self.no("debt", "add", stdin={"text": "t", "source": "framework", "accepted_by": "main GD", "date": "2026-02-30"}))
        self.assertIn("accepted_by: required", self.no("debt", "add", stdin={"text": "t", "source": "framework"}))
        self.ok("debt", "set-state", "DEBT-0001", "Paid", "--note", "fixed in abc1234")
        self.assertEqual(len(json.loads(self.ok("debt", "list", "--open", "--json"))), 2)
        self.assertIn("DEBT-0001", self.ok("debt", "search", "commit"))
        self.assertEqual(self.ok("debt", "render").splitlines()[2],
                         "| DEBT-0001 | 2026-01-01 | BUG-0007 | Gates miss commit messages | native git hooks | main GD | Paid |")


class TestFeature(Base):
    def add(self, slug="workflow-state-stores", **over):
        d = {"slug": slug, "size": "L", "cp": "CP2", "branch": "feature/" + slug, "base": "develop", "build_mode": "serial"}
        d.update(over)
        return self.ok("feature", "add", stdin=d).strip()

    def counters(self, slug="workflow-state-stores"):
        return json.loads(self.ok("feature", "counters", slug, "--json"))

    def test_registry_crud(self):
        self.assertEqual(self.add(), "workflow-state-stores")
        self.assertIn("already registered", self.no("feature", "add", stdin={"slug": "workflow-state-stores"}))
        self.assertIn("slug: expected kebab-case", self.no("feature", "add", stdin={"slug": "Bad_Slug"}))
        self.assertIn("cp", self.ok("feature", "update", "workflow-state-stores", stdin={"cp": "build", "next_step": "T1 attempt 1/4"}))
        self.assertIn("read-only", self.no("feature", "update", "workflow-state-stores", stdin={"slug": "other"}))
        self.assertIn("cp: must be one of", self.no("feature", "update", "workflow-state-stores", stdin={"cp": "CP5"}))
        r = self.show("feature", "workflow-state-stores")
        self.assertEqual((r["cp"], r["status"], r["review"], r["rework"]), ("build", "Open", {"used": 0, "cap": 3}, {"used": 0, "cap": 8}))
        self.assertIn("Open -> Closed", self.ok("feature", "set-state", "workflow-state-stores", "Closed", "--note", "CP4 approved"))
        self.assertEqual(json.loads(self.ok("feature", "list", "--open", "--json")), [])
        self.assertIn("workflow-state-stores", self.ok("feature", "search", "T1 attempt"))
        self.assertEqual(self.ok("feature", "render").splitlines()[2],
                         "| workflow-state-stores | Closed | build | L |  | feature/workflow-state-stores | T1 attempt 1/4 | 0/3 | 0/2 | 0/8 |")

    def test_counters_shape_and_record_lines(self):
        self.add(size="M")
        c = self.counters()
        self.assertEqual(c, {"slug": "workflow-state-stores", "found": True, "open": True, "size": "M", "review": {"used": 0, "cap": 3},
                             "qa": {"used": 0, "cap": 2}, "rework": {"used": 0, "cap": 6}, "record": ""})
        self.assertIn("review 1/3", self.ok("feature", "round", "workflow-state-stores", "review", "+1", "--note", "workflow review round 1"))
        self.assertIn("main GD only", self.no("feature", "extra-round", "workflow-state-stores", "review", "+1", "--note", "order"))
        self.assertIn("review 1/5", self.ok("feature", "extra-round", "workflow-state-stores", "review", "+2", "--note", "order", "--by", "main GD"))
        self.ok("feature", "stop-rule", "workflow-state-stores", "qa", "--extra-dispatch", "unused", now="2026-01-02T00:00:00Z")
        self.ok("feature", "stop-rule", "workflow-state-stores", "qa", "--extra-dispatch", "used", now="2026-01-03T00:00:00Z")
        self.ok("feature", "update", "workflow-state-stores", stdin={"size": "L"})
        c = self.counters()
        self.assertEqual((c["review"], c["rework"]), ({"used": 1, "cap": 5}, {"used": 0, "cap": 8}))
        self.assertEqual(c["record"].split("\n"), ["- Stop rule: qa root-caused 2026-01-03 · extra dispatch: used", "extra round: review +2"])
        self.assertIn("bad count", self.no("feature", "round", "workflow-state-stores", "qa", "+0", "--note", "n"))
        self.ok("feature", "set-state", "workflow-state-stores", "Abandoned", "--note", "main GD dropped it")
        self.assertFalse(self.counters()["open"])

    def test_unknown_feature_counters_and_the_default_caps(self):
        self.assertEqual(self.counters("nope"), {"slug": "nope", "found": False, "open": False, "size": None, "review": {"used": 0, "cap": 3},
                                                 "qa": {"used": 0, "cap": 2}, "rework": {"used": 0, "cap": 6}, "record": ""})
        self.add("small", size="S")
        self.assertEqual(self.counters("small")["rework"]["cap"], 6)
        self.assertIn("not found", self.no("feature", "round", "nope", "qa", "+1", "--note", "n"))

    def test_counter_sources_extend_caps_and_record(self):
        self.add(size="M")

        def csv_rows(ctx, slug):
            return [{"type": "extra_round", "counter": "qa", "n": 1, "date": "2026-01-05"},
                    {"type": "stop_rule", "counter": "rework", "extra_dispatch": "unused", "date": "2026-01-06"}]

        with mock.patch.object(records, "COUNTER_SOURCES", [csv_rows]):
            c = self.counters()
        self.assertEqual(c["qa"]["cap"], 3)
        self.assertEqual(c["record"], "- Stop rule: rework root-caused 2026-01-06 · extra dispatch: unused\nextra round: qa +1")

    def test_the_hook_regexes_match_the_record(self):
        import re
        self.add()
        self.ok("feature", "extra-round", "workflow-state-stores", "rework", "+1", "--note", "o", "--by", "main GD")
        self.ok("feature", "stop-rule", "workflow-state-stores", "review", "--extra-dispatch", "unused")
        rec = self.counters()["record"]
        self.assertRegex(rec, r"(?i)extra round")
        self.assertRegex(rec, re.compile(r"(?im)^- Stop rule:.*\breview\b"))
        self.assertNotRegex(rec, re.compile(r"(?im)^- Stop rule:.*\bqa\b"))


# ---------------------------------------------------------------- journal behaviour

class TestJournal(Base):
    def test_rebuild_after_deleting_the_db_gives_the_same_view(self):
        self.ok("backlog", "add", stdin=bl())
        self.ok("debt", "add", stdin={"text": "t", "source": "framework", "accepted_by": "main GD"})
        self.ok("feature", "add", stdin={"slug": "a-b", "size": "L"})
        self.ok("feature", "round", "a-b", "rework", "+2", "--note", "n")
        before = [self.ok(s, "render") for s in ("backlog", "debt", "feature")]
        for f in self.wf.glob("records.db*"):
            f.unlink()
        self.assertEqual([self.ok(s, "render") for s in ("backlog", "debt", "feature")], before)
        self.assertIn("rebuilt: backlog 1, fwbacklog 0, debt 1, feature 1", self.ok("rebuild"))
        lines = self.lines("features.jsonl")
        self.assertEqual([x["type"] for x in lines], ["create", "round"])
        self.assertEqual(set(lines[0]), {"event_uid", "uid", "ts", "type", "data", "by"})

    def test_a_changed_journal_rebuilds_only_its_store(self):
        self.ok("backlog", "add", stdin=bl())
        self.ok("debt", "add", stdin={"text": "t", "source": "framework", "accepted_by": "main GD"})
        db = sqlite3.connect(str(self.wf / "records.db"))
        db.execute("UPDATE debt SET text='sentinel'")  # a cache-only mark: a rebuild of debt would erase it
        db.commit()
        db.close()
        other = self.root / "elsewhere"
        other.mkdir()
        self.ok("backlog", "add", stdin=bl(feature="Elsewhere"), root=other)
        shutil.copy(other / ".workflow" / "backlog.jsonl", self.wf / "backlog.jsonl")  # what a git switch does to the file
        self.assertEqual([x["feature"] for x in json.loads(self.ok("backlog", "list", "--json"))], ["Elsewhere"])
        self.assertIn("sentinel", self.ok("sql", "SELECT text FROM debt"))

    def test_torn_tail_is_skipped_reported_and_repaired(self):
        self.ok("backlog", "add", stdin=bl())
        with open(self.wf / "backlog.jsonl", "ab") as f:
            f.write(b'{"event_uid":"x","uid"')
        self.assertEqual(len(json.loads(self.ok("backlog", "list", "--json"))), 1)
        self.assertIn("torn final line", self.no("doctor"))
        self.assertEqual(self.ok("backlog", "add", stdin=bl(feature="Two")).strip(), "BL-0002")
        self.assertEqual(len(self.lines("backlog.jsonl")), 2)
        with open(self.wf / "backlog.jsonl", "ab") as f:
            f.write(b'{"event_uid":"y"')
        code, out, err = self.run_cli("doctor", "--fix")
        self.assertNotIn("torn", err)
        self.assertTrue((self.wf / "backlog.jsonl").read_bytes().endswith(b"}\n"))

    def test_a_malformed_line_fails_closed_with_its_number(self):
        self.ok("debt", "add", stdin={"text": "t", "source": "framework", "accepted_by": "main GD"})
        with open(self.wf / "debt.jsonl", "ab") as f:
            f.write(b'{"bad": 1}\n')
        self.assertIn("line 2", self.no("debt", "list"))
        self.assertIn("line 2", self.no("doctor", "--fix"))
        self.ok("backlog", "list")  # another store's reads are not blocked

    def test_a_crash_after_the_append_is_healed(self):
        self.ok("backlog", "add", stdin=bl())
        code = ("import os, sys; sys.path.insert(0, %r); import records; records._after_append = lambda: os._exit(9); "
                "sys.exit(records.main(%r))") % (str(HERE), ["--root", str(self.root), "backlog", "set-state", "BL-0001", "done", "--note", "n"])
        self.assertEqual(subprocess.run([sys.executable, "-I", "-c", code], capture_output=True).returncode, 9)
        self.assertEqual(self.show("backlog", "BL-0001")["status"], "done")

    def test_a_failed_append_rolls_back_the_db(self):
        self.ok("backlog", "add", stdin=bl())
        with mock.patch.object(records.journal, "append_lines", side_effect=OSError("disk full")):
            self.assertIn("disk full", self.no("backlog", "update", "BL-0001", stdin={"risk": "x"}))
        self.assertIsNone(self.show("backlog", "BL-0001")["risk"])

    def test_no_journal_reads_empty_and_creates_nothing(self):
        self.assertIn("no records", self.ok("debt", "list"))
        self.assertIn("Records: backlog 0 open", self.ok("stats"))
        self.assertFalse(self.wf.exists())

    def test_sql_is_read_only(self):
        self.ok("backlog", "add", stdin=bl())
        self.assertIn("sql is read-only", self.no("sql", "DELETE FROM backlog"))
        self.assertIn("sql refused", self.no("sql", "SELECT 1; DELETE FROM backlog"))
        self.assertIn("refused", self.no("sql", "WITH x AS (SELECT 1) DELETE FROM backlog"))
        self.assertEqual(json.loads(self.ok("sql", "SELECT id, num FROM backlog", "--json")), [{"id": "BL-0001", "num": 1}])
        self.assertIn("Core", self.ok("sql", "SELECT feature FROM backlog_fts WHERE backlog_fts MATCH 'core'"))


class TestMerge(GitBase):
    def test_union_merge_with_new_rows_on_both_sides_and_doctor_fix(self):
        self.ok("backlog", "add", stdin=bl())
        self.ok("feature", "add", stdin={"slug": "shared", "size": "M"})
        self.commit("main 1")
        git(self.root, "switch", "-q", "-c", "b")
        self.assertEqual(self.ok("backlog", "add", stdin=bl(feature="B side", depends_on="2")).strip(), "BL-0002")
        self.ok("feature", "round", "shared", "review", "+1", "--note", "b", now="2026-01-02T00:00:00Z")
        self.commit("b")
        git(self.root, "switch", "-q", "main")
        self.assertEqual(len(json.loads(self.ok("backlog", "list", "--json"))), 1)  # the switch changed the journal: hash check
        self.assertEqual(self.ok("backlog", "add", stdin=bl(feature="Main side"), now="2026-01-03T00:00:00Z").strip(), "BL-0002")
        self.ok("feature", "round", "shared", "review", "+1", "--note", "main", now="2026-01-04T00:00:00Z")
        self.commit("main 2")
        r = git(self.root, "merge", "-q", "--no-edit", "b", check=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        code, out, err = self.run_cli("backlog", "list", "--json")
        self.assertEqual(code, 0)
        self.assertEqual([x["id"] for x in json.loads(out)], ["BL-0001", "BL-0002", "BL-0002"])
        self.assertIn("duplicate id BL-0002", err)
        self.assertIn("duplicate id", self.no("backlog", "update", "BL-0002", stdin={"risk": "x"}))
        self.assertEqual(self.ok("feature", "counters", "shared").count('"used": 2'), 1)  # one record, both sides' rounds
        self.assertIn("duplicate id BL-0002", self.no("doctor"))
        out = self.ok("doctor", "--fix")
        self.assertIn("renumbered BL-0002 to BL-0003", out)
        self.assertIn("check depends_on of BL-0002: 2 was held by two rows", out)
        self.assertEqual([(x["id"], x["feature"]) for x in json.loads(self.ok("backlog", "list", "--json"))],
                         [("BL-0001", "Core loop"), ("BL-0002", "B side"), ("BL-0003", "Main side")])
        self.assertIn("doctor: clean", self.ok("doctor"))
        self.assertEqual(self.ok("backlog", "add", stdin=bl(feature="Next")).strip(), "BL-0004")

    def test_doctor_reports_missing_attributes_and_an_ignored_journal(self):
        (self.root / ".gitattributes").write_text("", encoding="utf-8")
        (self.root / ".gitignore").write_text(".workflow/debt.jsonl\n.workflow/framework-backlog.jsonl\n", encoding="utf-8")
        err = self.no("doctor")
        self.assertIn("journal attributes: merge resolves to", err)
        self.assertIn("journal ignored by git: .workflow/debt.jsonl", err)
        self.assertNotIn("framework-backlog.jsonl must stay tracked", err)  # the framework repo ignores its own copy

    def test_a_linked_worktree_reads_the_main_data_and_every_write_is_refused(self):
        self.ok("backlog", "add", stdin=bl())
        self.commit("one")
        wt = Path(self.tmp) / "wt"
        git(self.root, "worktree", "add", "-q", str(wt), "-b", "lane")
        self.assertEqual(len(json.loads(self.ok("backlog", "list", "--json", root=wt))), 1)
        self.assertIn("linked worktree", self.no("backlog", "add", stdin=bl(), root=wt))
        self.assertIn("linked worktree", self.no("feature", "add", stdin={"slug": "x"}, root=wt))
        self.assertIn("linked worktree", self.no("ledger", "add", "--json", stdin=[{"key": "k", "counter": "qa", "id": "1"}], root=wt))
        self.assertFalse((wt / ".workflow" / "ledger.db").exists())

    def test_git_failing_reads_and_refuses_writes(self):
        self.ok("backlog", "add", stdin=bl())
        with mock.patch.object(records, "run_git", side_effect=OSError("no git")):
            self.ok("backlog", "list")
            self.assertIn("git failed", self.no("backlog", "add", stdin=bl()))
            self.ok("ledger", "add", "--json", stdin=[{"key": "k", "counter": "qa", "id": "1"}])  # the ledger needs no git


# ---------------------------------------------------------------- write rules

class TestWriteRules(Base):
    def test_vietnamese_and_control_characters_are_refused(self):
        self.assertIn("Vietnamese diacritics", self.no("backlog", "add", stdin=bl(feature="Vòng lặp")))
        self.assertIn("Vietnamese diacritics", self.no("debt", "add", stdin={"text": "Thiếu", "source": "framework", "accepted_by": "main GD"}))
        self.assertIn("control character", self.no("fwbacklog", "add", stdin={"item": "a\x07b"}))
        self.assertIn("must be one line", self.no("feature", "add", stdin={"slug": "a", "next_step": "x y"}))

    def test_a_secret_is_refused_and_never_echoed(self):
        for argv, stdin in ((["fwbacklog", "add"], {"item": "key %s here" % FAKE_KEY}),
                            (["backlog", "add"], bl(risk="key " + FAKE_KEY)),
                            (["backlog", "set-state", "BL-0001", "done", "--note", FAKE_KEY], None),
                            (["backlog", "show", FAKE_KEY], None),
                            (["fwbacklog", "add"], {FAKE_KEY: "x"})):
            with self.subTest(argv=argv[:2]):
                code, out, err = self.run_cli(*argv, stdin=stdin)
                self.assertNotEqual(code, 0)
                self.assertNotIn(FAKE_KEY, out + err)
        self.assertIn("secret-shaped value in item", self.no("fwbacklog", "add", stdin={"item": "key %s here" % FAKE_KEY}))
        self.assertFalse((self.wf / "framework-backlog.jsonl").exists())

    def test_pii_is_redacted(self):
        code, out, err = self.run_cli("debt", "add", stdin={"text": "Reported by %s" % EMAIL, "source": "framework", "accepted_by": "main GD"})
        self.assertEqual(code, 0, err)
        self.assertIn("redacted PII in: text", err)
        self.assertEqual(self.show("debt", "DEBT-0001")["text"], "Reported by [REDACTED:email]")
        self.assertNotIn(EMAIL.encode(), (self.wf / "debt.jsonl").read_bytes())

    def test_field_limits_refuse_not_truncate(self):
        self.assertIn("feature: 101 chars, limit 100", self.no("backlog", "add", stdin=bl(feature="x" * 101)))
        self.assertIn("text: 301 chars, limit 300", self.no("debt", "add", stdin={"text": "x" * 301, "source": "framework", "accepted_by": "main GD"}))
        self.assertIn("note: 201 chars, limit 200", self.no("feature", "add", stdin={"slug": "a", "note": "x" * 201}))
        self.assertIn("unknown field", self.no("debt", "add", stdin={"text": "t", "source": "framework", "accepted_by": "main GD", "severity": "High"}))


class TestFailClosed(Base):
    """An isolated copy of the framework: records.py, journal.py, and mem.py and its patterns only when asked."""

    def copy(self, with_mem=True, with_patterns=True):
        base = Path(self.tmp) / "framework"
        scripts = base / ".claude" / "skills" / "records" / "scripts"
        scripts.mkdir(parents=True)
        for name in ("records.py", "journal.py"):
            shutil.copy(HERE / name, scripts / name)
        if with_mem:
            m = base / ".claude" / "skills" / "mem" / "scripts"
            m.mkdir(parents=True)
            shutil.copy(SKILLS / "mem" / "scripts" / "mem.py", m / "mem.py")
        if with_patterns:
            h = base / ".claude" / "hooks"
            h.mkdir(parents=True)
            shutil.copy(SKILLS.parent / "hooks" / "secret-patterns.txt", h / "secret-patterns.txt")
        return scripts / "records.py"

    def cli(self, script, *argv, stdin=b""):
        return subprocess.run([sys.executable, "-I", str(script), "--root", str(self.root)] + list(argv), input=stdin, capture_output=True)

    def test_every_write_refuses_without_mem_or_patterns_and_reads_still_work(self):
        for kw in (dict(with_mem=False), dict(with_patterns=False)):
            with self.subTest(**kw):
                shutil.rmtree(Path(self.tmp) / "framework", ignore_errors=True)
                script = self.copy(**kw)
                r = self.cli(script, "backlog", "add", stdin=json.dumps(bl()).encode())
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn(b"write refused", r.stderr)
                self.assertNotIn(b"Traceback", r.stderr)
                self.assertEqual(self.cli(script, "backlog", "list").returncode, 0)
                r = self.cli(script, "backlog", "show", FAKE_KEY)
                self.assertNotIn(FAKE_KEY.encode(), r.stderr)
                self.assertEqual(self.cli(script, "ledger", "add", "--json", stdin=b'[{"key":"k","counter":"qa","id":"1"}]').returncode, 0)
        self.assertFalse((self.wf / "backlog.jsonl").exists())

    def test_a_missing_engine_says_so(self):
        script = self.copy()
        (script.parent / "journal.py").unlink()
        r = self.cli(script, "stats")
        self.assertEqual(r.returncode, 1)
        self.assertIn(b"journal.py is missing", r.stderr)
        self.assertNotIn(b"Traceback", r.stderr)


# ---------------------------------------------------------------- the round ledger

class TestLedger(Base):
    def get(self, **kw):
        return json.loads(self.ok("ledger", "get", "--json", **kw))

    def add(self, *events, **kw):
        return self.ok("ledger", "add", "--json", stdin=[{"key": k, "counter": c, "id": i} for k, c, i in events], **kw)

    def park(self, name, body):
        self.wf.mkdir(parents=True, exist_ok=True)
        p = self.wf / name
        p.write_bytes(body if isinstance(body, bytes) else json.dumps(body).encode("utf-8"))
        return p

    def test_get_add_order_and_dedupe(self):
        self.assertEqual(self.get(), {})
        self.assertFalse(self.wf.exists())
        self.assertIn("ledger: 3 new", self.add(("feature:a", "review", "r1"), ("bug:BUG-0001", "fix", "f1"), ("feature:a", "review", "r2")))
        self.assertIn("ledger: 0 new", self.add(("feature:a", "review", "r1")))
        self.add(("feature:a", "qa", "q1"))
        self.assertEqual(self.get(), {"feature:a": {"review": ["r1", "r2"], "qa": ["q1"]}, "bug:BUG-0001": {"fix": ["f1"]}})
        db = sqlite3.connect(str(self.wf / "ledger.db"))
        try:
            self.assertEqual(db.execute("PRAGMA journal_mode").fetchone()[0], "wal")
        finally:
            db.close()
        self.assertIn("ledger add", self.no("ledger", "add", "--json", stdin=[{"key": "k", "counter": "qa"}]))
        self.assertIn("JSON list", self.no("ledger", "add", "--json", stdin={"key": "k"}))

    def test_pending_files_merge_on_get_and_import_on_add(self):
        self.add(("k", "review", "1"))
        p = self.park("rounds.pending-20260101T000000000-aaaa.json", b"\xef\xbb\xbf" + json.dumps([{"key": "k", "counter": "review", "id": "2"}]).encode())
        q = self.park("rounds.pending-20260101T000000001-bbbb.json", {"key": "s", "counter": "qa", "id": "3"})  # one object, as PS may write it
        self.assertEqual(self.get(), {"k": {"review": ["1", "2"]}, "s": {"qa": ["3"]}})
        self.assertTrue(p.exists() and q.exists())  # get is read-only
        self.add(("k", "review", "4"))
        self.assertFalse(p.exists() or q.exists())
        self.assertEqual(self.get(), {"k": {"review": ["1", "4", "2"]}, "s": {"qa": ["3"]}})

    def test_an_unparsable_pending_file_blocks_get_and_is_kept_renamed(self):
        p = self.park("rounds.pending-20260101T000000000-cccc.json", b"{not json")
        self.assertIn("unparsable", self.no("ledger", "get", "--json", code=3))
        self.add(("k", "qa", "1"))
        self.assertFalse(p.exists())
        self.assertTrue((self.wf / "rounds.corrupt-pending-20260101T000000000-cccc.json").exists())
        err = self.no("ledger", "get", "--json", code=3)
        self.assertIn("rounds.corrupt-pending-20260101T000000000-cccc.json", err)
        self.assertEqual(len(err.strip().splitlines()), 1)

    def test_a_corrupt_db_blocks_get_and_add_moves_it_aside(self):
        self.add(("k", "qa", "1"))
        for f in self.wf.glob("ledger.db-*"):
            f.unlink()
        (self.wf / "ledger.db").write_bytes(b"this is not a database at all" * 200)
        self.assertIn("unreadable", self.no("ledger", "get", "--json", code=3))
        code, out, err = self.run_cli("ledger", "add", "--json", stdin=[{"key": "k", "counter": "qa", "id": "2"}])
        self.assertEqual(code, 0, err)
        self.assertIn("unreadable ledger moved to ledger.corrupt-", err)
        self.assertEqual(len(list(self.wf.glob("ledger.corrupt-*.db"))), 1)
        self.assertIn("ledger.corrupt-", self.no("ledger", "get", "--json", code=3))
        for f in self.wf.glob("ledger.corrupt-*"):
            f.unlink()
        self.assertEqual(self.get(), {"k": {"qa": ["2"]}})

    def test_busy_past_the_timeout_exits_75_and_leaves_parked_files(self):
        self.add(("k", "qa", "1"))
        p = self.park("rounds.pending-20260101T000000000-dddd.json", [{"key": "k", "counter": "qa", "id": "2"}])
        holder = sqlite3.connect(str(self.wf / "ledger.db"), isolation_level=None)
        try:
            holder.execute("BEGIN IMMEDIATE")
            with mock.patch.object(records, "LEDGER_BUSY_MS", 300):
                self.assertIn("busy", self.no("ledger", "add", "--json", stdin=[{"key": "k", "counter": "qa", "id": "3"}], code=75))
            self.assertTrue(p.exists())
            self.assertEqual(self.get(), {"k": {"qa": ["1", "2"]}})  # a WAL reader is not blocked by the writer
        finally:
            holder.execute("ROLLBACK")
            holder.close()

    def test_the_default_busy_timeout_is_five_seconds(self):
        self.assertEqual(records.LEDGER_BUSY_MS, 5000)

    def test_migrate_imports_rounds_json_once_and_renames_it(self):
        legacy = {"session:s1": {"review": ["round-1", "round-2"]}, "feature:x": {"qa": ["a"], "rework": "only-one"}}
        self.park("rounds.json", legacy)
        self.park("rounds.pending-20260101T000000000-eeee.json", [{"key": "feature:x", "counter": "qa", "id": "b"}])
        self.assertEqual(self.get(), {"session:s1": {"review": ["round-1", "round-2"]}, "feature:x": {"qa": ["a", "b"], "rework": ["only-one"]}})
        out = self.ok("ledger", "migrate")
        self.assertIn("migrated 4 event(s) from rounds.json (5 new)", out)
        self.assertFalse((self.wf / "rounds.json").exists())
        self.assertEqual(len(list(self.wf.glob("rounds.migrated-*.json"))), 1)
        self.assertEqual(list(self.wf.glob("rounds.pending-*.json")), [])
        self.assertIn("nothing to migrate", self.ok("ledger", "migrate"))
        self.assertEqual(self.get(), {"session:s1": {"review": ["round-1", "round-2"]}, "feature:x": {"qa": ["a", "b"], "rework": ["only-one"]}})

    def test_migrate_refuses_an_unparsable_rounds_json_and_leaves_it(self):
        p = self.park("rounds.json", b"{broken")
        self.assertIn("rounds.json is unparsable", self.no("ledger", "migrate"))
        self.assertTrue(p.exists())
        self.assertEqual(len(self.no("ledger", "get", "--json", code=3).strip().splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
