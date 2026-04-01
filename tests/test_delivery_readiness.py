import unittest

from agent_delivery_lab import SystemProfile, assess_delivery_readiness


class DeliveryReadinessTests(unittest.TestCase):
    def test_all_controls_enabled_scores_100(self) -> None:
        profile = SystemProfile(
            service_name="fully-hardened-agent",
            retries_configured=True,
            timeouts_configured=True,
            idempotent_operations=True,
            structured_logging=True,
            trace_ids=True,
            dead_letter_queue=True,
            fallback_mode=True,
            human_handoff=True,
            evaluation_suite=True,
            load_tested=True,
            alerting=True,
            rollback_strategy=True,
        )

        report = assess_delivery_readiness(profile)

        self.assertEqual(report.score, 100)
        self.assertEqual(report.readiness_level, "Production-ready")
        self.assertEqual(report.risks, ["No critical delivery risks detected in the current checklist"])

    def test_missing_required_controls_raise_top_risks(self) -> None:
        profile = SystemProfile(
            service_name="unsafe-agent",
            retries_configured=False,
            timeouts_configured=False,
            idempotent_operations=False,
            structured_logging=False,
            trace_ids=False,
            dead_letter_queue=False,
            fallback_mode=False,
            human_handoff=False,
            evaluation_suite=False,
            load_tested=False,
            alerting=False,
            rollback_strategy=False,
        )

        report = assess_delivery_readiness(profile)

        self.assertEqual(report.score, 0)
        self.assertEqual(report.readiness_level, "Fragile prototype")
        self.assertEqual(report.risks[0], "Retry strategy is missing")
        self.assertIn("Add or validate: retries configured", report.next_actions)

    def test_partial_controls_produce_middle_band(self) -> None:
        profile = SystemProfile(
            service_name="maturing-agent",
            retries_configured=True,
            timeouts_configured=True,
            idempotent_operations=True,
            structured_logging=True,
            trace_ids=False,
            dead_letter_queue=False,
            fallback_mode=True,
            human_handoff=False,
            evaluation_suite=True,
            load_tested=False,
            alerting=True,
            rollback_strategy=False,
        )

        report = assess_delivery_readiness(profile)

        self.assertEqual(report.score, 61)
        self.assertEqual(report.readiness_level, "Prototype with visible risk")
        self.assertIn("Retries configured", report.strengths)
        self.assertIn("Capacity limits are still unknown", report.risks)


if __name__ == "__main__":
    unittest.main()
