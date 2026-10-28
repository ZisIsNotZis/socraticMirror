#!/usr/bin/env python3
"""Deterministic rubric/state engine; no semantic interpretation or dependencies.

Input: JSON or the data files' YAML subset (mappings, sequences, scalar strings,
inline JSON lists, folded plain scalars). No YAML tags/anchors or executable types.
See schema/ for the persisted contract. Scores mutate state atomically; other
commands only read. Fusion scoring adds --scenario as an alternative to --node.
"""
import argparse
import ast
import json
import math
import os
from pathlib import Path
import sys
import tempfile

LEVELS = ('unknown', 'aware', 'operable', 'deep')
DIMS = ('identify', 'mechanism', 'application', 'boundary')
# M2 calibration knobs: ordered exponential-family rows give monotone likelihood
# ratios (higher rubric row always favors higher states). 0 and 1 share row zero.
LIKELIHOOD_TABLE = tuple(tuple(math.exp((r - 5.5) * (k - 1.5) * .32)
                               for k in range(4)) for r in range(12))
OFFSETS = {'explanation': 0, 'application': -1, 'boundary': -2,
           'diagnosis': -1, 'transfer': -2}
BASE = (.30, .35, .25, .10)
WEIGHTS = {'high': 3., 'medium': 2., 'low': 1.}
ABILITY = (.05, .25, .80, .97)
SLIP = .08
GUESS = .03
FAILURE_STRENGTH = .08  # ambiguous fusion failure barely moves any one node
PARENT_LIFT = .18      # small noisy-OR prior lift, never prerequisite certainty
PROPAGATION = .15      # one hop only; no recursive confidence amplification
HIGH_ENTROPY = 1.2
RECOVERY_FLOOR = .001  # gates are per-observation caps, not permanent impossibility


def dumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'


def scalar(text):
    text = text.strip()
    if text in ('[]', '{}', 'null', 'true', 'false') or text.startswith('["'):
        return json.loads(text)
    if text.startswith(('"', "'")):
        try:
            return ast.literal_eval(text)
        except (ValueError, SyntaxError) as exc:
            raise ValueError('unsupported quoted YAML scalar: ' + text) from exc
    if text.startswith(('!', '&', '*', '{', '[')):
        raise ValueError('unsupported YAML scalar; use JSON for complex inline data')
    return text


def load_data(path):
    text = Path(path).read_text(encoding='utf-8')
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    lines = [(len(s) - len(s.lstrip()), s.strip()) for s in text.splitlines()
             if s.strip() and not s.lstrip().startswith('#')]

    def parse(i, indent):
        seq = lines[i][1].startswith('- ')
        out = [] if seq else {}
        while i < len(lines) and lines[i][0] == indent:
            s = lines[i][1]
            if s.startswith('- ') != seq:
                break
            if seq:
                item = s[2:]
                if ': ' in item or item.endswith(':'):
                    # Sequence mapping item: recursively parse its indented tail.
                    lines[i] = (indent + 2, item)
                    value, i = parse(i, indent + 2)
                else:
                    value = scalar(item)
                    i += 1
                out.append(value)
                continue
            if ':' not in s:
                raise ValueError('expected YAML key: ' + s)
            key, rest = s.split(':', 1)
            if key in out:
                raise ValueError('duplicate YAML key: ' + key)
            i += 1
            if rest.strip():
                value = scalar(rest)
                # PyYAML plain scalars may wrap across physical lines.
                while i < len(lines) and lines[i][0] > indent:
                    value = str(value) + ' ' + lines[i][1]
                    i += 1
            elif i < len(lines) and (lines[i][0] > indent or
                                    (lines[i][0] == indent and lines[i][1].startswith('- '))):
                value, i = parse(i, lines[i][0])
            else:
                value = None
            out[key] = value
        return out, i

    if not lines:
        raise ValueError('empty data file')
    value, end = parse(0, lines[0][0])
    if end != len(lines):
        raise ValueError('unsupported YAML indentation')
    return value


def normalize(values):
    total = sum(values)
    if total <= 0:
        raise ValueError('zero probability mass')
    return [v / total for v in values]


def entropy(p):
    return -sum(v * math.log2(v) for v in p if v)


def posterior(p, likelihood):
    return normalize([a * b for a, b in zip(p, likelihood)])


def distribution(node):
    return [node['level'][k] for k in LEVELS]


def set_level(node, p):
    node['level'] = dict(zip(LEVELS, p))


def mastery(node):
    return sum(distribution(node)[2:])


def topology(nodes):
    order, visiting, done = [], set(), set()

    def visit(key):
        if key not in nodes:
            raise ValueError('dangling requires: ' + key)
        if key in visiting:
            raise ValueError('requires cycle: ' + key)
        if key in done:
            return
        visiting.add(key)
        for parent in sorted(nodes[key]['concept']['requires']):
            visit(parent)
        visiting.remove(key)
        done.add(key)
        order.append(key)
    for key in sorted(nodes):
        visit(key)
    return order


def initialize(graph, scenarios=None):
    concepts = load_data(graph)
    if isinstance(concepts, dict):
        concepts = concepts.get('concepts', concepts.get('nodes'))
    if not isinstance(concepts, list) or not concepts:
        raise ValueError('graph must contain a nonempty concept list')
    nodes = {}
    for c in concepts:
        key = c['id']
        if key in nodes:
            raise ValueError('duplicate concept: ' + key)
        if c['importance'] not in WEIGHTS or not isinstance(c['requires'], list):
            raise ValueError('invalid importance/requires: ' + key)
        nodes[key] = {'concept': c, 'level': {}, 'evidence': {
            'count': 0, 'question_types': {}, 'sharpness': 0., 'propagated': 0}}
    for key in topology(nodes):
        no_parent = 1.
        for parent in nodes[key]['concept']['requires']:
            no_parent *= 1 - mastery(nodes[parent])
        lift = PARENT_LIFT * (1 - no_parent)
        p = list(BASE)
        p[0] -= lift * BASE[0]
        p[1] -= lift * BASE[1]
        p[2] += lift * .65 * .75
        p[3] += lift * .65 * .25
        set_level(nodes[key], normalize(p))
    items = load_data(scenarios) if scenarios else []
    if isinstance(items, dict):
        items = items.get('scenarios')
    seen = set()
    for s in items:
        # Normalize the authored shape (list of {type, angle}) to the engine's
        # contract (list of question-type strings). The angles stay available
        # to the examiner as ask_detail.
        asks = s.get('asks')
        if asks and isinstance(asks[0], dict):
            s['ask_detail'] = asks
            s['asks'] = [a['type'] for a in asks if 'type' in a]
        if s['id'] in seen:
            raise ValueError('duplicate scenario: ' + s['id'])
        seen.add(s['id'])
        coverage = s['instantiates']
        if not 2 <= len(coverage) <= 5 or len(set(coverage)) != len(coverage):
            raise ValueError('scenario needs 2–5 distinct nodes')
        if not set(coverage) <= nodes.keys():
            raise ValueError('scenario has dangling concept')
        for field in ('title', 'brief', 'asks', 'expected_elements', 'difficulty', 'source'):
            if field not in s:
                raise ValueError('scenario missing ' + field)
    return {'version': 1, 'nodes': nodes, 'scenarios': items, 'history': []}


def fusion_model(state, coverage):
    """Noisy AND: P(pass|levels)=guess+(1-slip-guess)*product(ability).

    Conditional marginals are exact under independent node beliefs. Failure
    likelihoods are tempered toward 1: a miss localizes almost nothing. This is
    an explicitly conservative approximation, not an exact joint posterior.
    """
    means = {k: sum(p * a for p, a in zip(distribution(state['nodes'][k]), ABILITY))
             for k in coverage}
    amplitude = 1 - SLIP - GUESS
    pass_prob = GUESS + amplitude * math.prod(means.values())
    success, failure = {}, {}
    for key in coverage:
        others = math.prod(means[k] for k in coverage if k != key)
        success[key] = [GUESS + amplitude * a * others for a in ABILITY]
        failure[key] = [1 - FAILURE_STRENGTH * v for v in success[key]]
    return pass_prob, success, failure


def score(state, coverage, question_type, scores, quotes, probe):
    if not isinstance(scores, dict) or set(scores) != set(DIMS) or any(type(scores[d]) is not int or
                                       not 0 <= scores[d] <= 3 for d in DIMS):
        raise ValueError('scores require four integer dimensions in 0..3')
    if not isinstance(quotes, dict):
        raise ValueError('quotes must be an object')
    if question_type not in OFFSETS or probe not in ('direct', 'after_prompt'):
        raise ValueError('invalid question_type/probe')
    for d in DIMS:
        quote = quotes.get(d)
        if not isinstance(quote, str) or not quote.strip():
            if d == 'boundary' and scores[d] == 0:
                print('warning: boundary=0 without quotation', file=sys.stderr)
            else:
                raise ValueError('missing quotation: ' + d)
    if not coverage or len(coverage) > 5 or not set(coverage) <= state['nodes'].keys():
        raise ValueError('invalid coverage')
    total = sum(scores.values())
    row = max(0, min(11, total - 1 + OFFSETS[question_type]))
    likelihood = list(LIKELIHOOD_TABLE[row])
    # First omission is weak evidence; a prompted omission is fully diagnostic.
    if row < 6 and probe == 'direct':
        likelihood = [v ** .35 for v in likelihood]
    cap = 1 if scores['mechanism'] == 0 else (2 if scores['boundary'] == 0 and
                                             scores['mechanism'] <= 2 else 3)
    before = {k: state['nodes'][k]['level'].copy() for k in coverage}
    _, positive, negative = fusion_model(state, coverage)
    for key in coverage:
        node = state['nodes'][key]
        evidence_likelihood = likelihood
        if len(coverage) > 1:
            # A high fusion rubric is shared strong positive evidence. A failed
            # fusion cannot assign blame; use weak noisy-AND failure marginals.
            if row >= 7:
                evidence_likelihood = [a * b for a, b in zip(likelihood, positive[key])]
            else:
                strength = 3 if probe == 'after_prompt' else 1
                evidence_likelihood = [v ** strength for v in negative[key]]
        # A previous hard gate must not make later demonstrated learning
        # mathematically impossible (Bayesian zero is otherwise absorbing).
        prior = normalize([max(RECOVERY_FLOOR, v) for v in distribution(node)])
        updated = posterior(prior, evidence_likelihood)
        # Gates cap support, not merely argmax; a strong prior cannot evade them.
        updated = normalize([v if i <= cap else 0. for i, v in enumerate(updated)])
        set_level(node, updated)
        e = node['evidence']
        e['count'] += 1
        e['question_types'][question_type] = e['question_types'].get(question_type, 0) + 1
        e['sharpness'] = 1 - math.exp(-e['count'] / 3)
    # Only strong direct evidence lifts immediate prerequisites; never recurse.
    parents = set()
    if row >= 9 and cap == 3:
        for key in coverage:
            if mastery(state['nodes'][key]) >= .75:
                parents.update(state['nodes'][key]['concept']['requires'])
    for parent in sorted(parents - set(coverage)):
        node = state['nodes'][parent]
        set_level(node, posterior(distribution(node), [1, 1, 1 + PROPAGATION,
                                                     1 + PROPAGATION]))
        node['evidence']['propagated'] += 1
    state['history'].append({'nodes': list(coverage), 'question_type': question_type,
                             'scores': scores, 'quotes': quotes, 'probe': probe,
                             'total': total, 'row': row, 'before': before,
                             'after': {k: state['nodes'][k]['level'].copy() for k in coverage}})
    return state


def candidate(state, scenario, coverage, question_type):
    probability, positive, negative = fusion_model(state, coverage)
    gain = 0.
    hsum = 0.
    for key in coverage:
        node = state['nodes'][key]
        p = distribution(node)
        h = entropy(p)
        hsum += h
        delta = h - probability * entropy(posterior(p, positive[key])) - (
            1 - probability) * entropy(posterior(p, negative[key]))
        gain += WEIGHTS[node['concept']['importance']] * delta
    cost = 1 + .3 * hsum + .15 * (len(coverage) - 1)
    return {'scenario': scenario, 'S': coverage, 'question_type': question_type,
            'gain': gain, 'cost': cost, 'utility': gain / cost,
            'reason': 'Importance-weighted expected entropy reduction over %d nodes per unit cost.' % len(coverage)}


def pick(state, top=5):
    candidates = []
    sources = [(s['id'], s['instantiates'], s['asks']) for s in state['scenarios']]
    if not sources:
        sources = [(None, [k], ['application']) for k in sorted(state['nodes'])]
    for sid, coverage, asks in sources:
        selected = sorted(k for k in coverage if not state['nodes'][k]['evidence']['count'] or
                          entropy(distribution(state['nodes'][k])) >= HIGH_ENTROPY)
        if not selected:
            continue
        types = sorted(set(asks) & OFFSETS.keys()) or ['diagnosis']
        for qtype in types:
            candidates.append(candidate(state, sid, selected, qtype))
    return sorted(candidates, key=lambda c: (-c['utility'], c['scenario'] or '',
                                            c['S'], c['question_type']))[:top]


def bisect(state, sid):
    s = next((s for s in state['scenarios'] if s['id'] == sid), None)
    if s is None:
        raise ValueError('unknown scenario: ' + sid)
    coverage = sorted(s['instantiates'])
    half = len(coverage) // 2
    return [candidate(state, sid, part, 'diagnosis') for part in
            (coverage[:half], coverage[half:])]


def report(state):
    nodes, clusters = {}, {}
    for key, node in sorted(state['nodes'].items()):
        nodes[key] = {'level': node['level'], 'evidence': node['evidence'],
                      'p_mastery': mastery(node), 'entropy': entropy(distribution(node))}
        cluster = node['concept']['cluster']
        clusters.setdefault(cluster, []).append(key)
    summary = {c: {'nodes': keys, 'mean_p_mastery': sum(nodes[k]['p_mastery'] for k in keys) / len(keys),
                   'tested': sum(state['nodes'][k]['evidence']['count'] > 0 for k in keys)}
               for c, keys in clusters.items()}
    # Kahn ordering, importance first among ready nodes; no dependent can jump a prerequisite.
    pending, path = set(state['nodes']), []
    while pending:
        ready = [k for k in pending if not (set(state['nodes'][k]['concept']['requires']) & pending)]
        key = min(ready, key=lambda k: (-WEIGHTS[state['nodes'][k]['concept']['importance']],
                                        nodes[k]['p_mastery'], k))
        path.append(key)
        pending.remove(key)
    return {'nodes': nodes, 'clusters': summary, 'learning_path': path,
            'calibration': {'observations': state['history'],
                            'semantic_hedging': None,
                            'note': 'Raw rubric/quotes only; hedging and correctness require external labels.'}}


def save(path, state):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         delete=False) as out:
            temporary = out.name
            out.write(dumps(state))
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('--graph', required=True)
    init.add_argument('--scenarios')
    init.add_argument('--out', required=True)
    for name in ('score', 'pick', 'bisect', 'report-data'):
        cmd = sub.add_parser(name)
        cmd.add_argument('--state', required=True)
        if name == 'score':
            target = cmd.add_mutually_exclusive_group(required=True)
            target.add_argument('--node')
            target.add_argument('--scenario')
            cmd.add_argument('--question-type', choices=OFFSETS, required=True)
            cmd.add_argument('--scores', required=True)
            cmd.add_argument('--quotes', required=True)
            cmd.add_argument('--probe', choices=('direct', 'after_prompt'), required=True)
        elif name == 'pick':
            cmd.add_argument('--top', type=int, default=5)
        elif name == 'bisect':
            cmd.add_argument('--scenario', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'init':
            state = initialize(args.graph, args.scenarios)
            save(args.out, state)
            result = {'nodes': len(state['nodes']), 'scenarios': len(state['scenarios']), 'out': args.out}
        else:
            state = load_data(args.state)
            topology(state['nodes'])
            if args.command == 'score':
                if args.node:
                    coverage = [args.node]
                else:
                    item = next((s for s in state['scenarios'] if s['id'] == args.scenario), None)
                    if item is None:
                        raise ValueError('unknown scenario: ' + args.scenario)
                    coverage = item['instantiates']
                score(state, coverage, args.question_type, json.loads(args.scores),
                      json.loads(args.quotes), args.probe)
                save(args.state, state)
                result = state['history'][-1]
            elif args.command == 'pick':
                if args.top < 1:
                    raise ValueError('--top must be positive')
                result = pick(state, args.top)
            elif args.command == 'bisect':
                result = bisect(state, args.scenario)
            else:
                result = report(state)
        print(dumps(result), end='')
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print('error: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
