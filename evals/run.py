"""Score recorded agent outputs against synthetic structured contracts."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent


def load_catalog():
    catalog = json.loads((ROOT / 'catalog.json').read_text())
    cases = catalog['cases']
    if [c['id'] for c in cases] != [f'E{i:02}' for i in range(1, 59)]:
        raise ValueError('Catalog must contain E01–E58 exactly once in order')
    for case in cases:
        if case['fixture']:
            fixture = json.loads((ROOT / case['fixture']).read_text())
            if fixture['case_id'] != case['id'] or fixture['scorer'] != 'exact-json-v1':
                raise ValueError(f"Invalid fixture for {case['id']}")
    return catalog


def score(case, record):
    result = {'case_id': case['id'], 'critical': case['critical'],
              'status': 'not_run', 'reason': 'No recorded output supplied'}
    if not case['fixture']:
        result['reason'] = 'Fixture/scorer not implemented'
        return result
    if record is None:
        return result
    fixture = json.loads((ROOT / case['fixture']).read_text())
    result.update(fixture_version=fixture['version'], scorer=fixture['scorer'])
    if not isinstance(record, dict):
        return dict(result, status='error', reason='Record must be an object')
    if record.get('status') != 'completed':
        return dict(result, status='error', reason='Agent execution did not complete')
    required = ('agent_version', 'prompt_version', 'model', 'fixture_version')
    if any(key not in record for key in required) or 'output' not in record:
        return dict(result, status='error', reason='Missing output or provenance metadata')
    if record['fixture_version'] != fixture['version']:
        return dict(result, status='error', reason='Fixture version mismatch')
    result['provenance'] = {key: record[key] for key in required}
    result['actual_output'] = record['output']
    # Comparing canonical JSON keeps booleans distinct from integers.
    passed = json.dumps(record['output'], sort_keys=True) == json.dumps(fixture['expected_output'], sort_keys=True)
    return dict(result, status='passed' if passed else 'failed',
                reason='Exact structured contract matched' if passed else 'Structured output differs from reference')


def evaluate(records):
    catalog = load_catalog()
    unknown = set(records) - {c['id'] for c in catalog['cases']}
    if unknown:
        raise ValueError(f'Unknown case IDs: {sorted(unknown)}')
    results = [score(case, records.get(case['id'])) for case in catalog['cases']]
    counts = dict(Counter(r['status'] for r in results))
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip())
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    return {'catalog_version': catalog['version'], 'evaluator_version': 1,
            'created_at': datetime.now(timezone.utc).isoformat(), 'commit': commit,
            'working_tree_dirty': dirty, 'scope': 'structured contract checks only',
            'release_ready': False,
            'release_blockers': ['Full runtime and semantic suites are not implemented',
                                 'Required held-out experiments and human review are outstanding'],
            'counts': counts, 'results': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outputs', type=Path, help='JSON object keyed by case ID')
    parser.add_argument('--report', type=Path, help='Write detailed JSON results')
    parser.add_argument('--require-complete', action='store_true', help='Fail if any catalog case did not pass')
    args = parser.parse_args()
    try:
        records = json.loads(args.outputs.read_text()) if args.outputs else {}
        if not isinstance(records, dict):
            raise ValueError('Outputs must be an object keyed by case ID')
        report = evaluate(records)
    except (ValueError, KeyError, OSError) as exc:
        parser.error(str(exc))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'counts': report['counts'], 'release_ready': False}, indent=2))
    failed = any(r['status'] in ('failed', 'error') for r in report['results'])
    incomplete = any(r['status'] != 'passed' for r in report['results'])
    return int(failed or (args.require_complete and incomplete))


if __name__ == '__main__':
    raise SystemExit(main())
