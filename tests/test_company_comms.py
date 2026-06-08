import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "test.py"


def load_sample():
    spec = importlib.util.spec_from_file_location("twilio_debug_sample", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CompanyCommsTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
