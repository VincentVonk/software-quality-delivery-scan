"""Assessment model and static configuration for the capability scan."""

from __future__ import annotations

from dataclasses import dataclass


SCORE_LABELS = {
    1: "Not implemented",
    2: "Partially implemented",
    3: "Implemented",
    4: "Managed and measured",
    5: "Continuously improved",
}


@dataclass(frozen=True)
class Question:
    id: str
    text: str
    evidence: str


@dataclass(frozen=True)
class Domain:
    name: str
    weight: float
    questions: tuple[Question, ...]


DOMAINS: tuple[Domain, ...] = (
    Domain(
        name="Business & Governance",
        weight=0.15,
        questions=(
            Question("BG1", "Is software quality explicitly linked to business objectives and risk appetite?", "Quality strategy, OKRs, risk register"),
            Question("BG2", "Are delivery governance forums defined with clear decision rights?", "Governance calendar, RACI, steering minutes"),
            Question("BG3", "Are quality expectations embedded in supplier and partner agreements?", "Contracts, SLAs, quality clauses"),
            Question("BG4", "Is portfolio prioritization informed by value, risk, and delivery capacity?", "Portfolio board packs, prioritization model"),
            Question("BG5", "Are audit, regulatory, and compliance obligations translated into delivery controls?", "Control matrix, audit evidence"),
            Question("BG6", "Do teams have clear escalation paths for quality and delivery risks?", "Escalation process, risk logs"),
        ),
    ),
    Domain(
        name="Requirements & Change Management",
        weight=0.15,
        questions=(
            Question("RC1", "Are requirements captured with clear acceptance criteria and business ownership?", "User stories, acceptance criteria, product owner sign-off"),
            Question("RC2", "Is impact analysis performed before approving scope or requirement changes?", "Change records, impact assessments"),
            Question("RC3", "Are requirements traceable to tests, releases, and business outcomes?", "Traceability matrix, ALM links"),
            Question("RC4", "Are non-functional requirements defined early and validated throughout delivery?", "NFR catalogue, performance/security tests"),
            Question("RC5", "Are backlog refinement and prioritization routines consistently followed?", "Backlog reports, sprint planning notes"),
            Question("RC6", "Are requirement ambiguities and defects measured and reduced over time?", "Defect taxonomy, root-cause reports"),
        ),
    ),
    Domain(
        name="Development Process",
        weight=0.15,
        questions=(
            Question("DP1", "Are delivery methods standardized while allowing team-level tailoring?", "Delivery playbook, team working agreements"),
            Question("DP2", "Are coding standards, peer reviews, and definition of done consistently applied?", "Code review policy, DoD checklist"),
            Question("DP3", "Is branching, merging, and release preparation controlled and repeatable?", "Branching strategy, release checklist"),
            Question("DP4", "Are architecture and technical debt decisions visible and governed?", "Architecture decision records, debt backlog"),
            Question("DP5", "Are security and reliability practices integrated into daily engineering work?", "Threat models, secure coding checks"),
            Question("DP6", "Are retrospectives translated into measurable process improvements?", "Retro actions, improvement tracking"),
        ),
    ),
    Domain(
        name="Testing & Quality",
        weight=0.20,
        questions=(
            Question("TQ1", "Is there a risk-based test strategy covering functional and non-functional quality?", "Test strategy, risk assessment"),
            Question("TQ2", "Are test levels, responsibilities, and entry/exit criteria clearly defined?", "Test plan, quality gates"),
            Question("TQ3", "Is defect management consistent from discovery through root-cause analysis?", "Defect workflow, RCA records"),
            Question("TQ4", "Are regression suites maintained and reviewed against product risk?", "Regression inventory, coverage review"),
            Question("TQ5", "Are exploratory, usability, accessibility, performance, and security testing used where relevant?", "Specialist test reports"),
            Question("TQ6", "Are production incidents fed back into test design and quality controls?", "Incident PIRs, test updates"),
            Question("TQ7", "Is quality owned jointly by product, engineering, and test roles?", "Role descriptions, team ceremonies"),
        ),
    ),
    Domain(
        name="Test Data & Environments",
        weight=0.10,
        questions=(
            Question("TE1", "Are test environments representative, stable, and available when needed?", "Environment inventory, uptime reports"),
            Question("TE2", "Is test data provisioned through controlled and compliant processes?", "Data request workflow, masking evidence"),
            Question("TE3", "Are environment dependencies, integrations, and versions visible to teams?", "CMDB, environment dashboards"),
            Question("TE4", "Can teams refresh, reset, or seed test data efficiently?", "Data tooling, refresh logs"),
            Question("TE5", "Are environment incidents tracked and analyzed for delivery impact?", "Incident logs, delay reports"),
        ),
    ),
    Domain(
        name="Tooling & Automation",
        weight=0.15,
        questions=(
            Question("TA1", "Are CI/CD pipelines standardized and used across teams?", "Pipeline inventory, build history"),
            Question("TA2", "Are automated tests reliable, maintained, and integrated into delivery gates?", "Automation reports, flaky test analysis"),
            Question("TA3", "Are static analysis, dependency, and security scans automated?", "Scan dashboards, policy rules"),
            Question("TA4", "Are deployment, rollback, and release activities automated where feasible?", "Deployment logs, runbooks"),
            Question("TA5", "Are tool integrations reducing manual handoffs and duplicate data entry?", "Toolchain map, integration records"),
            Question("TA6", "Is automation value measured through lead time, quality, or effort reduction?", "Benefits tracking, metrics reports"),
        ),
    ),
    Domain(
        name="Metrics & Reporting",
        weight=0.10,
        questions=(
            Question("MR1", "Are delivery and quality metrics defined consistently across teams?", "Metrics catalogue, reporting standards"),
            Question("MR2", "Do dashboards show leading and lagging indicators of delivery health?", "Dashboards, KPI definitions"),
            Question("MR3", "Are metrics reviewed in governance forums and used to drive action?", "Meeting packs, action logs"),
            Question("MR4", "Are customer, business, and operational outcomes connected to delivery reporting?", "Outcome reports, service metrics"),
            Question("MR5", "Are data quality issues in reporting identified and corrected?", "Data quality checks, reconciliation logs"),
        ),
    ),
)


STATUS_RULES = (
    (4.0, "Green", "#2e7d32"),
    (2.8, "Amber", "#f9a825"),
    (0.0, "Red", "#c62828"),
)
