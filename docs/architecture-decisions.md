# Architecture decision records — public edition

[Back to profile](../README.md) · [Evidence boundaries](engineering-evidence.md)

These records summarize decisions described in the already-public case studies. They are retrospective public summaries, not copies of private architecture records or claims that all capabilities are production-ready.

## ADR-001 — Govern model routing and execution (AI Company)

**Status:** documented design direction and development-branch implementation.

**Context:** An AI assistant must separate what its owner requests from what it is permitted to execute. Provider selection, authorization, and approval need to remain observable.

**Decision:** Keep model routing policy-owned, use scoped identity and approval-aware workflows, and record attempts and verification.

**Trade-off:** Additional policy and state management adds complexity and latency but improves control, accountability and recovery.

**Evidence:** [Public AI Company case study](https://github.com/parasaf1/engineering-showcase/blob/main/projects/AI_COMPANY.md) · [Current public metadata](https://github.com/parasaf1/engineering-showcase/blob/main/data/ai-company.json).

## ADR-002 — Prefer explicit local speech capture (AI Company)

**Status:** local speech-to-text validated on the development branch; full voice interaction remains unverified.

**Context:** Voice input requires privacy controls and acceptable recognition quality.

**Decision:** Use explicit local-only microphone capture and offline speech recognition, with model selection and integrity checks.

**Trade-off:** Local inference reduces cloud-audio exposure but introduces hardware constraints. Public CPU trials reported roughly 19–23 seconds to process a ten-second Persian sample.

**Evidence:** [Public Phase 14 metadata](https://github.com/parasaf1/engineering-showcase/blob/main/data/ai-company.json).

## ADR-003 — Separate learner experience from service and media boundaries (LearnAva)

**Status:** documented implementation approach; active development.

**Context:** Exam-oriented learning requires coherent client behavior and authorized generated-media delivery.

**Decision:** Connect a feature-oriented Flutter client to modular FastAPI services; validate generated audio and use ownership-aware delivery rather than treating provider output as automatically correct.

**Trade-off:** Explicit contracts and media validation require more integration work but support maintainability and reliable learner workflows.

**Evidence:** [Public LearnAva case study](https://github.com/parasaf1/engineering-showcase/blob/main/projects/LEARNAva.md).

## ADR-004 — Generate public dashboards from approved evidence

**Status:** implemented in the public profile.

**Context:** A visual profile must remain current without exposing proprietary projects or relying on unverifiable statistics.

**Decision:** Use local SVG assets, sanitized public metadata, real GitHub calendar counts and scheduled automation. Validate local links and referenced assets before generated changes are published.

**Trade-off:** Scheduled snapshots are not real-time and require ongoing checks. In exchange, public claims are traceable, and visual assets are owned by the repository.

**Evidence:** [Profile guide](profile-guide.md) · [Public engineering journal](../journal/README.md) · [Quality workflow](https://github.com/parasaf1/parasaf1/actions/workflows/profile-quality.yml).
