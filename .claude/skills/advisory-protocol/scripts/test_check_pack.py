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

    def table(self, name, text):
        (self.d / name).write_text(text, encoding="utf-8")

    def fails(self, needle="identifies"):
        return any(needle in p for p in check_pack.check_pack(self.d))

    def test_an_aggregated_pack_passes(self):
        self.table("retention.csv", "cohort_date,build_id,d1,d7,d30\n2026-10-01,140,0.4,0.15,0.05\n")
        self.table("ads.csv", "placement_id,impressions_per_dau,ecpm\nrewarded,1.5,12\n")
        self.assertEqual(check_pack.check_pack(self.d), [])

    def test_identifying_headers_fail_in_any_spelling(self):
        for header in ("user_id", "User ID", "userId", "email", "IDFA", "gaid", "advertising-id", "user_pseudo_id", "ip_address",
                       "purchase_token", "id", "uuid", "guid", "user_hash", "customer", "steamid", "playfab_id", "push_token",
                       "user_agent", "latitude", "device_id", "order_id", "transactionId", "session_key"):
            self.table("x.csv", "cohort_date,%s,d1\n" % header)
            self.assertTrue(self.fails(), header)

    def test_dimension_ids_and_metrics_pass(self):
        self.table("x.csv", "build_id,level_id,sku_id,placement_id,users_active,ip_share_percent,playerbase,is_paid,d1\n1,2,3,4,5,6,7,8,9\n")
        self.assertEqual(check_pack.check_pack(self.d), [])

    def test_every_spreadsheet_separator_is_split(self):
        for sep in (",", ";", "\t", "|"):
            self.table("x.csv", sep.join(("cohort_date", "user_id", "revenue_usd")) + "\n1" + sep + "2" + sep + "3\n")
            self.assertTrue(self.fails(), repr(sep))

    def test_a_header_holding_a_separator_fails(self):
        self.table("x.csv", "date,user_id;revenue\n1,2\n")
        self.assertTrue(self.fails("still holds a separator"))

    def test_identifying_cell_values_fail_without_echoing_them(self):
        for cell, what in (("a.b@example.com", "an email"), ("8.8.8.8", "an IP"), ("+84 912 345 678", "a phone"),
                           ("123e4567-e89b-12d3-a456-426614174000", "a UUID")):
            self.table("x.csv", "segment,d1\n%s,0.4\n" % cell)
            problems = check_pack.check_pack(self.d)
            self.assertTrue(any(what in p for p in problems), cell)
            self.assertFalse(any(cell in p for p in problems), cell)

    def test_bom_on_the_first_header_does_not_hide_it(self):
        self.table("x.csv", "﻿user_id,d1\n1,2\n")
        self.assertTrue(self.fails())

    def test_a_missing_manifest_fails(self):
        (self.d / "manifest.md").unlink()
        self.table("x.csv", "date,d1\n")
        self.assertTrue(self.fails("manifest"))

    def test_an_uncheckable_file_is_refused(self):
        self.table("x.csv", "date,d1\n")
        self.table("raw.json", "{}")
        self.assertTrue(self.fails("refused"))

    def test_an_empty_pack_fails(self):
        self.assertTrue(self.fails("no CSV"))

    def test_a_missing_folder_cannot_be_checked(self):
        self.assertEqual(check_pack.main(["check_pack.py", str(self.d / "nope")]), 2)


if __name__ == "__main__":
    unittest.main()
