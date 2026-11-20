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

    def test_stats_json_holds_the_line_and_the_open_features(self):
        self.assertEqual(json.loads(self.ok("stats", "--json")), {"line": self.ok("stats").strip(), "open_features": []})
        self.ok("feature", "add", stdin={"slug": "b-two", "cp": "build", "next_step": "review"})
        self.ok("feature", "add", stdin={"slug": "a-one"})
        self.ok("feature", "add", stdin={"slug": "c-done"})
        self.ok("feature", "set-state", "c-done", "Closed", "--note", "n")
        got = json.loads(self.ok("stats", "--json"))
        self.assertIn("features 2 open", got["line"])
        self.assertEqual(got["open_features"], [{"slug": "a-one", "cp": None, "next_step": None},
                                                {"slug": "b-two", "cp": "build", "next_step": "review"}])

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
                (self.wf / "features").mkdir(parents=True, exist_ok=True)
                (self.wf / "features" / "x.md").write_text("# x\n", encoding="utf-8")
                r = self.cli(script, "csv", "add", "log", "--feature", "x", stdin=b'{"agent": "a"}')
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn(b"write refused", r.stderr)
                self.assertIn(b"write refused", self.cli(script, "migrate", "--from-md", "--dry-run").stderr)
        self.assertFalse((self.wf / "backlog.jsonl").exists())
        self.assertFalse((self.wf / "features" / "x").exists())

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
        self.assertIn("1 event(s) refused", self.no("ledger", "add", "--json", stdin=[{"key": "k", "counter": "qa"}], code=4))
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


# ---------------------------------------------------------------- feature CSV tables

ROW = {
    "log": {"agent": "general-purpose (T1)", "lane": "serial", "changed": "`a.py`, `b.py`", "verified": "tests 12 OK", "attempts": "1/4", "limitations": "none"},
    "tests": {"criterion": "AC1", "test_id": "`test_a.py`", "mode": "automated", "owner": "qa-automation-engineer", "last_result": "12 OK"},
    "decisions": {"date": "2026-11-05", "kind": "decision", "decision": "CP2 approved", "cost": "one review round"},
    "limitations": {"date": "2026-11-05", "text": "Python 3.10 runtime not run", "accepted_by": "main GD"},
    "debt": {"date": "2026-11-05", "kind": "workaround", "text": "Retry twice on a timeout", "source": "BUG-0003", "accepted_by": "main GD",
             "next_step": "a backoff policy", "state": "Open"},
    "notes": {"date": "2026-11-05", "topic": "Save slots", "text": "Slot 3 races the autosave", "anchor": "Save.cs:41", "state": "Open"},
}
FILES = {"log": ".workflow/features/shop/log.csv", "tests": ".workflow/features/shop/tests.csv",
         "decisions": ".workflow/features/shop/decisions.csv", "limitations": ".workflow/features/shop/limitations.csv",
         "debt": "Assets/Shop/DEBT.csv", "notes": "Assets/Shop/NOTES.csv"}


class CsvBase(Base):
    slug = "shop"

    def register(self, slug=None, root="Assets/Shop", **over):
        d = {"slug": slug or self.slug, "size": "M"}
        if root:
            d["feature_root"] = root
        d.update(over)
        return self.ok("feature", "add", stdin=d)

    def csv(self, *argv, feature=None, **kw):
        return self.ok("csv", *argv, "--feature", feature or self.slug, **kw)

    def csv_no(self, *argv, feature=None, **kw):
        return self.no("csv", *argv, "--feature", feature or self.slug, **kw)

    def rows(self, table, feature=None):
        return json.loads(self.csv("list", table, "--json", feature=feature))

    def path(self, table):
        return self.root / FILES[table]


class TestCsvTables(CsvBase):
    def test_every_table_add_update_list_render(self):
        self.register()
        for name, table in records.TABLES.items():
            with self.subTest(table=name):
                rid = self.csv("add", name, stdin=ROW[name]).strip()
                self.assertEqual(rid, table.fmt_id(1))
                self.assertEqual(self.csv("add", name, stdin=ROW[name]).strip(), table.fmt_id(2))
                raw = self.path(name).read_bytes()
                self.assertTrue(raw.startswith(",".join(table.columns).encode() + b"\n"))
                self.assertNotIn(b"\r", raw)
                self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
                field = "text" if "text" in table.fields else table.fields[-1]
                self.assertIn("updated: %s" % field, self.csv("update", name, rid, stdin={field: "changed value"}))
                self.assertIn("no change", self.csv("update", name, rid, stdin={field: "changed value"}))
                got = self.rows(name)
                self.assertEqual(got[0], dict(ROW[name], id=rid, **{field: "changed value"}, **({"mirrored": ""} if name == "limitations" else {})))
                self.assertEqual(len(got), 2)
                lines = self.csv("render", name).splitlines()
                self.assertEqual(lines[0], "| %s |" % " | ".join(table.labels))
                self.assertEqual(lines[1], "|%s|" % "|".join("---" for _ in table.labels))
                self.assertEqual(lines[2], "| %s |" % " | ".join(got[0][c] for c in table.columns))
                self.assertIn(rid, self.csv("list", name))

    def test_add_defaults_and_choices(self):
        self.register()
        self.csv("add", "decisions", stdin={"decision": "Gates: review yes"})
        self.assertEqual(self.rows("decisions")[0], {"id": "D-001", "date": "2026-01-01", "kind": "decision", "decision": "Gates: review yes", "cost": ""})
        self.csv("add", "debt", stdin={"kind": "limitation", "text": "No offline queue"})
        self.assertEqual(self.rows("debt")[0]["state"], "Open")
        self.assertIn("kind: required", self.csv_no("add", "debt", stdin={"text": "t"}))
        self.assertIn("kind: must be one of", self.csv_no("add", "decisions", stdin={"kind": "vote", "decision": "x"}))
        self.assertIn("state: must be one of", self.csv_no("add", "debt", stdin={"kind": "limitation", "text": "t", "state": "Closed"}))
        self.assertIn("date: expected YYYY-MM-DD", self.csv_no("add", "decisions", stdin={"decision": "a", "date": "x"}))
        self.assertIn("unknown field", self.csv_no("add", "log", stdin={"agent": "a", "severity": "High"}))
        self.assertIn("date: expected YYYY-MM-DD", self.csv_no("add", "limitations", stdin={"text": "t", "date": "2026-02-30"}))
        self.assertIn("id: assigned", self.csv_no("add", "log", stdin={"id": "L-009", "agent": "a"}))
        self.assertIn("agent: required", self.csv_no("add", "log", stdin={"lane": "serial"}))
        self.assertIn("source: expected", self.csv_no("add", "debt", stdin={"kind": "limitation", "text": "t", "source": "Some Feature"}))
        self.assertIn("set by csv mirror", self.csv_no("add", "limitations", stdin={"text": "t", "mirrored": "DEBT-001"}))
        self.assertIn("state: expected Open, Debt or Promoted", self.csv_no("add", "notes", stdin={"text": "t", "state": "Done"}))
        self.csv("add", "notes", stdin={"text": "t", "state": "Promoted:CONTRACTS.md"})
        self.assertIn("not found", self.csv_no("update", "log", "L-001", stdin={"agent": "b"}))
        self.assertIn("id: never updated", self.csv_no("update", "debt", "DEBT-001", stdin={"id": "DEBT-002"}))
        self.assertIn("set by csv mirror", self.csv_no("update", "limitations", "LIM-001", stdin={"mirrored": "x"}))

    def test_quoting_round_trips_and_a_line_break_is_refused(self):
        self.register()
        value = 'a, "quoted" b | pipe'
        self.csv("add", "log", stdin={"agent": "main session", "changed": value})
        self.assertIn(b'"a, ""quoted"" b | pipe"', self.path("log").read_bytes())
        self.assertEqual(self.rows("log")[0]["changed"], value)
        self.assertIn("a, \"quoted\" b \\| pipe", self.csv("render", "log"))
        for bad in ("a\nb", "a\r\nb", "a b"):
            self.assertIn("must be one line", self.csv_no("add", "log", stdin={"agent": "x", "verified": bad}))
        self.assertEqual(len(self.rows("log")), 1)

    def test_the_value_limit_is_1000_and_refuses_not_truncates(self):
        self.register()
        self.csv("add", "limitations", stdin={"text": "x" * 1000})
        self.assertIn("text: 1001 chars, limit 1000", self.csv_no("add", "limitations", stdin={"text": "x" * 1001}))
        self.assertEqual(len(self.rows("limitations")), 1)

    def test_secret_vietnamese_and_pii(self):
        self.register()
        code, out, err = self.run_cli("csv", "add", "decisions", "--feature", "shop", stdin={"decision": "key %s here" % FAKE_KEY})
        self.assertEqual(code, 1)
        self.assertIn("secret-shaped value in decision", err)
        self.assertNotIn(FAKE_KEY, out + err)
        self.assertIn("Vietnamese diacritics", self.csv_no("add", "decisions", stdin={"decision": "Bạn chọn"}))
        self.assertIn("control character", self.csv_no("add", "log", stdin={"agent": "a\x07b"}))
        self.assertFalse(self.path("decisions").exists())  # never a header-only file
        code, out, err = self.run_cli("csv", "add", "log", "--feature", "shop", stdin={"agent": "QA", "verified": "mail %s" % EMAIL})
        self.assertEqual(code, 0, err)
        self.assertIn("redacted PII in: verified", err)
        self.assertNotIn(EMAIL.encode(), self.path("log").read_bytes())

    def test_root_tables_need_a_feature_root_and_feature_tables_a_known_feature(self):
        err = self.csv_no("add", "debt", stdin=ROW["debt"])
        self.assertIn("not in the registry", err)
        self.assertIn("feature add", err)
        self.register(root=None)
        err = self.csv_no("add", "notes", stdin=ROW["notes"])
        self.assertIn("has no feature_root", err)
        self.assertIn("feature update shop", err)
        self.assertIn("no registry row and no .workflow/features/nope.md", self.csv_no("add", "log", stdin=ROW["log"], feature="nope"))
        (self.wf / "features").mkdir(parents=True, exist_ok=True)
        (self.wf / "features" / "md-only.md").write_text("# x\n", encoding="utf-8")
        self.csv("add", "log", stdin=ROW["log"], feature="md-only")
        self.assertIn("bad slug", self.csv_no("add", "log", stdin=ROW["log"], feature="../up"))
        self.ok("feature", "update", "shop", stdin={"feature_root": "../outside"})
        self.assertIn("expected a folder relative", self.csv_no("add", "debt", stdin=ROW["debt"]))
        self.ok("feature", "update", "shop", stdin={"feature_root": "`Assets/Shop/`"})
        self.csv("add", "debt", stdin=ROW["debt"])
        self.assertTrue((self.root / "Assets" / "Shop" / "DEBT.csv").exists())

    def test_journal_kinds_go_through_the_feature_commands(self):
        self.register()
        for kind in ("extra-round", "stop-rule"):
            err = self.csv_no("add", "decisions", stdin={"kind": kind, "decision": "review +1"})
            self.assertIn("use records.py feature %s" % kind, err)
        self.assertFalse(self.path("decisions").exists())
        self.assertIn("review 0/4", self.ok("feature", "extra-round", "shop", "review", "+1", "--note", "main GD order after round 3", "--by", "main GD"))
        self.ok("feature", "stop-rule", "shop", "qa", "--extra-dispatch", "unused", now="2026-01-02T00:00:00Z")
        self.assertEqual(self.rows("decisions"), [
            {"id": "D-001", "date": "2026-01-01", "kind": "extra-round", "decision": "review +1: main GD order after round 3", "cost": ""},
            {"id": "D-002", "date": "2026-01-02", "kind": "stop-rule", "decision": "qa root-caused · extra dispatch: unused", "cost": ""}])
        self.csv("add", "decisions", stdin={"decision": "CP2 approved"})
        self.assertIn("use records.py feature extra-round", self.csv_no("update", "decisions", "D-003", stdin={"kind": "extra-round"}))
        self.assertIn("use records.py feature stop-rule", self.csv_no("update", "decisions", "D-002", stdin={"kind": "decision"}))
        self.csv("update", "decisions", "D-001", stdin={"cost": "one narrow review"})
        # A hand-written extra-round row is never counted: the journal is the counters' only source.
        with open(self.path("decisions"), "ab") as f:
            f.write(b"D-004,2026-01-03,extra-round,review +9: forged,\n")
        c = json.loads(self.ok("feature", "counters", "shop", "--json"))
        self.assertEqual(c["review"]["cap"], 4)
        self.assertEqual(c["record"].split("\n"), ["- Stop rule: qa root-caused 2026-01-02 · extra dispatch: unused", "extra round: review +1"])

    def test_a_broken_decisions_file_refuses_before_the_journal_write(self):
        self.register()
        self.path("decisions").parent.mkdir(parents=True, exist_ok=True)
        self.path("decisions").write_bytes(b"id,date,kind,decision,cost\nD-001,2026-01-01,decision\n")
        before = (self.wf / "features.jsonl").read_bytes()
        self.assertIn("3 values, expected 5", self.no("feature", "extra-round", "shop", "qa", "+1", "--note", "o", "--by", "main GD"))
        self.assertIn("3 values, expected 5", self.no("feature", "stop-rule", "shop", "qa", "--extra-dispatch", "used"))
        self.assertEqual((self.wf / "features.jsonl").read_bytes(), before)
        self.assertEqual(list(self.path("decisions").parent.glob(".*.tmp")), [])

    def test_a_failed_move_in_leaves_the_journal_right_and_names_the_repair(self):
        self.register()
        with mock.patch.object(records.Pending, "commit", side_effect=OSError("disk full")):
            err = self.no("feature", "extra-round", "shop", "review", "+1", "--note", "order", "--by", "main GD")
        self.assertIn("counters are right", err)
        self.assertIn("csv add decisions --feature shop", err)
        self.assertEqual(json.loads(self.ok("feature", "counters", "shop"))["review"]["cap"], 4)


class TestCsvDoctor(CsvBase):
    def write(self, table, data: bytes):
        p = self.path(table)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return p

    def test_crlf_and_bom_are_reported_and_normalized(self):
        self.register()
        p = self.write("log", b"\xef\xbb\xbfid,agent,lane,changed,verified,attempts,limitations\r\nL-001,QA,serial,\"a, b\",ok,1/1,none\r\n")
        err = self.csv_no("doctor", "log")
        self.assertIn("UTF-8 BOM", err)
        self.assertIn("CRLF line endings", err)
        self.assertIn("csv doctor: clean (log)", self.csv("doctor", "log", "--fix"))
        self.assertEqual(p.read_bytes(), b'id,agent,lane,changed,verified,attempts,limitations\nL-001,QA,serial,"a, b",ok,1/1,none\n')

    def test_malformed_rows_are_reported_for_a_hand_fix_and_kept(self):
        self.register()
        body = (b"id,agent,lane,changed,verified,attempts,limitations\nL-001,QA,serial\nL-002,QA,serial,\"a\nb\",ok,1,none\n"
                b"X-9,QA,,,,,\nL-003,QA,,key " + FAKE_KEY.encode() + b",,,\nL-004, QA,,,,,\n")
        p = self.write("log", body)
        code, out, err = self.run_cli("csv", "doctor", "log", "--feature", "shop", "--fix")
        self.assertEqual(code, 1)
        for want in ("line 2: 3 values, expected 7", "line 3: a line break in changed", "line 5: bad id", "line 6: refused: secret-shaped value in changed",
                     "line 7: agent is not in its stored form"):
            self.assertIn(want, err)
        self.assertNotIn(FAKE_KEY, out + err)
        self.assertEqual(p.read_bytes(), body)  # nothing to repair, nothing rewritten
        self.assertIn("writes refused", self.csv_no("add", "log", stdin=ROW["log"]))
        self.write("log", b"id,agent\nL-001,QA\n")
        self.assertIn("header is", self.csv_no("doctor", "log"))
        self.assertIn("header is", self.csv_no("list", "log"))

    def test_header_only_and_empty_files_are_reported_and_deleted_by_fix(self):
        self.register()
        p = self.write("tests", b"id,criterion,test_id,mode,owner,last_result\n")
        self.assertIn("header-only file", self.csv_no("doctor", "tests"))
        self.assertIn("deleted, it held no rows", self.csv("doctor", "tests", "--fix"))
        self.assertFalse(p.exists())
        self.assertIn("csv doctor: clean", self.csv("doctor"))  # every table, absent files included

    def test_doctor_skips_root_tables_without_a_feature_root(self):
        self.register(root=None)
        out = self.csv("doctor")
        self.assertIn("DEBT.csv: skipped", out)
        self.assertIn("csv doctor: clean (log, tests, decisions, limitations)", out)


class TestCsvMerge(GitBase):
    def setUp(self):
        super().setUp()
        (self.root / ".gitattributes").write_text(".workflow/*.jsonl text eol=lf merge=union\n*.csv text eol=lf merge=union\n", encoding="utf-8")
        self.ok("feature", "add", stdin={"slug": "shop", "size": "M", "feature_root": "Assets/Shop"})
        self.commit("setup")

    def add(self, table, **row):
        return self.ok("csv", "add", table, "--feature", "shop", stdin=row).strip()

    def test_union_merge_of_two_branches_appending_rows_then_doctor_fix(self):
        self.assertEqual(self.add("log", agent="git-expert"), "L-001")
        self.commit("one row")
        git(self.root, "switch", "-q", "-c", "b")
        self.assertEqual(self.add("log", agent="B side"), "L-002")
        self.commit("b")
        git(self.root, "switch", "-q", "main")
        self.assertEqual(self.add("log", agent="Main side"), "L-002")
        self.commit("main")
        r = git(self.root, "merge", "-q", "--no-edit", "b", check=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        err = self.no("csv", "doctor", "log", "--feature", "shop")
        self.assertIn("duplicate id L-002 on lines 3, 4", err)
        self.assertIn("duplicate id L-002", self.no("csv", "update", "log", "L-002", "--feature", "shop", stdin={"lane": "serial"}))
        self.assertEqual(self.add("log", agent="after merge"), "L-003")  # an add is not blocked by a duplicate
        out = self.ok("csv", "doctor", "log", "--feature", "shop", "--fix")
        self.assertIn("line 4: renumbered L-002 to L-004", out)
        rows = json.loads(self.ok("csv", "list", "log", "--feature", "shop", "--json"))
        self.assertEqual([(r["id"], r["agent"]) for r in rows], [("L-001", "git-expert"), ("L-002", "Main side"), ("L-004", "B side"), ("L-003", "after merge")])
        self.assertIn("csv doctor: clean", self.ok("csv", "doctor", "--feature", "shop"))
        self.assertEqual(self.add("log", agent="next"), "L-005")

    def test_two_branches_creating_one_file_leave_a_header_row_that_fix_drops(self):
        git(self.root, "switch", "-q", "-c", "b")
        self.add("notes", text="B note")
        self.commit("b")
        git(self.root, "switch", "-q", "main")
        self.add("notes", text="Main note")
        self.commit("main")
        r = git(self.root, "merge", "-q", "--no-edit", "b", check=False)
        notes = self.root / "Assets" / "Shop" / "NOTES.csv"
        if r.returncode:  # a git that does not union an add/add: build what a union would leave
            git(self.root, "merge", "--abort", check=False)
            notes.write_bytes(b"id,date,topic,text,anchor,state\nN-001,2026-01-01,,Main note,,Open\nid,date,topic,text,anchor,state\nN-001,2026-01-01,,B note,,Open\n")
        err = self.no("csv", "doctor", "notes", "--feature", "shop")
        self.assertIn("duplicate id N-001", err)
        out = self.ok("csv", "doctor", "notes", "--feature", "shop", "--fix")
        self.assertIn("renumbered N-001 to N-002", out)
        self.assertEqual(notes.read_bytes().count(b"id,date"), 1)
        self.assertEqual(sorted(r["text"] for r in json.loads(self.ok("csv", "list", "notes", "--feature", "shop", "--json"))), ["B note", "Main note"])

    def test_writes_from_a_linked_worktree_are_refused(self):
        wt = Path(self.tmp) / "wt"
        git(self.root, "worktree", "add", "-q", str(wt), "-b", "lane")
        self.assertIn("linked worktree", self.no("csv", "add", "log", "--feature", "shop", stdin={"agent": "x"}, root=wt))
        self.assertIn("linked worktree", self.no("csv", "mirror", "--feature", "shop", root=wt))
        self.assertIn("linked worktree", self.no("csv", "doctor", "--feature", "shop", "--fix", root=wt))
        self.assertIn("linked worktree", self.no("migrate", "--from-md", root=wt))
        (self.wf / "DEBT.md").write_text("- BUG-0001: a gap.\n", encoding="utf-8")
        self.assertIn(".workflow/DEBT.md: 1 bullets -> debt", self.ok("migrate", "--from-md", "--dry-run", root=wt))  # the main checkout's data
        self.assertFalse((self.wf / "debt.jsonl").exists())
        self.assertFalse((wt / ".workflow" / "features").exists())


class TestCsvMirror(CsvBase):
    def test_mirror_copies_unmirrored_limitations_once(self):
        self.register()
        self.csv("add", "limitations", stdin={"date": "2026-11-05", "text": "No offline queue", "accepted_by": "main GD"})
        self.csv("add", "limitations", stdin={"text": "Python 3.10 not run", "accepted_by": "main GD"})
        self.csv("add", "debt", stdin=ROW["debt"])
        out = self.csv("mirror")
        self.assertIn("mirrored 2 limitation(s) into Assets/Shop/DEBT.csv: LIM-001 -> DEBT-002, LIM-002 -> DEBT-003", out)
        debt = self.rows("debt")
        self.assertEqual(debt[1], {"id": "DEBT-002", "date": "2026-11-05", "kind": "accepted-gap", "text": "No offline queue", "source": "shop",
                                   "accepted_by": "main GD", "next_step": "", "state": "Open"})
        self.assertEqual([r["mirrored"] for r in self.rows("limitations")], ["DEBT-002", "DEBT-003"])
        self.assertIn("nothing to mirror", self.csv("mirror"))
        self.assertEqual(len(self.rows("debt")), 3)
        # A run cut short after DEBT.csv was written: the next run reuses the row, never copies it twice.
        p = self.path("limitations")
        p.write_bytes(p.read_bytes().replace(b",DEBT-003\n", b",\n"))
        self.assertIn("LIM-002 -> DEBT-003", self.csv("mirror"))
        self.assertEqual(len(self.rows("debt")), 3)
        self.csv("add", "limitations", stdin={"text": "Third", "accepted_by": "main GD"})
        self.assertIn("LIM-003 -> DEBT-004", self.csv("mirror"))

    def test_mirror_needs_a_feature_root(self):
        self.register(root=None)
        self.csv("add", "limitations", stdin={"text": "t"})
        self.assertIn("has no feature_root", self.csv_no("mirror"))


# ---------------------------------------------------------------- migrate --from-md

FW_MD = """# Framework backlog

Open work on the agent framework.

| Item | State |
|---|---|
| **Hook misfires** on a `-C` path | Open |
| Fix the gate \\| pipe inside | Done: `23f75ce` |
| Allowed tools list no shell | Recorded: allowed-tools only pre-approves |
| Pilot v2 | Recorded (GD decision) |

### Zero-Mem known limitations (GD-accepted 2026-10-28)
- Python runtime untested.

## Pre-slim history

| Item | State |
|---|---|
| Old row | Awaiting GD |

## Deferred and recorded

| Item | State |
|---|---|
| **Enforcement is advisory.** Deferred until a miss | Deferred |
| Native git hooks | Open |
"""

DEBT_MD = """# Debt\r
\r
No-feature and framework debt. Each line mirrors a bug the main GD accepted.\r
\r
- BUG-0006: secret gates pass hidden forms. Next: native git hooks, framework backlog.\r
- alpha-feature (closed 2026-11-06, main GD accepted): AC10 pilot not run. Next: run it on the test game.\r
- alpha-feature: advisory store is per machine.\r
- Hooks trust a cached interpreter path.\r
"""

BACKLOG_MD = """# Backlog

| # | Feature | Milestone | Size | Risk | Depends on | Status |
|---|---|---|---|---|---|---|
| 1 | Core loop | M1 | M | - | - | done |
| 2 | Shop | M1 | S | real-money IAP | 1 | in progress (`/feature shop`) |
"""

ALPHA_MD = """# Alpha feature

- Status: Closed
- CP: CP4 — closed 2026-11-06; next step: git-expert merges into develop
- Session: s-1 · 2026-11-05
- Size: L · Risk flag: no
- Rounds: review 0/3 (+1 extra round) · QA 0/2 · rework 1/8 (file count)
- Profile: n/a
- Feature root: `Assets/_Project/Scripts/Alpha/`
- Branch: feature/alpha-feature · Base: develop @ e4a7fae
- Assemblies: none
- Build mode: serial
- Worktrees: none

## Request (verbatim)
> make the alpha feature

## Main GD decisions
- 2026-11-05 CP1: n/a, direction given.
- 2026-11-06 extra round: review +1. Main GD's order after round 3; cost: one narrow review.

- 2026-11-06 CP4: closed, gaps accepted.

## Spec
`docs/alpha.md`

### Acceptance criteria
- AC1 Works.

## Log
| # | Agent | Lane | Changed | Verified | Attempts n/N | Limitations / Needs main GD |
|---|---|---|---|---|---|---|
| 1 | git-expert | serial | branch at `abc1234` | `git branch` | 1/1 | none |
| 2 | general-purpose (T1) | serial | `a.py`, `b.py` \\| two files | tests 12 OK | 1/4 | Commit made |

| 3 | code-reviewer | parallel | none | Approve | 1 | Lows fixed |

## Tests
| Criterion | Test id | Mode | Owner | Last result |
|---|---|---|---|---|
| AC1 | `test_alpha.py` | automated | qa-automation-engineer | 12 OK |

## Bugs
| ID | Title | Priority |
|---|---|---|
| BUG-0009 | Something | Medium |

## Known limitations
- `check.py` fails closed on purpose, by design.
- Token cost per run not measured.

- Stop rule: check.py (same cause, review rounds 1 and 2) root-caused 2026-11-06 by technical-architect: redesigned · extra dispatch: used (main session)

<!-- a comment kept verbatim -->
"""

ALPHA_AFTER = """# Alpha feature

- State: records.py feature show alpha-feature

## Request (verbatim)
> make the alpha feature

## Main GD decisions

- Rows: records.py csv render decisions --feature alpha-feature

## Spec
`docs/alpha.md`

### Acceptance criteria
- AC1 Works.

## Log

- Rows: records.py csv render log --feature alpha-feature

## Tests

- Rows: records.py csv render tests --feature alpha-feature

## Bugs

- Bugs: bugs.py list --feature alpha-feature

## Known limitations

- Rows: records.py csv render limitations --feature alpha-feature

<!-- a comment kept verbatim -->
"""

BETA_MD = """# Beta feature

- Status: Open
- CP: build — next step: T2 attempt 1/4
- Size: M · Risk flag: save-data migration
- Rounds: review 1/5 · QA 0/2 · rework 2/6
- Feature root: `Assets/_Project/Scripts/Beta/`
- Branch: feature/beta-feature · Base: develop

## Request (verbatim)
> beta

## GD decisions
- 2026-11-07 extra round: review +2 (cap 3 to 5). Cost stated: two more review rounds.
- Accepted without a date: a waiver of AC3.

## Known limitations
- 2026-11-08 Python 3.10 runtime not run.

- Stop rule: qa root-caused 2026-11-08 · extra dispatch: unused
"""

BETA_DEBT_MD = """# Beta debt

- Workaround: the shop retries twice on a timeout. Next: a backoff policy.
- 2026-11-08 Accepted gap: BUG-0012: no offline queue.
- Coins can go negative for one frame.
"""

BETA_NOTES_MD = """# Notes
- **Save slots**: overwriting slot 3 during autosave races the writer.
- A plain observation.
"""

ROUNDS_JSON = {"feature:alpha-feature": {"review": ["round-1", "round-2"], "qa": ["q1"]}, "target:abc": {"extra-review": "gd-1"}}


class MigrateBase(Base):
    def fixture(self, **over):
        files = {".workflow/framework-backlog.md": FW_MD, ".workflow/DEBT.md": DEBT_MD, ".workflow/backlog.md": BACKLOG_MD,
                 ".workflow/features/alpha-feature.md": ALPHA_MD.replace("\n", "\r\n"), ".workflow/features/alpha-feature.spec.md": "# spec\n",
                 ".workflow/features/beta-feature.md": BETA_MD, "Assets/_Project/Scripts/Beta/DEBT.md": BETA_DEBT_MD,
                 "Assets/_Project/Scripts/Beta/NOTES.md": BETA_NOTES_MD, ".workflow/rounds.json": json.dumps(ROUNDS_JSON)}
        files.update(over)
        for rel, text in files.items():
            if text is None:
                (self.root / rel).unlink(missing_ok=True)
                continue
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(text.encode("utf-8"))

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in sorted(self.root.rglob("*")) if p.is_file() and ".git" not in p.parts}

    def rows(self, table, slug):
        return json.loads(self.ok("csv", "list", table, "--feature", slug, "--json"))


class TestMigrate(MigrateBase):
    def test_dry_run_reports_counts_and_writes_nothing(self):
        self.fixture()
        before = self.snapshot()
        out = self.ok("migrate", "--from-md", "--dry-run")
        self.assertEqual(self.snapshot(), before)
        for want in (".workflow/framework-backlog.md: 6 rows -> fwbacklog; 1 table rows in other sections kept",
                     ".workflow/backlog.md: 2 rows -> backlog; 1 status suffix(es)",
                     ".workflow/DEBT.md: 4 bullets -> debt; 2 other lines kept",
                     ".workflow/features/alpha-feature.md: registry 1 (Closed) · decisions 4 · log 3 · tests 1 · limitations 2 · journal round 1, extra_round 1, stop_rule 1 · 1 other lines kept",
                     ".workflow/features/beta-feature.md: registry 1 (Open) · decisions 3 · log 0 · tests 0 · limitations 1 · journal round 2, extra_round 1, stop_rule 1",
                     "Assets/_Project/Scripts/Beta/DEBT.md: 3 bullets -> Assets/_Project/Scripts/Beta/DEBT.csv",
                     "Assets/_Project/Scripts/Beta/NOTES.md: 2 bullets -> Assets/_Project/Scripts/Beta/NOTES.csv",
                     ".workflow/rounds.json: 4 events", "counters equal for 1 open feature(s)", "dry run: nothing written"):
            self.assertIn(want, out)

    def test_migrate_converts_every_source_and_keeps_the_counters(self):
        self.fixture()
        out = self.ok("migrate", "--from-md")
        self.assertIn("wrote", out)
        # framework backlog: both tables, in order; state cells split into state and ref
        self.assertEqual([(r["id"], r["item"], r["state"], r["ref"]) for r in json.loads(self.ok("fwbacklog", "list", "--json"))], [
            ("FW-0001", "**Hook misfires** on a `-C` path", "Open", None), ("FW-0002", "Fix the gate | pipe inside", "Done", "`23f75ce`"),
            ("FW-0003", "Allowed tools list no shell", "Recorded", "allowed-tools only pre-approves"),
            ("FW-0004", "Pilot v2", "Recorded (main GD decision)", None),
            ("FW-0005", "**Enforcement is advisory.** Deferred until a miss", "Deferred", None), ("FW-0006", "Native git hooks", "Open", None)])
        self.assertEqual([(r["id"], r["feature"], r["status"], r["depends_on"]) for r in json.loads(self.ok("backlog", "list", "--json"))],
                         [("BL-0001", "Core loop", "done", None), ("BL-0002", "Shop", "in progress", "1")])
        debt = json.loads(self.ok("debt", "list", "--json"))
        self.assertEqual([(r["source"], r["text"], r["next_step"], r["date"]) for r in debt], [
            ("BUG-0006", "secret gates pass hidden forms.", "native git hooks, framework backlog.", "2026-01-01"),
            ("alpha-feature", "(closed 2026-11-06, main GD accepted) AC10 pilot not run.", "run it on the test game.", "2026-11-06"),
            ("alpha-feature", "advisory store is per machine.", None, "2026-01-01"),
            ("framework", "Hooks trust a cached interpreter path.", None, "2026-01-01")])
        # registry
        a = self.show("feature", "alpha-feature")
        self.assertEqual({k: a[k] for k in ("status", "cp", "next_step", "session", "size", "risk", "profile", "feature_root", "branch", "base",
                                             "assemblies", "build_mode", "worktrees")},
                         {"status": "Closed", "cp": "CP4", "next_step": "closed 2026-11-06; next step: git-expert merges into develop",
                          "session": "s-1 · 2026-11-05", "size": "L", "risk": "no", "profile": "n/a", "feature_root": "Assets/_Project/Scripts/Alpha/",
                          "branch": "feature/alpha-feature", "base": "develop @ e4a7fae", "assemblies": "none", "build_mode": "serial", "worktrees": "none"})
        b = self.show("feature", "beta-feature")
        self.assertEqual((b["cp"], b["next_step"], b["risk"]), ("build", "T2 attempt 1/4", "save-data migration"))
        # counters: what the hook read from the md before equals what counters returns now
        c = json.loads(self.ok("feature", "counters", "beta-feature", "--json"))
        self.assertEqual((c["review"], c["qa"], c["rework"]), ({"used": 1, "cap": 5}, {"used": 0, "cap": 2}, {"used": 2, "cap": 6}))
        self.assertEqual(c["record"], "- Stop rule: qa root-caused 2026-11-08 · extra dispatch: unused\nextra round: review +2")
        a = json.loads(self.ok("feature", "counters", "alpha-feature", "--json"))
        self.assertEqual((a["open"], a["review"]["cap"], a["rework"]["used"]), (False, 4, 1))
        self.assertIn("- Stop rule: review root-caused 2026-11-06 · extra dispatch: used", a["record"])
        # the feature CSVs
        self.assertEqual(self.rows("decisions", "alpha-feature"), [
            {"id": "D-001", "date": "2026-11-05", "kind": "decision", "decision": "CP1: n/a, direction given.", "cost": ""},
            {"id": "D-002", "date": "2026-11-06", "kind": "extra-round", "decision": "extra round: review +1. Main GD's order after round 3; cost: one narrow review.", "cost": ""},
            {"id": "D-003", "date": "2026-11-06", "kind": "decision", "decision": "CP4: closed, gaps accepted.", "cost": ""},
            {"id": "D-004", "date": "2026-11-06", "kind": "stop-rule", "cost": "",
             "decision": "Stop rule: check.py (same cause, review rounds 1 and 2) root-caused 2026-11-06 by technical-architect: redesigned · extra dispatch: used (main session)"}])
        self.assertEqual(self.rows("decisions", "beta-feature")[1:], [
            {"id": "D-002", "date": "", "kind": "decision", "decision": "Accepted without a date: a waiver of AC3.", "cost": ""},
            {"id": "D-003", "date": "2026-11-08", "kind": "stop-rule", "decision": "Stop rule: qa root-caused 2026-11-08 · extra dispatch: unused", "cost": ""}])
        self.assertEqual(self.rows("log", "alpha-feature"), [
            {"id": "L-001", "agent": "git-expert", "lane": "serial", "changed": "branch at `abc1234`", "verified": "`git branch`", "attempts": "1/1", "limitations": "none"},
            {"id": "L-002", "agent": "general-purpose (T1)", "lane": "serial", "changed": "`a.py`, `b.py` | two files", "verified": "tests 12 OK", "attempts": "1/4", "limitations": "Commit made"},
            {"id": "L-003", "agent": "code-reviewer", "lane": "parallel", "changed": "none", "verified": "Approve", "attempts": "1", "limitations": "Lows fixed"}])
        self.assertEqual(self.rows("tests", "alpha-feature"), [{"id": "T-001", "criterion": "AC1", "test_id": "`test_alpha.py`", "mode": "automated",
                                                                "owner": "qa-automation-engineer", "last_result": "12 OK"}])
        self.assertEqual([(r["text"], r["mirrored"]) for r in self.rows("limitations", "alpha-feature")],
                         [("`check.py` fails closed on purpose, by design.", "pre-migration"), ("Token cost per run not measured.", "pre-migration")])
        self.assertEqual(self.rows("limitations", "beta-feature"), [{"id": "LIM-001", "date": "2026-11-08", "text": "Python 3.10 runtime not run.",
                                                                     "accepted_by": "main GD", "mirrored": ""}])
        self.assertEqual([(r["kind"], r["source"], r["text"], r["next_step"], r["accepted_by"]) for r in self.rows("debt", "beta-feature")], [
            ("workaround", "", "the shop retries twice on a timeout.", "a backoff policy.", ""),
            ("accepted-gap", "BUG-0012", "no offline queue.", "", "main GD"), ("limitation", "", "Coins can go negative for one frame.", "", "")])
        self.assertEqual([(r["topic"], r["text"]) for r in self.rows("notes", "beta-feature")],
                         [("Save slots", "overwriting slot 3 during autosave races the writer."), ("", "A plain observation.")])
        # the md files
        alpha = (self.wf / "features" / "alpha-feature.md").read_bytes()
        self.assertEqual(alpha, ALPHA_AFTER.replace("\n", "\r\n").encode("utf-8"))  # CRLF kept
        self.assertEqual((self.wf / "features" / "alpha-feature.spec.md").read_text(encoding="utf-8"), "# spec\n")
        self.assertIn("- Rows: records.py csv render decisions --feature beta-feature", (self.wf / "features" / "beta-feature.md").read_text(encoding="utf-8"))
        for old in (".workflow/framework-backlog.md", ".workflow/DEBT.md", ".workflow/backlog.md", ".workflow/rounds.json",
                    "Assets/_Project/Scripts/Beta/DEBT.md", "Assets/_Project/Scripts/Beta/NOTES.md"):
            self.assertFalse((self.root / old).exists(), old)
        self.assertEqual(len(list(self.wf.glob("framework-backlog.migrated-*.md"))), 1)
        self.assertEqual(len(list((self.root / "Assets/_Project/Scripts/Beta").glob("NOTES.migrated-*.md"))), 1)
        self.assertEqual(json.loads(self.ok("ledger", "get", "--json")),
                         {"feature:alpha-feature": {"review": ["round-1", "round-2"], "qa": ["q1"]}, "target:abc": {"extra-review": ["gd-1"]}})
        # a second run finds nothing left but the migrated feature files
        out = self.ok("migrate", "--from-md")
        self.assertIn("alpha-feature.md: already migrated, skipped", out)
        self.assertIn("framework-backlog.md: absent", out)
        self.assertEqual(len(json.loads(self.ok("fwbacklog", "list", "--json"))), 6)

    def test_counters_equal_before_and_after_for_an_open_feature(self):
        self.fixture()
        # What round-cap.ps1 computed from BETA_MD: review 1/5 (an extra round recorded), QA 0/2 stopped, rework 2/6.
        legacy = records.legacy_counters(BETA_MD.split("\n"), [s for s in records.md_sections(BETA_MD.split("\n"))
                                                               if s[0] is not None and BETA_MD.split("\n")[s[0]] == "## GD decisions"])
        self.assertEqual(legacy, {"open": True, "review": (1, 5, False), "qa": (0, 2, True), "rework": (2, 6, False)})
        self.ok("migrate", "--from-md")
        c = json.loads(self.ok("feature", "counters", "beta-feature", "--json"))
        for name in ("review", "qa", "rework"):
            stopped = bool(__import__("re").search(r"(?im)^- Stop rule:.*\b%s\b" % name, c["record"]))
            self.assertEqual((c[name]["used"], c[name]["cap"], stopped), legacy[name])

    def test_a_counter_that_would_change_refuses_the_whole_migrate(self):
        self.fixture(**{".workflow/features/beta-feature.md": BETA_MD.replace("review 1/5", "review 1/4")})
        before = self.snapshot()
        err = self.no("migrate", "--from-md")
        self.assertIn("beta-feature.md:6: verification: review counter would change from used 1, cap 4", err)
        self.assertEqual(self.snapshot(), before)

    def test_refusals_roll_back_everything_and_name_each_line(self):
        bad = BETA_MD.replace("a waiver of AC3.", "a waiver of AC3, key %s." % FAKE_KEY)
        self.fixture(**{".workflow/features/beta-feature.md": bad,
                        ".workflow/features/alpha-feature.md": ALPHA_MD.replace("Token cost per run", "Chi phí token").replace("\n", "\r\n")})
        before = self.snapshot()
        code, out, err = self.run_cli("migrate", "--from-md")
        self.assertEqual(code, 1)
        self.assertIn("migrate refused, nothing was changed: 2 line(s) to fix by hand", err)
        self.assertIn(".workflow/features/alpha-feature.md:50: text: Vietnamese diacritics", err)
        self.assertIn(".workflow/features/beta-feature.md:15: refused: secret-shaped value in decision", err)
        self.assertNotIn(FAKE_KEY, out + err)
        self.assertEqual(self.snapshot(), before)

    def test_a_failed_verification_rolls_back(self):
        self.fixture()
        before = self.snapshot()
        real = records.render_lines
        with mock.patch.object(records, "render_lines", lambda ctx, store: real(ctx, store)[:3] if store.name == "fwbacklog" else real(ctx, store)):
            err = self.no("migrate", "--from-md")
        self.assertIn("framework-backlog.md:8: verification: the fwbacklog render does not hold this row (FW-0002)", err)
        self.assertEqual(self.snapshot(), before)

    def test_a_busy_ledger_stops_the_swap_before_any_file(self):
        self.fixture()
        before = self.snapshot()
        with mock.patch.object(records, "ledger_write", side_effect=records.LedgerBusy()):
            self.assertIn("ledger busy", self.no("migrate", "--from-md"))
        self.assertEqual(self.snapshot(), before)

    def test_bad_source_shapes_are_refused(self):
        self.fixture(**{".workflow/framework-backlog.md": FW_MD.replace("| Open |\n| Fix", "| Started |\n| Fix"),
                        ".workflow/features/beta-feature.md": BETA_MD.replace("- Status: Open", "- Status: Paused")})
        err = self.no("migrate", "--from-md")
        self.assertIn("framework-backlog.md:7: state", err)
        self.assertIn("beta-feature.md:3: Status", err)
        self.fixture(**{".workflow/framework-backlog.md": None, ".workflow/features/beta-feature.md": BETA_MD})
        (self.wf / "features" / "alpha-feature.md").write_bytes(ALPHA_MD.replace("| Attempts n/N |", "| Severity |").encode())
        self.assertIn("alpha-feature.md:31: column", self.no("migrate", "--from-md"))

    def test_a_source_changed_during_the_run_refuses_the_swap(self):
        self.fixture()
        real = records.Migration.verify

        def verify_then_write(m):
            real(m)
            with open(self.wf / "DEBT.md", "ab") as f:  # another session's write, after the staging read
                f.write(b"- BUG-0099: late.\r\n")

        with mock.patch.object(records.Migration, "verify", verify_then_write):
            self.assertIn(".workflow/DEBT.md changed while the migration ran", self.no("migrate", "--from-md"))
        self.assertFalse((self.wf / "debt.jsonl").exists())
        self.assertTrue((self.wf / "rounds.json").exists())

    def test_a_source_that_is_not_utf8_is_named(self):
        self.fixture(**{".workflow/DEBT.md": None})
        (self.wf / "DEBT.md").write_bytes(b"# Debt\n- \xff bad\n")
        self.assertIn(".workflow/DEBT.md:2: not UTF-8", self.no("migrate", "--from-md", "--dry-run"))

    def test_nothing_to_migrate(self):
        out = self.ok("migrate", "--from-md")
        self.assertIn("framework-backlog.md: absent", out)
        self.assertIn("no feature files", out)
        self.assertIn("usage", self.no("migrate", code=2).lower())


# ---------------------------------------------------------------- ledger batches and the hook's budget

class TestLedgerBatch(Base):
    """One refused event never refuses its batch: the valid ones count, the refused ones wait in one rounds.rejected file."""

    LONG = "target:" + "a" * 300

    def get(self):
        return json.loads(self.ok("ledger", "get", "--json"))

    def park(self, name, body):
        self.wf.mkdir(parents=True, exist_ok=True)
        (self.wf / name).write_bytes(json.dumps(body).encode("utf-8"))
        return self.wf / name

    def rejected(self):
        return sorted(self.wf.glob("rounds.rejected-*.json"))

    def test_add_records_the_valid_events_and_keeps_the_refused_ones(self):
        code, out, err = self.run_cli("ledger", "add", "--json", stdin=[
            {"key": "feature:a", "counter": "review", "id": "r1"}, {"key": self.LONG, "counter": "review", "id": "r1"},
            {"key": "k", "counter": "qa"}, {"key": "feature:a", "counter": "qa", "id": "q1"}])
        self.assertEqual(code, 4, err)
        self.assertIn("ledger: 2 new", out)
        files = self.rejected()
        self.assertEqual(len(files), 1)
        self.assertIn("2 event(s) refused", err)
        self.assertIn(files[0].name, err)
        self.assertNotIn("a" * 41, err)  # the refused value is never echoed
        self.assertEqual(json.loads(files[0].read_bytes()), [{"key": self.LONG, "counter": "review", "id": "r1"}, {"key": "k", "counter": "qa"}])
        self.assertEqual(self.get(), {"feature:a": {"review": ["r1"], "qa": ["q1"]}})  # exit 0: a reject file blocks nothing
        self.assertEqual(records.ledger_marks(records.Ctx(str(self.root), use_git=False)), [])

    def test_a_refused_event_in_a_parked_file_does_not_poison_it(self):
        p = self.park("rounds.pending-20260101T000000000-aaaa.json",
                      [{"key": self.LONG, "counter": "review", "id": "round-1"}, {"key": "feature:a", "counter": "review", "id": "round-1"}])
        code, out, err = self.run_cli("ledger", "get", "--json")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out), {"feature:a": {"review": ["round-1"]}})
        self.assertIn("1 parked event(s) a write refuses are not counted", err)
        self.assertTrue(p.exists())  # get is read-only
        code, out, err = self.run_cli("ledger", "add", "--json", stdin=[{"key": "feature:a", "counter": "qa", "id": "q1"}])
        self.assertEqual(code, 0, err)  # the caller's own events were all valid
        self.assertFalse(p.exists())
        self.assertEqual(list(self.wf.glob("rounds.corrupt-*")), [])
        self.assertEqual(len(self.rejected()), 1)
        self.assertIn(self.rejected()[0].name, err)
        self.assertEqual(self.get(), {"feature:a": {"review": ["round-1"], "qa": ["q1"]}})

    def test_parked_and_stdin_refusals_share_one_reject_file(self):
        self.park("rounds.pending-20260101T000000000-bbbb.json", [{"key": self.LONG, "counter": "qa", "id": "x"}])
        self.park("rounds.pending-20260101T000000001-cccc.json", {"key": "k", "counter": "qa", "id": "y\nz"})
        code, _, err = self.run_cli("ledger", "add", "--json", stdin=[{"key": "k", "counter": "qa", "id": ""}])
        self.assertEqual(code, 4, err)
        self.assertEqual(len(self.rejected()), 1)
        self.assertEqual(len(json.loads(self.rejected()[0].read_bytes())), 3)
        self.assertEqual(list(self.wf.glob("rounds.pending-*")), [])

    def test_a_failed_reject_write_keeps_the_parked_file_for_the_next_add(self):
        p = self.park("rounds.pending-20260101T000000000-dddd.json",
                      [{"key": self.LONG, "counter": "qa", "id": "x"}, {"key": "k", "counter": "qa", "id": "good"}])
        with mock.patch.object(records, "save_rejected", side_effect=OSError("disk full")):
            self.no("ledger", "add", "--json", stdin=[{"key": "k", "counter": "qa", "id": "mine"}], code=1)
        self.assertTrue(p.exists())
        self.assertEqual(self.get(), {"k": {"qa": ["mine", "good"]}})  # committed once; the parked copy dedupes
        self.ok("ledger", "add", "--json", stdin=[])
        self.assertFalse(p.exists())
        self.assertEqual(len(self.rejected()), 1)
        self.assertEqual(self.get(), {"k": {"qa": ["mine", "good"]}})

    def test_rounds_json_with_a_refused_event_still_reads_and_migrates(self):
        self.park("rounds.json", {"feature:a": {"review": ["r1"]}, self.LONG: {"review": ["r2"]}})
        self.assertEqual(self.get(), {"feature:a": {"review": ["r1"]}})
        out = self.run_cli("ledger", "migrate")
        self.assertEqual(out[0], 0, out[2])
        self.assertIn("migrated 1 event(s) from rounds.json", out[1])
        self.assertEqual(len(self.rejected()), 1)
        self.assertEqual(self.get(), {"feature:a": {"review": ["r1"]}})
        with self.assertRaises(ValueError):  # migrate --from-md still refuses the source
            records.parse_rounds_json(json.dumps({self.LONG: {"review": ["r2"]}}).encode())

    def test_an_unparsable_parked_file_still_blocks(self):
        (self.wf).mkdir(parents=True, exist_ok=True)
        (self.wf / "rounds.pending-20260101T000000000-eeee.json").write_bytes(b"[{ broken")
        self.ok("ledger", "add", "--json", stdin=[{"key": "k", "counter": "qa", "id": "1"}])
        self.assertTrue((self.wf / "rounds.corrupt-pending-20260101T000000000-eeee.json").exists())
        self.no("ledger", "get", "--json", code=3)


class TestHookBudget(GitBase):
    """round-cap.ps1 starts one Python per registered-feature dispatch, and its reads never run git or wait long on a lock."""

    def setUp(self):
        super().setUp()
        self.ok("feature", "add", stdin={"slug": "demo", "size": "M"})
        self.ok("ledger", "add", "--json", stdin=[{"key": "feature:demo", "counter": "review", "id": "round-1"}])

    def test_counters_with_ledger_embeds_the_ledger_view(self):
        plain = json.loads(self.ok("feature", "counters", "demo", "--json"))
        both = json.loads(self.ok("feature", "counters", "demo", "--json", "--with-ledger"))
        self.assertNotIn("ledger", plain)
        self.assertEqual(both.pop("ledger"), json.loads(self.ok("ledger", "get", "--json")))
        self.assertEqual(both, plain)
        unknown = json.loads(self.ok("feature", "counters", "nope", "--json", "--with-ledger"))
        self.assertEqual((unknown["found"], unknown["ledger"]), (False, {"feature:demo": {"review": ["round-1"]}}))

    def test_with_ledger_exits_as_ledger_get_does(self):
        (self.wf / "rounds.corrupt-pending-x.json").write_bytes(b"[")
        self.assertIn("unreadable ledger file", self.no("feature", "counters", "demo", "--json", "--with-ledger", code=3))
        self.ok("feature", "counters", "demo", "--json")  # without the flag the ledger is not read
        (self.wf / "rounds.corrupt-pending-x.json").unlink()
        with mock.patch.object(records, "ledger_rows", side_effect=records.LedgerBusy()):
            self.assertIn("ledger busy past 2000 ms", self.no("feature", "counters", "demo", "--json", "--with-ledger", code=75))

    def test_the_hook_reads_never_run_git(self):
        with mock.patch.object(records, "run_git", wraps=records.run_git) as spy:
            self.ok("feature", "counters", "demo", "--json", "--with-ledger")
            self.ok("ledger", "get", "--json")
            self.ok("ledger", "add", "--json", stdin=[])
            self.assertEqual(spy.call_count, 0)
            self.ok("feature", "list")
            self.assertGreater(spy.call_count, 0)  # every other command keeps the git cross-check

    def test_the_hook_reads_wait_briefly_on_a_locked_cache(self):
        self.assertEqual((records.READ_BUSY_MS, records.journal.BUSY_SECONDS, records.LEDGER_BUSY_MS), (2000, 10, 5000))
        holder = sqlite3.connect(str(self.wf / "records.db"), isolation_level=None)
        try:
            holder.execute("BEGIN EXCLUSIVE")
            import time
            t0 = time.monotonic()
            self.assertIn("locked", self.no("feature", "counters", "demo", "--json", "--with-ledger", code=1))
            self.assertLess(time.monotonic() - t0, 5)  # READ_BUSY_MS, not the 10 s every other command waits
        finally:
            holder.execute("ROLLBACK")
            holder.close()
        self.ok("feature", "counters", "demo", "--json", "--with-ledger")


# ---------------------------------------------------------------- loading a framework script by path

class TestLoadByPath(Base):
    """journal.load_by_path: one sys.modules entry per name and file, no .pyc, nothing cached from a file that fails."""

    def setUp(self):
        super().setUp()
        self.name = "records_test_loaded_%s" % Path(self.tmp).name.replace("-", "_")
        self.addCleanup(sys.modules.pop, self.name, None)
        self.load = records.journal.load_by_path

    def script(self, text, name="mod.py"):
        path = Path(self.tmp) / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_a_second_load_of_the_same_file_is_the_cached_module(self):
        path = self.script("VALUE = object()\n")
        first = self.load(self.name, path)
        self.assertIs(sys.modules[self.name], first)
        self.assertIs(self.load(self.name, Path(self.tmp) / "." / "mod.py"), first)  # keyed by the resolved path
        self.assertFalse((Path(self.tmp) / "__pycache__").exists())

    def test_a_cached_entry_from_another_file_is_replaced(self):
        first = self.load(self.name, self.script("WHO = 'a'\n", "a.py"))
        second = self.load(self.name, self.script("WHO = 'b'\n", "b.py"))
        self.assertIsNot(first, second)
        self.assertEqual(second.WHO, "b")
        self.assertIs(sys.modules[self.name], second)

    def test_a_missing_file_refuses_and_names_it(self):
        path = Path(self.tmp) / "gone" / "mod.py"
        with self.assertRaises(records.Refused) as caught:
            self.load(self.name, path, " (skill test)")
        self.assertEqual(str(caught.exception), "%s is missing (skill test)" % path.resolve())
        self.assertNotIn(self.name, sys.modules)

    def test_a_file_that_fails_is_not_cached_and_the_bytecode_flag_is_restored(self):
        path = self.script("raise RuntimeError('broken')\n")
        for flag in (False, True):
            with self.subTest(dont_write_bytecode=flag), mock.patch.object(sys, "dont_write_bytecode", flag):
                with self.assertRaises(RuntimeError):
                    self.load(self.name, path)
                self.assertIs(sys.dont_write_bytecode, flag)
                self.assertNotIn(self.name, sys.modules)
        path.write_text("OK = 1\n", encoding="utf-8")
        with mock.patch.object(sys, "dont_write_bytecode", False):
            self.assertEqual(self.load(self.name, path).OK, 1)
            self.assertFalse(sys.dont_write_bytecode)

    def test_load_bugs_is_cached(self):
        self.addCleanup(sys.modules.pop, "records_bugs", None)
        bugs = records.load_bugs()
        self.assertIs(records.load_bugs(), bugs)
        self.assertIs(sys.modules["records_bugs"], bugs)
        self.assertIs(bugs.journal, records.journal)  # one engine, so one Refused class across both CLIs

    def test_a_broken_mem_module_refuses_every_write_without_a_traceback(self):
        for body in ("raise SystemExit(3)\n", "def broken(:\n", "# no API\n"):
            with self.subTest(body=body):
                shutil.rmtree(Path(self.tmp) / "framework", ignore_errors=True)
                script = TestFailClosed.copy(self)
                (script.parents[2] / "mem" / "scripts" / "mem.py").write_text(body, encoding="utf-8")
                r = TestFailClosed.cli(self, script, "backlog", "add", stdin=json.dumps(bl()).encode())
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn(b"write refused", r.stderr)
                self.assertIn(b"cannot be loaded", r.stderr)
                self.assertNotIn(b"Traceback", r.stderr)
                self.assertEqual(TestFailClosed.cli(self, script, "backlog", "list").returncode, 0)
        self.assertFalse((self.wf / "backlog.jsonl").exists())


GAMMA_MD = """# Gamma feature

- Status: Open
- Size: M
- Rounds: review 1/3 · QA 0/2 · rework 0/6

## Bugs
Found in QA round 1:
| ID | Title | Status |
|---|---|---|
| BUG-0001 | Crash on load | Fixed |
| BUG-0002 | Wrong label | Open |

## Notes
free text
"""

GAMMA_AFTER = """# Gamma feature

- State: records.py feature show gamma-feature

## Bugs

- Bugs: bugs.py list --feature gamma-feature

Found in QA round 1:

## Notes
free text
"""


class TestMigrateBugsSection(MigrateBase):
    def write(self, text):
        p = self.wf / "features" / "gamma-feature.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.encode("utf-8"))
        return p

    def test_the_bugs_table_is_dropped_and_its_other_lines_kept(self):
        p = self.write(GAMMA_MD)
        before = self.snapshot()
        out = self.ok("migrate", "--from-md", "--dry-run")
        self.assertEqual(self.snapshot(), before)
        self.assertIn(".workflow/features/gamma-feature.md: registry 1 (Open) · decisions 0 · log 0 · tests 0 · limitations 0 · "
                      "journal round 1, extra_round 0, stop_rule 0 · 1 other lines kept · bugs table rows dropped 2 (bugs.py holds them)", out)
        self.assertIn("counters equal for 1 open feature(s)", out)
        self.ok("migrate", "--from-md")
        self.assertEqual(p.read_bytes(), GAMMA_AFTER.encode("utf-8"))
        self.assertFalse((self.wf / "features" / "gamma-feature").exists())  # no CSV for the bugs table
        c = json.loads(self.ok("feature", "counters", "gamma-feature", "--json"))
        self.assertEqual((c["review"], c["qa"], c["rework"]), ({"used": 1, "cap": 3}, {"used": 0, "cap": 2}, {"used": 0, "cap": 6}))

    def test_a_bugs_section_without_a_table_gets_the_pointer_line(self):
        lines = GAMMA_MD.split("\n")
        p = self.write("\n".join(lines[:7] + ["No bugs filed."] + lines[12:]))
        out = self.ok("migrate", "--from-md")
        self.assertNotIn("bugs table rows dropped", out)
        self.assertEqual(p.read_bytes(), GAMMA_AFTER.replace("Found in QA round 1:", "No bugs filed.").encode("utf-8"))


class TestCsvFormulaPrefix(CsvBase):
    DASH = "-, which"  # any leading -, whatever follows it
    BAD = {"=1+1": "=", "+1": "+", "@SUM(A1)": "@", "\tnote": "a TAB", "\rnote": "a CR", "-1": DASH, "-x(": DASH,
           "  =trimmed": "=", "--1+cmd|' /C calc'!A0": DASH, "- 1+cmd|' /C calc'!A0": DASH, "-- cmd|' /C calc'!A0": DASH,
           "-1 HP": DASH, "- 1 item": DASH, "-": DASH, "--": DASH, "--Dry-run": DASH, "--dry-run|calc": DASH, "  -1 HP": DASH,
           "- a+cmd|' /C calc'!A0": DASH, "--flag|x": DASH, "--dry-run x|y": DASH, "  - a|b": DASH,
           "- fix the hook budget": DASH, "--dry-run": DASH, "--with-ledger used by round-cap": DASH, "- item": DASH,
           '- WEBSERVICE("https://host/?"&A2)': DASH, "--dry-run WEBSERVICE(x)": DASH}
    GOOD = ("plain text", "a = b", "e-mail @ desk", "use a|b pipe in the middle", "fix the hook budget - later",
            "Run --dry-run first")

    def test_each_prefix_is_refused_on_add_and_update(self):
        self.register()
        rid = self.csv("add", "log", stdin={"agent": "QA", "changed": "first"}).strip()
        before = self.path("log").read_bytes()
        for bad, lead in self.BAD.items():
            with self.subTest(value=bad):
                err = self.csv_no("add", "log", stdin={"agent": "QA", "changed": bad})
                self.assertIn("changed: starts with %s" % lead, err)
                self.assertIn("runs as a formula", err)
                err = self.csv_no("update", "log", rid, stdin={"changed": bad})
                self.assertIn("changed: starts with %s" % lead, err)
                self.assertIn("decision: starts with", self.csv_no("add", "decisions", stdin={"decision": bad}))
        self.assertEqual(self.path("log").read_bytes(), before)
        self.assertFalse(self.path("decisions").exists())

    def test_a_long_formula_is_never_echoed(self):
        self.register()
        value = '=HYPERLINK("https://example.invalid/' + "x" * 60 + '","open")'
        err = self.csv_no("add", "notes", stdin={"text": value})
        self.assertIn("text: starts with =", err)
        self.assertNotIn("HYPERLINK", err)

    def test_dash_lists_flags_and_plain_text_are_accepted(self):
        self.register()
        for good in self.GOOD:
            with self.subTest(value=good):
                rid = self.csv("add", "log", stdin={"agent": "QA", "changed": good}).strip()
                self.csv("update", "log", rid, stdin={"verified": good})
        self.assertEqual([r["changed"] for r in self.rows("log")], list(self.GOOD))

    def test_doctor_reports_a_planted_cell_and_fix_keeps_it(self):
        self.register()
        p = self.path("log")
        p.parent.mkdir(parents=True, exist_ok=True)
        body = (b'id,agent,lane,changed,verified,attempts,limitations\n'
                b'L-001,QA,serial,"=HYPERLINK(""x"")",ok,1/1,\n'
                b'L-002,QA,,-2+3,,,\n'
                b'L-003,QA,,item list,by main GD,,\n'
                b"L-004,QA,,-- cmd|' /C calc'!A0,,,\n")
        p.write_bytes(b"\xef\xbb\xbf" + body)
        code, out, err = self.run_cli("csv", "doctor", "log", "--feature", "shop")
        self.assertEqual(code, 1)
        self.assertIn("line 2: changed: starts with =", err)
        self.assertIn("line 3: changed: starts with -, which", err)
        self.assertNotIn("line 4", err)
        self.assertIn("line 5: changed: starts with -, which", err)
        self.assertNotIn("HYPERLINK", err)
        self.assertNotIn("calc", err)
        code, out, err = self.run_cli("csv", "doctor", "log", "--feature", "shop", "--fix")
        self.assertEqual(code, 1)
        self.assertIn("line 2: changed: starts with =", err)
        self.assertEqual(p.read_bytes(), body)  # BOM repaired, the formula cells written back for a hand fix


if __name__ == "__main__":
    unittest.main()
