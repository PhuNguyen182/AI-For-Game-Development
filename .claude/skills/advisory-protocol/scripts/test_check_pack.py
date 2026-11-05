"""Tests for check_pack.py. Run: python -I .claude/skills/advisory-protocol/scripts/test_check_pack.py"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_pack  # noqa: E402


class PackTest(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        (self.d / "manifest.md").write_text("source: Firebase\n", encoding="utf-8")

    def table(self, name, header):
        (self.d / name).write_text(header + "\n1,2,3\n", encoding="utf-8")

    def test_an_aggregated_pack_passes(self):
        self.table("retention.csv", "cohort_date,build,d1,d7,d30")
        self.table("ads.csv", "placement,impressions_per_dau,ecpm")
        self.assertEqual(check_pack.check_pack(self.d), [])

    def test_identifying_headers_fail_in_any_spelling(self):
        for header in ("user_id", "User ID", "userId", "email", "IDFA", "gaid", "advertising-id", "user_pseudo_id", "ip_address", "purchase_token"):
            self.table("x.csv", "cohort_date,%s,d1" % header)
            problems = check_pack.check_pack(self.d)
            self.assertTrue(any("identifies" in p for p in problems), header)

    def test_a_metric_name_holding_a_banned_word_passes(self):
        self.table("x.csv", "users_active,ip_share_percent,playerbase,d1")
        self.assertEqual(check_pack.check_pack(self.d), [])

    def test_tsv_headers_are_read(self):
        (self.d / "x.tsv").write_text("date\tuser_id\n1\t2\n", encoding="utf-8")
        self.assertTrue(check_pack.check_pack(self.d))

    def test_bom_on_the_first_header_does_not_hide_it(self):
        (self.d / "x.csv").write_text("﻿user_id,d1\n1,2\n", encoding="utf-8")
        self.assertTrue(check_pack.check_pack(self.d))

    def test_a_missing_manifest_fails(self):
        (self.d / "manifest.md").unlink()
        self.table("x.csv", "date,d1")
        self.assertTrue(any("manifest" in p for p in check_pack.check_pack(self.d)))

    def test_an_uncheckable_file_is_refused(self):
        self.table("x.csv", "date,d1")
        (self.d / "raw.json").write_text("{}", encoding="utf-8")
        self.assertTrue(any("refused" in p for p in check_pack.check_pack(self.d)))

    def test_an_empty_pack_fails(self):
        self.assertTrue(any("no CSV" in p for p in check_pack.check_pack(self.d)))

    def test_a_missing_folder_cannot_be_checked(self):
        self.assertEqual(check_pack.main(["check_pack.py", str(self.d / "nope")]), 2)


if __name__ == "__main__":
    unittest.main()
