#!/usr/bin/env python3
"""Deterministic artifact checks, not a semantic scorer."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from calibration.fixtures import GOOD, DELETE_B, PRIMARY
ROOT=Path(__file__).resolve().parent
class CalibrationTests(unittest.TestCase):
 def test_mechanical_deletions_only(self):
  for key,parts in GOOD.items():
   folder=ROOT/'answers'/('scen_wp1b_'+key)
   self.assertEqual((folder/'a.md').read_text(),'\n\n'.join(parts)+'\n')
   expected='\n\n'.join(parts[:2])+'\n'
   for deletion in DELETE_B[key]: expected=expected.replace(deletion,'',1)
   self.assertEqual((folder/'b.md').read_text(),expected)
 def test_evidence_quotes_and_no_fabricated_missing_scores(self):
  for key in GOOD:
   sid='scen_wp1b_'+key
   for v in 'abcd':
    p=ROOT/'sessions'/f'{sid}-{v}'
    state=json.loads((p/'state.json').read_text())
    judgment=json.loads((p/'judgment.json').read_text())
    answer=(ROOT/'answers'/sid/f'{v}.md').read_text()
    for q in judgment['quotes'].values():
     if q is not None:self.assertIn(q,answer)
    if v in 'ac':
     self.assertEqual(len(state['history']),1)
     self.assertEqual(state['history'][0]['nodes'],[PRIMARY[key]])
     self.assertEqual(judgment['framework_A'],judgment['framework_B'])
    else:
     self.assertEqual(state['history'],[])
     self.assertTrue(all(n['evidence']['count']==0 for n in state['nodes'].values()))
 def test_partial_order_and_full_chain_not_claimed(self):
  rows=json.loads((ROOT/'results.json').read_text())
  self.assertEqual(len(rows),40)
  for key in GOOD:
   a,b,c,d=[r for r in rows if r['scenario']=='scen_wp1b_'+key]
   self.assertGreater(a['p_mastery'],c['p_mastery'])
   self.assertGreater(a['covered_mean_p_mastery'],c['covered_mean_p_mastery'])
   self.assertLess(c['p_mastery'],c['initial_prior'])
   self.assertIsNone(b['p_mastery']);self.assertIsNone(d['p_mastery'])
 def test_selection_is_from_fresh_cli(self):
  selected=json.loads((ROOT/'selection/selected.json').read_text())
  picks=json.loads((ROOT/'selection/pick.json').read_text())
  state=json.loads((ROOT/'selection/state.json').read_text())
  self.assertEqual(state['history'],[])
  self.assertEqual(len(selected),10)
  for s in selected:
   self.assertTrue(any(all(s[k]==p[k] for k in ('scenario','S','question_type')) for p in picks))
   self.assertEqual(s['importance'],'high')
   self.assertTrue(set(s['observed_nodes'])<=set(s['S']))
if __name__=='__main__': unittest.main(verbosity=2)
