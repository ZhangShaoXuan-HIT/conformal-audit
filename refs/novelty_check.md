# 阶段 3A：新颖性检查报告

日期：2026-11-06
数据库：OpenAlex、arXiv、Crossref。Semantic Scholar 返回 429，未使用。
检索方式：标题与摘要检索，不做全文检索。

## 检索规模

| 轮次 | 查询组 | 原始记录 | 去重后 |
|---|---|---|---|
| 第一轮 | 6 组：empty sets、post-processing、ACI implementation、pitfalls、coverage inflation、benchmark | 186 | 173 |
| 第二轮 | 5 组：empty set、post-processing、implementation、audit、coverage inflation | 约 220 | 194 |

Crossref 在前两组查询上出现 SSL 握手超时，记录为 0。两轮结果没有完全合并去重，但重叠很少。

## 最接近的十二项工作

| # | 工作 | 年份 / 出处 | 它做了什么 | 与我们的差别 | 威胁 |
|---|---|---|---|---|---|
| 1 | Mehrtens, Bucher & Brinker, Pitfalls of Conformal Predictions for Medical Image Classification | 2025, arXiv 2506.18162；DOI 10.1007/978-3-031-44336-7_20 | 医学影像中的坑：分布漂移、用共形选预测、类子集不可靠、类别数少时价值有限 | 没有涉及空集、非空后处理、ACI 更新式 | 中（pitfalls 这个词被占） |
| 2 | Aguru, What Split Conformal Prediction Guarantees, and What It Does Not | 2026, Zenodo，DOI 10.5281/zenodo.23582987 | 二分类的精确覆盖律；证明阈值大于等于 1/2 时集合不空、小于 1/2 时不含两个标签；类条件失败与 Mondrian 修复 | 只做二分类；没有测量后处理；没有 ACI | 高（阈值几何的事实已被证明） |
| 3 | Gauthier, Bach & Jordan, Adaptive Coverage Policies in Conformal Prediction | 2025, arXiv 2510.04318 | 指出覆盖水平过低会产生空集；提出数据依赖的自适应覆盖策略 | 把空集当作设计选择，不审计强制非空造成的报告偏差 | 低到中（空集现象已知） |
| 4 | Al Bataineh, Certified Label-Free Drift Alarms From Empty Conformal Prediction Sets | 2026, IEEE Sensors Letters，DOI 10.1109/lsens.2026.3748815 | 把空集计数当作漂移报警信号，给出 beta-binomial 误报界 | 用途相反：他们把空集当信号，我们测量把空集填掉之后的覆盖率 | 低 |
| 5 | Boman, Benchmarking non-conformity score functions in conformal prediction | 2026, arXiv 2605.24983 | 系统比较非一致性分数对集合大小的影响，含类不平衡 | 比较分数，不比较填空前后的报告差异 | 低到中（审计 B 的相邻工作） |
| 6 | Susmann, Chambaz & Josse, AdaptiveConformal: An R Package for Adaptive Conformal Inference | 2023, arXiv 2312.00448 | 实现五种 ACI 算法，附模拟与流感案例 | 是实现，不是实现审计；但它决定这个 bug 有多普遍 | 中（3B 必须查它的更新式） |
| 7 | Zhou, Fathony, Nguyen & Sesia, Audited Conformal Prediction for Classification under Unknown Distribution Shift | 2026, arXiv 2606.14909 | 提出 ACP 方法，用目标域小样本训练审计模型 | 是方法，不是实现审计 | 低 |
| 8 | Opoku & Banahene, Two ways an AKI prediction model can look better than it is | 2026, Research Square，DOI 10.21203/rs.3.rs-10463539/v2 | 特征泄漏与只报边际覆盖会让模型看起来更好 | 机制不同：他们讲研究设计，我们讲后处理与更新式 | 低到中（看起来更好的框架相邻） |
| 9 | Zwart, Conformal Tradeoffs: Operational Profiles Beyond Coverage | 2026, arXiv 2602.18045 | 覆盖之外的部署指标：承诺频率、弃答、决定性错误 | 决策论视角，不做实现审计 | 低（可作为讨论节引用） |
| 10 | Zhan, Phan & Wu, A Review of Conformal Prediction-Based Post-Processing Methods for Calibrating Prediction Intervals | 2026, IEEE I&CPS Asia，DOI 10.1109/icpsasia70813.2026.11691987 | 电力预测区间的后处理综述 | post-processing 指区间校准，不是集合填充 | 低（但标题撞词，正文要避免单用 post-processing） |
| 11 | Ng, When the Promise Is Broken: Auditing Conformal Predictions for Financial Document Classification Under Domain Change | 2026, SSRN，DOI 10.2139/ssrn.7496318 | 域变化下的共形审计 | 审计漂移，不审计实现 | 低到中（audit 这个词也被用了） |
| 12 | Indri, Tamara & Spathoulas, Contract Cards for Auditable Private Conformal Prediction | 2026, Zenodo，DOI 10.5281/zenodo.23456635 | 给隐私共形预测做可审计的记录卡 | 记录配置，不测量实现偏差 | 低 |

## 判定

没有找到直接做非空后处理审计或 ACI 更新式审计的工作。这两块仍然是空的。

但周边已经被占了三块：

1. 阈值大于等于 1/2 时集合只能是单元素或空集，Aguru 2026 已经在二分类上证明。多分类是直接推论（概率和为 1，至多一个类超过 0.5）。所以审计 A 的这句话不能写成我们发现，必须写成这是已知事实的多分类推论，我们测量它在真实实现中的后果。
2. 空集是一个活跃话题。Gauthier 2025 把它当作覆盖水平过低的结果，Al Bataineh 2026 把它当作漂移信号。没有人测量把空集填成 argmax 之后，报告的覆盖率会怎样。
3. pitfalls 这个词被 Mehrtens 2025 占了，而且他们讲的是另一组坑。标题和摘要里再用 pitfalls，会被误认为重复工作。

## 对论文框架的影响

1. 标题与摘要：不要用 pitfalls。用 audit、accounting、what the numbers actually measure 这一类词。
2. 4.1 节：引用 Aguru 2026，明确说阈值几何是已知的；我们的贡献是多分类的经验后果，以及校准阈值就是分裂共形这一等价在真实流程里的含义。
3. 4.2 节：这是真正的空档。引用 Gauthier 2025 与 Al Bataineh 2026，说明空集本身有人研究，但强制非空的报告偏差没有人系统测量。
4. 4.3 节：引用 Susmann 2023。更新式本身不是新发现，审计实现才是。
5. 相关工作：至少要有 Mehrtens 2025、Aguru 2026、Gauthier 2025、Al Bataineh 2026、Boman 2026、Susmann 2023 六条，并逐条说明差别。

## 判定门：通过，但要把主张收窄

结论是可以做 3B 库审计，但论文的主张要从 common traps 改成在本文审计的实现范围内，这三种选择会让报告覆盖率偏离实际覆盖率。

如果库审计发现主流库都规避了这些坑，故事改成文献里的坑与库里的现状之间的差距，仍然是有效结果，只是不再是普遍失效。

3B 的优先目标：

| 库 | 语言 | 查什么 |
|---|---|---|
| AdaptiveConformal | R | ACI 更新式用固定 alpha 还是 alpha_t |
| MAPIE | Python | 空集是否被强制填充；是否暴露校准阈值接口 |
| TorchCP | Python | APS/RAPS 的空集行为 |
| crepes | Python | 分类接口与空集处理 |
| puncc | Python | APS/RAPS 的默认后处理 |
| coverforest | Python | 随机森林共形的空集行为 |

## 局限

- Crossref 两组查询 SSL 超时，Semantic Scholar 429，实际覆盖不完整。
- 只做标题摘要检索，没有全文检索；可能漏掉在正文里讨论空集但不进摘要的工作。
- 没有中文文献。
- 这不是系统综述，只是决定要不要做库审计的判定门。正式的 PRISMA 式检索放在 3C。

## 下一步

1. 把这份报告里的六条相关工作写进 paper/main.md 的定位段。
2. 修改 4.1、4.2、4.3 的措辞，避免我们发现和 pitfalls。
3. 开始 3B：先装 MAPIE、TorchCP、crepes，写 audit_libraries.py，第一个查 AdaptiveConformal 的更新式。
