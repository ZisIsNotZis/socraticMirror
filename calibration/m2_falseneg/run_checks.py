#!/usr/bin/env python3
"""WP-9 dry-run checks: false-negative control + two-session stability.

Reads the two dry-run sessions, applies the per-node judgments in
judgments.json through the real engine, then asserts:
  1. no fixture node is left at level `unknown` after scoring
     (a node the examinee certainly knows must not be judged "不会");
  2. the same node does not move two levels between session A and B.

This is a calibration harness, not a product session: probes are targeted at
fixture nodes instead of being chosen by `pick`, and the examinee is a model.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'engine'))
import state as E  # noqa: E402

LEVELS = list(E.LEVELS)
PROBES = json.loads((Path(__file__).parent / 'probes.json').read_text())
JUDGMENTS = json.loads((Path(__file__).parent / 'judgments.json').read_text())


def label(node):
    return max(node['level'], key=node['level'].get)


def apply(state, probe, judgment):
    for node_id in judgment['discussed']:
        item = judgment['nodes'][node_id]
        E.score(state, [node_id], probe['question_type'], item['scores'],
                item['quotes'], 'direct', asks=())


def main():
    rows, failures = [], []
    states = {}
    for session, spec in PROBES['sessions'].items():
        state = E.initialize(str(ROOT / 'data/concepts.yaml'),
                             str(ROOT / 'data/scenarios.yaml'))
        for probe in spec['probes']:
            judgment = JUDGMENTS.get(probe['id'])
            if judgment is None:
                failures.append(f'{probe["id"]}: missing judgment')
                continue
            apply(state, probe, judgment)
        E.save(str(ROOT / spec['state']), state)
        states[session] = state

    for session, spec in PROBES['sessions'].items():
        for probe in spec['probes']:
            for node_id in probe['S']:
                node = states[session]['nodes'][node_id]
                lab = label(node)
                rows.append((session, probe['id'], node_id, lab,
                             round(E.mastery(node), 3)))
                if lab == 'unknown':
                    failures.append(f'{session}/{probe["id"]}: {node_id} judged unknown')

    # stability: same node across sessions, only where both sessions scored it
    stability = []
    nodes_a = {r[2]: r for r in rows if r[0] == 'A'}
    nodes_b = {r[2]: r for r in rows if r[0] == 'B'}
    scored_a = {n for p in PROBES['sessions']['A']['probes']
                for n in JUDGMENTS.get(p['id'], {}).get('discussed', [])}
    scored_b = {n for p in PROBES['sessions']['B']['probes']
                for n in JUDGMENTS.get(p['id'], {}).get('discussed', [])}
    for node_id in sorted(set(nodes_a) & set(nodes_b) & scored_a & scored_b):
        a, b = nodes_a[node_id], nodes_b[node_id]
        delta = abs(LEVELS.index(a[3]) - LEVELS.index(b[3]))
        stability.append((node_id, a[3], b[3], delta))
        if delta >= 2:
            failures.append(f'stability: {node_id} {a[3]} -> {b[3]} (jump {delta})')

    out = {
        'rows': rows,
        'stability': stability,
        'failures': failures,
        'false_negative_count': sum(1 for r in rows if r[3] == 'unknown'),
        'stable': not any(s[3] >= 2 for s in stability),
        'nodes_measured_in_both': sorted(scored_a & scored_b),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())
