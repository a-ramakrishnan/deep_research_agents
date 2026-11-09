import json
import unittest
from evals.run import ROOT, evaluate, load_catalog, score


class EvaluationHarnessTests(unittest.TestCase):
    def test_catalog_matches_spec(self):
        import re
        spec = (ROOT.parent / 'flagship-solution-and-agent-methodology.md').read_text()
        rows = re.findall(r'^\| (E\d\d) \| (.*?) \| (.*?) \| (.*?) \|$', spec, re.M)
        cases = load_catalog()['cases']
        self.assertEqual(len(rows), 58)
        for case, (case_id, stimulus, expected, gate) in zip(cases, rows):
            self.assertEqual((case['id'], case['stimulus'], case['expected_behavior'], case['gate']),
                             (case_id, stimulus, expected, gate))
            self.assertEqual(case['critical'], 'critical' in gate)

    def test_missing_agents_never_pass(self):
        report = evaluate({})
        self.assertEqual(report['counts'], {'not_run': 58})
        self.assertFalse(report['release_ready'])

    def test_scorers_accept_reference_and_reject_mutations(self):
        # Harness self-test only: reference replay is never an agent experiment.
        for case in load_catalog()['cases']:
            if not case['fixture']:
                continue
            with self.subTest(case=case['id']):
                fixture = json.loads((ROOT / case['fixture']).read_text())
                record = dict(status='completed', agent_version='self-test',
                              prompt_version='none', model='none', fixture_version=1,
                              output=fixture['expected_output'])
                self.assertEqual(score(case, record)['status'], 'passed')
                record['output'] = {'fabricated': True}
                self.assertEqual(score(case, record)['status'], 'failed')
                record['status'] = 'timeout'
                self.assertEqual(score(case, record)['status'], 'error')
                record['status'] = 'completed'
                record['fixture_version'] = 99
                self.assertEqual(score(case, record)['status'], 'error')
                self.assertEqual(score(case, [])['status'], 'error')
                del record['model']
                self.assertEqual(score(case, record)['status'], 'error')

    def test_unknown_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({'E99': {}})


if __name__ == '__main__':
    unittest.main()
