# Relay agent design

Relay uses seven logical roles in one research workflow. Initial research establishes a baseline. Daily refresh uses the same roles with prior findings and source checks, and can skip analysis when evidence is unchanged.

| Role | Reads | Produces | Evaluation cases |
| --- | --- | --- | --- |
| Coordinator | Report spec, prior coverage, source health and run limits | Bounded tasks, question IDs, priorities and stop reason | E01–E03 |
| Source researcher | Tasks, permitted sources and fetch metadata | Source candidates, snapshots and check results via the tool gateway | E04–E06, E41 |
| Evidence assessor | Snapshots, excerpts, entity and date context | Supported or attributed findings, conflicts and gaps | E07–E12, E55 |
| Change analyst | Current observations and comparable baselines | Before-and-after events, unchanged checks or unknown comparisons | E13–E20 |
| Domain analyst | Validated findings, changes and prior assessments | Company profile revisions or literature themes, with evidence dependencies | E21–E25, E51–E58 |
| Report writer | Frozen accepted findings, source health and edition requirements | Full dated draft with citations, changes and limitations | E26–E29, E32 |
| Reviewer | Candidate draft, report spec and frozen evidence | Pass, partial or reject verdict with specific issues and at most one repair request | E30–E32 |

The case mapping describes which role the cases help exercise. Several cases also depend on other roles or runtime services.

## Handoffs and boundaries

1. The coordinator assigns research tasks. The researcher retrieves material through a restricted tool gateway and records fetch outcomes.
2. The assessor evaluates evidence and can return a named gap to the coordinator for bounded follow-up.
3. The change analyst compares like-for-like observations. An initial observation establishes a baseline. A failed check leaves freshness uncertain and preserves the previous baseline.
4. The domain analyst revises supported findings and dependent interpretations. A deterministic service validates and commits accepted knowledge.
5. The writer uses a frozen evidence manifest to draft an edition. The reviewer can request one bounded repair. A deterministic publisher verifies ownership and advances the edition pointer after successful publication.

The scheduler, tool gateway, knowledge committer and publisher are software services. The agent roles can share one workflow process and model configuration. The literature profile substitutes corpus accounting, paper versions and theme analysis for company-specific findings.

## Agent Activity page

The page groups activity by run. It shows role status, a timestamped handoff timeline, evidence references where available, and the planned evaluation cases linked to each role. The local prototype replays a synthetic Acme pricing update and reads the repository eval catalog. All evals currently display “Not run.”

For live integration, each run should expose a snapshot and ordered events with a run ID, sequence number, timestamp, role, status, optional destination, and safe evidence or artifact references. The backend owns status transitions. Include failed, skipped and cancelled states, and distinguish a stale connection from current activity. Publish eval results separately with case ID, fixture version, agent and model versions, status and timestamp. Associate results with a research run only when the evaluation actually targeted that run. Use concise handoff summaries and references in the UI.

## Setup order

Start with the offline company fixture and deterministic baseline and change handling. Add the writer and reviewer contracts around frozen evidence, then connect persisted run events and eval outputs to the page. Add model-backed roles, the literature profile and LangSmith experiments as their contracts become executable.

See the [main specification](flagship-solution-and-agent-methodology.md) and [evaluation harness](evals/README.md).
