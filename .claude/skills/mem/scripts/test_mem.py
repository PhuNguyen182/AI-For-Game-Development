"""Tests for mem.py. Run: python -I .claude/skills/mem/scripts/test_mem.py"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mem  # noqa: E402

PATTERNS = HERE.parents[2] / "hooks" / "secret-patterns.txt"
FAKE_KEY = "AK" + "IA" + "Q" * 16  # built at runtime so this file holds no secret-shaped literal
PEM_KIND = "RSA PRIVATE" + " KEY"


def git(cwd, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(cwd)] + list(args),
                   check=True, capture_output=True)


def write(root, path, text):
    p = Path(root) / path
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:  # write_text(newline=) needs 3.10
        f.write(text)
    return p


def note(slug, desc, ntype="feedback", body="", status="active", extra=""):
    return "---\nname: %s\ndescription: %s\ntype: %s\ntags: [t]\npaths: []\nstatus: %s\nupdated: 2026-10-01\n%s---\n\n%s\n" % (
        slug, desc, ntype, status, extra, body)


def run(root, *argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = mem.main(["--root", str(root)] + list(argv))
    return code, out.getvalue()


def new_repo(base, name="repo"):
    root = Path(base) / name
    root.mkdir()
    git(root, "init", "-q")
    write(root, ".gitignore", ".memory/.index/\n.memory/.state/\n")
    shutil.copy(PATTERNS, write(root, ".claude/hooks/secret-patterns.txt", ""))
    write(root, ".claude/agents/ui-engineer.md", "---\nname: ui-engineer\n---\nBuilds UI.\n")
    write(root, ".claude/skills/fix/SKILL.md", "---\nname: fix\ndescription: Fix a bug end to end. Use for any defect.\n---\n# Fix\nReproduce first.\n")
    write(root, ".claude/rules/core.md", "# Core\n\n## Tools\n- One Unity Editor at a time; the editor-lock.ps1 hook enforces it.\n\n## Memory\n- Save an error-prevention memory.\n")
    write(root, "docs/adr/0001-netcode.md", "# ADR-1 Netcode\n\n- Status: Superseded\n\nWe chose Mirror.\n")
    write(root, "docs/adr/0002-netcode.md", "# ADR-2 Netcode\n\n- Status: Accepted\n\nWe chose FishNet over Mirror.\n")
    write(root, "Assets/Plugins/Vendor/README.md", "# Vendor\nThird-party readme about FishNet.\n")
    return root


def transcript(path, root, secret):
    lines = [
        {"type": "user", "timestamp": "2026-10-28T01:00:00Z", "message": {"role": "user", "content": [
            {"type": "text", "text": "<ide_opened_file>noise</ide_opened_file>Fix the editor lock bug, key %s" % secret}]}},
        {"type": "assistant", "timestamp": "2026-10-28T01:00:05Z", "message": {"content": [
            {"type": "thinking", "thinking": "private reasoning"},
            {"type": "text", "text": "Looking at the lock hook."},
            {"type": "tool_use", "id": "r1", "name": "Edit", "input": {"file_path": str(Path(root) / ".claude/hooks/editor-lock.ps1")}},
            {"type": "tool_use", "id": "r2", "name": "Read", "input": {"file_path": "C:/Elsewhere/outside.cs"}}]}},
        {"type": "user", "timestamp": "2026-10-28T01:00:06Z", "message": {"content": [
            {"type": "tool_result", "tool_use_id": "r1", "content": "TOOL OUTPUT SHOULD NOT BE CAPTURED"}]}},
        {"type": "assistant", "timestamp": "2026-10-28T01:00:07Z", "message": {"content": [
            {"type": "tool_use", "id": "a1", "name": "Agent", "input": {"subagent_type": "ui-engineer", "description": "Fix HUD", "prompt": "Brief: fix the HUD binding."}}]}},
        {"type": "user", "timestamp": "2026-10-28T01:01:00Z", "message": {"content": [
            {"type": "tool_result", "tool_use_id": "a1", "content": [{"type": "text", "text": "Done: HUD bound via HudPresenter."}]}]}},
        {"type": "assistant", "timestamp": "2026-10-28T01:01:05Z", "message": {"content": [
            {"type": "tool_use", "id": "q1", "name": "AskUserQuestion", "input": {"questions": []}}]}},
        {"type": "user", "timestamp": "2026-10-28T01:02:00Z", "message": {"content": [
            {"type": "tool_result", "tool_use_id": "q1", "content": "User answered: use FishNet"}]}},
        {"type": "attachment", "timestamp": "2026-10-28T01:02:10Z", "attachment": {"type": "queued_command", "prompt":
            "<task-notification><summary>Agent done</summary><result>Explore found HudPresenter.cs</result></task-notification>"}},
        {"type": "attachment", "timestamp": "2026-10-28T01:02:20Z", "attachment": {"type": "queued_command", "prompt": "<browser_instruction>gone</browser_instruction>also check the score"}},
        {"type": "user", "timestamp": "2026-10-28T01:02:21Z", "message": {"content": "<browser_instruction>gone</browser_instruction>also check the score"}},
        {"type": "assistant", "timestamp": "2026-10-28T01:02:30Z", "message": {"content": [{"type": "text", "text": "Checking score."}]}},
        {"type": "assistant", "timestamp": "2026-10-28T01:02:31Z", "message": {"content": [
            {"type": "tool_use", "id": "w1", "name": "Write", "input": {"file_path": str(Path(root) / "Assets/Score.cs")}}]}},
        {"type": "assistant", "timestamp": "2026-10-28T01:02:40Z", "message": {"content": [{"type": "text", "text": "Score fixed."}]}},
        {"type": "user", "isCompactSummary": True, "timestamp": "2026-10-28T01:03:00Z", "message": {"content": "LLM summary"}},
        {"type": "user", "isSidechain": True, "timestamp": "2026-10-28T01:03:00Z", "message": {"content": "sidechain"}},
        {"type": "attachment", "timestamp": "2026-10-28T01:03:00Z"},
        "not json",
    ]
    with open(path, "w", encoding="utf-8") as f:
        for l in lines:
            f.write((l if isinstance(l, str) else json.dumps(l)) + "\n")


class MemTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="memtest-")
        self.root = new_repo(self.tmp)
        os.environ.pop("MEM_CAPTURE", None)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def capture(self, secret=FAKE_KEY, session="abcdef12-3456"):
        t = Path(self.tmp) / ("t-%s.jsonl" % session)
        transcript(t, self.root, secret)
        code, _ = run(self.root, "capture", "--transcript", str(t), "--session", session)
        self.assertEqual(code, 0)
        return t

    def test_layers_indexed_and_excludes_respected(self):
        write(self.root, ".memory/notes/feedback/ask-gd.md", note("ask-gd", "Ask the GD via multiple choice"))
        code, out = run(self.root, "stats")
        self.assertIn("M 1 notes", out)
        _, out = run(self.root, "q", "Third-party readme")
        self.assertNotIn("Assets/Plugins", out)

    def test_note_ranks_first_and_labels_layer(self):
        write(self.root, ".memory/notes/lesson/editor-lock.md", note("editor-lock", "Never run two Editors; editor-lock.ps1 blocks it", "lesson"))
        _, out = run(self.root, "q", "editor lock")
        first = out.splitlines()[0]
        self.assertTrue(first.startswith("m:lesson/editor-lock | "), out)
        self.assertIn("k:.claude/rules/core.md#tools :3 rule | ", out)

    def test_superseded_filtered_unless_all(self):
        write(self.root, ".memory/notes/project/old.md", note("old", "Netcode uses Mirror", "project", status="superseded"))
        _, out = run(self.root, "q", "netcode Mirror")
        self.assertNotIn("m:project/old", out)
        self.assertNotIn("0001-netcode", out)
        self.assertIn("0002-netcode", out)
        _, out = run(self.root, "q", "netcode Mirror", "--all")
        self.assertIn("m:project/old", out)

    def test_incremental_edit_and_delete(self):
        p = write(self.root, "docs/guide.md", "# Guide\nalpha bravo\n")
        self.assertIn("docs/guide.md", run(self.root, "q", "bravo")[1])
        time.sleep(0.05)
        write(self.root, "docs/guide.md", "# Guide\ncharlie delta\n")
        self.assertEqual("no hits", run(self.root, "q", "bravo")[1].strip())
        self.assertIn("docs/guide.md", run(self.root, "q", "charlie")[1])
        p.unlink()
        self.assertEqual("no hits", run(self.root, "q", "charlie")[1].strip())

    def test_capture_redacts_and_skips_tool_output(self):
        self.capture()
        files = list((self.root / ".memory/traces").rglob("*.jsonl"))
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].name, "2026-10-28-abcdef12.jsonl")
        text = files[0].read_text(encoding="utf-8")
        self.assertNotIn(FAKE_KEY, text)
        self.assertIn("[REDACTED:AWS access key]", text)
        for absent in ("TOOL OUTPUT", "private reasoning", "noise", "LLM summary", "sidechain", "outside.cs", "gone"):
            self.assertNotIn(absent, text)
        turns = [json.loads(l) for l in text.splitlines()]
        self.assertEqual([t["role"] for t in turns],
                         ["user", "assistant", "brief", "agent", "answer", "agent", "user", "assistant", "assistant"])
        self.assertEqual(turns[1]["files"], [".claude/hooks/editor-lock.ps1"])
        self.assertEqual(turns[2]["agent"], "ui-engineer")
        self.assertIn("Explore found HudPresenter.cs", turns[5]["text"])
        self.assertEqual(turns[6]["text"], "also check the score")
        self.assertEqual((turns[7]["text"], turns[7]["files"]), ("Checking score.", ["Assets/Score.cs"]))
        self.assertEqual((turns[8]["text"], turns[8].get("files")), ("Score fixed.", None))

    def test_capture_idempotent_and_opt_out(self):
        t = self.capture()
        f = next((self.root / ".memory/traces").rglob("*.jsonl"))
        before = f.read_bytes()
        run(self.root, "capture", "--transcript", str(t), "--session", "abcdef12-3456")
        shutil.rmtree(self.root / ".memory/.state")
        run(self.root, "capture", "--transcript", str(t), "--session", "abcdef12-3456")
        self.assertEqual(before, f.read_bytes())
        os.environ["MEM_CAPTURE"] = "0"
        self.capture(session="ffff0000-1")
        self.assertEqual(len(list((self.root / ".memory/traces").rglob("*.jsonl"))), 1)

    def test_trace_query_get_ctx_and_entity_graph(self):
        write(self.root, ".memory/.gitignore", "traces/\n")  # gitignored traces are still indexed
        write(self.root, ".memory/notes/lesson/lock.md", note("lock", "editor-lock.ps1 blocks two Editors", "lesson"))
        self.capture()
        _, out = run(self.root, "q", "HUD binding", "-l", "T")
        self.assertIn("t:2026-10-28-abcdef12#3 brief | ", out)
        _, out = run(self.root, "get", "t:2026-10-28-abcdef12#3")
        self.assertIn(".memory/traces/2026/10/2026-10-28-abcdef12.jsonl:3", out.splitlines()[0])
        _, out = run(self.root, "get", "t:2026-10-28-abcdef12#3", "--ctx", "1")
        self.assertIn("#2", out)
        self.assertIn("#4", out)
        _, out = run(self.root, "ent", "editor-lock.ps1")
        self.assertIn("editor-lock.ps1 [file]", out)
        see = [l for l in out.splitlines() if l.strip().startswith("see:")][0]
        self.assertIn("m:lesson/lock . k:.claude/rules/core.md#tools", see)
        _, out = run(self.root, "for", ".claude/hooks/editor-lock.ps1")
        self.assertIn("t:2026-10-28-abcdef12#2", out)
        _, out = run(self.root, "sessions")
        self.assertIn("2026-10-28-abcdef12", out)

    def test_graph_finds_doc_without_shared_words(self):
        write(self.root, "docs/a.md", "# A\nThe HudPresenter talks to ScoreModel.\n")
        write(self.root, "docs/b.md", "# B\nScoreModel is pure C#.\n")
        _, out = run(self.root, "q", "HudPresenter")
        self.assertIn("docs/b.md", out)

    def test_budget_trims_output(self):
        for i in range(12):
            write(self.root, "docs/n%d.md" % i, "# Note %d\nshared keyword zebra\n" % i)
        _, out = run(self.root, "q", "zebra", "--budget", "200", "-n", "12")
        self.assertRegex(out, r"\(\+\d+ more\)\n$")
        self.assertLessEqual(len(out.splitlines()), 4)

    def test_add_and_lint(self):
        self.assertEqual(run(self.root, "add", "lesson", "use-fishnet", "--desc", "Netcode is FishNet")[0], 0)
        self.assertEqual(run(self.root, "add", "lesson", "use-fishnet", "--desc", "dup")[0], 1)
        self.assertEqual(run(self.root, "add", "lesson", "leak", "--desc", "key %s" % FAKE_KEY)[0], 1)
        self.assertEqual(run(self.root, "add", "bogus", "x", "--desc", "y")[0], 1)
        self.assertEqual(run(self.root, "lint")[0], 0)
        write(self.root, ".memory/notes/lesson/bad.md", note("other", "", "project"))
        code, out = run(self.root, "lint")
        self.assertEqual(code, 1)
        self.assertIn("name must equal", out)
        self.assertIn("missing description", out)
        self.assertIn("type must equal", out)

    def capture_lines(self, entries, session="eeee0000-1"):
        t = Path(self.tmp) / ("t-%s.jsonl" % session)
        with open(t, "a", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        self.assertEqual(run(self.root, "capture", "--transcript", str(t), "--session", session)[0], 0)
        out = list((self.root / ".memory/traces").rglob("*-%s.jsonl" % session[:8]))
        return out[0] if out else None

    @staticmethod
    def user(text, ts="2026-10-28T02:00:00.123Z"):
        return {"type": "user", "timestamp": ts, "message": {"content": text}}

    def test_redaction_pem_body_paths_email(self):
        pem = "-----BEGIN %s-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASC\nabcdEFGH\n-----END %s-----" % (PEM_KIND, PEM_KIND)
        home = str(Path.home())
        f = self.capture_lines([self.user("key:\n%s\nsee %s/Assets/A.cs and %s/x.txt, mail dev@example.com" % (pem, self.root, home))])
        text = f.read_text(encoding="utf-8")
        for absent in ("MIIEvQ", "abcdEFGH", "END RSA", "dev@example.com", str(self.root).replace("\\", "\\\\"), home.replace("\\", "\\\\")):
            self.assertNotIn(absent, text)
        self.assertIn("<root>/Assets/A.cs", text)
        self.assertIn("~/x.txt", text)
        self.assertIn("[REDACTED:email]", text)

    def test_missing_patterns_fail_closed(self):
        (self.root / ".claude/hooks/secret-patterns.txt").write_text("# only comments\n", encoding="utf-8")
        self.assertIsNone(self.capture_lines([self.user("key %s" % FAKE_KEY)]))
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(run(self.root, "lint")[0], 1)
        self.assertIn("no secret patterns", err.getvalue())

    def test_append_only_keeps_hand_edits_and_repeated_prompts(self):
        f = self.capture_lines([self.user("ok"), self.user("secret plan alpha"), self.user("ok")])
        self.assertEqual([json.loads(l)["text"] for l in f.read_text(encoding="utf-8").splitlines()], ["ok", "secret plan alpha", "ok"])
        lines = f.read_text(encoding="utf-8").splitlines()
        lines[1] = json.dumps({"ts": "", "role": "user", "text": "[hand-redacted]"})
        write(self.root, f.relative_to(self.root).as_posix(), "\n".join(lines) + "\n")
        self.capture_lines([self.user("next")])
        texts = [json.loads(l)["text"] for l in f.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(texts, ["ok", "[hand-redacted]", "ok", "next"])

    def test_deleted_trailing_line_stays_deleted(self):
        f = self.capture_lines([self.user("one"), self.user("pasted token by mistake")])
        lines = f.read_text(encoding="utf-8").splitlines()
        write(self.root, f.relative_to(self.root).as_posix(), lines[0] + "\n")
        self.capture_lines([self.user("three")])
        self.assertEqual([json.loads(l)["text"] for l in f.read_text(encoding="utf-8").splitlines()], ["one", "three"])

    def test_turn_growing_after_stop_is_appended(self):
        def said(text, ts):
            return {"type": "assistant", "timestamp": ts, "message": {"content": [{"type": "text", "text": text}]}}
        f = self.capture_lines([self.user("go"), said("Part one.", "2026-10-28T02:00:01Z")])
        self.capture_lines([said("Part two.", "2026-10-28T02:00:09Z")])
        texts = [json.loads(l)["text"] for l in f.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(texts, ["go", "Part one.", "Part two."])

    def test_git_bash_paths_and_package_specs(self):
        home = Path.home()
        drive = str(home)[0].lower()
        bash = "/" + drive + str(home).replace("\\", "/")[2:]
        f = self.capture_lines([self.user("see %s/notes and C:\\Users\\%s\\other, add com.cysharp.unitask@2.5.0" % (bash, home.name))])
        text = f.read_text(encoding="utf-8")
        self.assertNotIn(bash, text)
        self.assertIn("~/notes", text)
        self.assertIn("com.cysharp.unitask@2.5.0", text)
        if home.name.lower() != "users":
            self.assertNotIn("Users\\\\%s" % home.name, text)

    def test_agent_reports_unwrapped_and_attributed(self):
        def tool_use(i, agent):
            return {"type": "assistant", "timestamp": "2026-10-28T03:00:00Z", "message": {"content": [
                {"type": "tool_use", "id": i, "name": "Agent", "input": {"subagent_type": agent, "prompt": "brief " + agent}}]}}

        def result(i, text):
            return {"type": "user", "timestamp": "2026-10-28T03:00:01Z", "message": {"content": [
                {"type": "tool_result", "tool_use_id": i, "content": [{"type": "text", "text": text}]}]}}
        handback = ("<tools-used-before-summary>Glob</tools-used-before-summary>\n[Subagent hand-back] The text below is the final"
                    " report of a subagent. The report follows:\n  [harness: note]\n  Status: Done\n  Found X.\n")
        f = self.capture_lines([
            self.user("go"),
            tool_use("u1", "Explore"), result("u1", handback),
            tool_use("u2", "code-reviewer"), result("u2", "Async agent launched successfully.\nagentId: abc123 (internal)"),
            dict(self.user('Another Claude session sent a message:\n<agent-message from="abc123">\n' + handback +
                           '</agent-message>\n\nThat "other Claude session" is an agent working inside this session.'),
                 isMeta=True, origin={"kind": "peer", "from": "abc123"}),
            dict(self.user("peer chatter without a report"), isMeta=True, origin={"kind": "peer"}),
            dict(self.user("hidden meta prompt"), isMeta=True),
            tool_use("u3", "qa-lead"), result("u3", "Async agent launched successfully.\nagentId: def456 (internal)"),
            {"type": "attachment", "timestamp": "2026-10-28T03:00:09Z", "attachment": {"type": "queued_command", "prompt":
                "<task-notification><tool-use-id>u3</tool-use-id><summary>done</summary><result>Plan ready.</result></task-notification>"}},
            {"type": "attachment", "timestamp": "2026-10-28T03:00:10Z", "attachment": {"type": "queued_command", "prompt":
                "<task-notification><tool-use-id>u2</tool-use-id><result>This agent's report was delivered to you as a message from x</result></task-notification>"}},
        ])
        turns = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines()]
        agents = [(t.get("agent"), t["text"]) for t in turns if t["role"] == "agent"]
        self.assertEqual(agents, [("Explore", "Status: Done\nFound X."), ("code-reviewer", "Status: Done\nFound X."),
                                  ("qa-lead", "done\n\nPlan ready.")])
        self.assertEqual([t["text"] for t in turns if t["role"] == "user"], ["go"])

    def test_user_folder_slug_and_foreign_files_removed(self):
        leaf = Path.home().name
        slug = "C--Users-%s-Projects-X" % leaf
        tool = {"type": "assistant", "timestamp": "2026-10-28T04:00:00Z", "message": {"content": [
            {"type": "text", "text": "ok"},
            {"type": "tool_use", "id": "e1", "name": "Edit", "input": {"file_path": "~/notes/t.md"}},
            {"type": "tool_use", "id": "e2", "name": "Edit", "input": {"file_path": slug + "/memory/M.md"}},
            {"type": "tool_use", "id": "e3", "name": "Edit", "input": {"file_path": "./docs/adr/0002-netcode.md"}}]}}
        f = self.capture_lines([self.user("transcripts live in ~/.claude/projects/%s/, quoted `Users\\\\%s`" % (slug, leaf)), tool])
        text = f.read_text(encoding="utf-8")
        self.assertNotIn("Users-%s" % leaf, text)
        self.assertNotIn("\\\\%s" % leaf, text)
        self.assertIn("C--Users-<user>-Projects-X", text)
        turns = [json.loads(l) for l in text.splitlines()]
        self.assertEqual(turns[1]["files"], ["docs/adr/0002-netcode.md"])

    def test_dotted_user_name_slug_removed(self):
        old = Path.home
        try:
            Path.home = staticmethod(lambda: Path("C:/Users/john.doe"))
            rec = mem.trace_record(self.root, {"role": "user", "text": "see C--Users-john-doe-Game/memory and C:\\Users\\john.doe\\x"},
                                   mem.load_secret_patterns(self.root))
        finally:
            Path.home = old
        self.assertNotIn("john", rec["text"])

    def test_unwrap_handles_unindented_harness_line(self):
        text = "[Subagent hand-back] x. The report follows:\n[harness: note]\n  FIRST\n    nested\n  SECOND\n"
        self.assertEqual(mem.unwrap_agent(text), "FIRST\n  nested\nSECOND")

    def test_non_object_json_lines_do_not_stop_capture(self):
        t = Path(self.tmp) / "t-odd.jsonl"
        t.write_text("[1,2,3]\nnull\n\"s\"\n42\n" + json.dumps(self.user("still captured")) + "\n", encoding="utf-8")
        run(self.root, "capture", "--transcript", str(t), "--session", "0dd00000")
        f = next((self.root / ".memory/traces").rglob("*-0dd00000.jsonl"))
        self.assertIn("still captured", f.read_text(encoding="utf-8"))

    def test_mark_survives_lost_state_and_deleted_line(self):
        f = self.capture_lines([self.user("alpha"), self.user("bravo"), self.user("charlie")])
        lines = f.read_text(encoding="utf-8").splitlines()
        write(self.root, f.relative_to(self.root).as_posix(), lines[0] + "\n" + lines[2] + "\n")
        shutil.rmtree(self.root / ".memory/.state")
        self.capture_lines([self.user("delta")])
        self.assertEqual([json.loads(l)["text"] for l in f.read_text(encoding="utf-8").splitlines()], ["alpha", "charlie", "delta"])

    def test_get_caps_body_unless_full(self):
        write(self.root, ".memory/notes/lesson/long.md", note("long", "Long note", "lesson", body="word " * 1500))
        _, out = run(self.root, "get", "m:lesson/long")
        self.assertIn("chars; --full]", out)
        self.assertLess(len(out), mem.GET_CAP + 200)
        _, out = run(self.root, "get", "m:lesson/long", "--full")
        self.assertNotIn("--full]", out)
        self.assertGreater(len(out), 7000)

    def test_ent_caps_cards_by_mentions(self):
        write(self.root, "docs/z1.md", "# Z\nzeta1.cs zeta2.cs zeta3.cs zeta4.cs zeta5.cs\n")
        for i in (2, 3, 4):  # indexed after z1: the most-mentioned name is the newest entity
            write(self.root, "docs/z%d.md" % i, "# Z\nzeta6.cs\n")
        _, out = run(self.root, "ent", "zeta")
        self.assertTrue(out.startswith("zeta6.cs [file] 3 mentions"), out)
        self.assertEqual(out.count(" mentions"), mem.ENT_CAP, out)
        self.assertTrue(out.endswith("(+3 more)\n"), out)

    def test_get_ctx_caps_target_turn(self):
        self.capture_lines([self.user("word " * 1500), self.user("short")])
        _, out = run(self.root, "get", "t:2026-10-28-eeee0000#1", "--ctx", "1")
        self.assertIn("## t:2026-10-28-eeee0000#1 .memory/traces/2026/10/2026-10-28-eeee0000.jsonl:1 ", out)
        self.assertIn("chars; --full]", out)
        self.assertNotIn("--full]", run(self.root, "get", "t:2026-10-28-eeee0000#1", "--ctx", "1", "--full")[1])

    def test_age_days_handles_milliseconds(self):
        self.assertGreater(mem.age_days("2020-01-01T00:00:00.786Z"), 1000)
        self.assertGreater(mem.age_days("2020-01-01"), 1000)
        self.assertEqual(mem.age_days("garbage"), 0.0)

    def test_tracked_file_deleted_in_worktree_is_dropped(self):
        write(self.root, "docs/gone.md", "# Gone\nkiwifruit\n")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "x")
        self.assertIn("docs/gone.md", run(self.root, "q", "kiwifruit")[1])
        (self.root / "docs/gone.md").unlink()
        self.assertEqual("no hits", run(self.root, "q", "kiwifruit")[1].strip())

    def test_duplicate_headings_get_unique_ids(self):
        write(self.root, "docs/dup.md", "# Foo\nmango one\n# Foo\nmango two\n# Foo 2\nmango three\n")
        _, out = run(self.root, "q", "mango", "-n", "9")
        ids = [l.split()[0] for l in out.splitlines() if l.startswith("k:docs/dup.md")]
        self.assertEqual(len(set(ids)), 3, out)

    def test_superseded_only_from_doc_header(self):
        write(self.root, "docs/index.md", "# ADR index\nList of records.\n## Old\n- Status: Superseded\npapaya\n")
        self.assertIn("docs/index.md", run(self.root, "q", "papaya")[1])

    def test_stats_time_budget_is_partial_then_completes(self):
        _, out = run(self.root, "stats", "--seconds", "0.000001")
        self.assertIn("indexing, continues", out)
        _, out = run(self.root, "stats")
        self.assertNotIn("indexing", out)

    def test_add_rejects_frontmatter_injection(self):
        self.assertEqual(run(self.root, "add", "lesson", "x", "--desc", "d", "--tags", "a]\nstatus: superseded")[0], 1)

    def test_merge_two_machines(self):
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "base")
        a, b = Path(self.tmp) / "a", Path(self.tmp) / "b"
        git(self.tmp, "clone", "-q", str(self.root), str(a))
        git(self.tmp, "clone", "-q", str(self.root), str(b))
        write(a, ".memory/notes/lesson/from-a.md", note("from-a", "Lesson alpha from machine A", "lesson"))
        git(a, "add", "-A")
        git(a, "commit", "-q", "-m", "a")
        write(b, ".memory/notes/lesson/from-b.md", note("from-b", "Lesson beta from machine B", "lesson"))
        write(b, ".memory/traces/2026/10/2026-10-28-bbbbbbbb.jsonl", json.dumps({"ts": "2026-10-28T00:00:00Z", "role": "user", "text": "gamma question"}) + "\n")
        git(b, "add", "-A")
        git(b, "commit", "-q", "-m", "b")
        run(b, "stats")  # b has a stale index from before the merge
        git(b, "pull", "-q", "--no-rebase", "--no-edit", str(a))
        _, out = run(b, "stats")
        self.assertIn("M 2 notes", out)
        self.assertIn("T 1 turns", out)
        self.assertIn("m:lesson/from-a", run(b, "q", "alpha")[1])


if __name__ == "__main__":
    unittest.main(verbosity=1)
