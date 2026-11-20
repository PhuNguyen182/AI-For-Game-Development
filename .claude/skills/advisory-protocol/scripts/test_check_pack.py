"""Tests for check_pack.py. Run: python -I .claude/skills/advisory-protocol/scripts/test_check_pack.py

Every past review finding has its own named case, so a rewrite that drops a rule fails here.
"""
import shutil
import subprocess
import sys
import tempfile
import time
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

    def test_non_ascii_headers_fail_and_are_never_echoed(self):  # review round 4, security N1
        for h in ("cohort 用户名", "level имя", "user 王小明", "user ８８８", "ｕｓｅｒ"):
            with self.subTest(header=h):
                problems = self.one_column(h)
                self.assertTrue(problems, h)
                self.assertFalse(any(h in p for p in problems), h)

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


class PackEdgeTest(unittest.TestCase):
    """QA edge cases (game-production-agent, qa-lead plan C5). The helpers are the PackTest ones, without its tests."""
    setUp = PackTest.setUp
    table = PackTest.table
    one_column = PackTest.one_column

    def raw_table(self, data, name="x.csv"):
        for old in self.d.glob("*.[ct]sv"):
            old.unlink()
        (self.d / name).write_bytes(data)
        return check_pack.check_pack(self.d)

    def test_the_user_id_header_is_a_literal_case_not_a_pattern(self):
        self.assertIn("user_id", FAIL_IDENTIFIES)
        problems = self.one_column("user_id")
        self.assertEqual(problems, ["x.csv: column 1 ('user_id') identifies a person or device"])

    def test_a_quoted_cell_holding_the_separator_is_one_cell(self):
        self.assertEqual(self.table('segment,d1\n"paid, high spenders",0.4\n'), [])

    def test_a_quoted_cell_holding_a_quote_and_a_newline_is_one_cell(self):
        self.assertEqual(self.table('segment,d1\n"paid ""big""\nspenders",0.4\n'), [])

    def test_an_identifier_inside_a_quoted_cell_with_a_comma_still_fails_without_echo(self):
        problems = self.table('segment,d1\n"hello, a.b@example.com",0.4\n')
        self.assertTrue(any("email" in p for p in problems))
        self.assertFalse(any("example" in p for p in problems))

    def test_a_quoted_header_holding_a_separator_fails_closed(self):
        self.assertTrue(any("separator" in p for p in self.table('"user,id",d1\n1,2\n')))

    def test_windows_line_endings_are_read_and_a_bad_header_still_fails(self):
        self.assertEqual(self.raw_table(b"cohort_date,d1\r\n2026-10-01,0.4\r\n"), [])
        self.assertEqual(self.raw_table(b"user_id,d1\r\n1,0.4\r\n"), ["x.csv: column 1 ('user_id') identifies a person or device"])
        self.assertTrue(any("email" in p for p in self.raw_table(b"segment,d1\r\na.b@example.com,0.4\r\n")))

    def test_old_mac_line_endings_are_read_too(self):
        self.assertEqual(self.raw_table(b"cohort_date,d1\r2026-10-01,0.4\r"), [])  # a clean CR-only pack passes
        self.assertEqual(self.raw_table(b"user_id,d1\r1,0.4\r"), ["x.csv: column 1 ('user_id') identifies a person or device"])

    def test_bytes_that_are_not_utf8_are_unreadable_and_never_echoed(self):
        for data in (b"d1\n\xff\xfe\x00\n", b"d1\n\xc3\x28\n", "d1\n1\n".encode("utf-16")):
            with self.subTest(data=data[:6]):
                problems = self.raw_table(data)
                self.assertEqual(problems, ["x.csv: unreadable (UnicodeDecodeError)"])

    def test_zero_width_and_full_width_headers_that_hide_a_person_word_are_rejected(self):
        for h in ("use​r_id", "u‍ser_id", "us﻿er_id", "user​id", "ｕｓｅｒ_id", "ＵＳＥＲ", "user　id"):
            with self.subTest(header=h):
                self.assertTrue(any("column 1" in p for p in self.one_column(h)), h)

    def test_a_full_width_header_is_never_echoed_when_it_is_outside_the_vocabulary(self):
        for h in ("ｕｓｅｒ_id", "use​r_id", "ＵＳＥＲ"):
            with self.subTest(header=h):
                problems = self.one_column(h)
                self.assertTrue(problems)
                self.assertFalse(any(h in p or ascii(h)[1:-1] in p for p in problems), problems)

    def test_a_ten_digit_full_width_run_makes_its_column_text_and_is_a_long_digit_run_without_echo(self):
        # RX_NUMBER starts with an ASCII [1-9] or 0, so a full-width number is not a number: even under the numeric-looking
        # header d1 the column is text and the text rule ("holds a long digit run") applies, not the numeric-id rule.
        ten = "".join(chr(0xFF10 + int(c)) for c in "0912345678")
        for header, table, expected in (("segment", "segment,d1\n%s,0.4\n", "x.csv: column 1 ('segment') holds a long digit run"),
                                        ("d1", "d1\n0.4\n%s\n", "x.csv: column 1 ('d1') holds a long digit run")):
            with self.subTest(header=header):
                self.assertEqual(self.table(table % ten), [expected])

    def test_a_fifteen_digit_full_width_number_is_a_long_digit_run_in_a_text_column_not_a_numeric_id(self):
        cell = "".join(chr(0xFF10 + int(c)) for c in "123456789012345")
        self.assertEqual(self.table("d1\n0.4\n%s\n" % cell), ["x.csv: column 1 ('d1') holds a long digit run"])

    def test_identifying_values_fail_under_several_allowed_headers(self):
        values = {"a UUID": "123e4567-e89b-12d3-a456-426614174000", "an email": "a.b@example.com", "an IP address": "8.8.8.8"}
        for header in ("segment", "campaign", "placement", "country_code", "event_name"):
            for kind, cell in values.items():
                with self.subTest(header=header, kind=kind):
                    problems = self.table("%s,d1\n%s,0.4\n" % (header, cell))
                    self.assertTrue(any(kind in p for p in problems), problems)
                    self.assertFalse(any(cell in p for p in problems))

    def test_an_ipv4_shaped_value_under_a_version_or_build_header_is_allowed_by_design(self):
        # check_pack.py exempts "version" and "build" headers so 1.0.0.140 passes; a real address there passes too.
        self.assertEqual(self.table("app_version,d1\n1.0.0.140,0.4\n"), [])

    def test_header_case_does_not_change_the_verdict(self):
        for h in ("UsEr_Id", "USER_ID", "User_ID", "pLaYeR_iD", "DEVICE_ID", "E-Mail"):
            with self.subTest(header=h):
                self.assertTrue(any("identifies" in p for p in self.one_column(h)), h)
        for h in ("Cohort_DATE", "D1_Retention", "ARPDAU", "Revenue_Per_User", "eCPM_USD"):
            with self.subTest(header=h):
                self.assertEqual(self.one_column(h), [], h)

    def test_a_large_file_is_checked_in_bounded_time(self):
        rows = "".join("2026-10-%02d,1.0.%d,0.4,0.15,%d,0.15\n" % (i % 28 + 1, i % 50, i) for i in range(100000))
        start = time.monotonic()
        problems = self.table("cohort_date,build_version,d1,d7,active_users,revenue_usd\n" + rows)
        elapsed = time.monotonic() - start
        self.assertEqual(problems, [])
        self.assertLess(elapsed, 30.0, "100k rows took %.1fs" % elapsed)

    def test_a_huge_cell_or_header_fails_closed_in_bounded_time(self):
        start = time.monotonic()
        self.assertEqual(self.table("segment\n" + "a" * 3000000 + "\n"), ["x.csv: unreadable (Error)"])
        self.assertEqual(self.table("a" * 3000000 + "\n1\n"), ["x.csv: unreadable (Error)"])
        self.assertLess(time.monotonic() - start, 30.0)

    def test_a_wide_file_is_checked_in_bounded_time(self):
        start = time.monotonic()
        problems = self.table(",".join(["d1"] * 20000) + "\n" + ",".join(["1"] * 20000) + "\n")
        self.assertEqual(problems, [])
        self.assertLess(time.monotonic() - start, 30.0)

    def run_cli(self):
        r = subprocess.run([sys.executable, "-I", str(Path(check_pack.__file__)), str(self.d)], capture_output=True)
        return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")

    def test_the_exit_message_holds_neither_the_unknown_word_nor_the_value(self):
        word, value = "zebrafoo", "a.b.secret@example.com"
        (self.d / "x.csv").write_text("%s,segment\n1,%s\n" % (word, value), encoding="utf-8")
        code, out, err = self.run_cli()
        self.assertEqual(code, 1)
        self.assertIn("FAIL", out)
        for text in (out, err):
            self.assertNotIn(word, text)
            self.assertNotIn(value, text)
            self.assertNotIn("secret", text)
            self.assertNotIn("example", text)
        self.assertIn("column 1", out)

    def test_the_exit_message_holds_no_value_for_every_identifying_cell(self):
        for cell in ID_VALUES:
            with self.subTest(cell=cell):
                (self.d / "x.csv").write_text("segment,d1\n%s,0.4\n" % cell, encoding="utf-8")
                code, out, err = self.run_cli()
                self.assertEqual(code, 1, cell)
                self.assertNotIn(cell, out + err)

    def test_a_non_utf8_pack_exits_1_and_echoes_no_byte(self):
        (self.d / "x.csv").write_bytes(b"d1\n\xff\xfeSENTINELVALUE\n")
        code, out, err = self.run_cli()
        self.assertEqual(code, 1)
        self.assertNotIn("SENTINELVALUE", out + err)
        self.assertNotIn("�", out + err)


if __name__ == "__main__":
    unittest.main()
