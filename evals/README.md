# Relay evaluation foundation

This directory tracks all 58 design cases. Nine synthetic development fixtures
(E09, E13–E15, E17, E26, E29, E51–E52) provide exact structured-output contracts.
These are partial checks for their named cases, not complete semantic or runtime
evaluations. The remaining cases have catalog entries, not executable fixtures.
There are no implemented agents, provider calls, LangSmith uploads, or paid runs.

## Run locally

Python 3.11+; standard library only. From the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 -m evals.run --report eval-results/readiness.json
```

With no agent outputs, the runner reports **58 not_run**, never 58 passes.
The unit tests validate catalog consistency and the scoring harness, including
negative outputs. Reference replay in those tests is not agent performance.
CI runs these checks without secrets and uploads the readiness report.

## Evaluate an agent

Supply each fixture's `inputs` to your implementation and record its output in
an object keyed by case ID. Do not give the agent `expected_output`. Example
record shape (the empty output below intentionally fails E13):

```json
{
  "E13": {
    "status": "completed",
    "fixture_version": 1,
    "agent_version": "implementation-commit",
    "prompt_version": "prompt-v1",
    "model": "provider/model-version",
    "output": {}
  }
}
```

```sh
python3 -m evals.run --outputs /path/to/outputs.json --report eval-results/run.json
```

The exact scorer requires the entire fixture output shape, values and array
ordering to match. It does not judge arbitrary prose or citation entailment.
Failed/time-out execution, missing metadata, and mismatched fixture versions
are errors, never passes. Unknown case IDs are rejected. A missing fixture or
output remains not_run. Failed/error checks produce nonzero exit status;
`--require-complete` also fails on not_run. Default zero exit status only means
no supplied check failed; it is not release approval. Reports always mark
`release_ready: false` until full release gates are implemented.

Recorded outputs and reports can contain sensitive material; keep them local.
Only the synthetic catalog/fixtures belong in public datasets.

## Remaining implementation

- Expand each catalog case into full role/runtime fixtures and scorers, including
  PostgreSQL recovery, rendering parity and scheduling integration tests.
- Add human-labeled semantic examples, separate development and held-out splits
  (at least 20% held out), and three repeats of model-dependent release cases.
  These nine development fixtures are public and cannot serve as held-out data.
- Add claim-level support/coverage and change precision/recall metrics with
  explicit denominators, human review and versioned judge rubrics.
- Add opt-in LangSmith integration after the model/agent contracts exist. Retain
  dataset provenance, code/prompt/model versions and failed evaluator statuses;
  sanitize content before any upload. No credentials are needed for this harness.
- Compare single-call synthesis and full-regeneration baselines with equal inputs.
- Implement the complete release gate; passing these contracts alone is insufficient.
