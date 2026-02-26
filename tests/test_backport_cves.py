"""
Tests validating the backported CVE fixes from Django 4.2.x to 3.2.x.

Tests are taken from upstream Django security commits and adapted for
3.2.x where necessary. Each test class documents the CVE and upstream
commit it covers.
"""
import gc
import time
from datetime import datetime
from unittest import mock

from django.contrib.auth.hashers import (
    UNUSABLE_PASSWORD_PREFIX,
    check_password,
    make_password,
)
from django.core.exceptions import DisallowedRedirect, SuspiciousFileOperation, SuspiciousOperation
from django.core.validators import URLValidator, ValidationError
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.template.defaultfilters import floatformat
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils.html import strip_tags, urlize
from django.utils.http import MAX_URL_REDIRECT_LENGTH
from django.utils.log import log_response
from django.utils.translation.trans_real import get_supported_language_variant


# -- CVE-2024-39329: Timing side-channel in password check --
# Upstream commit: 5d8645857936 (4.2.x: 75e53690cd)
#
# Upstream tests hasher.verify() directly, but 3.2 applies the fix in
# check_password() instead. Adapted to test check_password() which is
# where the fake runtime logic lives in 3.2.
class CVE_2024_39329_Tests(SimpleTestCase):
    @override_settings(
        PASSWORD_HASHERS=["django.contrib.auth.hashers.PBKDF2PasswordHasher"]
    )
    def test_check_password_calls_make_password_to_fake_runtime(self):
        encoded = make_password("lètmein")

        with mock.patch(
            "django.contrib.auth.hashers.make_password",
            wraps=make_password,
        ) as mock_make_password:
            # Correct password: make_password is NOT called to fake runtime.
            self.assertTrue(check_password("lètmein", encoded))
            mock_make_password.assert_not_called()

            # Incorrect password: make_password is NOT called to fake runtime.
            self.assertFalse(check_password("incorrect", encoded))
            mock_make_password.assert_not_called()

            # Unusable password: make_password IS called once to fake runtime.
            self.assertFalse(check_password("lètmein", UNUSABLE_PASSWORD_PREFIX))
            mock_make_password.assert_called_once()


# -- CVE-2024-39330: Path traversal in Storage.save() --
# Upstream commit: 2b00edc0151a (4.2.x: cd237758d6)
#
# Upstream 4.2 expects "Could not find file name" error message. Our 3.2
# backport raises "Detected path traversal attempt" instead. Adapted
# message accordingly.
class CVE_2024_39330_Tests(SimpleTestCase):
    def test_save_file_name_with_dot_segments(self):
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage

        msg = "Detected path traversal attempt in"
        tests = [
            "../path",
            ".././path",
            "/../path",
            "../../path",
            "../../../path",
        ]
        for file_name in tests:
            with self.subTest(file_name=file_name):
                with self.assertRaisesMessage(SuspiciousFileOperation, msg):
                    default_storage.save(file_name, ContentFile(""))


# -- CVE-2024-39614: DoS via get_supported_language_variant() --
# Upstream commit: 9e9792228a6b (4.2.x: 6c3c32ef3d)
class CVE_2024_39614_Tests(SimpleTestCase):
    def test_get_supported_language_variant_rejects_none_language(self):
        """Regression test for CVE-2024-39614."""
        tests = [None, ""]
        for lang_code in tests:
            with self.subTest(lang_code=lang_code):
                with self.assertRaises(LookupError):
                    get_supported_language_variant(lang_code)


# -- CVE-2024-41989: DoS via floatformat template filter --
# Upstream commit: c19465ad87e3 (4.2.x: 5e2f4f3b9c)
#
# Upstream adds test_max_decimal_places (floatformat(1.2345, 1001) == "").
# 3.2's floatformat doesn't have the max decimal places guard -- instead
# the fix prevents DoS from scientific notation like "1e200". We test
# that the large-number inputs return quickly without hanging.
class CVE_2024_41989_Tests(SimpleTestCase):
    def test_negative_zero_values(self):
        tests = [
            (-0.01, -1, "0.0"),
            (-0.001, 2, "0.00"),
        ]
        for num, decimal_pos, expected in tests:
            with self.subTest(num=num, decimal_pos=decimal_pos):
                self.assertEqual(floatformat(num, decimal_pos), expected)

    def test_large_number_does_not_hang(self):
        # The key property: these return quickly without DoS.
        cases = [
            "1e200",
            "1E200",
            "1E10000000000000000",
            "-1E10000000000000000",
        ]
        for value in cases:
            with self.subTest(value=value):
                result = floatformat(value)
                self.assertIn(value, result)


# -- CVE-2024-41990: DoS via urlize/urlizetrunc --
# Upstream commit: ecf1f8fb900f (4.2.x: fa83e26b6c)
class CVE_2024_41990_Tests(SimpleTestCase):
    def test_urlize_unchanged_inputs(self):
        tests = [
            ("a" + "@a" * 50000),
            ("a" + "." * 50000),
            ("a" + "a" * 50000),
        ]
        for test in tests:
            with self.subTest(test=test):
                self.assertEqual(urlize(test), test)


# -- CVE-2024-41991: DoS via URLValidator with long URLs --
# Upstream commit: 5f1757142feb (4.2.x: daa54e0a8a)
class CVE_2024_41991_Tests(SimpleTestCase):
    def test_long_url_rejected(self):
        validator = URLValidator()
        with self.assertRaises(ValidationError):
            validator("http://" + "a" * 2084)


# -- CVE-2024-42005: SQL injection via QuerySet.values()/values_list() --
# Upstream commit: c87bfaacf8fb (4.2.x: 77e78d8c33)
#
# Upstream tests with Author.objects.values() which requires DB setup.
# We test the check_alias() validation directly since it's the core fix.
class CVE_2024_42005_Tests(SimpleTestCase):
    def test_values_raw_expression_rejected(self):
        """Crafted column aliases with SQL injection must be rejected."""
        from django.db.models.sql.query import Query

        crafted_alias = """name") AS "name"""
        msg = (
            "Column aliases cannot contain whitespace characters, quotation marks, "
            "semicolons, or SQL comments."
        )
        q = Query(None)
        with self.assertRaisesMessage(ValueError, msg):
            q.check_alias(crafted_alias)


# -- CVE-2024-45230: DoS via urlize/urlizetrunc (large inputs) --
# Upstream commit: 320dd27412e7 (4.2.x: d1d505de0c)
#
# Upstream commit had no test changes. This test verifies the fix.
class CVE_2024_45230_Tests(SimpleTestCase):
    def test_urlize_large_entity_input(self):
        value = "&" + ";:" * 100_000
        self.assertEqual(urlize(value), value)


# -- CVE-2024-45231: Password reset email enumeration --
# Upstream commit: 8c35a0a903fd (4.2.x: 1132507025)
#
# Upstream commit had no test changes. This test verifies the fix.
class CVE_2024_45231_Tests(TestCase):
    @override_settings(ROOT_URLCONF="django.contrib.auth.urls")
    def test_send_email_exceptions_are_caught_and_logged(self):
        from django.contrib.auth.forms import PasswordResetForm
        from django.contrib.auth.models import User
        from django.core import mail

        User.objects.create_user("testuser", "test@example.com", "testpass")
        form = PasswordResetForm({"email": "test@example.com"})
        self.assertTrue(form.is_valid())

        with (
            mock.patch(
                "django.core.mail.message.EmailMessage.send",
                side_effect=Exception("SMTP error"),
            ),
            self.assertLogs("django.contrib.auth", level=0) as cm,
        ):
            form.save(domain_override="testserver")

        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(len(cm.output), 1)
        self.assertIn("Failed to send password reset email", cm.output[0])


# -- CVE-2024-53907: DoS via strip_tags() --
# Upstream commit: 49ff1042aa66 (4.2.x: cd2d9e08f7)
class CVE_2024_53907_Tests(SimpleTestCase):
    def test_strip_tags_large_input(self):
        # From upstream. If an infinite loop occurs, the test will time out.
        self.assertEqual(strip_tags("x" * 100_001), "x" * 100_001)
        self.assertEqual(strip_tags("x" * 200_001), "x" * 200_001)

    def test_strip_tags_runs_in_constant_time(self):
        # From upstream.
        small_input = "x" * 50
        large_input = "x" * 50_000
        start_time = datetime.now()
        strip_tags(small_input)
        elapsed_time_small = datetime.now() - start_time
        start_time = datetime.now()
        strip_tags(large_input)
        elapsed_time_large = datetime.now() - start_time
        # The large input should take less than 1000x longer than the small
        # input, even though the large input is 1000x longer.
        self.assertLess(elapsed_time_large, elapsed_time_small * 1000)


# -- CVE-2024-53908: SQL injection via HasKey lookup on Oracle --
# Upstream commit: 8f8dc5a1fca7
# Oracle-specific, no test needed for PostgreSQL.


# -- CVE-2025-32873: DoS via strip_tags() large open tags --
# Upstream commit: 9f3419b51979 (4.2.x: ded5bd1af1)
#
# Upstream expects strip_tags to return "" for incomplete tags and raises
# ValueError for max length. Our 3.2 backport uses SuspiciousOperation
# and different thresholds. Adapted accordingly.
class CVE_2025_32873_Tests(SimpleTestCase):
    def test_strip_tags_with_incomplete_tags(self):
        # Adapted from upstream. Our implementation raises SuspiciousOperation
        # for inputs that exceed MAX_STRIP_TAGS_DEPTH instead of processing.
        # Verify simple incomplete tag cases still work.
        self.assertEqual(strip_tags("<p>" * 49), "")
        self.assertEqual(strip_tags("</p>" * 49), "")
        self.assertEqual(strip_tags("<p>foo</p>" * 49), "foo" * 49)

    def test_strip_tags_excessive_input_raises(self):
        # Our 3.2 implementation raises SuspiciousOperation for deeply nested
        # or large inputs.
        with self.assertRaises(SuspiciousOperation):
            strip_tags("<p" * 50_000)


# -- CVE-2025-48432: Log injection via request path --
# Upstream commit: ac03c5e7df (4.2.x backport commit from README)
class CVE_2025_48432_Tests(SimpleTestCase):
    def test_unicode_escape_escaping(self):
        # From upstream ac03c5e7df.
        test_cases = [
            # Control characters.
            ("line\nbreak", "line\\nbreak"),
            ("carriage\rreturn", "carriage\\rreturn"),
            ("tab\tseparated", "tab\\tseparated"),
            ("formfeed\f", "formfeed\\x0c"),
            ("bell\a", "bell\\x07"),
            ("multi\nline\ntext", "multi\\nline\\ntext"),
            # Slashes.
            ("slash\\test", "slash\\\\test"),
            ("back\\slash", "back\\\\slash"),
            # Quotes.
            ('quote"test"', 'quote"test"'),
            ("quote'test'", "quote'test'"),
            # ANSI escape sequences.
            ("escape\x1b[31mred\x1b[0m", "escape\\x1b[31mred\\x1b[0m"),
            (
                "/\x1b[1;31mCAUTION!!YOU ARE PWNED\x1b[0m/",
                "/\\x1b[1;31mCAUTION!!YOU ARE PWNED\\x1b[0m/",
            ),
            (
                "/\r\n\r\n1984-04-22 INFO    Listening on 0.0.0.0:8080\r\n\r\n",
                "/\\r\\n\\r\\n1984-04-22 INFO    Listening on 0.0.0.0:8080\\r\\n\\r\\n",
            ),
            # Plain safe input.
            ("normal-path", "normal-path"),
            ("slash/colon:", "slash/colon:"),
            # Non strings.
            (0, "0"),
            ([1, 2, 3], "[1, 2, 3]"),
        ]

        msg = "Test message: %s"
        for case, expected in test_cases:
            with (
                self.assertLogs("django.request", level="ERROR") as cm,
                self.subTest(case=case),
            ):
                response = HttpResponse(status=318)
                log_response(msg, case, response=response, level="error")
                record = cm.records[0]
                self.assertEqual(record.getMessage(), msg % expected)
                # Log record is always a single line.
                self.assertEqual(len(record.getMessage().splitlines()), 1)


# -- CVE-2025-57833: URLValidator crash on edge-case IPv6 URLs --
# Upstream commit: e8b4feddc34f (backport: cce97f118b)
class CVE_2025_57833_Tests(SimpleTestCase):
    def test_urlvalidator_edge_case_idna(self):
        # From upstream.
        validator = URLValidator()
        with self.assertRaises(ValidationError):
            validator("http://xn-.com")
        with self.assertRaises(ValidationError):
            validator("http://[xn--.com")


# -- CVE-2025-64458: Open redirect via long URLs --
# Upstream commit: 770eea38d7 (4.2.x backport commit from README)
class CVE_2025_64458_Tests(SimpleTestCase):
    def test_redirect_rejects_long_url(self):
        # From upstream 770eea38d7.
        with self.assertRaises(DisallowedRedirect):
            HttpResponseRedirect("\u00e9" * (MAX_URL_REDIRECT_LENGTH + 1))

    def test_redirect_allows_normal_url(self):
        response = HttpResponseRedirect("http://example.com/path")
        self.assertEqual(response.status_code, 302)


# -- CVE-2025-64459: SQL injection via Q() connector --
# Upstream commit: 59ae82e670 (4.2.x backport commit from README)
#
# Upstream error message includes Q.XOR but 3.2 doesn't have XOR.
class CVE_2025_64459_Tests(SimpleTestCase):
    def test_connector_validation(self):
        # From upstream 59ae82e670, adapted (no Q.XOR in 3.2).
        msg = f"_connector must be one of {Q.AND!r}, {Q.OR!r}, or None."
        with self.assertRaisesMessage(ValueError, msg):
            Q(_connector="evil")

    def test_valid_connectors(self):
        # From upstream 59ae82e670.
        Q(_connector=None)
        Q(_connector=Q.AND)
        Q(_connector=Q.OR)


class CVE_2025_64459_FilterKwargs_Tests(SimpleTestCase):
    def test_prohibited_filter_kwargs(self):
        from django.db.models.query import PROHIBITED_FILTER_KWARGS

        self.assertIn("_connector", PROHIBITED_FILTER_KWARGS)
        self.assertIn("_negated", PROHIBITED_FILTER_KWARGS)


# -- CVE-2025-13372: SQL injection via FilteredRelation on PostgreSQL --
# Upstream commit: 5b90ca1e7591
# Requires database models — tested via the annotations test suite.


# -- CVE-2025-64460: DoS via XML Deserializer --
# Upstream commit: 4d2b8803be (4.2.x backport commit from README)
class CVE_2025_64460_Tests(SimpleTestCase):
    def test_crafted_xml_performance(self):
        """The time to process invalid inputs is not quadratic."""
        # From upstream 4d2b8803be.
        from django.core.serializers.xml_serializer import Deserializer

        def build_crafted_xml(depth, leaf_text_len):
            nested_open = "<nested>" * depth
            nested_close = "</nested>" * depth
            leaf = "x" * leaf_text_len
            field_content = f"{nested_open}{leaf}{nested_close}"
            return f"""
                <django-objects version="1.0">
                   <object model="contenttypes.contenttype" pk="1">
                      <field name="app_label">{field_content}</field>
                      <field name="model">m</field>
                   </object>
                </django-objects>
            """

        def deserialize(crafted_xml):
            iterator = Deserializer(crafted_xml)
            gc.collect()
            start_time = time.perf_counter()
            result = list(iterator)
            end_time = time.perf_counter()
            self.assertEqual(len(result), 1)
            return end_time - start_time

        def assertFactor(label, params, factor=2):
            factors = []
            prev_time = None
            for depth, length in params:
                crafted_xml = build_crafted_xml(depth, length)
                elapsed = deserialize(crafted_xml)
                if prev_time is not None:
                    factors.append(elapsed / prev_time)
                prev_time = elapsed

            with self.subTest(label):
                # Assert based on the average factor to reduce test flakiness.
                self.assertLessEqual(sum(factors) / len(factors), factor)

        assertFactor(
            "varying depth, varying length",
            [(50, 2000), (100, 4000), (200, 8000), (400, 16000), (800, 32000)],
            2,
        )
        assertFactor("constant depth, varying length", [(100, 1), (100, 1000)], 2)
