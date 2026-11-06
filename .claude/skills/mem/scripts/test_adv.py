"""Tests for adv.py. Run: python -I .claude/skills/mem/scripts/test_adv.py"""
import contextlib
import io
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import adv  # noqa: E402

FAKE_KEY = "AK" + "IA" + "Q" * 16  # built at runtime so this file holds no secret-shaped literal
RETURN = """Advisory-Return: v1
Status: Done

### F1 [High] Interstitial after level 3 breaks the first session
D1 retention 31% [measured: retention.csv, 2026-10, 1.4.0] drops at this point.

### F2 [Low] Thoi gian tai man hinh dau
Benchmark note [benchmark: https://example.com/x, 2026-11-05, T2].
"""
BRIEF = "Workflow: /product-review\nAdvisory-Thread: milestone-2\nData-Period: 2026-10\nTarget: Assets/"


class AdvTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / ".gitignore").write_text(".memory/advisory/\n", encoding="utf-8")

    def run_cli(self, *argv, stdin=None):
        out, err = io.StringIO(), io.StringIO()
        real = sys.stdin
        if stdin is not None:
            sys.stdin = type("S", (), {"buffer": io.BytesIO(stdin.encode("utf-8"))})()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = adv.main(["--root", str(self.root)] + list(argv))
        finally:
            sys.stdin = real
        return code, out.getvalue(), err.getvalue()

    def ingest(self, agent="product-owner", body=RETURN, brief=BRIEF, agent_id=None):
        return self.run_cli("ingest", stdin=json.dumps({"agent": agent, "return": body, "brief": brief, "session": "s1", "agent_id": agent_id}))

    def test_the_same_return_twice_is_stored_once(self):
        self.ingest(agent_id="a1")
        code, out, _ = self.ingest(agent_id="a1")
        self.assertEqual(code, 0)
        self.assertIn("adv:1 (already stored)", out)
        self.assertIn("product-owner 0", self.run_cli("rounds", "milestone-2")[1])

    def test_a_new_return_or_another_agent_is_stored(self):
        self.ingest(agent_id="a1")
        self.ingest(body=RETURN + "\nMore.", agent_id="a1")
        self.ingest(agent_id="a2")
        self.assertIn("product-owner 2", self.run_cli("rounds", "milestone-2")[1])

    def test_ingest_splits_findings_and_reads_markers(self):
        code, out, _ = self.ingest()
        self.assertEqual(code, 0)
        self.assertIn("adv:1 (2 findings)", out)
        _, listed, _ = self.run_cli("list", "--thread", "milestone-2")
        self.assertIn("adv:1.1", listed)
        self.assertIn("adv:1.2", listed)
        self.assertIn("[High]", listed)
        _, got, _ = self.run_cli("get", "adv:1")
        self.assertIn("workflow=/product-review", got)
        self.assertIn("data=2026-10", got)

    def test_return_is_stored_verbatim(self):
        self.ingest()
        _, got, _ = self.run_cli("get", "adv:1")
        self.assertIn(RETURN.strip(), got)

    def test_query_finds_a_finding_and_ignores_diacritics(self):
        self.ingest()
        _, out, _ = self.run_cli("q", "interstitial")
        self.assertIn("adv:1.1", out)
        _, out, _ = self.run_cli("q", "thời gian")
        self.assertIn("adv:1.2", out)
        _, out, _ = self.run_cli("q", "interstitial", "--agent", "game-designer")
        self.assertEqual(out, "")

    def test_decide_needs_the_main_gd(self):
        self.ingest()
        for by in ("GD", "main session", " main GD"):
            code, _, err = self.run_cli("decide", "adv:1.1", "accepted", "--by", by)
            self.assertEqual(code, 2, by)
            self.assertIn("main GD only", err)
        code, _, _ = self.run_cli("decide", "adv:1.1", "accepted", "--by", "main GD", "--note", "backlog row 4")
        self.assertEqual(code, 0)
        _, got, _ = self.run_cli("get", "adv:1.1")
        self.assertIn("status: accepted by=main GD", got)
        self.assertIn("note: backlog row 4", got)
        _, listed, _ = self.run_cli("list", "--status", "open")
        self.assertNotIn("adv:1.1", listed)
        self.assertIn("adv:1.2", listed)

    def test_decide_needs_a_finding_not_a_return(self):
        self.ingest()
        code, _, err = self.run_cli("decide", "adv:1", "accepted", "--by", "main GD")
        self.assertEqual(code, 2)
        self.assertIn("names a return", err)

    def test_useful_mark(self):
        self.ingest()
        self.assertEqual(self.run_cli("useful", "adv:1.2", "no")[0], 0)
        self.assertIn("useful=0", self.run_cli("get", "adv:1.2")[1])

    def test_rounds_count_follow_ups_per_agent(self):
        self.ingest()
        self.ingest(body=RETURN + "\nFollow-up.")
        self.ingest("game-designer")
        _, out, _ = self.run_cli("rounds", "milestone-2")
        self.assertIn("product-owner 1", out)
        self.assertIn("game-designer 0", out)

    def test_refuses_when_not_ignored_and_stores_nothing(self):
        (self.root / ".gitignore").write_text("", encoding="utf-8")
        code, _, err = self.ingest()
        self.assertEqual(code, 2)
        self.assertIn("not git-ignored", err)
        self.assertFalse((self.root / adv.DB_REL).exists())

    def test_refuses_outside_a_repository(self):
        shutil.rmtree(self.root / ".git")
        code, _, err = self.ingest()
        self.assertEqual(code, 2)
        self.assertFalse((self.root / adv.DB_REL).exists())

    def test_refuses_a_secret_shape_and_stores_nothing(self):
        code, _, err = self.ingest(body=RETURN + "\nkey " + FAKE_KEY)
        self.assertEqual(code, 2)
        self.assertIn("secret-shaped", err)
        self.assertFalse((self.root / adv.DB_REL).exists())

    def test_redacts_pii(self):
        self.ingest(body="Advisory-Return: v1\n\n### F1 [Low] Mail\nplayer a.b@example.com at 8.8.8.8")
        _, got, _ = self.run_cli("get", "adv:1")
        self.assertNotIn("a.b@example.com", got)
        self.assertNotIn("8.8.8.8", got)

    def test_a_return_with_no_findings_is_stored_and_searchable(self):
        self.ingest(body="Advisory-Return: v1\nNothing wrong with onboarding.")
        self.assertIn("adv:1", self.run_cli("q", "onboarding")[1])

    def test_ingest_needs_agent_and_return(self):
        self.assertEqual(self.run_cli("ingest", stdin=json.dumps({"agent": "x"}))[0], 2)

    def test_export_refuses_a_tracked_path_and_copies_to_an_ignored_one(self):
        self.ingest()
        code, _, err = self.run_cli("export", str(self.root / "docs" / "copy.db"))
        self.assertEqual(code, 2)
        self.assertIn("not git-ignored", err)
        target = self.root / ".memory" / "advisory" / "backup.db"
        self.assertEqual(self.run_cli("export", str(target))[0], 0)
        db = sqlite3.connect(str(target))
        self.assertEqual(db.execute("SELECT COUNT(*) FROM finding").fetchone()[0], 2)
        db.close()

    def test_export_into_another_repository_must_be_ignored_there(self):
        self.ingest()
        other = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, other, ignore_errors=True)
        subprocess.run(["git", "init", "-q", str(other)], check=True)
        code, _, err = self.run_cli("export", str(other / "copy.db"))
        self.assertEqual(code, 2)
        self.assertIn("not git-ignored", err)
        (other / ".gitignore").write_text("*.db\n", encoding="utf-8")
        self.assertEqual(self.run_cli("export", str(other / "copy.db"))[0], 0)

    def test_a_refused_export_leaves_no_folders(self):
        self.ingest()
        target = self.root / "docs" / "deep" / "copy.db"
        self.assertEqual(self.run_cli("export", str(target))[0], 2)
        self.assertFalse((self.root / "docs").exists())

    def mock_rev_parse(self, code, err):
        real = adv.subprocess.run

        def fake(cmd, **kw):
            if "rev-parse" in cmd:
                return subprocess.CompletedProcess(cmd, code, b"", err)
            return real(cmd, **kw)
        adv.subprocess.run = fake
        self.addCleanup(setattr, adv.subprocess, "run", real)

    def test_export_refuses_when_git_cannot_answer(self):
        self.ingest()
        other = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, other, ignore_errors=True)
        subprocess.run(["git", "init", "-q", str(other)], check=True)
        self.mock_rev_parse(128, b"fatal: detected dubious ownership in repository")
        code, _, err = self.run_cli("export", str(other / "copy.db"))
        self.assertEqual(code, 2)
        self.assertIn("cannot tell", err)

    def test_export_refuses_a_gitfile_to_a_missing_gitdir(self):  # review round 3, S2: real git, no mock
        self.ingest()
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / ".git").write_text("gitdir: %s\n" % (d / "missing"), encoding="utf-8")
        code, _, err = self.run_cli("export", str(d / "copy.db"))
        self.assertEqual(code, 2)
        self.assertIn("cannot tell", err)
        self.assertFalse((d / "copy.db").exists())

    def test_no_repository_does_not_depend_on_git_message_text(self):  # review round 3, S2: locale
        self.ingest()
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        if any((p / ".git").exists() for p in (d, *d.parents)):
            self.skipTest("the temp folder sits inside a repository")
        self.mock_rev_parse(128, "fatal: không phải kho git".encode("utf-8"))
        self.assertEqual(self.run_cli("export", str(d / "copy.db"))[0], 0)

    def test_marker_values_are_redacted(self):
        self.ingest(brief="Advisory-Thread: t1\nTarget: report for a.b@example.com")
        self.assertNotIn("a.b@example.com", self.run_cli("get", "adv:1")[1])

    def test_lint_passes_clean_and_fails_a_secret_or_a_lost_ignore_rule(self):
        self.ingest()
        self.assertEqual(self.run_cli("lint")[0], 0)
        db = sqlite3.connect(str(self.root / adv.DB_REL))
        with db:
            db.execute("UPDATE advice SET body = ?", (FAKE_KEY,))
        db.close()
        code, out, _ = self.run_cli("lint")
        self.assertEqual(code, 1)
        self.assertIn("secret shape", out)
        (self.root / ".gitignore").write_text("", encoding="utf-8")
        self.assertIn("not git-ignored", self.run_cli("lint")[1])

    def test_reads_before_any_write_do_not_create_the_store(self):
        self.assertIn("no advisory store", self.run_cli("list")[1])
        self.assertFalse((self.root / adv.DB_REL).exists())


if __name__ == "__main__":
    unittest.main()
