# 情景库全量审计

来源：INFERRED（WP-8b，按 `docs/0_ROADMAP.md` 的 D1–D12 与 `references/examiner.md` 审核）。

## 审计口径与结论

- 75/75 重写，0 删除、0 新增；id、概念连边与 source 原样保留。来源是教学/工程改写的依据，不是新增观测数据的实测背书；所有新增数字为题面设定。
- D 编号沿用路线图：D1 是可观测事实不足；一次一问同时归入 D1 的修复范围。每个 asks 是一个独立回合，不可把两条 asks 合并出题。boundary 的取舍依据和代价属于同一个决策，不是追加独立问题。
- required_observables 是本题决策必须处理的证据/硬约束，不是把模型元信息全当评分点；模型元信息只限定可推导范围。symptom_shape 表示主症状：bias=稳定偏差，spike=瞬时/轮间峰谷，silent=无报错但违规或证据失真，crash=执行失败，degradation=质量/容量/延迟退化。
- 自查严格区分“公式可推出”与“给定对照观测”：准确率变化通常不是从模型规模必然推出，不伪造这样的因果关系。诊断主任务可要求区分假设，不要求在观测不足时猜唯一代码行。
- 原题中明确出现参数不足以推出症状、或形态误写的高置信问题共 **3 个**：`scen_gpu_graph_memory`（原显存账不足）、`scen_bn_small_batch`（把稳定偏移写作波动）、`scen_attention_scale`（只有±40极值不能推出近one-hot，补前二差）。另外 `scen_wp1b_video` 标题“两帧”与.2秒×30fps=六帧不符，单列为文字形态错误。其余缺参数的题不追认数值错误，均补齐或缩小主张。
- 重写时显存草稿也触发算术检查：三层16384方阵+Adam+梯度仅12GiB，仍不够解释16GiB OOM；写入前改四层，详见对应行。此反例作为之后审题的检查规则：常驻总量加峰值临时张量必须跨过容量线，不能见大模型就断言OOM。
- 未完成外部廉价模型双型号盲试答；本表为人工/算术审计，不是 examiner 的试答 PASS 记录。仍未充分验证的项目与风险见末节，不宣称题库已获得真实会话校准。

缺陷命中（每题可多计）：D1: 5、D2: 21、D5: 71、D7: 32、D10: 75、D11: 75、D12: 6。D3/D4/D6/D8/D9属引擎/会话工作流，不在本次数据重写中声称修复。

## 逐条审计

| id | 旧缺陷类型 | 改了什么 | 自洽性自查（代入参数） |
|---|---|---|---|
| `scen_rank_deficient` | D1,D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：24GiB仅余0.5GiB；秩8与256误差均12%；前8奇异值能量99%。 | 单个4096方阵LoRA的参数为8192r，r=8为65536、r=256为2097152；能量集中不等于任务已解。 |
| `scen_pca_budget` | D2,D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：10000×2048 float32；64维；512MiB；同文余弦0.05。 | 原矩阵78.125MiB、2048方阵协方差16MiB、输出2.44MiB；须为工作区留余量，同文错位不是单纯截断必然结果。 |
| `scen_robust_constant` | D1,D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：1%贡献40%loss；符号串与罕见代码并存；两天；不能重爬。 | 高loss组单样本平均损失为其余组的(0.4/0.01)/(0.6/0.99)=66倍；不能据此推导全为坏数据。 |
| `scen_xor_mlp` | D2,D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：插值误差低于1e-5；40%到30%；两组2000步。 | 仿射复合满足f(αx+(1−α)y)=αf(x)+(1−α)f(y)；10点退化为对照观测，不由2000步必然推出。 |
| `scen_gradient_graph` | D2,D5,D7,D12,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：X全1为16×32；两个相同分支；差分32而反向16；float64。 | 每支对W导数16，两支总和32；16/32=50%，形态是固定低估而非抖动。 |
| `scen_batch_timing` | D1,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：10000到20000；B=100；10epoch衰减；1000步对照。 | 10000/100=100步/epoch，复制后200步/epoch；首次衰减从1000步变为2000步。 |
| `scen_adam_sparse` | D5,D7,D12,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：首步0.003162；β1=.9与β2=.999；成熟步.001；罕见词间隔1000。 | 未校正首步m=.1、v=.001，更新=.001×.1/√.001=.003162；校正后为.001。 |
| `scen_bn_small_batch` | D5,D7,D12,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：每卡B=2；剩余1GiB；train .8/eval .4；运行均值0与当前均值2。 | 相同方差下eval标准化均值约2，按当前批标准化约0；可支持稳定偏移，不支持把小批直接写成周期尖峰。 |
| `scen_house_leak` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：5改写；80/20划分；近重复67/100；不能重标。 | 给定一条在验证，其余4条至少一条入训练概率1−.2^4=.9984；67%为可检出的下界，非由概率保证的准确率差。 |
| `scen_shift_monitor` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：拒答5%到25%；方言30%；固定探针一致；原文不留存不出网。 | 若非方言仍5%，方言需(25%−.7×5%)/.3=71.7%拒答才解释总体；须测该分层而非断言退化原因。 |
| `scen_rare_fraud` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：50/10000攻击；每日审核100；A为40/100；B为48/500。 | 全放行9950/10000=.995，攻击召回0；A精度.4召回.8，B精度.096召回.96但超容量5倍。 |
| `scen_calibrate` | D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：0.9组700/1000；独立2000校准；类别排序不得改。 | 该箱经验正确率.7，过度自信.2；正温度缩放不改argmax，85%准确率不必改变。 |
| `scen_perplexity_tokens` | D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：10000 ASCII字节；A5000/PPL18；B8000/PPL12；不可重跑。 | A每字节NLL=5000ln18/10000=1.445，B=.8ln12=1.988；按共同单位A更低而非B。 |
| `scen_batch_online` | D1,D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：输入320/32000；B≤32；P99=8s；等待prefill6s；SLO2s。 | 等待6s已大于2s，光提高decode速度无法达标；长度比100，8−6=2s其余路径也需留余量。 |
| `scen_distill_edge` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：离线手机4GiB；50MiB；80ms；20M float32；100ms。 | 20M×4=80MB约76.3MiB超50；int8约19.1MiB但100ms不能据权重大小推断能降至80ms。 |
| `scen_beam_translation` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：64token；200ms；beam8 260ms；短-8完整-12。 | 原总logprob偏好−8>−12；按长度均分为−.8与−.3，排序可翻转；260>200必须降成本。 |
| `scen_lenet_shapes` | D2,D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：224；药片4像素；五次stride2；2GiB；不可4K。 | 224→112→56→28→14→7，药片宽映射4/32=.125格；可能丢细节而非必然由stride就消失。 |
| `scen_crowded_nms` | D2,D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：100图300框；100对IoU>.9；40遮挡；标签不全；复核20图。 | 300/100=3框/图；高IoU对不能独立证明重复物体，漏标会使真检出被计假阳性，先按遮挡分层核对。 |
| `scen_segmentation_crop` | D2,D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：框坐标；裁剪窗口；20%方位指代；不能整批重标。 | 裁剪后500×500，正确框[100,100,300,300]；原框x≥600越界，原图右侧在裁剪后未必仍属右侧。 |
| `scen_vit_resolution` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：224→448；patch16；B8 bf16；无checkpoint/flash；16GiB；分数0.2GiB。 | 含CLS为197→785 token，分数倍率(785/197)^2=15.88；分数约3.18GiB，其他激活近4倍时4.8×4+3.18≈22.4GiB可超16。 |
| `scen_rnn_detach` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：每段4MiB；100段396MiB；B32/T32/H1024；随机重排；余128MiB。 | 32×32×1024×4=4MiB每状态序列，99×4=396MiB；未声称仅100段必使整卡OOM。 |
| `scen_attention_scale` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：Q2×8×128×64；KV长256；std8；首两差16；padding非零。 | 点积方差64、标准差8，除√64=8后约1；exp(16)≈8.9e6支持饱和，但不声称±40单独足够。 |
| `scen_causal_mask` | D2,D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：loss .02；后缀扰动改变前缀logits；对照不变；现有缓存。 | exp(−.02)=.9802是训练目标平均几何概率，不能推出续写；后缀影响前缀违反因果不变性，标签错位仍须独立检查。 |
| `scen_word_vectors` | D1,D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：2000药名10子词；每请求20；1.4s/1s；词表冻结；静态表无条目。 | 20×10=200token是普通切分20×2=40的5倍；子词可表示不等于懂药名，负采样不能直接缩短现有LLM输入。 |
| `scen_bert_mask` | D2,D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：上限512；工单800；金额在700；续写100；无预训练预算。 | 700>512必被前截丢弃，800+100=900超原窗口；双向掩码目标不直接提供标准左到右续写分布。 |
| `scen_rag_freshness` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：v2按ID可读；top5全v1；强制v2答对；2s；不重训。 | 强制v2消除该样本错误而常规0/5新版，将检索路径与生成使用证据区分；2秒是需实测的上限而非保证。 |
| `scen_grid_value` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：30动作；γ.8；独立失败10%；失败终止；无逐步标签。 | 若第30动作得奖，γ^29=.00155；成功概率.9^30=.0424，开头期望约6.56e−5，奖励塑形须防目标改变。 |
| `scen_grid_q` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：5000轨迹3/6动作；付款无回报记录；真实不可探索；沙箱500条。 | 动作种类覆盖3/6=.5并不等于状态动作覆盖50%；未观测付款的高Q无可识别回报依据。 |
| `scen_pg_baseline` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：20轨迹；5%成功；终奖100；γ1；不能扩样。 | 成功数服从Binomial(20,.05)，零成功概率.95^20=.358；平均回报标准差100√(.05×.95/20)=4.87，0到10波动合理但基线不能凭空造成功。 |
| `scen_gpu_graph_memory` | D2,D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：四层16384方阵；B128 fp32；两个Adam状态；16GiB；反向OOM。 | 参数4×16384²=1073741824；fp32权重4GiB、Adam8GiB，前向约12GiB加少量激活；完整梯度再4GiB达到16GiB，额外激活与工作区使反向超16GiB。 |
| `scen_ddp_small_batch` | D2,D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：100M fp32；B32每卡；20ms；10GB/s；不重叠；全局B64。 | 梯度400MB，两卡ring allreduce每卡总传输400MB约40ms；无重叠20+40=60ms，与症状一致。 |
| `scen_run_lineage` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：40次仅1文件；.91；词表无历史；1旧GPU不可重跑全部。 | 40次到1文件是不可逆多对一映射，缺历史无法凭种子还原；.91只能当未绑定历史指标，不能承诺恢复。 |
| `scen_agent_webshop` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：剩3调用9秒；含运费<50；蓝M缺货；仅模拟无付款。 | 10−7=3次、30−21=9秒，最多3×3秒；详情缺货不满足终态，不能把意图报成购买成功。 |
| `scen_logistic_stability` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：logits100/99；线性输出有限；参考loss1.313；FP16；不可全FP32。 | FP16最大65504，exp100远超其范围；稳定loss=log(1+e^−1)+1=1.313，loss scaling不修复前向NaN。 |
| `scen_transfer_resolution` | D2,D5,D7,D12,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：200图/B2；权重相同；BN均值0→1.5；eval .8→.5；一次实验。 | 权重不变不代表状态不变；同方差下标准化值会平移−1.5，支持稳定输出偏移而非尖峰。 |
| `scen_wp1b_decoder` | D2,D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：loss.1；未来扰动改变过去；仅token缓存；不能重取。 | e^−.1=.905为训练目标几何概率，不代表因果生成；未来影响过去可检出可见性泄漏但不唯一锁定某行代码。 |
| `scen_wp1b_position` | D2,D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：8K训练/64K合同；位置迁移95%/40%；两张80GiB；不能丢条款。 | KV=2×32×8×128×65536×2=8GiB；全注意力算术随长度约64倍，容量可行不保证位置外推正确。 |
| `scen_wp1b_moe` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：8192分发/层；热点45%；100MB/层；25Gbps；不丢token。 | 均衡每专家1024，热点.45×8192=3686约3.6倍；100MB/3.125GBps≈32ms每层下界，不能只靠增容量消通信。 |
| `scen_wp1b_pretrain` | D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：300B；重复30%；代码2%；逐字重叠；已有候补。 | 重复约90B、代码约6B，过滤不补齐则只剩210B；重叠使评估独立性失效但不证明每道题靠记忆。 |
| `scen_wp1b_sft` | D2,D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：24GiB增量；2万对话；5亿token；两角色损失非零；隐私不能留存。 | 7B bf16权重约13.04GiB，完整Adam约104GiB级超过24；5亿手册token不等同2万轮回复监督，PEFT不等于脱敏。 |
| `scen_wp1b_preference` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：80%长胜；700→600/1000；匹配组110:90；一天审计。 | 长胜约9600对，解决率降10点；匹配200题新胜45%而非奖励升就成功，长度是待测伪特征非已证唯一原因。 |
| `scen_wp1b_dpo` | D2,D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：5000对20轮；参考logprob变化；胜率+10/合规−15；一次重跑。 | 20×5000=100000对次不增加独立样本；固定序列参考值漂移与固定参考目标矛盾，15点为观测非20轮必然结果。 |
| `scen_wp1b_ppo` | D5,D7,D12,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：同批16更新；第12次KL .02→2；裁剪.1→.9；终态奖励。 | KL上升100倍且裁剪率9倍是实测突增，不由共享骨干单独推断；PPO裁剪不构成严格KL上界。 |
| `scen_wp1b_reasoning` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：8采样；700→200；单位错误仍过；4GPU小时。 | 8到16约需8GPU小时超预算；通过率70%→20%是单位变换观测，不可把原验证器通过率称推理正确率。 |
| `scen_wp1b_constitution` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：20原则不得删；950/1000恶意拒答；300/1000误拒；复核100。 | 恶意漏拒50条，良性误拒300条；95%不是全请求安全率，30%是良性条件误拒率。 |
| `scen_wp1b_injection` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：外部页面指令；未授权付款；卡号不可记录；一个关口。 | 恶意页面1/200=.5%并不代表付款风险.5%；数据到动作越界证据是收款方一致且无用户授权，仍需脱敏轨迹。 |
| `scen_wp1b_permissions` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：累计≤500；20×499；前两笔成功；审批超时；一个校验点。 | 两笔已998>500，总请求9980=上限19.96倍；每笔合规不代表累计合规，超时不能当批准。 |
| `scen_wp1b_guardrail` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：3/100漏报；80/900误报；90/100ms；不出网；一层。 | 漏报率3%、误报8.89%，串行额外仅余10ms；不能拿3/1000当攻击漏报率。 |
| `scen_wp1b_sandbox` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：超时10s；20文件不见；无回收站；共享盘他人数据；临时目录可写。 | 超时不蕴含未执行，20文件缺失是副作用证据；重试可能扩损，300文件数不提供可安全重试保证。 |
| `scen_wp1b_function` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：5元；amount500；回执500元；100/min；20%非ASCII；仅适配层。 | 5元=500分，但实扣500元为100倍；每分钟约20个非ASCII姓名须无损校验，合法整数本身不足。 |
| `scen_wp1b_loop` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：30次上限；重复20次403；禁止登录；剩9次；不可扩窗。 | 已到第21次提议后剩30−21=9；重复403无新证据，压缩不得把禁止登录变成可遗忘事实。 |
| `scen_wp1b_mcp` | D2,D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：3服务器同名pay；2租户串摘要；凭据标识相同；不出网。 | 同名至少2/3造成身份歧义，A拿到B资源已证隔离失效；命名消歧不等于授权隔离，协议兼容不等于可信。 |
| `scen_wp1b_trace` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：4交接；12/100丢号；输入完整；只有终态；版本更换。 | 12/100=12%端到端失败；若独立等风险每交接q，则1−(1−q)^4=.12得q≈3.15%，不能凭总率断言具体哪次。 |
| `scen_wp1b_wiki` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：10万页小时更新；500token块；原文403/摘要可读；2s；一层失效。 | 小时刷新存在最长近3600s窗口，2s回答SLO不等于2s撤权；原文403而摘要可读区分源访问与派生缓存。 |
| `scen_wp1b_hybrid` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：2M×768fp32；16GiB；E-104稠密未召回；65/80ms。 | 原向量约5.72GiB，索引另算；串行仅余15ms，重排20个没有目标的候选不能救回该工单。 |
| `scen_wp1b_search` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：离线；去年参数；3个月前快照；今天价格；5s。 | 至少3个月时间差不能被5秒推理弥补；蒸馏不产生今日证据，无法确定实时价格必须缩小主张。 |
| `scen_wp1b_vlm` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：1024→336；12像素药名；裁剪90/100整图40/100；500标注；禁云。 | 缩小后字高12×336/1024≈3.94像素；裁剪对照支持分辨率瓶颈但不是语言流畅度证据。 |
| `scen_wp1b_clip` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：50类80/100；接口无框；30带框；本地禁云。 | 80/100分类正确与框IoU没有可计算映射；30张区域监督可作起点但不能承诺相同80%定位率。 |
| `scen_wp1b_video` | D5,D7,D12,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：600s×30fps；16帧；.2s事件；8GiB；6MiB/帧；1/100。 | 全片18000帧约105.5GiB；均匀间隔约37.5s，随机相位覆盖约16×.2/600=.53%，1/100合理；.2s是6帧非两帧。 |
| `scen_wp1b_robot` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：20Hz；延迟150ms；滑移100ms；95/100对60/100；禁止伤害。 | 周期1/20=50ms，150ms跨3周期且超过100ms滑移窗；成功率差35点是观测，不由频率单独推出。 |
| `scen_wp1b_drive` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：误差.3m；5/100碰撞；雷达20%缺失；对照1/100；仅封闭100次。 | 碰撞率5%对1%样本小，标准误分别约2.18与.995点；平均.3m不能推导零碰撞，不把相关性写成已证根因。 |
| `scen_wp1b_diffusion` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：12GiB峰8；10步上限；CFG5→20；255截顶；20/70布局。 | CFG条件差项由5倍变20倍即4倍；步数1/5不保证质量不变，两因素同时改不能唯一归因。 |
| `scen_wp1b_dit` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：VAE8/patch2；512→1024；8→26GiB；B1bf16无checkpoint/flash；小字重建丢失。 | latent token=(512/8/2)^2=1024，1024图为4096，分数16倍；固定6GiB+线性1×4+注意力1×16=26GiB；512时6+1+1=8GiB，SGD无Adam额外状态，非Flash分数规模自洽。 |
| `scen_wp1b_flash` | D2,D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：A100；B1/8192/bf16；60→30GiB；差1e-3/容差2e-3；padding。 | bf16相对间隔约.0078，1e−3绝对差可能为舍入且在2e−3容差内；显存减半不意味着N²计算变线性。 |
| `scen_wp1b_kv` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：80GiB权重14；100×32000；32层8KV/128/bf16；不增卡保长度。 | 每会话2×32×8×128×32000×2=3.906GiB，100个390.6GiB>66GiB可用；理想上限16长会话还未留工作区。 |
| `scen_wp1b_prefill` | D2,D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：90%共享8K公开前缀；2s中1.6s；两租户；一份公开缓存。 | 理想命中可省1.6s，平均节省上界.9×1.6=1.44s，不包括查找成本；共享边界不能越过公开前缀。 |
| `scen_wp1b_quant` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：8GiB；7B4bit；B1/512；财务−20均分−1；无财务校准；禁上传。 | 7B×.5字节约3.26GiB不含scale与KV，bf16权重13GiB不能直接单卡替代；财务若占5%，−20可贡献均分−1。 |
| `scen_wp1b_eval` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：100+50任务失败30；模拟无付款；生产审批；邮箱不出网。 | 端到端成功120/150=80%，不能推出网页或桌面各自80%；无权限模拟未覆盖真实付款风险。 |
| `scen_wp1b_budget` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：4草稿/40ms；验证80ms；接受20%；1000ms；8链2异1800ms。 | 简化独立接受模型，期望提交1+α+α²+α³+α⁴，α=.8为3.36、.2为1.2496；120/1.2496≈96ms/token反慢于80ms；多链1800>1000。 |
| `scen_wp1b_resume` | D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：上限30/保存28；第29付款；处理中；不可回滚可查询；不许重复。 | 保存28意味着账面余2，但已发29副作用不能回退；处理中既非失败也非完成，状态恢复不保证恰好一次。 |
| `scen_wp1b_contexts` | D2,D5,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：100凭据；提示泄露1个；8K；A见B工具但服务拒绝；一个导出接口。 | 1/100暴露已足以泄密，8K压缩不是保密机制；隐藏工具名不能替代已起作用的服务端授权。 |
| `scen_wp1b_tool_guard` | D2,D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：100ms扣500；300ms才阻断；无授权；不可撤销；一个阻塞关口。 | 300−100=200ms竞态窗口，输出阻断晚于不可逆扣款；必须在100ms副作用前完成授权而非事后补偿。 |
| `scen_wp1b_kvquant` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：B8/32K；KV32→16GiB；总52→36；40GiB；尾召回−15；合同不可缩。 | KV减半省16/52=30.8%与症状一致；FP16 B4 KV16GiB，加14+6=36GiB可容纳但吞吐有代价。 |
| `scen_wp1b_dispatch` | D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：4机8GPU；50Gbps；250MB/轮；60→100ms；专家均衡。 | 250MB/6.25GBps=40ms，与60+40=100ms相符；固定每轮token吞吐比60/100=.6即降40%，负载已均衡不能再归因热点。 |
| `scen_wp1b_iteration` | D2,D5,D7,D10,D11 | 去根因预置、补足观测并改为单决策/受限取舍；承重证据：3轮；196→160/200；两角色有梯度；一次重跑；历史快照。 | 196/200=.98、160/200=.80，差18点远大于单组约1至2.8点标准误；两角色梯度不是后续退化唯一原因，需阶段对照。 |

## 删除或建议删除

无。75个id全部保留；有歧义的根因断言改为实验/修复任务，不通过删题隐藏问题。

## 验证证据

本次共享工作树验证（WP-8a 的引擎更新同时存在；不声称是在旧引擎上的独立回归）：

```text
$ python3 engine/state.py init --graph data/concepts.yaml --scenarios data/scenarios.yaml --out /tmp/audit/state.json
{
  "nodes": 282,
  "out": "/tmp/audit/state.json",
  "scenarios": 75
}
$ python3 engine/state.py pick --state /tmp/audit/state.json --top 5
scen_beam_translation | application | S=autoregressive_decoding,beam_search,language_model
scen_beam_translation | boundary | S=autoregressive_decoding,beam_search,language_model
scen_wp1b_dit | boundary | S=dit,latent_diffusion,transformer,vae
scen_wp1b_dit | diagnosis | S=dit,latent_diffusion,transformer,vae
scen_wp1b_iteration | boundary | S=direct_preference_optimization,iterative_posttraining,rejection_sampling,sft_loss_mask
$ python3 engine/test_state.py
test_pick_exclude (__main__.RealDataTests.test_pick_exclude) ... ok
test_pick_on_shipped_data (__main__.RealDataTests.test_pick_on_shipped_data) ... ok
test_bisect_partitions_original (__main__.StateTests.test_bisect_partitions_original) ... ok
test_boundary_gate (__main__.StateTests.test_boundary_gate) ... ok
test_boundary_zero_quote_exception_and_other_zero_rejection (__main__.StateTests.test_boundary_zero_quote_exception_and_other_zero_rejection) ... warning: boundary=0 without quotation
ok
test_correct_fusion_raises_every_node (__main__.StateTests.test_correct_fusion_raises_every_node) ... ok
test_cycle_rejected (__main__.StateTests.test_cycle_rejected) ... ok
test_determinism_byte_for_byte_all_commands (__main__.StateTests.test_determinism_byte_for_byte_all_commands) ... ok
test_determinism_with_new_flags (__main__.StateTests.test_determinism_with_new_flags) ... ok
test_difficulty_offsets_and_clamp (__main__.StateTests.test_difficulty_offsets_and_clamp) ... ok
test_evidence_and_single_hop_propagation (__main__.StateTests.test_evidence_and_single_hop_propagation) ... ok
test_failed_fusion_entropy_almost_unchanged (__main__.StateTests.test_failed_fusion_entropy_almost_unchanged) ... ok
test_gate_does_not_permanently_prevent_learning (__main__.StateTests.test_gate_does_not_permanently_prevent_learning) ... ok
test_invalid_scores (__main__.StateTests.test_invalid_scores) ... ok
test_mechanism_gate_overrides_even_strong_prior (__main__.StateTests.test_mechanism_gate_overrides_even_strong_prior) ... ok
test_missing_quote_rejected_cli_no_write (__main__.StateTests.test_missing_quote_rejected_cli_no_write) ... ok
test_no_scenarios_fallback (__main__.StateTests.test_no_scenarios_fallback) ... ok
test_nodes_must_be_subset (__main__.StateTests.test_nodes_must_be_subset) ... ok
test_nodes_subset_skips_others (__main__.StateTests.test_nodes_subset_skips_others) ... ok
test_noisy_and_expectation_and_cost (__main__.StateTests.test_noisy_and_expectation_and_cost) ... ok
test_only_dimension_does_not_double_count (__main__.StateTests.test_only_dimension_does_not_double_count) ... ok
test_only_marginalizes_unobserved_scores (__main__.StateTests.test_only_marginalizes_unobserved_scores) ... ok
test_prompted_negative_stronger (__main__.StateTests.test_prompted_negative_stronger) ... ok
test_report_and_topology (__main__.StateTests.test_report_and_topology) ... ok
test_required_observables_passthrough (__main__.StateTests.test_required_observables_passthrough) ... ok
test_rows_monotone (__main__.StateTests.test_rows_monotone) ... ok
test_tested_low_entropy_nodes_not_selected (__main__.StateTests.test_tested_low_entropy_nodes_not_selected) ... ok
test_yaml_real_format_and_folded_source (__main__.StateTests.test_yaml_real_format_and_folded_source) ... ok

----------------------------------------------------------------------
Ran 28 tests in 1.427s

OK
```

附加结构断言：75/75 id与顺序、source对象、instantiates连边对比HEAD不变；每项2–5个有效概念、至少3个expected_elements，新增字段非空且形态在五值枚举内。审计表75行逐一对齐场景id。以上结构断言与下列数值反例检查均通过。

数值检查规则（在写入后运行）：旧三层8192即便按float32 Adam的16字节/参数计仅3GiB，不能解释16GiB OOM；新四层16384训练状态恰16GiB，临时张量使其越界；视频.2×30=6帧；256候选最大次大差16时最大softmax下界>.999；100个长会话KV=390.625GiB>66GiB。


## 残余风险 / 尚未达到的质量门

- 没有独立双型号盲试答，因此75题均仍待会话前试答；不能将本次人工审计冒充试答通过。
- `scen_wp1b_dit` 已明确SGD与峰值分解，8/26GiB可按固定/线性/二次项验算；但具体内核工作区未逐字节实测，不能作为硬件容量承诺。
- `scen_wp1b_dispatch` 的250MB是流量观测，不是仅由top2必然算出；网络拓扑与重叠已由60→100ms时线限定，迁移到实际硬件仍需trace验证。
- 本轮未联网复核每个source URL正文；严格保留既有来源，不声称这些场景是论文中的原题/实测。expected_elements仍是私有评分方向，不能原样泄给被诊断者。
