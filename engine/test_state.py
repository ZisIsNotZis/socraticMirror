#!/usr/bin/env python3
"""Run from any directory: python3 /path/to/engine/test_state.py."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state as engine

HERE = Path(__file__).resolve().parent
GRAPH = HERE / 'fixtures/concepts.yaml'
SCENARIOS = HERE / 'fixtures/scenarios.yaml'
QUOTES = {k: 'quoted supporting assertion' for k in engine.DIMS}


class StateTests(unittest.TestCase):
    def setUp(self):
        self.state = engine.initialize(GRAPH, SCENARIOS)
        self.coverage = self.state['scenarios'][0]['instantiates']

    def score(self, state=None, coverage=None, values=(3, 3, 3, 3), probe='direct', qtype='explanation'):
        return engine.score(self.state if state is None else state,
                            self.coverage if coverage is None else coverage,
                            qtype, dict(zip(engine.DIMS, values)), QUOTES, probe)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(HERE / 'state.py'), *map(str, args)],
                              capture_output=True, text=True)

    def test_correct_fusion_raises_every_node(self):
        before = {k: engine.mastery(self.state['nodes'][k]) for k in self.coverage}
        self.score()
        for k in self.coverage:
            self.assertGreater(engine.mastery(self.state['nodes'][k]), before[k])

    def test_failed_fusion_entropy_almost_unchanged(self):
        before = {k: engine.entropy(engine.distribution(self.state['nodes'][k])) for k in self.coverage}
        self.score(values=(0, 1, 0, 1))
        for k in self.coverage:
            after = engine.entropy(engine.distribution(self.state['nodes'][k]))
            self.assertLess(abs(after - before[k]), .02)

    def test_bisect_partitions_original(self):
        halves = engine.bisect(self.state, 's0')
        self.assertEqual(len(halves), 2)
        self.assertEqual(set.union(*(set(h['S']) for h in halves)), set(self.coverage))
        self.assertFalse(set(halves[0]['S']) & set(halves[1]['S']))
        for half in halves:
            self.assertTrue(0 < len(half['S']) < len(self.coverage))

    def test_missing_quote_rejected_cli_no_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'state.json'
            engine.save(path, self.state)
            before = path.read_bytes()
            result = self.cli('score', '--state', path, '--node', 'n0',
                              '--question-type', 'explanation', '--scores',
                              json.dumps(dict.fromkeys(engine.DIMS, 3)), '--quotes', '{}',
                              '--probe', 'direct')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('missing quotation', result.stderr)
            self.assertEqual(path.read_bytes(), before)

    def test_cycle_rejected(self):
        concepts = engine.load_data(GRAPH)
        concepts[0]['requires'] = ['n2']
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'cycle.json'
            path.write_text(json.dumps(concepts))
            with self.assertRaisesRegex(ValueError, 'cycle'):
                engine.initialize(path)
            self.assertNotEqual(self.cli('init', '--graph', path, '--out', Path(tmp) / 'out').returncode, 0)

    def test_determinism_byte_for_byte_all_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = [Path(tmp) / ('state%d.json' % i) for i in range(2)]
            for path in paths:
                result = self.cli('init', '--graph', GRAPH, '--scenarios', SCENARIOS, '--out', path)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())
            for command, args in [('pick', []), ('bisect', ['--scenario', 's0']), ('report-data', [])]:
                results = [self.cli(command, '--state', p, *args) for p in paths]
                self.assertTrue(all(r.returncode == 0 for r in results))
                self.assertEqual(results[0].stdout, results[1].stdout)
            results = [self.cli('score', '--state', p, '--scenario', 's0',
                                '--question-type', 'application', '--scores', json.dumps(dict.fromkeys(engine.DIMS, 3)),
                                '--quotes', json.dumps(QUOTES), '--probe', 'direct') for p in paths]
            self.assertTrue(all(r.returncode == 0 for r in results))
            self.assertEqual(results[0].stdout, results[1].stdout)
            self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())

    def test_mechanism_gate_overrides_even_strong_prior(self):
        node = self.state['nodes']['n0']
        engine.set_level(node, [.001, .001, .001, .997])
        self.score(coverage=['n0'], values=(3, 0, 3, 3))
        self.assertEqual(node['level']['operable'], 0)
        self.assertEqual(node['level']['deep'], 0)

    def test_boundary_gate(self):
        self.score(coverage=['n0'], values=(3, 2, 3, 0))
        self.assertEqual(self.state['nodes']['n0']['level']['deep'], 0)

    def test_gate_does_not_permanently_prevent_learning(self):
        self.score(coverage=['n0'], values=(3, 0, 3, 3))
        self.assertEqual(engine.mastery(self.state['nodes']['n0']), 0)
        self.score(coverage=['n0'])
        self.assertGreater(engine.mastery(self.state['nodes']['n0']), 0)

    def test_boundary_zero_quote_exception_and_other_zero_rejection(self):
        quotes = {k: v for k, v in QUOTES.items() if k != 'boundary'}
        engine.score(self.state, ['n0'], 'explanation',
                     dict(zip(engine.DIMS, (3, 2, 3, 0))), quotes, 'direct')
        with self.assertRaisesRegex(ValueError, 'missing quotation'):
            engine.score(self.state, ['n0'], 'explanation',
                         dict.fromkeys(engine.DIMS, 0), {}, 'direct')

    def test_tested_low_entropy_nodes_not_selected(self):
        for node in self.state['nodes'].values():
            node['evidence']['count'] = 1
            engine.set_level(node, [0, 0, 0, 1])
        self.assertEqual(engine.pick(self.state), [])

    def test_no_scenarios_fallback(self):
        state = engine.initialize(GRAPH)
        selected = engine.pick(state)
        self.assertEqual(len(selected), 5)
        self.assertTrue(all(c['scenario'] is None and len(c['S']) == 1 for c in selected))

    def test_invalid_scores(self):
        cases = [dict.fromkeys(engine.DIMS, 4), dict.fromkeys(engine.DIMS, -1),
                 {'identify': 3}, dict.fromkeys(engine.DIMS, 1.5), dict.fromkeys(engine.DIMS, True)]
        for scores in cases:
            with self.subTest(scores=scores), self.assertRaises(ValueError):
                engine.score(self.state, ['n0'], 'explanation', scores, QUOTES, 'direct')

    def test_prompted_negative_stronger(self):
        other = copy.deepcopy(self.state)
        self.score(coverage=['n0'], values=(1, 1, 1, 1))
        self.score(state=other, coverage=['n0'], values=(1, 1, 1, 1), probe='after_prompt')
        self.assertLess(engine.mastery(other['nodes']['n0']), engine.mastery(self.state['nodes']['n0']))

    def test_rows_monotone(self):
        expectations = []
        for row in engine.LIKELIHOOD_TABLE:
            p = engine.posterior(engine.BASE, row)
            expectations.append(sum(i * v for i, v in enumerate(p)))
        self.assertEqual(expectations, sorted(expectations))
        self.assertEqual(len(engine.LIKELIHOOD_TABLE), 12)

    def test_difficulty_offsets_and_clamp(self):
        for qtype, row in [('explanation', 9), ('application', 8), ('boundary', 7)]:
            state = copy.deepcopy(self.state)
            self.score(state=state, coverage=['n0'], values=(3, 3, 2, 2), qtype=qtype)
            self.assertEqual(state['history'][-1]['row'], row)
        self.score(coverage=['n0'], values=(0, 0, 0, 0), qtype='boundary')
        self.assertEqual(self.state['history'][-1]['row'], 0)

    def test_evidence_and_single_hop_propagation(self):
        original = copy.deepcopy(self.state)
        self.score(coverage=['n4'])
        self.assertGreater(engine.mastery(self.state['nodes']['n2']), engine.mastery(original['nodes']['n2']))
        self.assertEqual(self.state['nodes']['n0'], original['nodes']['n0'])
        e = self.state['nodes']['n4']['evidence']
        self.assertEqual(e['count'], 1)
        self.assertGreater(e['sharpness'], 0)
        self.assertEqual(e['question_types'], {'explanation': 1})

    def test_report_and_topology(self):
        report = engine.report(self.state)
        path = report['learning_path']
        for k in path:
            for parent in self.state['nodes'][k]['concept']['requires']:
                self.assertLess(path.index(parent), path.index(k))
        self.assertEqual(len(report['nodes']), 10)
        self.assertEqual(len(report['clusters']), 2)
        self.assertIn('observations', report['calibration'])

    def test_noisy_and_expectation_and_cost(self):
        probability, positive, negative = engine.fusion_model(self.state, self.coverage)
        self.assertTrue(0 < probability < 1)
        c = engine.candidate(self.state, 's0', self.coverage, 'diagnosis')
        gain = 0
        hsum = 0
        for key in self.coverage:
            node = self.state['nodes'][key]
            p = engine.distribution(node)
            h = engine.entropy(p)
            hsum += h
            gain += engine.WEIGHTS[node['concept']['importance']] * (
                h - probability * engine.entropy(engine.posterior(p, positive[key])) -
                (1 - probability) * engine.entropy(engine.posterior(p, negative[key])))
        self.assertAlmostEqual(c['gain'], gain)
        self.assertAlmostEqual(c['cost'], 1 + .3 * hsum + .15 * (len(self.coverage) - 1))

    def test_yaml_real_format_and_folded_source(self):
        text = '''- id: a\n  name: Alpha\n  aliases:\n  - Alias\n  cluster: math\n  importance: high\n  source:\n    type: textbook\n    ref: https://example.org/ — Chapter\n      One\n    confidence: high\n  requires: []\n- id: b\n  name: Beta\n  importance: low\n  cluster: math\n  requires:\n  - a\n'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'graph.yaml'
            path.write_text(text)
            state = engine.initialize(path)
            self.assertEqual(state['nodes']['a']['concept']['source']['ref'], 'https://example.org/ — Chapter One')
            self.assertGreater(engine.mastery(state['nodes']['b']), engine.mastery(state['nodes']['a']))

class RealDataTests(unittest.TestCase):
    """The shipped data/ must work without adaptation. Catches schema drift
    between the scenario authors and the engine contract."""

    def test_pick_on_shipped_data(self):
        root = Path(__file__).resolve().parent.parent
        graph, scenarios = root / 'data/concepts.yaml', root / 'data/scenarios.yaml'
        if not (graph.exists() and scenarios.exists()):
            self.skipTest('shipped data absent')
        state = engine.initialize(graph, scenarios)
        self.assertGreater(len(state['nodes']), 50)
        self.assertGreater(len(state['scenarios']), 10)
        picked = engine.pick(state, 5)
        self.assertTrue(picked)
        for c in picked:
            self.assertGreaterEqual(len(c['S']), 2)
            self.assertLessEqual(len(c['S']), 5)
            self.assertIsInstance(c['question_type'], str)
        b = engine.bisect(state, picked[0]['scenario'])
        self.assertEqual(len(b), 2)
        engine.report(state)


if __name__ == '__main__':
    unittest.main(verbosity=2)
