import importlib.util
import io
import logging
from pathlib import Path
from contextlib import redirect_stderr, redirect_stdout
import unittest
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "test.py"


def load_sample():
    spec = importlib.util.spec_from_file_location("twilio_debug_sample", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeLogger:
    def __init__(self):
        self.level = None

    def setLevel(self, level):
        self.level = level


class FakeHttpClient:
    def __init__(self):
        self.logger = FakeLogger()


class FakeMessages:
    def __init__(self, client):
        self.client = client
        self.payload = None

    def create(self, **payload):
        self.payload = payload
        return type("Message", (), {"sid": "SM123"})()


class FakeTwilioClient:
    instances = []

    def __init__(self, account_sid, auth_token):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.http_client = FakeHttpClient()
        self.messages = FakeMessages(self)
        FakeTwilioClient.instances.append(self)


class CompanyCommsTest(unittest.TestCase):
    def setUp(self):
        FakeTwilioClient.instances = []

    def test_dry_run_uses_environment_without_twilio_import(self):
        sample = load_sample()
        comms = sample.CompanyComms(env={
            "TWILIO_TO": "to-4567",
            "TWILIO_FROM": "from-4321",
            "TWILIO_BODY": "hello from dry run",
        })

        result = comms.sendMsg(None, None, None)

        self.assertEqual(result["dry_run"], True)
        self.assertEqual(result["to"], "***4567")
        self.assertEqual(result["from"], "*****4321")
        self.assertEqual(result["body_length"], 18)

    def test_explicit_arguments_override_environment(self):
        sample = load_sample()
        comms = sample.CompanyComms(env={
            "TWILIO_TO": "env-to",
            "TWILIO_FROM": "env-from",
            "TWILIO_BODY": "from env",
        })

        result = comms.sendMsg("to-3333", "from-5555", "argument body")

        self.assertEqual(result["to"], "***3333")
        self.assertEqual(result["from"], "*****5555")
        self.assertEqual(result["body_length"], 13)

    def test_explicit_arguments_do_not_read_environment_fallbacks(self):
        sample = load_sample()

        class FailingEnvironment:
            def get(self, name, default=None):
                if name in {"TWILIO_TO", "TWILIO_FROM", "TWILIO_BODY"}:
                    raise AssertionError("unexpected environment lookup: " + name)
                return default

        comms = sample.CompanyComms(env=FailingEnvironment())

        result = comms.send_msg("to-3333", "from-5555", "argument body")

        self.assertEqual(result["to"], "***3333")
        self.assertEqual(result["from"], "*****5555")
        self.assertEqual(result["body_length"], 13)

    def test_explicit_blank_arguments_do_not_fall_back_to_environment(self):
        sample = load_sample()
        env = {
            "TWILIO_TO": "env-to",
            "TWILIO_FROM": "env-from",
            "TWILIO_BODY": "from env",
        }
        overrides = {
            "to": ("   ", None, None),
            "from": (None, "   ", None),
            "body": (None, None, "   "),
        }

        for missing_name, args in overrides.items():
            with self.subTest(missing_name=missing_name):
                comms = sample.CompanyComms(env=env, client_factory=FakeTwilioClient)
                with self.assertRaisesRegex(
                    sample.MessageValidationError,
                    missing_name,
                ):
                    comms.send_msg(*args)

        self.assertEqual(FakeTwilioClient.instances, [])

    def test_message_settings_are_trimmed_before_dry_run(self):
        sample = load_sample()
        comms = sample.CompanyComms(env={
            "TWILIO_TO": "  to-4567  ",
            "TWILIO_FROM": "  from-4321  ",
            "TWILIO_BODY": "  hello  ",
        })

        result = comms.send_msg()

        self.assertEqual(result["to"], "***4567")
        self.assertEqual(result["from"], "*****4321")
        self.assertEqual(result["body_length"], 5)

    def test_blank_message_body_is_missing(self):
        sample = load_sample()
        comms = sample.CompanyComms(env={
            "TWILIO_TO": "to-4567",
            "TWILIO_FROM": "from-4321",
            "TWILIO_BODY": "   ",
        })

        with self.assertRaisesRegex(ValueError, "body"):
            comms.send_msg()

    def test_oversized_message_body_is_rejected(self):
        sample = load_sample()
        comms = sample.CompanyComms(env={
            "TWILIO_TO": "to-4567",
            "TWILIO_FROM": "from-4321",
            "TWILIO_BODY": "x" * (sample.MAX_MESSAGE_BODY_LENGTH + 1),
        })

        with self.assertRaisesRegex(ValueError, "1600 characters"):
            comms.send_msg()

    def test_live_send_requires_credentials_before_importing_twilio(self):
        sample = load_sample()
        comms = sample.CompanyComms(env={
            "TWILIO_SEND_LIVE": "true",
            "TWILIO_TO": "to-4567",
            "TWILIO_FROM": "from-4321",
            "TWILIO_BODY": "hello",
        })

        with self.assertRaisesRegex(RuntimeError, "TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN"):
            comms.sendMsg(None, None, None)

    def test_live_send_flag_allows_surrounding_whitespace(self):
        sample = load_sample()

        self.assertTrue(sample.should_send_live({"TWILIO_SEND_LIVE": " TRUE "}))

    def test_python_live_send_log_level_defaults_to_info(self):
        sample = load_sample()
        comms = sample.CompanyComms(env={
            "TWILIO_SEND_LIVE": "true",
            "TWILIO_ACCOUNT_SID": "AC123",
            "TWILIO_AUTH_TOKEN": "secret",
            "TWILIO_TO": "to-4567",
            "TWILIO_FROM": "from-4321",
            "TWILIO_BODY": "hello",
        }, client_factory=FakeTwilioClient)

        message = comms.send_msg()

        self.assertEqual(message.sid, "SM123")
        self.assertEqual(
            FakeTwilioClient.instances[0].http_client.logger.level,
            logging.INFO,
        )

    def test_python_live_send_log_level_requires_supported_opt_in(self):
        sample = load_sample()

        self.assertEqual(
            sample.twilio_log_level({"TWILIO_LOG_LEVEL": " DEBUG "}),
            logging.DEBUG,
        )
        self.assertEqual(
            sample.twilio_log_level({"TWILIO_LOG_LEVEL": "noisy"}),
            logging.INFO,
        )
        self.assertEqual(
            sample.twilio_log_level({"TWILIO_LOG_LEVEL": "silent"}),
            logging.CRITICAL + 10,
        )

    def test_main_reports_validation_errors_without_traceback(self):
        sample = load_sample()
        stderr = io.StringIO()

        with mock.patch.dict(sample.os.environ, {}, clear=True):
            with redirect_stderr(stderr):
                exit_code = sample.main()

        self.assertEqual(exit_code, 1)
        self.assertIn("Missing required Twilio message settings", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_main_redacts_created_message_sid(self):
        sample = load_sample()
        stdout = io.StringIO()
        message = type("Message", (), {"sid": "SM1234567890"})()

        with mock.patch.object(sample.CompanyComms, "send_msg", return_value=message):
            with redirect_stdout(stdout):
                exit_code = sample.main()

        self.assertEqual(exit_code, 0)
        self.assertIn("********7890", stdout.getvalue())
        self.assertNotIn("SM1234567890", stdout.getvalue())

    def test_main_handles_created_message_without_sid(self):
        sample = load_sample()
        stdout = io.StringIO()
        message = object()

        with mock.patch.object(sample.CompanyComms, "send_msg", return_value=message):
            with redirect_stdout(stdout):
                exit_code = sample.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "Created message: ***nown\n")

    def test_cli_error_message_preserves_credential_validation_errors(self):
        sample = load_sample()
        error = sample.CredentialValidationError(
            "Missing required Twilio credentials: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN"
        )

        self.assertEqual(
            sample.cli_error_message(error),
            "Missing required Twilio credentials: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN",
        )

    def test_main_hides_unexpected_provider_error_details(self):
        sample = load_sample()
        stderr = io.StringIO()

        with mock.patch.object(
            sample.CompanyComms,
            "send_msg",
            side_effect=RuntimeError("provider response included auth-token-secret"),
        ):
            with redirect_stderr(stderr):
                exit_code = sample.main()

        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr.getvalue(), "Twilio request failed.\n")
        self.assertNotIn("auth-token-secret", stderr.getvalue())

    def test_cli_error_message_hides_unexpected_value_errors(self):
        sample = load_sample()

        message = sample.cli_error_message(
            ValueError("provider response included auth-token-secret")
        )

        self.assertEqual(message, "Twilio request failed.")
        self.assertNotIn("auth-token-secret", message)


if __name__ == "__main__":
    unittest.main()
