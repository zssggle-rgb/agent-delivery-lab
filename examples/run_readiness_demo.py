from agent_delivery_lab import SystemProfile, assess_delivery_readiness


def main() -> None:
    profile = SystemProfile(
        service_name="research-orchestrator",
        retries_configured=True,
        timeouts_configured=True,
        idempotent_operations=True,
        structured_logging=True,
        trace_ids=True,
        dead_letter_queue=False,
        fallback_mode=True,
        human_handoff=False,
        evaluation_suite=True,
        load_tested=False,
        alerting=True,
        rollback_strategy=False,
    )

    report = assess_delivery_readiness(profile)
    print(report.as_text())


if __name__ == "__main__":
    main()
