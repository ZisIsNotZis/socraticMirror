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

    def score_cli(self, path, *flags):
        return self.cli('score', '--state', path, '--scenario', 's0',
                        '--question-type', 'explanation', '--scores',
                        json.dumps(dict.fromkeys(engine.DIMS, 3)), '--quotes',
                        json.dumps(QUOTES), '--probe', 'direct', *flags)

    def test_only_dimension_does_not_double_count(self):
        self.score(coverage=['n0'])
        before = copy.deepcopy(self.state['nodes']['n0']['evidence'])
        engine.score(self.state, ['n0'], 'explanation', dict.fromkeys(engine.DIMS, 3),
                     QUOTES, 'direct', only=['mechanism'])
        after = self.state['nodes']['n0']['evidence']
        self.assertEqual(after['count'], before['count'] + 1)
        for d in ('identify', 'application', 'boundary'):
            self.assertEqual(after['dimensions'][d], before['dimensions'][d])
        self.assertEqual(after['dimensions']['mechanism']['count'], 2)

    def test_only_marginalizes_unobserved_scores(self):
        other = copy.deepcopy(self.state)
        engine.score(self.state, ['n0'], 'explanation', dict.fromkeys(engine.DIMS, 3),
                     QUOTES, 'direct', only=['mechanism'])
        # Gates stay identical while unused values change.
        engine.score(other, ['n0'], 'explanation',
                     dict(zip(engine.DIMS, (0, 3, 0, 3))), QUOTES, 'direct',
                     only=['mechanism'])
        self.assertEqual(self.state['nodes'], other['nodes'])
        likelihood = [sum(engine.LIKELIHOOD_TABLE[min(11, 2 + sum(v))][i]
                          ** (.35 if min(11, 2 + sum(v)) < 6 else 1)
                          for v in engine.itertools.product(range(4), repeat=3)) / 64
                      for i in range(4)]
        expected = engine.posterior(engine.BASE, likelihood)
        for got, want in zip(engine.distribution(self.state['nodes']['n0']), expected):
            self.assertAlmostEqual(got, want)

    def test_nodes_subset_skips_others(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'state.json'
            engine.save(path, self.state)
            result = self.score_cli(path, '--nodes', self.coverage[-1])
            self.assertEqual(result.returncode, 0, result.stderr)
            updated = engine.load_data(path)
            for k in set(self.state['nodes']) - {self.coverage[-1]}:
                self.assertEqual(updated['nodes'][k], self.state['nodes'][k])
            self.assertEqual(engine.report(updated)['contaminated_nodes'], [])

    def test_nodes_must_be_subset(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'state.json'
            engine.save(path, self.state)
            before = path.read_bytes()
            for flags in [('--nodes', 'not-covered'), ('--nodes', ''),
                          ('--nodes', self.coverage[0] + ',not-covered'),
                          ('--only', 'invalid')]:
                result = self.score_cli(path, *flags)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(path.read_bytes(), before)

    def test_required_observables_passthrough(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'state.json'
            for present in (False, True):
                if present:
                    self.state['scenarios'][0]['required_observables'] = {'dtype': ['fp16', 'fp32']}
                engine.save(path, self.state)
                result = self.score_cli(path)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('whole-coverage scoring may contaminate untested nodes', result.stderr)
                output = json.loads(result.stdout)
                if present:
                    self.assertEqual(output['required_observables'],
                                     self.state['scenarios'][0]['required_observables'])
                else:
                    self.assertNotIn('required_observables', output)
                report = json.loads(self.cli('report-data', '--state', path).stdout)
                self.assertEqual(report['contaminated_nodes'], sorted(self.coverage))

    def test_determinism_with_new_flags(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = [Path(tmp) / ('state%d.json' % i) for i in range(2)]
            results = []
            for path in paths:
                engine.save(path, self.state)
                results.append(self.score_cli(path, '--nodes', ','.join(self.coverage[:2]),
                                               '--only', 'mechanism,identify',
                                               '--only', 'mechanism'))
            self.assertTrue(all(r.returncode == 0 for r in results), results)
            self.assertEqual(results[0].stdout, results[1].stdout)
            self.assertEqual(results[0].stderr, results[1].stderr)
            self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())

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

    def test_pick_exclude(self):
        root = Path(__file__).resolve().parent.parent
        graph, scenarios = root / 'data/concepts.yaml', root / 'data/scenarios.yaml'
        if not (graph.exists() and scenarios.exists()):
            self.skipTest('shipped data absent')
        state = engine.initialize(graph, scenarios)
        picked = engine.pick(state, 5)
        self.assertTrue(picked)
        excluded = {c['scenario'] for c in picked if c['scenario']}
        again = engine.pick(state, 5, excluded)
        self.assertFalse({c['scenario'] for c in again} & excluded)



class ThreeStateTests(unittest.TestCase):
    def setUp(self):
        self.state = engine.initialize(GRAPH, SCENARIOS)

    def apply(self, values, state=None, **kwargs):
        target = self.state if state is None else state
        engine.score(target, ['n0'], kwargs.pop('qtype', 'boundary'),
                     dict(zip(engine.DIMS, values)), QUOTES, 'direct', **kwargs)
        return target['nodes']['n0']

    def test_mixed_states_accepted(self):
        node = self.apply((3, 2, 'absent_asked', 'unverified'))
        dims = node['evidence']['dimensions']
        for d, status, value in [('identify', 'scored', 3),
                                 ('application', 'absent_asked', None),
                                 ('boundary', 'unverified', None)]:
            self.assertEqual((dims[d]['status'], dims[d]['value']), (status, value))
        self.assertEqual(dims['application']['count'], 0)
        self.assertEqual(dims['application']['sharpness'], 0)
        with self.assertRaises(ValueError):
            engine.score(self.state, ['n0'], 'boundary', {'identify': 3}, {}, 'direct')

    def test_absent_asked_weaker_than_zero(self):
        other = copy.deepcopy(self.state)
        absent = self.apply((3, 3, 3, 'absent_asked'))
        zero = self.apply((3, 3, 3, 0), other)
        self.assertGreater(engine.mastery(absent), engine.mastery(zero))
        # Exactly half zero likelihood plus half marginalized likelihood.
        neutral = copy.deepcopy(engine.initialize(GRAPH, SCENARIOS))
        p = engine.distribution(neutral['nodes']['n0'])
        rows = [engine.LIKELIHOOD_TABLE[6 + v] for v in range(4)]
        mix = [.5 * rows[0][i] + .5 * sum(r[i] for r in rows) / 4 for i in range(4)]
        for got, want in zip(engine.distribution(absent), engine.posterior(p, mix)):
            self.assertAlmostEqual(got, want)

    def test_unverified_dim_not_in_likelihood(self):
        other = copy.deepcopy(self.state)
        self.apply((3, 3, 3, 3))
        self.apply((3, 3, 3, 3), other)
        count = self.state['nodes']['n0']['evidence']['dimensions']['application']['count']
        self.apply((3, 3, 'unverified', 3))
        self.apply((3, 3, 3, 3), other, only=['identify', 'mechanism', 'boundary'])
        self.assertEqual(self.state['nodes']['n0']['level'], other['nodes']['n0']['level'])
        self.assertEqual(self.state['nodes']['n0']['evidence']['dimensions']['application']['count'], count)

    def test_gate_ignores_non_scored_mechanism(self):
        for mechanism in ('absent_asked', 'unverified'):
            fresh = engine.initialize(GRAPH, SCENARIOS)
            node = self.apply((3, mechanism, 3, 3), fresh)
            self.assertGreater(node['level']['deep'], 0)
            self.assertGreater(engine.mastery(node), 0)

    def test_absent_asked_rejected_when_not_asked(self):
        before = engine.dumps(self.state)
        with self.assertRaisesRegex(ValueError, 'use unverified'):
            self.apply((3, 'absent_asked', 3, 3), qtype='diagnosis')
        self.assertEqual(engine.dumps(self.state), before)
        self.apply((3, 'absent_asked', 3, 3), qtype='diagnosis', asks=['boundary'])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'state.json'
            fresh = engine.initialize(GRAPH, SCENARIOS)
            fresh['scenarios'][0]['asks'] = ['boundary']
            engine.save(path, fresh)
            result = subprocess.run([sys.executable, str(HERE / 'state.py'), 'score',
                # Use authored coverage, not an assumed fixture node (n0 is outside s0).
                '--state', str(path), '--scenario', 's0', '--nodes', fresh['scenarios'][0]['instantiates'][0],
                '--question-type', 'diagnosis', '--scores',
                json.dumps(dict(zip(engine.DIMS, (3, 'absent_asked', 3, 3)))),
                '--quotes', json.dumps(QUOTES), '--probe', 'direct'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_report_null_p_mastery_when_unscored(self):
        self.assertIsNone(engine.report(self.state)['nodes']['n0']['p_mastery'])
        before = copy.deepcopy(self.state['nodes']['n0']['level'])
        self.apply(('unverified',) * 4)
        self.assertEqual(self.state['nodes']['n0']['level'], before)
        self.apply(('absent_asked',) * 4)
        report = engine.report(self.state)
        self.assertIsNone(report['nodes']['n0']['p_mastery'])
        self.assertEqual(report['nodes']['n0']['status'], 'unverified')
        self.assertIsNone(report['clusters'][self.state['nodes']['n0']['concept']['cluster']]['mean_p_mastery'])
        self.apply((3, 'unverified', 'unverified', 'unverified'))
        self.assertEqual(engine.report(self.state)['nodes']['n0']['status'], 'scored')

    def test_legacy_integer_scores_equivalent(self):
        for values in ((3, 3, 3, 3), (3, 0, 3, 3), (3, 2, 3, 0), (1, 1, 1, 1)):
            a = engine.initialize(GRAPH, SCENARIOS)
            b = copy.deepcopy(a)
            integers = dict(zip(engine.DIMS, values))
            explicit = {d: {'status': 'scored', 'value': v} for d, v in integers.items()}
            for scores, target in ((integers, a), (explicit, b)):
                engine.score(target, ['n0'], 'explanation', scores, QUOTES, 'direct')
            self.assertEqual(engine.dumps(a), engine.dumps(b))

    def test_determinism_with_three_states(self):
        states = [copy.deepcopy(self.state) for _ in range(2)]
        for state in states:
            self.apply((3, 'absent_asked', 2, 'unverified'), state)
        self.assertEqual(engine.dumps(states[0]), engine.dumps(states[1]))
        self.assertEqual(engine.dumps(engine.report(states[0])), engine.dumps(engine.report(states[1])))


if __name__ == '__main__':
    unittest.main(verbosity=2)
