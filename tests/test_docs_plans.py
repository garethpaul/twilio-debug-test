from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS_PLANS = ROOT / "docs" / "plans"
CANONICAL_PLAN = DOCS_PLANS / "2026-06-08-twilio-debug-test-baseline.md"
NODE_CREDENTIAL_PLAN = DOCS_PLANS / "2026-06-09-node-credential-errors.md"
NODE_MESSAGE_SETTINGS_PLAN = DOCS_PLANS / "2026-06-09-node-message-setting-errors.md"
SCRIPTED_BASELINE_PLAN = DOCS_PLANS / "2026-06-09-scripted-baseline-check.md"
MESSAGE_BODY_LENGTH_PLAN = DOCS_PLANS / "2026-06-09-message-body-length.md"
CI_RUNTIME_MATRIX_PLAN = DOCS_PLANS / "2026-06-10-ci-runtime-matrix.md"


class DocsPlansTest(unittest.TestCase):
    def test_canonical_plan_is_completed_and_verified(self):
        self.assertTrue(DOCS_PLANS.is_dir(), "docs/plans must exist")
        plans = sorted(DOCS_PLANS.glob("*.md"))
        self.assertIn(CANONICAL_PLAN, plans)
        self.assertIn(NODE_CREDENTIAL_PLAN, plans)
        self.assertIn(NODE_MESSAGE_SETTINGS_PLAN, plans)
        self.assertIn(SCRIPTED_BASELINE_PLAN, plans)
        self.assertIn(MESSAGE_BODY_LENGTH_PLAN, plans)
        self.assertIn(CI_RUNTIME_MATRIX_PLAN, plans)

        for plan in plans:
            text = plan.read_text(encoding="utf-8")
            self.assertIn("Status: Completed", text)
            self.assertIn("make check", text)

    def test_check_gate_runs_scripted_baseline(self):
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn("scripts/check-baseline.sh", makefile)


if __name__ == "__main__":
    unittest.main()
