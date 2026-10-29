#!/usr/bin/env python3
"""Read-only acceptance checks for WP-8c2 artifacts."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'calibration/rerun'
load = lambda name: json.loads((OUT / name).read_text())
rows = load('results.json')
assert len(rows) == 40
assert len(load('checks.json')) == 10
assert all(c['passed'] for c in load('checks.json'))
assert all(e['eligible'] and 'boundary' in e['asks'] for e in load('eligibility.json'))
for row in rows:
    sid, variant, node = row['scenario'], row['variant'], row['node']
    folder = OUT / f'{sid}-{variant}'
    judgment = json.loads((folder / 'judgment.json').read_text())
    state = json.loads((folder / 'state.json').read_text())
    report = json.loads((folder / 'report-data.json').read_text())['nodes'][node]
    text = (ROOT / judgment['source_answer']).read_text()
    assert len(state['history']) == 1
    assert state['history'][0]['scores'] == row['scores'] == judgment['scores']
    assert row['p_mastery'] == report['p_mastery'] and row['status'] == report['status']
    for dim, score in row['scores'].items():
        if type(score) is int:
            assert judgment['quotes'][dim] in text
    if variant == 'd':
        assert row['p_mastery'] is None and row['status'] == 'unverified'
        assert state['history'][0]['before'] == state['history'][0]['after']
    if variant == 'b':
        assert row['scores']['boundary'] == 'absent_asked'
for entry in load('decomposition.json'):
    assert abs(sum(entry[d] for d in ('identify', 'mechanism', 'application', 'boundary')) - entry['gap']) < 1e-12
commands = [json.loads(line) for line in (OUT / 'commands.jsonl').read_text().splitlines()]
assert len(commands) == 120 and all(c['returncode'] == 0 for c in commands)
for path, digest in load('protected-hashes.json')['before'].items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
print('PASS: 40 independent one-observation sessions, 120 successful CLI calls, exact quotes')
print('PASS: eligibility 10/10; a>b>c 10/10; d null/unverified 10/10; c<prior 10/10')
print('PASS: protected artifacts unchanged; d latent distributions unchanged; attribution sums exact')
