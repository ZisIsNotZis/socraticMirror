#!/usr/bin/env python3
"""Replay manually labelled fixtures through the real CLI; never grades text."""
from pathlib import Path
import json, subprocess, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine.state import DIMS, load_data
from calibration.construct import WRONG
from calibration.fixtures import GOOD, PRIMARY, A_SCORES, C_SCORES, DELETE_B
ROOT=Path(__file__).resolve().parent
BOUNDARY={
'preference':'标签偏向长度时，奖励上升不能推出解决率提升，应以独立任务盲测阻止退化上线。',
'dpo':'离线偏好缺少的新分布没有保障，JSON合规继续下降就回滚旧快照。',
'function':'JSON合法也不能替代金额与授权验证，回执异常时停止重试扣款并对账。',
'loop':'403不产生登录权限，找不到授权来源就终止而不是绕过禁止登录。',
'vlm':'原图无法辨认的药名不能凭流畅措辞猜测，无法核实就人工复核。',
'clip':'类别相似分高不证明细小瑕疵能定位，留出定位召回不足则人工复核。',
'flash':'输出当前过容差不保证梯度和其他mask正确，回归失败则保留旧内核。',
'kv':'分页不能消除每会话存储成本，峰值容量不够就排队而不能截短会话。',
'pretrain':'过强去重会误删合理模板，按域审查误删并调低阈值。',
'sft':'助理标签含号码时仅屏蔽用户仍会泄露，应修标签并在泄露时暂停发布。'}
def cli(*args):
 cmd=['python3','engine/state.py',*map(str,args)]
 p=subprocess.run(cmd,text=True,capture_output=True)
 if p.returncode: raise RuntimeError(f'{cmd}\n{p.stdout}\n{p.stderr}')
 return json.loads(p.stdout)
def mean(report, nodes):
 return sum(report['nodes'][n]['p_mastery'] for n in nodes)/len(nodes)
def main():
 initial=ROOT/'selection/state.json'
 cli('init','--graph','data/concepts.yaml','--scenarios','data/scenarios.yaml','--out',initial)
 picks=cli('pick','--state',initial,'--top','1000')
 (ROOT/'selection/pick.json').write_text(json.dumps(picks,ensure_ascii=False,indent=2)+'\n')
 concepts={n['id']:n for n in load_data('data/concepts.yaml')}
 selected=[]; results=[]
 baseline=cli('report-data','--state',initial)
 for key,parts in GOOD.items():
  sid='scen_wp1b_'+key
  rank,pick=next((i+1,p) for i,p in enumerate(picks) if p['scenario']==sid)
  node=PRIMARY[key]; assert node in pick['S']
  selected.append(dict(pick,rank=rank,observed_nodes=[node],importance=concepts[node]['importance']))
  folder=ROOT/'answers'/sid;folder.mkdir(parents=True,exist_ok=True)
  b_text='\n\n'.join(parts[:2])+'\n'
  for deletion in DELETE_B[key]:
   assert deletion in b_text
   b_text=b_text.replace(deletion,'',1)
  texts={'a':'\n\n'.join(parts)+'\n','b':b_text,'c':WRONG[key]+'\n\n'+BOUNDARY[key]+'\n','d':'我不知道。\n'}
  for variant,text in texts.items():
   (folder/f'{variant}.md').write_text(text)
   session=ROOT/'sessions'/f'{sid}-{variant}'; session.mkdir(parents=True,exist_ok=True)
   state=session/'state.json'
   cli('init','--graph','data/concepts.yaml','--scenarios','data/scenarios.yaml','--out',state)
   scores=A_SCORES if variant=='a' else C_SCORES.get(key) if variant=='c' else None
   if scores:
    quotes=dict(zip(DIMS,[parts[0],parts[0],parts[1],parts[2]] if variant=='a' else [WRONG[key],WRONG[key],WRONG[key],BOUNDARY[key]]))
    for q in quotes.values(): assert q in text
    labels=dict(zip(DIMS,scores))
    rationale=({'identify':'排除当前关键近邻混淆并关联决策；见第一段。','mechanism':'完整因果链并说明关键条件变化的影响；见第一段。','application':'执行、验证、失败识别与调整均明确；见第二段。','boundary':'失效范围、原因/信号与退路；见第三段。'} if variant=='a' else {'identify':'辨认情景关键对象，但未用正确机制排除近邻混淆。','mechanism':'核心因果明确错误，不是另一种无法排除的可能根因；详见report逐题反证。','application':'按应用锚点判断具体方案，不能由结论方向正确推定方案可行。','boundary':'指出一条当前失效条件、影响与处理，但未完整界定范围。'})
    evidence={'observed_nodes':[node],'scores':labels,'framework_A':labels,'framework_B':labels,'low_confidence':False,'quotes':quotes,'anchor_reasons':rationale,'assertion_correct':True,'mechanism_correct':variant=='a','probe':'direct'}
    (session/'judgment.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    accepted=cli('score','--state',state,'--scenario',sid,'--nodes',node,'--question-type',pick['question_type'],'--scores',json.dumps(labels),'--quotes',json.dumps(quotes,ensure_ascii=False),'--probe','direct')
    (session/'accepted.json').write_text(json.dumps(accepted,ensure_ascii=False,indent=2)+'\n')
   else:
    evidence={'observed_nodes':[] if variant=='d' else [node],'scores':dict(zip(DIMS,[3,3,2,'unverified'] if variant=='b' else ['unverified']*4)),'submitted':False,'reason':'边界整段删除，无反证，不得以0补空；score强制四整数。' if variant=='b' else '不知道不是四维错误证据；保留先验但不作已测估计。','quotes':dict(zip(DIMS,[b_text.split('\n\n')[0],b_text.split('\n\n')[0],b_text.split('\n\n')[1].strip(),None])) if variant=='b' else {d:None for d in DIMS}}
    (session/'judgment.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
   report=cli('report-data','--state',state)
   (session/'report-data.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
   results.append({'scenario':sid,'variant':variant,'scores':evidence['scores'],'submitted':bool(scores),'observed_nodes':evidence['observed_nodes'],'p_mastery':mean(report,[node]) if scores else None,'covered_mean_p_mastery':mean(report,pick['S']) if scores else None,'initial_prior':mean(baseline,[node]),'coverage_initial_prior':mean(baseline,pick['S'])})
 (ROOT/'selection/selected.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
 print('Created 40 answers + independent sessions; 20 score submissions; b/d deferred.')
 for key in GOOD:
  rows=[r for r in results if r['scenario']=='scen_wp1b_'+key]
  a,b,c,d=rows
  assert a['p_mastery']>c['p_mastery']
  assert a['covered_mean_p_mastery']>c['covered_mean_p_mastery']
  assert c['p_mastery']<c['initial_prior']
 print('a > c: 10/10; c < initial prior: 10/10; full a>b>c>d: 0/10 evaluable (b/d unverified).')
if __name__=='__main__': main()
