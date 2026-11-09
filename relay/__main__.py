"""Run the synthetic company workflow and publish inspectable artifacts."""
from __future__ import annotations
import argparse
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
import json
from pathlib import Path

from evals.run import ROOT as EVAL_ROOT, evaluate


@dataclass(frozen=True)
class Snapshot:
    date: str
    id: str
    plan: str
    excerpt: str


@dataclass(frozen=True)
class Finding:
    plan: str
    evidence: str


@dataclass(frozen=True)
class Change:
    before: str
    after: str
    evidence: tuple[str, str]


@dataclass(frozen=True)
class Edition:
    date: str
    finding: Finding
    changes: tuple[Change, ...]
    comparison: str


@dataclass(frozen=True)
class RunEvent:
    timestamp: str
    sender: str
    recipient: str
    detail: str


def compare(previous: Snapshot | None, current: Snapshot) -> tuple[str, tuple[Change, ...]]:
    if previous is None:
        return "baseline", ()
    if previous.plan == current.plan:
        return "unchanged", ()
    return "changed", (Change(previous.plan, current.plan, (previous.id, current.id)),)


def run(snapshots: list[Snapshot], destination: Path) -> list[dict]:
    evidence: dict[str, Snapshot] = {}
    runs = []
    previous = None
    for snapshot in snapshots:
        day = date.fromisoformat(snapshot.date).isoformat()
        events = []

        def handoff(sender, recipient, detail):
            events.append(RunEvent(datetime.now(timezone.utc).isoformat(), sender, recipient, detail))

        handoff("CLI", "Coordinator", f"Opened fixture check for {day}.")
        handoff("Coordinator", "Source researcher", "Check the supplied Acme pricing snapshot.")
        evidence.setdefault(snapshot.id, snapshot)
        handoff("Source researcher", "Evidence assessor", f"Recorded a successful check of {snapshot.id}.")
        finding = Finding(snapshot.plan, snapshot.id)
        handoff("Evidence assessor", "Change analyst", f"Accepted the SSO plan from {finding.evidence}.")
        comparison, changes = compare(previous, snapshot)
        edition = Edition(day, finding, changes, comparison)
        handoff("Change analyst", "Domain analyst", f"Comparison: {comparison}.")
        handoff("Domain analyst", "Report writer", f"Current SSO entry plan: {finding.plan}.")
        change_text = {
            "baseline": "First observation. Established the pricing baseline.",
            "unchanged": "No verified material change.",
            "changed": "",
        }[comparison]
        if changes:
            change = changes[0]
            change_text = f"SSO entry plan moved from {change.before} to {change.after} [{', '.join(change.evidence)}]."
        cited = dict.fromkeys([finding.evidence, *(ref for change in changes for ref in change.evidence)])
        citations = "\n".join(
            f"- [{ref}] {evidence[ref].excerpt} (synthetic pricing snapshot, {evidence[ref].date})"
            for ref in cited
        )
        markdown = (
            f"# Acme research edition · {day}\n\nSynthetic fixture · Pricing checked {day}\n\n"
            f"## Current findings\n\nSSO starts on {finding.plan} [{finding.evidence}].\n\n"
            f"## Daily changes\n\n{change_text}\n\n## Evidence\n\n{citations}\n"
        )
        handoff("Report writer", "Reviewer", "Prepared the full edition and its evidence references.")
        if not all(ref in evidence and f"[{ref}]" in markdown for ref in cited):
            raise ValueError("Edition has an unresolved evidence reference")
        handoff("Reviewer", "Publisher", "Validated the edition's evidence references.")
        filename = f"{day}.md"
        (destination / filename).write_text(markdown, encoding="utf-8")
        handoff("Publisher", "Edition history", f"Saved {filename}.")
        runs.append({"edition": asdict(edition), "report": filename,
                     "events": [asdict(event) for event in events]})
        previous = snapshot
    return runs


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("relay-output"),
                        help="New output directory. Use a fresh path for each run.")
    args = parser.parse_args()
    try:
        args.output.mkdir(parents=True)
    except FileExistsError:
        parser.error("Output directory already exists. Choose a fresh --output path.")
    snapshots = [Snapshot(**item) for item in json.loads(
        Path(__file__).with_name("acme.json").read_text(encoding="utf-8"))]
    runs = run(snapshots, args.output)
    fixture = json.loads((EVAL_ROOT / "fixtures/E13.json").read_text(encoding="utf-8"))
    plan = fixture["inputs"]["current"]["plan"]
    comparison, changes = compare(None, Snapshot(snapshots[0].date, "E13", plan, ""))
    records = {
        case_id: {"status": "completed", "fixture_version": 1,
                  "agent_version": "offline-v1", "prompt_version": "none",
                  "model": "deterministic", "output": output}
        for case_id, output in {
            "E13": {"comparison": comparison, "events": list(changes)},
            "E26": {"editions": json.loads(json.dumps([item["edition"] for item in runs]))},
        }.items()
    }
    report = evaluate(records)
    write_json(args.output / "evals.json", report)
    write_json(args.output / "activity.json", {"runs": runs, "evaluations": report["results"]})
    print(f"Wrote {len(runs)} editions and evaluation results to {args.output}")
    print(json.dumps(report["counts"], sort_keys=True))
    return int(any(item["status"] in {"failed", "error"} for item in report["results"]))


if __name__ == "__main__":
    raise SystemExit(main())
