# WP-4 implementation handoff

Source: INFERRED technical choices; requirements are the assigned WP-4 plus `docs/0_STAGING.md` scoring/Max Entropy sections. No docs/data edits, dependencies, randomness, natural-language judgments or generated question wording.

## State and CLI contract

The schemas were created before `state.py`. `schema/state.schema.json` defines persisted v1 and references `scenario.schema.json` (a single scenario record). Additional semantic invariants (normalization, DAG, references) are enforced by initialization/tests, not expressible entirely in JSON Schema. The runtime does not include a general JSON Schema validator.

- `version`: 1.
- `nodes`: concept ID → `{concept, level, evidence}`. `concept` preserves original graph metadata. `level` contains normalized `unknown/aware/operable/deep` probabilities.
- `evidence`: direct scored `count`, counts by `question_types`, `sharpness = 1-exp(-count/3)` (evidence quantity, NOT posterior concentration), and separate `propagated` count. An untested concentrated prior is still untested.
- `scenarios`: embedded records; no external file dependency after initialization. Empty when omitted.
- `history`: each scored observation's coverage, type, rubric, verbatim input quotes, probe stage, total, table row, and before/after distributions. No fabricated session calibration number: report exports these raw records and marks semantic hedging unavailable.

Run `python3 engine/state.py --help`. `score` updates the specified state atomically and returns the observation. `pick`, `bisect`, and `report-data` are read-only JSON outputs. `init` returns node/scenario counts and output path. Invalid arguments/scores/quotes exit nonzero without changing state.

Fusion scoring is exposed as `score --scenario <id>` mutually exclusive with the requested `--node <id>`; otherwise all flags match the task. This extra interface makes fusion AC directly runnable. `bisect` returns two disjoint diagnosis candidates with the original scenario ID and explicit half-sized `S`; an examiner must honor `S` rather than reuse all scenario nodes. There is no question wording in the engine.

Input accepts JSON (also valid YAML), or a deliberately limited YAML mapping/sequence/plain-scalar format, including the real graph's indentless lists and wrapped plain scalars. YAML tags, anchors, arbitrary flow syntax, and block scalars are unsupported: use JSON for richer strings. No unsafe evaluation; quoted strings use `ast.literal_eval`. Fixtures are ten concepts/two clusters and three explicitly synthetic scenarios, not product data.

Example:

```sh
python3 engine/state.py init --graph engine/fixtures/concepts.yaml --scenarios engine/fixtures/scenarios.yaml --out /tmp/mirror-state.json
python3 engine/state.py pick --state /tmp/mirror-state.json --top 5
python3 engine/state.py score --state /tmp/mirror-state.json --scenario s0 --question-type application --scores '{"identify":3,"mechanism":3,"application":3,"boundary":3}' --quotes '{"identify":"assertion","mechanism":"causal chain","application":"worked example","boundary":"failure condition"}' --probe direct
python3 engine/state.py bisect --state /tmp/mirror-state.json --scenario s0
python3 engine/state.py report-data --state /tmp/mirror-state.json
```

## Pick objective and inference

Entropy is in bits over all four levels. Importance weights high/medium/low = 3/2/1. Candidate sets are each scenario's untested or entropy≥1.2 nodes, at most five; without scenarios each eligible concept is a singleton. Recognized `asks` values select question types; free-text asks fall back to diagnosis. Types currently share one observation model, so ties are lexicographic rather than claiming calibrated type-specific information.

For node i, level k has ability `a[k]=[.05,.25,.80,.97]`. Let `m_i=Σ p_i[k]a[k]`. Noisy-AND pass probability is `q=.03+.89·Π m_i` (guess .03, slip .08). Positive marginal likelihood is `L_i+[k]=.03+.89·a[k]·Π(j≠i)m_j`. The conservative failed-fusion marginal is `L_i−[k]=1−.08·L_i+[k]`. Normalize `p_i*L_i±` for branch posteriors.

`gain = Σ w_i [H(p_i) − q H(p_i+) − (1−q) H(p_i−)]`.

`cost = 1 + .3 Σ H(p_i) + .15 (|S|−1)`; rank by `gain/cost`, deterministic lexical tiebreak. Cost penalizes cognitive entropy and coverage length, not natural-language length (which the engine never reads).

**Approximation/risk:** tempering negative marginals intentionally departs from an exact joint Bayesian noisy-AND posterior to preserve the specification's weak individual failure evidence. Branch weights still use q, so this is a conservative heuristic expected-entropy objective, not exact mutual information. No global optimum or calibration quality is claimed. Whole-scenario success is shared across S; failure is weak and followed by bisect. This is a node-factorized model, not storage of the exponential joint state.

## Calibration constants and choices

All tunable values live at the top of `state.py`:

- Broad root prior `[.30,.35,.25,.10]`; prerequisite mastery lifts prior by noisy-OR `lift=.18·(1−Π(1−p_mastery(parent)))`, moving `lift*.65` mass from unknown/aware to operable/deep in ratio 3:1. Importance weights affect objective/path, not claim certainty.
- Twelve rows: `L[r,k]=exp((r−5.5)(k−1.5)*.32)`. This exponential family has monotone likelihood ratios. Total 0 and 1 share row 0; `row=clamp(total−1+offset,0,11)` resolves 13 totals versus 12 rows. Offsets explanation 0, application/diagnosis −1, boundary/transfer −2 (last two are inferred analogies).
- A direct low-row observation uses likelihood exponent .35; after_prompt uses full strength. Fusion low-row likelihood uses exponent 1 direct, 3 after_prompt. Fusion high rows (≥7) multiply rubric likelihood by noisy-AND positive likelihood.
- mechanism=0 caps support at **aware**, the stricter staging rule; boundary=0 and mechanism≤2 caps at operable. These are hard support caps, even with a very strong prior. Gates override ambiguity: a zero-mechanism fusion can reduce entropy substantially; the weak-failure guarantee applies to failures without a gate. This is a consequence of simultaneously applying rubric hard gates and weak fusion blame.
- Gate recovery floor .001 before the next direct update prevents Bayesian zero from permanently forbidding later learning. Review found the absorbing-zero failure mode; `test_gate_does_not_permanently_prevent_learning` is its deterministic regression check.
- Strong row≥9 and resulting mastery≥.75 gives immediate parents only a 1.15 mastery likelihood multiplier. Parents already directly scored in S are excluded. Never recursively propagate or count indirect evidence as direct.
- Evidence saturation constant 3, high-entropy threshold 1.2 bits; these are M2 tuning seeds, not measured population parameters.

Report clusters contain node membership, mean mastery and tested count. Learning candidates include all nodes in dependency-respecting Kahn order, importance then low mastery among currently ready nodes; the consumer may filter/limit them without putting a dependent before an included prerequisite.

## Validation evidence

The following output is captured directly while the final validation runs. Tests include all eight requested cases, negative/invalid-score checks, quote exception, offset clamping, monotone table, evidence/one-hop propagation, gate recovery, low-entropy filtering, report topology and independent expected-gain arithmetic. Real-data validation uses a temporary directory, removed after execution; no `sessions/` pollution. Only the real graph is read, never the parallel real scenarios file.

### `python3 engine/test_state.py`

```text
test_bisect_partitions_original (__main__.StateTests.test_bisect_partitions_original) ... ok
test_boundary_gate (__main__.StateTests.test_boundary_gate) ... ok
test_boundary_zero_quote_exception_and_other_zero_rejection (__main__.StateTests.test_boundary_zero_quote_exception_and_other_zero_rejection) ... warning: boundary=0 without quotation
ok
test_correct_fusion_raises_every_node (__main__.StateTests.test_correct_fusion_raises_every_node) ... ok
test_cycle_rejected (__main__.StateTests.test_cycle_rejected) ... ok
test_determinism_byte_for_byte_all_commands (__main__.StateTests.test_determinism_byte_for_byte_all_commands) ... ok
test_difficulty_offsets_and_clamp (__main__.StateTests.test_difficulty_offsets_and_clamp) ... ok
test_evidence_and_single_hop_propagation (__main__.StateTests.test_evidence_and_single_hop_propagation) ... ok
test_failed_fusion_entropy_almost_unchanged (__main__.StateTests.test_failed_fusion_entropy_almost_unchanged) ... ok
test_gate_does_not_permanently_prevent_learning (__main__.StateTests.test_gate_does_not_permanently_prevent_learning) ... ok
test_invalid_scores (__main__.StateTests.test_invalid_scores) ... ok
test_mechanism_gate_overrides_even_strong_prior (__main__.StateTests.test_mechanism_gate_overrides_even_strong_prior) ... ok
test_missing_quote_rejected_cli_no_write (__main__.StateTests.test_missing_quote_rejected_cli_no_write) ... ok
test_no_scenarios_fallback (__main__.StateTests.test_no_scenarios_fallback) ... ok
test_noisy_and_expectation_and_cost (__main__.StateTests.test_noisy_and_expectation_and_cost) ... ok
test_prompted_negative_stronger (__main__.StateTests.test_prompted_negative_stronger) ... ok
test_report_and_topology (__main__.StateTests.test_report_and_topology) ... ok
test_rows_monotone (__main__.StateTests.test_rows_monotone) ... ok
test_tested_low_entropy_nodes_not_selected (__main__.StateTests.test_tested_low_entropy_nodes_not_selected) ... ok
test_yaml_real_format_and_folded_source (__main__.StateTests.test_yaml_real_format_and_folded_source) ... ok

----------------------------------------------------------------------
Ran 20 tests in 0.694s

OK
```

### Real graph init and fallback smoke test

Command: `python3 engine/state.py init --graph data/concepts.yaml --out <temporary-directory>/state.json`, followed by `pick --state <same> --top 5`; both exit 0. Output and programmatically inspected measurements:

```json
{
  "nodes": 155,
  "out": "/tmp/wp4-real-9hju0b0p/state.json",
  "scenarios": 0
}
{
  "nodes": 155,
  "scenarios": 0,
  "topologically_ordered_nodes": 155,
  "all_distributions_normalized": true,
  "state_bytes": 127138,
  "state_sha256": "73a77825adafd4354803a21830f66e83702dfa095a9f493a199916bb71bc53c5",
  "fallback_pick_candidates": 5
}
```
