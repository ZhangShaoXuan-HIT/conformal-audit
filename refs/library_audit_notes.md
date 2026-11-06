# 阶段 3B：库审计笔记

日期：2026-11-06。版本：MAPIE 1.6.0、TorchCP 1.2.1、puncc 0.9.3、crepes 0.9.1、
coverforest 0.0.3、AdaptiveConformal（GitHub main，R 包）。
R 未安装，AdaptiveConformal 只读源码，未运行。

## 方法

- 五个 Python 库下载 wheel/sdist 后解包，读源码，不依赖运行时行为。
- MAPIE 额外跑了一个五分类合成数据实验，五个种子，α=0.10，比较 LAC 与 APS 的三种
  include_last_label 设置。代码在 code/exp_mapie_empty.py，结果在 results/mapie_empty.json。
- 其余库只做源码检查，标注“仅源码”是必要的诚实。

## 发现一：空集策略不统一

| 库 | 空集 | 默认策略 |
|---|---|---|
| MAPIE | LAC 可以；APS 取决于 include_last_label | APS 默认 True，不产生空集，覆盖率偏高 |
| TorchCP | 可以 | 布尔掩码 (scores <= q_hat)，不填充 |
| puncc | 可以 | 返回索引列表，没有类别通过时为空 |
| crepes | 可以 | 布尔掩码 (p_values >= 1-confidence)，不填充 |
| coverforest | 默认可以 | allow_empty_sets=True；False 才避免空集，文档说要少用 |

这不是“库都错了”，而是“库的策略不同”。论文应该把它写成一张策略地图，而不是一篇控诉。

## 发现二：MAPIE 默认 APS 就是后处理陷阱

五种子，α=0.10：

| 设置 | 覆盖率 | 空集率 | 集合大小 |
|---|---|---|---|
| LAC | 0.9016 ± 0.0080 | 0.0000 | 3.151 |
| APS，默认（True） | 0.9457 ± 0.0107 | 0.0000 | 3.676 |
| APS，False | 0.8284 ± 0.0150 | 0.0000 | 2.684 |
| APS，randomized | 0.8998 ± 0.0105 | 0.0004 | 3.232 |

默认设置比目标高 4.6 个百分点，空集率为 0；随机化设置正好落在 0.90。

MAPIE 的源码文档在 aps.py 第 355 到 358 行明确写了：True 或 False 可能让覆盖率高于
1−α，因为与 randomized 不同，它们不产生空集。也就是说，库知道这件事，但没有给出
幅度，也没有说默认值与精确规则差多少。

这是审计 B 最强的外部证据：陷阱不是假想，是一个主流库的默认行为。

## 发现三：α_t 的 bug 不在这些库里

| 库 | ACI 更新 | 证据 |
|---|---|---|
| MAPIE | alpha_t + gamma * (alpha_0 - err)，固定 alpha_0 | regression/time_series_regression.py:329 |
| TorchCP | alpha_t + gamma * (alpha - err)，固定 alpha | regression/predictor/aci.py:197 |
| AdaptiveConformal | theta + gamma * (1 - covered - (1 - alpha))，固定 alpha | R/aci_algorithm.R:78-81 |

三个实现都是正确的固定 α 更新。原稿里的 α_t 是手写代码的错误，不是生态的默认。

这改变了审计 C 的主张。不能说“常见实现用错了”，只能说“手写实现容易错，而且错了
之后看起来更有效”。这是更窄、但更诚实的结论。

## 对论文的影响

1. 第 4 节加一个小节“Do real libraries do this?”，用表 8 和 MAPIE 的五种子结果。
2. 审计 B 的主张从“库会偷偷填充”改成“库会显式选择，默认值可能让覆盖率偏离目标；
   我们量化偏离的幅度”。
3. 审计 C 的主张从“常见 bug”改成“手写实现的风险；三个主流库都是对的”。
4. 相关工作里要引用 MAPIE、TorchCP 等库的文档，不能只引论文。

## 局限

- 五个库只做了源码检查，只有 MAPIE 跑了运行时实验。
- 版本是 2026-11-06 的当前版本，行号会随版本变化。
- 没有覆盖 R 的运行时行为；AdaptiveConformal 只读了 GitHub main。
- MAPIE 实验用的是合成五分类数据，真实数据上的幅度可能不同。
- 没有覆盖 MAPIE 的旧接口（MapieClassifier v0），只看了 v1 的 SplitConformalClassifier。


## 运行时补充（2026-11-06）

同一份五分类合成数据，逻辑回归，2,000 个测试点，α=0.10，准确率 0.487。

| 库 | 设置 | 覆盖率 | 空集率 | 集合大小 |
|---|---|---|---|---|
| MAPIE | LAC | 0.895 | 0.000 | 2.87 |
| MAPIE | APS 默认 | 0.949 | 0.000 | 3.46 |
| MAPIE | APS False | 0.809 | 0.000 | 2.48 |
| MAPIE | APS randomized | 0.892 | 0.001 | 3.02 |
| puncc | LAC | 0.895 | 0.000 | 2.87 |
| puncc | APS rand=True | 0.889 | 0.002 | 2.98 |
| puncc | APS rand=False | 0.977 | 0.000 | 4.06 |
| crepes | LAC | 0.895 | 0.000 | 2.87 |

- puncc 的 rand=False 与 MAPIE 的 include_last_label=True 是同一类政策：用非空规则换覆盖率。puncc 的差是 8.8 个点，MAPIE 的差是 5.7 个点（这次单种子运行）。
- 三个库的 LAC 结果完全一致（0.895，2.87），说明审计脚本本身是可比的。
- coverforest 0.0.3 与 sklearn 1.9 不兼容（_get_n_samples_bootstrap 缺 sample_weight 参数），未能运行；保留源码结论。
- TorchCP 1.2.1 的顶层 import 依赖 torch_geometric，未安装；保留源码结论。


## 八库补充（2026-11-06）

- nonconformist 2.1.0：ICP + margin，0.890 / 0.000 / 3.50；no forcing；smoothing=True。
- conformal 0.1：per-label thresholds at 100-epsilon percentile，0.890 / 0.000 / 3.02；no forcing；minimal API。
- 八库中五个跑过（MAPIE、puncc、crepes、nonconformist、conformal），三个只读源码（TorchCP、coverforest、AdaptiveConformal）。
- puncc APS rand=True 没有固定种子，空集率在 0.0–0.2% 之间波动；正文写 "below 0.2 percent"。
