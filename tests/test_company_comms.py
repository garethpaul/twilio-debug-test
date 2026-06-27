import importlib.util
import io
import logging
from pathlib import Path
from contextlib import redirect_stderr, redirect_stdout
import sys
import types
import unittest
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "test.py"
VALID_ACCOUNT_SID = "AC" + "0123456789abcdef" * 2
VALID_AUTH_TOKEN = "0123456789abcdef" * 2


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
            "TWILIO_TO": "+12025550123",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "hello from dry run",
        })

        result = comms.sendMsg(None, None, None)

        self.assertEqual(result["dry_run"], True)
        self.assertEqual(result["to"], "********0123")
        self.assertEqual(result["from"], "********0124")
        self.assertEqual(result["body_length"], 18)

    def test_explicit_arguments_override_environment(self):
        sample = load_sample()
        comms = sample.CompanyComms(env={
            "TWILIO_TO": "env-to",
            "TWILIO_FROM": "env-from",
            "TWILIO_BODY": "from env",
        })

        result = comms.sendMsg("+12025550125", "+12025550126", "argument body")

        self.assertEqual(result["to"], "********0125")
        self.assertEqual(result["from"], "********0126")
        self.assertEqual(result["body_length"], 13)

    def test_explicit_arguments_do_not_read_environment_fallbacks(self):
        sample = load_sample()

        class FailingEnvironment:
            def get(self, name, default=None):
                if name in {"TWILIO_TO", "TWILIO_FROM", "TWILIO_BODY"}:
                    raise AssertionError("unexpected environment lookup: " + name)
                return default

        comms = sample.CompanyComms(env=FailingEnvironment())

        result = comms.send_msg("+12025550125", "+12025550126", "argument body")

        self.assertEqual(result["to"], "********0125")
        self.assertEqual(result["from"], "********0126")
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
            "TWILIO_TO": "  +12025550123  ",
            "TWILIO_FROM": "  +12025550124  ",
            "TWILIO_BODY": "  hello  ",
        })

        result = comms.send_msg()

        self.assertEqual(result["to"], "********0123")
        self.assertEqual(result["from"], "********0124")
        self.assertEqual(result["body_length"], 5)

    def test_e164_phone_boundaries_are_accepted(self):
        sample = load_sample()
        comms = sample.CompanyComms(env={
            "TWILIO_TO": "+12",
            "TWILIO_FROM": "+123456789012345",
            "TWILIO_BODY": "hello",
        })

        result = comms.send_msg()

        self.assertTrue(result["dry_run"])
        self.assertEqual(FakeTwilioClient.instances, [])

    def test_phone_settings_must_use_e164(self):
        sample = load_sample()
        invalid_values = (
            "15551234567",
            "+05551234567",
            "+1 5551234567",
            "+1-555-123-4567",
            "+12025550123x9",
            "+١٢",
            "+1234567890123456",
        )

        for field in ("TWILIO_TO", "TWILIO_FROM"):
            for invalid_value in invalid_values:
                with self.subTest(field=field, invalid_value=invalid_value):
                    env = {
                        "TWILIO_TO": "+12025550123",
                        "TWILIO_FROM": "+12025550124",
                        "TWILIO_BODY": "hello",
                    }
                    env[field] = invalid_value
                    comms = sample.CompanyComms(
                        env=env,
                        client_factory=FakeTwilioClient,
                    )

                    with self.assertRaisesRegex(
                        sample.MessageValidationError,
                        "{} must be an E.164 phone number".format(field),
                    ):
                        comms.send_msg()

        self.assertEqual(FakeTwilioClient.instances, [])

    def test_blank_message_body_is_missing(self):
        sample = load_sample()
        comms = sample.CompanyComms(env={
            "TWILIO_TO": "+12025550123",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "   ",
        })

        with self.assertRaisesRegex(ValueError, "body"):
            comms.send_msg()

    def test_oversized_message_body_is_rejected(self):
        sample = load_sample()
        comms = sample.CompanyComms(env={
            "TWILIO_TO": "+12025550123",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "x" * (sample.MAX_MESSAGE_BODY_LENGTH + 1),
        })

        with self.assertRaisesRegex(ValueError, "1600 UTF-16 code units"):
            comms.send_msg()

    def test_message_body_limit_counts_emoji_as_utf16_units(self):
        sample = load_sample()
        accepted = sample.CompanyComms(env={
            "TWILIO_TO": "+12025550123",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "😀" * 800,
        }).send_msg()

        self.assertEqual(sample.message_body_units("😀" * 800), 1600)
        self.assertEqual(accepted["body_length"], 1600)

        rejected = sample.CompanyComms(env={
            "TWILIO_TO": "+12025550123",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "😀" * 801,
        })
        with self.assertRaisesRegex(ValueError, "1600 UTF-16 code units"):
            rejected.send_msg()

    def test_live_send_requires_credentials_before_importing_twilio(self):
        sample = load_sample()
        comms = sample.CompanyComms(env={
            "TWILIO_SEND_LIVE": "true",
            "TWILIO_ALLOW_NONINTERACTIVE": "true",
            "TWILIO_CONFIRM_TO": "+12025550123",
            "TWILIO_TO": "+12025550123",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "hello",
        })

        with self.assertRaisesRegex(RuntimeError, "TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN"):
            comms.sendMsg(None, None, None)

    def test_live_send_rejects_malformed_credentials_before_client_setup(self):
        sample = load_sample()
        valid_env = {
            "TWILIO_SEND_LIVE": "true",
            "TWILIO_ALLOW_NONINTERACTIVE": "true",
            "TWILIO_CONFIRM_TO": "+12025550123",
            "TWILIO_ACCOUNT_SID": VALID_ACCOUNT_SID,
            "TWILIO_AUTH_TOKEN": VALID_AUTH_TOKEN,
            "TWILIO_TO": "+12025550123",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "hello",
        }
        invalid_credentials = {
            "TWILIO_ACCOUNT_SID": (
                "SK" + VALID_ACCOUNT_SID[2:],
                VALID_ACCOUNT_SID[:-1],
                VALID_ACCOUNT_SID + "0",
                VALID_ACCOUNT_SID[:-1] + "G",
                "AC０" + VALID_ACCOUNT_SID[3:-1],
            ),
            "TWILIO_AUTH_TOKEN": (
                VALID_AUTH_TOKEN[:-1],
                VALID_AUTH_TOKEN + "0",
                VALID_AUTH_TOKEN[:-1] + "G",
                "０" + VALID_AUTH_TOKEN[1:-1],
            ),
        }

        for field, invalid_values in invalid_credentials.items():
            for invalid_value in invalid_values:
                with self.subTest(field=field, invalid_value=invalid_value):
                    env = dict(valid_env)
                    env[field] = invalid_value
                    comms = sample.CompanyComms(
                        env=env,
                        client_factory=FakeTwilioClient,
                    )

                    with self.assertRaisesRegex(
                        sample.CredentialValidationError,
                        "{} has an invalid format".format(field),
                    ):
                        comms.send_msg()

        self.assertEqual(FakeTwilioClient.instances, [])

    def test_live_send_rejects_malformed_credentials_before_prompting(self):
        sample = load_sample()
        interactive_input = mock.Mock()
        interactive_input.isatty.return_value = True
        prompt_reader = mock.Mock(return_value="send 0123")
        comms = sample.CompanyComms(
            env={
                "TWILIO_SEND_LIVE": "true",
                "TWILIO_CONFIRM_TO": "+12025550123",
                "TWILIO_ACCOUNT_SID": "not-an-account-sid",
                "TWILIO_AUTH_TOKEN": VALID_AUTH_TOKEN,
                "TWILIO_TO": "+12025550123",
                "TWILIO_FROM": "+12025550124",
                "TWILIO_BODY": "hello",
            },
            client_factory=FakeTwilioClient,
            input_stream=interactive_input,
            prompt_reader=prompt_reader,
        )

        with self.assertRaisesRegex(
            sample.CredentialValidationError,
            "TWILIO_ACCOUNT_SID has an invalid format",
        ):
            comms.send_msg()

        prompt_reader.assert_not_called()
        self.assertEqual(FakeTwilioClient.instances, [])

    def test_dry_run_ignores_malformed_credentials(self):
        sample = load_sample()
        comms = sample.CompanyComms(env={
            "TWILIO_ACCOUNT_SID": "not-an-account-sid",
            "TWILIO_AUTH_TOKEN": "not-an-auth-token",
            "TWILIO_CONFIRM_TO": "not-a-phone",
            "TWILIO_TO": "+12025550123",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "hello",
        }, client_factory=FakeTwilioClient)

        result = comms.send_msg()

        self.assertTrue(result["dry_run"])
        self.assertEqual(FakeTwilioClient.instances, [])

    def test_live_send_flag_allows_surrounding_whitespace(self):
        sample = load_sample()

        self.assertTrue(sample.should_send_live({"TWILIO_SEND_LIVE": " TRUE "}))

    def test_python_live_send_log_level_defaults_to_info(self):
        sample = load_sample()
        comms = sample.CompanyComms(env={
            "TWILIO_SEND_LIVE": "true",
            "TWILIO_ALLOW_NONINTERACTIVE": "true",
            "TWILIO_CONFIRM_TO": "+12025550123",
            "TWILIO_ACCOUNT_SID": VALID_ACCOUNT_SID,
            "TWILIO_AUTH_TOKEN": VALID_AUTH_TOKEN,
            "TWILIO_TO": "+12025550123",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "hello",
        }, client_factory=FakeTwilioClient)

        message = comms.send_msg()

        self.assertEqual(message.sid, "SM123")
        self.assertEqual(
            FakeTwilioClient.instances[0].http_client.logger.level,
            logging.INFO,
        )

    def test_default_python_client_uses_bounded_provider_timeout(self):
        sample = load_sample()
        created = {}

        class DefaultHttpClient(FakeHttpClient):
            def __init__(self, timeout=None, max_retries=None):
                super().__init__()
                created["timeout"] = timeout
                created["max_retries"] = max_retries

        def default_client(account_sid, auth_token, http_client=None):
            created["account_sid"] = account_sid
            created["auth_token"] = auth_token
            created["http_client"] = http_client
            client = FakeTwilioClient(account_sid, auth_token)
            client.http_client = http_client
            return client

        twilio_module = types.ModuleType("twilio")
        http_module = types.ModuleType("twilio.http")
        http_client_module = types.ModuleType("twilio.http.http_client")
        rest_module = types.ModuleType("twilio.rest")
        http_client_module.TwilioHttpClient = DefaultHttpClient
        rest_module.Client = default_client

        env = {
            "TWILIO_SEND_LIVE": "true",
            "TWILIO_ALLOW_NONINTERACTIVE": "true",
            "TWILIO_CONFIRM_TO": "+12025550123",
            "TWILIO_ACCOUNT_SID": VALID_ACCOUNT_SID,
            "TWILIO_AUTH_TOKEN": VALID_AUTH_TOKEN,
            "TWILIO_TO": "+12025550123",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "hello",
        }
        with mock.patch.dict(sys.modules, {
            "twilio": twilio_module,
            "twilio.http": http_module,
            "twilio.http.http_client": http_client_module,
            "twilio.rest": rest_module,
        }):
            message = sample.CompanyComms(env=env).send_msg()

        self.assertEqual(message.sid, "SM123")
        self.assertEqual(created["account_sid"], VALID_ACCOUNT_SID)
        self.assertEqual(created["auth_token"], VALID_AUTH_TOKEN)
        self.assertEqual(
            created["timeout"],
            sample.PROVIDER_REQUEST_TIMEOUT_SECONDS,
        )
        self.assertEqual(created["timeout"], 30)
        self.assertEqual(created["max_retries"], 0)
        self.assertIs(
            created["http_client"],
            FakeTwilioClient.instances[0].http_client,
        )

    def test_live_send_requires_matching_recipient_confirmation_before_client_setup(self):
        sample = load_sample()
        base_env = {
            "TWILIO_SEND_LIVE": "true",
            "TWILIO_ACCOUNT_SID": VALID_ACCOUNT_SID,
            "TWILIO_AUTH_TOKEN": VALID_AUTH_TOKEN,
            "TWILIO_TO": "+12025550123",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "hello",
        }
        invalid_confirmations = (
            ({}, "Missing required live recipient confirmation"),
            ({"TWILIO_CONFIRM_TO": "not-a-phone"}, "must be an E.164 phone number"),
            ({"TWILIO_CONFIRM_TO": "+12025550125"}, "must match TWILIO_TO"),
        )

        for override, expected_error in invalid_confirmations:
            with self.subTest(override=override):
                env = dict(base_env)
                env.update(override)
                comms = sample.CompanyComms(
                    env=env,
                    client_factory=FakeTwilioClient,
                )

                with self.assertRaisesRegex(
                    sample.MessageValidationError,
                    expected_error,
                ):
                    comms.send_msg()

        self.assertEqual(FakeTwilioClient.instances, [])

    def test_live_send_accepts_whitespace_normalized_recipient_confirmation(self):
        sample = load_sample()
        comms = sample.CompanyComms(env={
            "TWILIO_SEND_LIVE": "true",
            "TWILIO_ALLOW_NONINTERACTIVE": "true",
            "TWILIO_CONFIRM_TO": "  +12025550123  ",
            "TWILIO_ACCOUNT_SID": VALID_ACCOUNT_SID,
            "TWILIO_AUTH_TOKEN": VALID_AUTH_TOKEN,
            "TWILIO_TO": "+12025550123",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "hello",
        }, client_factory=FakeTwilioClient)

        message = comms.send_msg()

        self.assertEqual(message.sid, "SM123")
        self.assertEqual(len(FakeTwilioClient.instances), 1)

    def test_live_send_requires_per_invocation_confirmation_or_noninteractive_opt_in(self):
        sample = load_sample()
        env = {
            "TWILIO_SEND_LIVE": "true",
            "TWILIO_CONFIRM_TO": "+12025550123",
            "TWILIO_ACCOUNT_SID": VALID_ACCOUNT_SID,
            "TWILIO_AUTH_TOKEN": VALID_AUTH_TOKEN,
            "TWILIO_TO": "+12025550123",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "hello",
        }
        noninteractive_input = mock.Mock()
        noninteractive_input.isatty.return_value = False
        comms = sample.CompanyComms(
            env=env,
            client_factory=FakeTwilioClient,
            input_stream=noninteractive_input,
        )

        with self.assertRaisesRegex(
            sample.MessageValidationError,
            "TTY confirmation or TWILIO_ALLOW_NONINTERACTIVE=true",
        ):
            comms.send_msg()

        self.assertEqual(FakeTwilioClient.instances, [])

    def test_unreadable_stdin_fails_closed_before_client_setup(self):
        sample = load_sample()
        env = {
            "TWILIO_SEND_LIVE": "true",
            "TWILIO_CONFIRM_TO": "+12025550123",
            "TWILIO_ACCOUNT_SID": VALID_ACCOUNT_SID,
            "TWILIO_AUTH_TOKEN": VALID_AUTH_TOKEN,
            "TWILIO_TO": "+12025550123",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "hello",
        }
        unreadable_input = mock.Mock()
        unreadable_input.isatty.side_effect = OSError("stdin unavailable")
        comms = sample.CompanyComms(
            env=env,
            client_factory=FakeTwilioClient,
            input_stream=unreadable_input,
        )

        with self.assertRaisesRegex(
            sample.MessageValidationError,
            "TTY confirmation or TWILIO_ALLOW_NONINTERACTIVE=true",
        ):
            comms.send_msg()

        self.assertEqual(FakeTwilioClient.instances, [])

    def test_interactive_live_send_requires_matching_one_shot_phrase(self):
        sample = load_sample()
        env = {
            "TWILIO_SEND_LIVE": "true",
            "TWILIO_CONFIRM_TO": "+12025550123",
            "TWILIO_ACCOUNT_SID": VALID_ACCOUNT_SID,
            "TWILIO_AUTH_TOKEN": VALID_AUTH_TOKEN,
            "TWILIO_TO": "+12025550123",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "hello",
        }
        interactive_input = mock.Mock()
        interactive_input.isatty.return_value = True
        wrong_prompt = mock.Mock(return_value="send 9999")
        comms = sample.CompanyComms(
            env=env,
            client_factory=FakeTwilioClient,
            input_stream=interactive_input,
            prompt_reader=wrong_prompt,
        )

        with self.assertRaisesRegex(
            sample.MessageValidationError,
            "Interactive confirmation did not match",
        ):
            comms.send_msg()

        self.assertEqual(FakeTwilioClient.instances, [])
        prompt = wrong_prompt.call_args.args[0]
        self.assertIn("********0123", prompt)
        self.assertNotIn("+12025550123", prompt)

        confirmed = sample.CompanyComms(
            env=env,
            client_factory=FakeTwilioClient,
            input_stream=interactive_input,
            prompt_reader=mock.Mock(return_value="send 0123"),
        ).send_msg()
        self.assertEqual(confirmed.sid, "SM123")

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

    def test_main_reports_invalid_phone_without_traceback(self):
        sample = load_sample()
        stderr = io.StringIO()
        env = {
            "TWILIO_TO": "not-a-phone",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "hello",
        }

        with mock.patch.dict(sample.os.environ, env, clear=True):
            with redirect_stderr(stderr):
                exit_code = sample.main()

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            stderr.getvalue(),
            "TWILIO_TO must be an E.164 phone number.\n",
        )
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_main_reports_missing_live_recipient_confirmation_without_traceback(self):
        sample = load_sample()
        stderr = io.StringIO()
        env = {
            "TWILIO_SEND_LIVE": "true",
            "TWILIO_TO": "+12025550123",
            "TWILIO_FROM": "+12025550124",
            "TWILIO_BODY": "hello",
        }

        with mock.patch.dict(sample.os.environ, env, clear=True):
            with redirect_stderr(stderr):
                exit_code = sample.main()

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            stderr.getvalue(),
            "Missing required live recipient confirmation: TWILIO_CONFIRM_TO\n",
        )
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

    def test_cli_error_message_preserves_credential_format_errors(self):
        sample = load_sample()
        error = sample.CredentialValidationError(
            "TWILIO_ACCOUNT_SID has an invalid format."
        )

        self.assertEqual(
            sample.cli_error_message(error),
            "TWILIO_ACCOUNT_SID has an invalid format.",
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
