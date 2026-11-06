"""Tests for check_pack.py. Run: python -I .claude/skills/advisory-protocol/scripts/test_check_pack.py

Every past review finding has its own named case, so a rewrite that drops a rule fails here.
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_pack  # noqa: E402

FAIL_IDENTIFIES = [
    "user_id", "User ID", "userId", "playerID", "uid", "user", "customer", "member_id", "account_id",
    # security round 2, N1: a dimension word before a person word
    "platform_user_id", "store_account_id", "network_player_id", "event_user_id",
    # code review round 2, High: email and IP suffixes
    "user_email", "player_email", "e-mail", "client_ip_address", "user_ip_address", "ip", "ip_address", "ipv6",
    "idfa", "IDFA", "idfv", "gaid", "aaid", "gps_adid", "advertising-id",
    "device_id", "android_id", "app_instance_id", "firebase_instance_id", "install_id", "user_pseudo_id",
    "steamid", "steam_id", "PlayFabId", "game_center_id", "fb_id", "appsflyer_id", "external_id", "customer_user_id",
    "id", "uuid", "guid", "name", "key", "token", "code",
    "purchase_token", "push_token", "receipt", "order_id", "transactionId", "session_id", "session_key",
    "user_agent", "latitude", "lat", "lng", "username", "nickname", "display_name", "first_name", "gamertag", "phone_number",
    "msisdn", "imei", "mac_address", "zip_code", "referral_code",
    "revenue_per_user_id",
    "user 8.8.8.8",  # review round 3, S1
]
# Review round 3, S1: digit groups are an open set, so a header made of them is a value, never a name.
FAIL_VOCABULARY = ["playerbase", "foo_metric", "Mã người chơi", "8.8.8.8", "+84 912 345 678", "2026-10-01", "level 1 2 3"]
# Identifying values: each fails in a text column and in an otherwise numeric one (review round 3, High: the numeric shortcut).
ID_VALUES = ["a.b@example.com", "8.8.8.8", "8.8.8.8:53", "2001:db8::1", "fe80::1ff:fe23:4567:890a", "+84 912 345 678",
             "+84912345678", "+14155552671", "0912345678", "0912 345 678", "091 234 5678", "(091) 234-5678",
             "123e4567-e89b-12d3-a456-426614174000", "0123456789abcdef0123456789abcdef", "a1b2c3d4e5f6a7b8",
             "id 123456789", "xXSlayer99Xx", "x" * 81, "1.0.0.140"]
PASS_HEADERS = [
    "cohort_date", "build_id", "level_id", "sku_id", "placement_id", "ad_unit_id", "ad_unit_name", "level_name", "event_name",
    "country_code", "currency_code", "app_version", "build_version", "platform", "os",
    "d1", "d30", "D1 retention", "retention_d7", "dau", "arpdau", "arppu", "ecpm", "eCPM", "ipm", "impressions_per_dau",
    "fill_rate", "revenue_usd", "iap_revenue", "is_paid",
    "active_users", "new_users", "users_active", "paying_users", "installs", "payers", "crash_free_users",
    "Avg. engagement time per active user", "Event count per user", "revenue_per_user",
    "level 10", "season 2026", "level 1-10",
]


class PackTest(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        (self.d / "manifest.md").write_text("source: Firebase\n", encoding="utf-8")

    def table(self, text, name="x.csv"):
        for old in self.d.glob("*.[ct]sv"):
            old.unlink()
        (self.d / name).write_text(text, encoding="utf-8")
        return check_pack.check_pack(self.d)

    def one_column(self, header, cell="1"):
        return self.table("%s\n%s\n" % (header, cell))

    def test_identifying_headers_fail(self):
        for h in FAIL_IDENTIFIES:
            with self.subTest(header=h):
                self.assertTrue(any("identifies" in p for p in self.one_column(h)), h)

    def test_unknown_words_fail_as_vocabulary(self):
        for h in FAIL_VOCABULARY:
            with self.subTest(header=h):
                self.assertTrue(any("vocabulary" in p for p in self.one_column(h)), h)

    def test_aggregate_headers_pass(self):
        for h in PASS_HEADERS:
            with self.subTest(header=h):
                self.assertEqual(self.one_column(h), [], h)

    def test_an_aggregated_pack_passes(self):
        self.table("cohort_date,build_version,d1,d7,active_users,ipm,revenue_usd\n2026-10-01,1.0.0.140,0.4,0.15,1200,12.5,0.15000000000000002\n")
        self.assertEqual(check_pack.main(["check_pack.py", str(self.d)]), 0)

    def test_a_failing_pack_returns_1(self):
        self.table("user_id,d1\n1,2\n")
        self.assertEqual(check_pack.main(["check_pack.py", str(self.d)]), 1)

    def test_every_spreadsheet_separator_is_split(self):  # security round 1, High
        for sep in (",", ";", "\t", "|"):
            with self.subTest(sep=repr(sep)):
                problems = self.table(sep.join(("cohort_date", "user_id", "revenue_usd")) + "\n1" + sep + "2" + sep + "3\n")
                self.assertTrue(any("identifies" in p for p in problems))

    def test_a_header_holding_a_separator_fails(self):
        self.assertTrue(any("separator" in p for p in self.table("date,user_id;revenue\n1,2\n")))

    def test_space_and_colon_separated_files_still_fail(self):
        for text in ("date user_id revenue\n1 2 3\n", "date:user_id:revenue\n1:2:3\n"):
            with self.subTest(text=text):
                self.assertTrue(self.table(text))

    def test_a_tsv_passes(self):
        self.assertEqual(self.table("cohort_date\td1\n2026-10-01\t0.4\n", name="x.tsv"), [])

    def test_bom_before_an_identifier_fails(self):
        self.assertTrue(any("identifies" in p for p in self.table("﻿user_id,d1\n1,2\n")))

    def test_an_empty_header_fails(self):
        self.assertTrue(any("no header" in p for p in self.table("d1,,d7\n1,2,3\n")))

    def test_a_row_longer_than_the_header_fails_and_its_tail_is_scanned(self):  # security round 2, N2
        problems = self.table("segment,d1\npaid,0.4,a.b@example.com\n")
        self.assertTrue(any("row 2 has 3 cells" in p for p in problems))
        self.assertTrue(any("past the header" in p and "email" in p for p in problems))
        self.assertFalse(any("a.b@example.com" in p for p in problems))

    def test_identifying_values_fail_without_echo(self):
        for cell in ID_VALUES:
            with self.subTest(cell=cell):
                problems = self.table("segment,d1\n%s,0.4\n" % cell)
                self.assertTrue(problems, cell)
                self.assertFalse(any(cell in p for p in problems), cell)

    def test_an_identifier_in_a_numeric_column_still_fails(self):  # review round 3, High
        for cell in ID_VALUES:
            with self.subTest(cell=cell):
                problems = self.table('d1\n0.4\n"%s"\n' % cell)
                self.assertTrue(problems, cell)
                self.assertFalse(any(cell in p for p in problems), cell)

    def test_number_grammar(self):
        self.assertIsNone(check_pack.RX_NUMBER.match("+84912345678"))
        for n in ("-0.5", "12%", "1e-05", "0", "1234567890123"):
            with self.subTest(n=n):
                self.assertTrue(check_pack.RX_NUMBER.match(n), n)

    def test_a_numeric_header_is_never_echoed(self):  # review round 3, S1
        for h in ("8.8.8.8", "+84 912 345 678", "user 8.8.8.8"):
            with self.subTest(header=h):
                problems = self.one_column(h)
                self.assertTrue(problems)
                self.assertFalse(any("8.8" in p or "912" in p for p in problems), h)
        self.assertFalse(any("8.8" in p for p in self.table("level 8.8.8.8\na.b@example.com\n")))

    def test_row_numbers_count_blank_rows(self):  # review round 3, Low
        problems = self.table("segment,d1\n\npaid,0.4,x\n")
        self.assertTrue(any("row 3 has 3 cells" in p for p in problems), problems)
        self.assertFalse(any("row 2 has" in p for p in problems))

    def test_a_long_number_fails_in_a_numeric_column(self):
        self.assertTrue(any("long numeric id" in p for p in self.table("d1\n76561198000000000\n")))

    def test_a_count_column_holding_text_fails(self):
        self.assertTrue(any("count column" in p for p in self.table("users\nalice\n")))

    def test_ordinary_values_pass(self):
        for header, cell in (("build_version", "1.0.0.140"), ("cohort_date", "2026-10-01"), ("cohort_date", "2026-10-01 13:00"),
                             ("cohort_date", "20261001"), ("d1", "0.15000000000000002"), ("revenue_usd", "1234567890123"),
                             ("placement", "rewarded_video"), ("country_code", "VN"), ("app_version", "1.4.0"),
                             ("level_name", "Level 10"), ("cohort_date", "13:00:00"), ("d1", "-0.5"), ("d1", "12%"),
                             ("d1", "1e-05"), ("cohort_date", "05/10/2026")):
            with self.subTest(cell=cell):
                self.assertEqual(self.table("%s\n%s\n" % (header, cell)), [], cell)

    def test_an_unknown_header_is_never_echoed(self):
        problems = self.one_column("a.b@example.com")
        self.assertTrue(problems)
        self.assertFalse(any("example" in p for p in problems))

    def test_vocabulary_invariants(self):
        self.assertEqual(check_pack.ALLOWED & check_pack.NEVER, set())
        self.assertTrue((check_pack.DIMENSIONS | check_pack.TAILS) <= check_pack.ALLOWED)

    def test_a_missing_manifest_fails(self):
        (self.d / "manifest.md").unlink()
        self.assertTrue(any("manifest" in p for p in self.table("d1\n1\n")))

    def test_an_uncheckable_file_is_refused(self):
        self.table("d1\n1\n")
        (self.d / "raw.json").write_text("{}", encoding="utf-8")
        self.assertTrue(any("refused" in p for p in check_pack.check_pack(self.d)))

    def test_an_empty_pack_fails(self):
        self.assertTrue(any("no CSV" in p for p in check_pack.check_pack(self.d)))

    def test_a_missing_folder_cannot_be_checked(self):
        self.assertEqual(check_pack.main(["check_pack.py", str(self.d / "nope")]), 2)


if __name__ == "__main__":
    unittest.main()
