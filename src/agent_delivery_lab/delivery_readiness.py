from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SystemProfile:
    service_name: str
    retries_configured: bool
    timeouts_configured: bool
    idempotent_operations: bool
    structured_logging: bool
    trace_ids: bool
    dead_letter_queue: bool
    fallback_mode: bool
    human_handoff: bool
    evaluation_suite: bool
    load_tested: bool
    alerting: bool
    rollback_strategy: bool


@dataclass(frozen=True)
class DeliveryReadinessReport:
    service_name: str
    score: int
    readiness_level: str
    strengths: list[str]
    risks: list[str]
    next_actions: list[str]

    def as_text(self) -> str:
        sections = [
            f"Service: {self.service_name}",
            f"Score: {self.score}/100",
            f"Readiness: {self.readiness_level}",
            "",
            "Strengths:",
            *[f"- {item}" for item in self.strengths],
            "",
            "Risks:",
            *[f"- {item}" for item in self.risks],
            "",
            "Next actions:",
            *[f"- {item}" for item in self.next_actions],
        ]
        return "\n".join(sections)


_CONTROL_WEIGHTS: list[tuple[str, str, int, bool, str]] = [
    ("retries_configured", "Retries configured", 10, True, "Retry strategy is missing"),
    ("timeouts_configured", "Timeouts configured", 10, True, "Timeout boundaries are undefined"),
    ("idempotent_operations", "Idempotent operations", 10, True, "Retries may create duplicated side effects"),
    ("structured_logging", "Structured logging", 8, True, "Operational debugging will be slower"),
    ("trace_ids", "Trace IDs across workflow steps", 8, True, "Cross-service execution is hard to trace"),
    ("dead_letter_queue", "Dead-letter handling", 8, False, "Failed work has no isolated recovery lane"),
    ("fallback_mode", "Fallback mode", 8, False, "The system may fail hard instead of degrading gracefully"),
    ("human_handoff", "Human handoff path", 8, False, "Escalation for ambiguous failures is missing"),
    ("evaluation_suite", "Evaluation suite", 8, True, "Behavior changes are hard to measure before release"),
    ("load_tested", "Load-tested critical path", 8, True, "Capacity limits are still unknown"),
    ("alerting", "Alerting on critical failures", 7, True, "Production incidents may be detected too late"),
    ("rollback_strategy", "Rollback strategy", 7, True, "Release recovery is underdefined"),
]


def assess_delivery_readiness(profile: SystemProfile) -> DeliveryReadinessReport:
    score = 0
    strengths: list[str] = []
    risks: list[tuple[int, str]] = []
    actions: list[tuple[int, str]] = []

    for field_name, label, weight, required, risk_message in _CONTROL_WEIGHTS:
        enabled = bool(getattr(profile, field_name))
        if enabled:
            score += weight
            strengths.append(label)
            continue

        risk_weight = weight + (5 if required else 0)
        risks.append((risk_weight, risk_message))
        actions.append((risk_weight, _action_for(label)))

    readiness_level = _readiness_level(score)
    ordered_risks = [message for _, message in sorted(risks, key=lambda item: item[0], reverse=True)]
    ordered_actions = [message for _, message in sorted(actions, key=lambda item: item[0], reverse=True)[:5]]

    if not ordered_risks:
        ordered_risks = ["No critical delivery risks detected in the current checklist"]
    if not ordered_actions:
        ordered_actions = ["Maintain the current delivery controls and keep validating under change"]

    return DeliveryReadinessReport(
        service_name=profile.service_name,
        score=score,
        readiness_level=readiness_level,
        strengths=strengths,
        risks=ordered_risks,
        next_actions=ordered_actions,
    )


def _readiness_level(score: int) -> str:
    if score >= 85:
        return "Production-ready"
    if score >= 70:
        return "Launchable with hardening"
    if score >= 50:
        return "Prototype with visible risk"
    return "Fragile prototype"


def _action_for(label: str) -> str:
    return f"Add or validate: {label.lower()}"
