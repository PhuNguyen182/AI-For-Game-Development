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
import unittest.mock
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
        write(self.root, ".memory/notes/feedback/ask-gd.md", note("ask-gd", "Ask the main GD via multiple choice"))
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

    # ---- advice stays off git: traces are committed in game projects
    FIGURE = "D7 11.2% [measured: retention.csv, 2026-10, 1.4.0]"
    FIGURE_BARE = "ARPDAU 0.083"

    @staticmethod
    def assistant(*blocks, ts="2026-10-28T02:00:01Z"):
        return {"type": "assistant", "timestamp": ts, "message": {"content": list(blocks)}}

    @staticmethod
    def agent_use(uid, agent, prompt):
        return {"type": "tool_use", "id": uid, "name": "Agent", "input": {"subagent_type": agent, "description": "read", "prompt": prompt}}

    @staticmethod
    def tool_result(uid, text):
        return {"type": "user", "timestamp": "2026-10-28T02:00:02Z", "message": {"content": [{"type": "tool_result", "tool_use_id": uid, "content": text}]}}

    def test_adviser_brief_and_return_leave_a_pointer(self):
        out = self.capture_lines([
            self.assistant(self.agent_use("a1", "monetization-designer", "Read the economy. " + self.FIGURE_BARE)),
            self.tool_result("a1", "Status: Done\nAdvisory-Return: v1\n### F1 [High] x\n" + self.FIGURE_BARE),
        ], session="adv00001-1")
        text = out.read_text(encoding="utf-8")
        self.assertNotIn(self.FIGURE_BARE, text)
        self.assertEqual(text.count(mem.ADVISORY_POINTER), 2)

    def test_a_background_adviser_return_leaves_a_pointer(self):
        out = self.capture_lines([
            self.assistant(self.agent_use("a2", "product-owner", "Read.")),
            self.tool_result("a2", "Async agent launched successfully.\nagentId: abc123"),
            self.user('<agent-message from="abc123">No marker here, ' + self.FIGURE_BARE + "</agent-message>"),
            {"type": "attachment", "timestamp": "2026-10-28T02:00:03Z", "attachment": {"type": "queued_command", "prompt":
                "<task-notification><tool-use-id>a2</tool-use-id><summary>done</summary><result>" + self.FIGURE_BARE + "</result></task-notification>"}},
        ], session="adv00002-1")
        self.assertNotIn(self.FIGURE_BARE, out.read_text(encoding="utf-8"))

    def test_any_agent_with_a_thread_marker_leaves_a_pointer(self):
        out = self.capture_lines([
            self.assistant(self.agent_use("a3", "critic", "Advisory-Thread: pricing\nAttack this. " + self.FIGURE_BARE)),
            self.tool_result("a3", "Attacked. " + self.FIGURE_BARE),
        ], session="adv00003-1")
        self.assertNotIn(self.FIGURE_BARE, out.read_text(encoding="utf-8"))

    def test_a_return_with_the_marker_leaves_a_pointer_with_no_known_agent(self):
        out = self.capture_lines([self.user('<agent-message from="unknown">Advisory-Return: v1\n' + self.FIGURE_BARE + "</agent-message>")],
                                 session="adv00004-1")
        self.assertNotIn(self.FIGURE_BARE, out.read_text(encoding="utf-8"))

    def test_marked_assistant_text_leaves_a_pointer_and_the_rest_stays(self):
        out = self.capture_lines([self.assistant({"type": "text", "text":
            "Before.\n<!-- advisory:begin -->\n" + self.FIGURE_BARE + "\n<!-- advisory:end -->\nAfter."})], session="adv00005-1")
        text = out.read_text(encoding="utf-8")
        self.assertNotIn(self.FIGURE_BARE, text)
        self.assertIn("Before.", text)
        self.assertIn("After.", text)
        self.assertIn(mem.ADVISORY_POINTER, text)

    def test_an_unterminated_marker_strips_to_the_end_of_the_turn(self):
        out = self.capture_lines([self.assistant({"type": "text", "text": "Before.\n<!-- advisory:begin -->\n" + self.FIGURE_BARE})], session="adv00006-1")
        text = out.read_text(encoding="utf-8")
        self.assertNotIn(self.FIGURE_BARE, text)
        self.assertIn("Before.", text)

    def test_a_marker_quoted_in_prose_strips_nothing(self):
        out = self.capture_lines([self.assistant({"type": "text", "text": "Use `<!-- advisory:begin -->` here. " + self.FIGURE_BARE})], session="adv00007-1")
        self.assertIn(self.FIGURE_BARE, out.read_text(encoding="utf-8"))

    def test_a_labelled_line_without_markers_leaves_a_pointer(self):
        out = self.capture_lines([self.assistant({"type": "text", "text": "Keep this.\n" + self.FIGURE})], session="adv00008-1")
        text = out.read_text(encoding="utf-8")
        self.assertNotIn("11.2%", text)
        self.assertIn("Keep this.", text)

    def test_a_labelled_answer_leaves_a_pointer(self):
        out = self.capture_lines([
            self.assistant({"type": "tool_use", "id": "q9", "name": "AskUserQuestion", "input": {"questions": []}}),
            self.tool_result("q9", "User answered: " + self.FIGURE),
        ], session="adv00009-1")
        self.assertNotIn("11.2%", out.read_text(encoding="utf-8"))

    def test_a_foreground_adviser_continued_by_message_leaves_a_pointer(self):
        out = self.capture_lines([
            self.assistant(self.agent_use("f1", "game-designer", "Read the loop.")),
            self.tool_result("f1", "Status: Done\nAdvisory-Return: v1\n\nagentId: fg1 (use SendMessage to continue)"),
            self.user('<agent-message from="fg1">Plain follow-up, ' + self.FIGURE_BARE + "</agent-message>"),
        ], session="adv00011-1")
        self.assertNotIn(self.FIGURE_BARE, out.read_text(encoding="utf-8"))

    def test_a_follow_up_notification_under_the_message_id_leaves_a_pointer(self):
        out = self.capture_lines([
            self.assistant(self.agent_use("a5", "critic", "Advisory-Thread: pricing\nAttack.")),
            self.tool_result("a5", "Async agent launched successfully.\nagentId: bg5"),
            self.assistant({"type": "tool_use", "id": "s5", "name": "SendMessage", "input": {"to": "bg5", "message": "again"}}),
            {"type": "attachment", "timestamp": "2026-10-28T02:00:04Z", "attachment": {"type": "queued_command", "prompt":
                "<task-notification><task-id>other</task-id><tool-use-id>s5</tool-use-id><summary>done</summary><result>Bare "
                + self.FIGURE_BARE + "</result></task-notification>"}},
        ], session="adv00012-1")
        self.assertNotIn(self.FIGURE_BARE, out.read_text(encoding="utf-8"))

    def test_a_notification_naming_an_adviser_task_leaves_a_pointer(self):
        out = self.capture_lines([
            self.assistant(self.agent_use("a6", "product-owner", "Read.")),
            self.tool_result("a6", "Async agent launched successfully.\nagentId: bg6"),
            {"type": "attachment", "timestamp": "2026-10-28T02:00:04Z", "attachment": {"type": "queued_command", "prompt":
                "<task-notification><task-id>bg6</task-id><tool-use-id>unknown</tool-use-id><summary>done</summary><result>"
                + self.FIGURE_BARE + "</result></task-notification>"}},
        ], session="adv00013-1")
        self.assertNotIn(self.FIGURE_BARE, out.read_text(encoding="utf-8"))

    def test_other_agents_keep_their_text(self):
        out = self.capture_lines([
            self.assistant(self.agent_use("a4", "ui-engineer", "Fix the HUD bar.")),
            self.tool_result("a4", "Status: Done, HUD bound."),
        ], session="adv00010-1")
        text = out.read_text(encoding="utf-8")
        self.assertIn("Fix the HUD bar.", text)
        self.assertIn("HUD bound", text)
        self.assertNotIn(mem.ADVISORY_POINTER, text)
        self.assertNotIn('"advisory"', text)

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

    def test_redaction_device_ids_ip_phone(self):
        f = self.capture_lines([self.user("logcat: adid=38400000-8cf0-11bd-b23e-10b96e40000d from 203.0.113.42, "
                                          "call +84 912 345 678; local 127.0.0.1, version 1.2.3")])
        text = f.read_text(encoding="utf-8")
        for absent in ("38400000-8cf0", "203.0.113.42", "912 345 678"):
            self.assertNotIn(absent, text)
        for kept in ("[REDACTED:device id]", "[REDACTED:ip]", "[REDACTED:phone]", "127.0.0.1", "version 1.2.3"):
            self.assertIn(kept, text)

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


class AdvisoryScrubEdgeTest(unittest.TestCase):
    """QA edge cases (game-production-agent, qa-lead plan C2). The helpers are the MemTest ones, without its tests."""
    setUp = MemTest.setUp
    tearDown = MemTest.tearDown
    capture_lines = MemTest.capture_lines
    assistant = staticmethod(MemTest.assistant)
    agent_use = staticmethod(MemTest.agent_use)
    tool_result = staticmethod(MemTest.tool_result)
    user = staticmethod(MemTest.user)
    BEGIN, END = "<!-- advisory:begin -->", "<!-- advisory:end -->"
    FIG = "ARPDAU 0.083"
    FIG2 = "CPI 1.77"

    def text_of(self, out):
        return out.read_text(encoding="utf-8")

    def say(self, text, session):
        return self.text_of(self.capture_lines([self.assistant({"type": "text", "text": text})], session=session))

    def test_two_closed_blocks_in_one_turn_both_leave_a_pointer_and_the_text_between_stays(self):
        text = self.say("a\n%s\n%s\n%s\nmid\n%s\n%s\n%s\nz" % (self.BEGIN, self.FIG, self.END, self.BEGIN, self.FIG2, self.END), "edge0001-1")
        self.assertNotIn(self.FIG, text)
        self.assertNotIn(self.FIG2, text)
        self.assertEqual(text.count(mem.ADVISORY_POINTER), 2)
        self.assertIn("mid", text)
        self.assertIn("z", text)

    def test_a_begin_inside_a_block_does_not_let_the_first_figures_out(self):
        # begin, begin, end: everything from the first begin to the first end is replaced. (Nesting depth is not tracked:
        # text after that end stays, which is reported as an observation, not asserted.)
        text = self.say("Before\n%s\n%s\n%s\n%s\n%s\nAfter" % (self.BEGIN, self.FIG, self.BEGIN, self.FIG2, self.END), "edge0002-1")
        self.assertNotIn(self.FIG, text)
        self.assertNotIn(self.FIG2, text)
        self.assertIn("Before", text)
        self.assertIn("After", text)

    def test_an_end_marker_with_no_begin_neither_crashes_capture_nor_swallows_the_turn(self):
        out = self.capture_lines([self.assistant({"type": "text", "text": "Keep this.\n%s\nand this." % self.END})], session="edge0003-1")
        text = self.text_of(out)
        self.assertIn("Keep this.", text)
        self.assertIn("and this.", text)

    def test_an_indented_marker_and_one_with_trailing_blanks_still_strip(self):
        text = self.say("x\n   %s   \n%s\n\t%s\t\nTailKept" % (self.BEGIN, self.FIG, self.END), "edge0004-1")
        self.assertNotIn(self.FIG, text)
        self.assertIn("TailKept", text)  # the text after the end marker survives
        self.assertEqual(text.count(mem.ADVISORY_POINTER), 1)

    def test_markers_with_windows_line_endings_still_strip(self):
        # BUG-0009 (AC3): RX_ADVISORY_BLOCK once ended in [ \t]*$, and in multiline mode $ stops before \n only, so a "\r"
        # after the marker stopped the match and CRLF text kept its figure in a committed trace.
        crlf = "Before\n%s\n%s\n%s\nAfter" % (self.BEGIN, self.FIG, self.END)
        text = self.say(crlf.replace("\n", "\r\n"), "edge0005-1")
        self.assertNotIn(self.FIG, text)
        self.assertIn("After", text)
        self.assertEqual(text.count(mem.ADVISORY_POINTER), 1)

    def test_an_unterminated_begin_with_windows_line_endings_still_strips(self):
        # Same cause (BUG-0009), for the unterminated form.
        crlf = "Before\n%s\n%s" % (self.BEGIN, self.FIG)
        text = self.say(crlf.replace("\n", "\r\n"), "edge0006-1")
        self.assertNotIn(self.FIG, text)
        self.assertIn("Before", text)

    def test_an_adviser_return_given_as_a_list_of_text_blocks_leaves_one_pointer_per_turn(self):
        blocks = [{"type": "text", "text": "Status: Done " + self.FIG}, {"type": "text", "text": "more " + self.FIG2}]
        out = self.capture_lines([
            self.assistant(self.agent_use("e1", "product-owner", "Read the economy. " + self.FIG)),
            {"type": "user", "timestamp": "2026-10-28T02:00:02Z", "message": {"content": [{"type": "tool_result", "tool_use_id": "e1", "content": blocks}]}},
        ], session="edge0007-1")
        text = self.text_of(out)
        self.assertNotIn(self.FIG, text)
        self.assertNotIn(self.FIG2, text)
        self.assertEqual(text.count(mem.ADVISORY_POINTER), 2)

    def test_a_marked_block_inside_another_agents_list_result_strips_and_the_rest_stays(self):
        blocks = [{"type": "text", "text": "Done\n%s\n%s\n%s\nok" % (self.BEGIN, self.FIG, self.END)}]
        out = self.capture_lines([
            self.assistant(self.agent_use("e2", "ui-engineer", "Fix the HUD.")),
            {"type": "user", "timestamp": "2026-10-28T02:00:02Z", "message": {"content": [{"type": "tool_result", "tool_use_id": "e2", "content": blocks}]}},
        ], session="edge0008-1")
        text = self.text_of(out)
        self.assertNotIn(self.FIG, text)
        self.assertIn("Done", text)
        self.assertIn("ok", text)

    def test_a_marked_block_in_a_list_answer_strips(self):
        blocks = [{"type": "text", "text": "User said\n%s\n%s\n%s" % (self.BEGIN, self.FIG, self.END)}]
        out = self.capture_lines([
            self.assistant({"type": "tool_use", "id": "e3", "name": "AskUserQuestion", "input": {"questions": []}}),
            {"type": "user", "timestamp": "2026-10-28T02:00:02Z", "message": {"content": [{"type": "tool_result", "tool_use_id": "e3", "content": blocks}]}},
        ], session="edge0009-1")
        self.assertNotIn(self.FIG, self.text_of(out))

    def test_a_marker_inside_an_ordinary_tool_result_is_never_captured(self):
        out = self.capture_lines([
            self.assistant({"type": "tool_use", "id": "e4", "name": "Bash", "input": {"command": "cat plan.md"}}),
            self.tool_result("e4", "%s\n%s\n%s" % (self.BEGIN, self.FIG, self.END)),
            self.assistant({"type": "text", "text": "Read it."}),
        ], session="edge0010-1")
        self.assertNotIn(self.FIG, self.text_of(out))

    def test_assistant_text_given_as_a_plain_string_is_not_captured(self):
        # The parser takes assistant content only as a list of blocks, so a string-form turn cannot reach a trace.
        out = self.capture_lines([{"type": "assistant", "timestamp": "2026-10-28T02:00:01Z", "message": {"content": "plain " + self.FIG}},
                                  self.assistant({"type": "text", "text": "kept"})], session="edge0011-1")
        text = self.text_of(out)
        self.assertNotIn(self.FIG, text)
        self.assertIn("kept", text)

    def test_the_exact_label_is_replaced_whole_line_wherever_it_sits_in_the_line(self):
        text = self.say("Keep.\nStart of line D7 11.2%% [measured: r.csv, 2026-10, 1.4.0] end of line %s\nKeep too." % self.FIG, "edge0012-1")
        self.assertNotIn("11.2%", text)
        self.assertNotIn(self.FIG, text)
        self.assertIn("Keep.", text)
        self.assertIn("Keep too.", text)

    def test_no_figure_survives_anywhere_under_the_memory_folder(self):
        # The fixture holds one known figure in every place a capture reads; the check reads the bytes of every file
        # capture wrote (traces, state), not just the trace the assertions above look at.
        fig = "ARPDAU 0.0831"
        labelled = "D7 11.27%% [measured: retention.csv, 2026-10, 1.4.0] %s" % fig
        self.capture_lines([
            self.assistant(self.agent_use("g1", "monetization-designer", "Read. " + fig)),
            self.tool_result("g1", "Status: Done\nAdvisory-Return: v1\n### F1 [High] x\n" + fig),
            self.assistant({"type": "text", "text": "Before.\n%s\n%s\n%s\nAfter." % (self.BEGIN, fig, self.END)}),
            self.assistant({"type": "text", "text": "Plain.\n" + labelled}),
            self.assistant({"type": "tool_use", "id": "g2", "name": "AskUserQuestion", "input": {"questions": []}}),
            self.tool_result("g2", "User answered: " + labelled),
            self.assistant({"type": "text", "text": "Tail."}),
        ], session="edge0013-1")
        files = [p for p in (self.root / ".memory").rglob("*") if p.is_file()]
        self.assertTrue(any(p.suffix == ".jsonl" for p in files), files)
        for p in files:
            data = p.read_bytes().decode("utf-8", "replace")
            self.assertNotIn(fig, data, p.name)
            self.assertNotIn("0.0831", data, p.name)
            self.assertNotIn("11.27", data, p.name)


CSC = Path(os.environ.get("WINDIR", "")) / "Microsoft.NET" / "Framework64" / "v4.0.30319" / "csc.exe"


@unittest.skipUnless(os.name == "nt" and CSC.exists(), "needs Windows and its csc.exe to build a stub git.exe")
class TestPlantedGit(unittest.TestCase):
    """A git in the working folder never runs: CreateProcess and shutil.which both try that folder before PATH.
    Unless NoDefaultCurrentDirectoryInExePath is set, as a Claude Code session sets it: nothing promises a hook that, so it is cleared."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.addCleanup(os.chdir, os.getcwd())
        env = unittest.mock.patch.dict(os.environ)
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop("NoDefaultCurrentDirectoryInExePath", None)
        self.root = self.tmp / "repo"
        self.root.mkdir()
        git(self.root, "init", "-q")
        write(self.root, "real.txt", "x")
        git(self.root, "add", "real.txt")
        self.planted = self.tmp / "planted"
        self.planted.mkdir()
        self.marker = self.tmp / "ran.txt"

    def stub_exe(self):
        src = self.tmp / "stub.cs"
        src.write_text('class P { static int Main() { System.IO.File.WriteAllText(@"%s", "ran"); System.Console.Write("planted.txt"); return 0; } }' % self.marker,
                       encoding="utf-8")
        subprocess.run([str(CSC), "/nologo", "/out:" + str(self.planted / "git.exe"), str(src)], check=True, capture_output=True)

    def test_a_git_exe_in_the_working_folder_never_runs(self):
        self.stub_exe()
        os.chdir(self.planted)
        self.assertEqual(mem.list_files(self.root), ["real.txt"])
        self.assertFalse(self.marker.exists())

    def test_a_git_cmd_in_the_working_folder_never_runs(self):
        (self.planted / "git.cmd").write_text('@echo ran> "%s"' % self.marker, encoding="ascii")
        os.chdir(self.planted)
        self.assertEqual(mem.list_files(self.root), ["real.txt"])
        self.assertFalse(self.marker.exists())

    def test_a_relative_path_entry_is_not_searched(self):
        self.stub_exe()
        os.chdir(self.planted)
        with unittest.mock.patch.dict(os.environ, {"PATH": "." + os.pathsep + os.environ["PATH"]}):
            self.assertNotEqual(Path(mem.git_exe()).parent, self.planted)

    def test_no_git_on_path_is_the_error_a_missing_program_raises(self):
        with unittest.mock.patch.dict(os.environ, {"PATH": str(self.tmp)}):
            with self.assertRaises(FileNotFoundError):
                mem.git_exe()


if __name__ == "__main__":
    unittest.main(verbosity=1)
