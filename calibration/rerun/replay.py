#!/usr/bin/env python3
"""WP-8c2: replay existing human judgments, never generate or rewrite answers."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engine import state as engine
OUT = ROOT / 'calibration/rerun'


def save(path, value):
    path.write_text(engine.dumps(value))


def cli(*args):
    cmd = ['python3', 'engine/state.py', *map(str, args)]
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    with (OUT / 'commands.jsonl').open('a') as f:
        f.write(json.dumps({'command': cmd, 'returncode': p.returncode,
                            'stdout': p.stdout, 'stderr': p.stderr}, ensure_ascii=False) + '\n')
    if p.returncode:
        raise RuntimeError(p.stderr)
    return json.loads(p.stdout)


def protected_hashes():
    paths = ['engine', 'references', 'data', 'docs', 'sessions',
             'calibration/answers', 'calibration/sessions', 'calibration/selection']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for name in paths for p in (ROOT / name).rglob('*')
            if p.is_file() and '__pycache__' not in p.parts}


def main():
    assert not (OUT / 'commands.jsonl').exists(), 'Do not overwrite a run'
    before = protected_hashes()
    selected = json.loads((ROOT / 'calibration/selection/selected.json').read_text())
    results, decomposition, checks, eligibility = [], [], [], []
    for pick in selected:
        sid, node = pick['scenario'], pick['observed_nodes'][0]
        baseline = None
        rows = []
        for variant in 'abcd':
            folder = OUT / f'{sid}-{variant}'
            folder.mkdir()
            statefile = folder / 'state.json'
            cli('init', '--graph', 'data/concepts.yaml', '--scenarios', 'data/scenarios.yaml', '--out', statefile)
            initial = json.loads(statefile.read_text())
            scenario = next(s for s in initial['scenarios'] if s['id'] == sid)
            if variant == 'a':
                eligibility.append({'scenario': sid, 'asks': scenario['asks'], 'eligible': 'boundary' in scenario['asks']})
            if 'boundary' not in scenario['asks']:
                break
            prior = engine.mastery(initial['nodes'][node])
            baseline = initial
            judgment = json.loads((ROOT / 'calibration/sessions' / f'{sid}-{variant}' / 'judgment.json').read_text())
            for k in ('submitted', 'reason'):
                judgment.pop(k, None)
            if variant == 'b':
                judgment['scores']['boundary'] = 'absent_asked'
                judgment['anchor_reasons'] = {'boundary': '按WP-8c2指定的整段边界消融标签；asks含boundary。保留正文仍可能含范围限制的判分歧义，见报告。', 'application': '保留可执行方案与验证，删除故障调整路径，维持原应用2。'}
            if variant == 'd':
                judgment['reason'] = '仅说我不知道；四维均无可判证据，全部unverified，不冒充0。'
            judgment['source_answer'] = f'calibration/answers/{sid}/{variant}.md'
            judgment['source_judgment'] = f'calibration/sessions/{sid}-{variant}/judgment.json'
            judgment['framework_A'] = judgment['scores'].copy()
            judgment['framework_B'] = judgment['scores'].copy()
            judgment['low_confidence'] = False
            text = (ROOT / judgment['source_answer']).read_text()
            for dim, score in judgment['scores'].items():
                if type(score) is int:
                    assert judgment['quotes'][dim] and judgment['quotes'][dim] in text
            save(folder / 'judgment.json', judgment)
            accepted = cli('score', '--state', statefile, '--scenario', sid, '--nodes', node,
                           '--question-type', pick['question_type'], '--scores', json.dumps(judgment['scores']),
                           '--quotes', json.dumps(judgment['quotes'], ensure_ascii=False), '--probe', 'direct')
            save(folder / 'accepted.json', accepted)
            report = cli('report-data', '--state', statefile)
            save(folder / 'report-data.json', report)
            result = {'scenario': sid, 'variant': variant, 'node': node, 'scores': judgment['scores'],
                      'initial_prior': prior, 'p_mastery': report['nodes'][node]['p_mastery'],
                      'status': report['nodes'][node]['status']}
            rows.append(result)
            results.append(result)
        if len(rows) != 4:
            checks.append({'scenario': sid, 'excluded': True})
            continue
        a, b, c, d = rows
        check = {'scenario': sid, 'a_gt_b_gt_c': all(r['p_mastery'] is not None for r in rows[:3]) and a['p_mastery'] > b['p_mastery'] > c['p_mastery'],
                 'd_unverified_null': d['p_mastery'] is None and d['status'] == 'unverified',
                 'c_below_prior': c['p_mastery'] < c['initial_prior']}
        check['passed'] = all(check[k] for k in ('a_gt_b_gt_c', 'd_unverified_null', 'c_below_prior'))
        checks.append(check)
        # Diagnostic only: two-factor Shapley attribution; no changed scores submitted.
        values = {}
        quotes = json.loads((OUT / f'{sid}-a/judgment.json').read_text())['quotes']
        for app_changed, boundary_changed in ((False, False), (True, False), (False, True), (True, True)):
            scores = a['scores'].copy()
            if app_changed:
                scores['application'] = b['scores']['application']
            if boundary_changed:
                scores['boundary'] = 'absent_asked'
            diagnostic = engine.score(copy.deepcopy(baseline), [node], pick['question_type'], scores, quotes, 'direct', restrict_updates=True, asks=scenario['asks'])
            values[f'{int(app_changed)}{int(boundary_changed)}'] = engine.mastery(diagnostic['nodes'][node])
        app = ((values['00'] - values['10']) + (values['01'] - values['11'])) / 2
        boundary = ((values['00'] - values['01']) + (values['10'] - values['11'])) / 2
        gap = a['p_mastery'] - b['p_mastery']
        assert abs(app + boundary - gap) < 1e-12
        decomposition.append({'scenario': sid, 'gap': gap, 'identify': 0, 'mechanism': 0,
                              'application': app, 'boundary': boundary, 'diagnostic_p': values})
    after = protected_hashes()
    assert before == after, 'Protected artifacts changed'
    save(OUT / 'protected-hashes.json', {'before': before, 'after_equal': True})
    save(OUT / 'results.json', results)
    save(OUT / 'checks.json', checks)
    save(OUT / 'eligibility.json', eligibility)
    save(OUT / 'decomposition.json', decomposition)
    print(f'40 reused answers; {len(results)} independent init/score/report sessions')
    print(f"Full contract: {sum(c.get('passed', False) for c in checks)}/10; eligibility: {sum(e['eligible'] for e in eligibility)}/10")
    print('Protected file hashes unchanged; scored quotations exact; decomposition sums verified')


if __name__ == '__main__':
    main()
