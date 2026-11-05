# 3C 文献检索协议

日期：2026-11-06
目标：60 到 80 条纳入文献，支撑二维地图与覆盖矩阵。

## 范围

共形分类、条件覆盖、风险控制、非可交换数据、以及 2023 年后的语言模型部署。
只收方法学贡献。纯应用论文（某个领域用共形做预测）只在提供新假设或新失效模式时纳入。
回归文献只在奠基性或直接支撑分类/风险控制时纳入。

## 数据库

- OpenAlex：主库，标题检索，按引用或相关度排序。
- arXiv：预印本与方法学前沿。
- Crossref：仅用于元数据核对，不做主检索（前两轮有 SSL 超时）。

## 查询组

| id | 主题 | OpenAlex | arXiv |
|---|---|---|---|
| foundations | 奠基与综述 | title.search: conformal prediction，按引用排序 | ti:"conformal prediction" |
| split | 分裂共形 | title.search: split conformal | ti:"split conformal" |
| aps | 自适应分数 | title.search: adaptive prediction sets | ti:"adaptive prediction sets" |
| risk | 风险控制 | title.search: conformal risk control | ti:"conformal risk control" |
| conditional | 条件覆盖 | title.search: conditional coverage conformal | ti:"conditional coverage" AND abs:conformal |
| group | 群条件与 Mondrian | title.search: group conditional conformal | ti:group AND ti:conformal |
| aci | 自适应共形推断 | title.search: adaptive conformal inference | ti:"adaptive conformal inference" |
| nonexch | 非可交换 | title.search: non-exchangeable conformal | ti:"non-exchangeable conformal" |
| llm | 语言模型 | title.search: conformal language model | ti:conformal AND ti:"language model" |
| survey | 综述 | title.search: conformal prediction survey | ti:"conformal prediction" AND ti:survey |

## 纳入标准

1. 2005 到 2026 年。
2. 英文。
3. 有方法学贡献：新分数、新保证、新假设、新失效模式、系统性评估。
4. 分类、条件覆盖、风险控制、非可交换、语言模型五类之一。

## 排除标准

1. 纯应用，且不引入新假设或新失效模式。
2. 只做回归，且不支撑分类或风险控制。
3. 非共形的不确定性方法（贝叶斯、深度集成、证据学习），除非作为基线。
4. 无法解析 DOI 或 arXiv 号的条目。

## 筛选流程

1. 标题与摘要筛，记录在 refs/screening_3c.csv。
2. 对 20 到 30 篇关键文献读全文或至少读方法与实验节。
3. 目标：检索 200 到 400 条，去重后 150 到 250 条，纳入 60 到 80 条。
4. 每一条纳入文献必须有 DOI 或 arXiv 号，字段经 Crossref/arXiv 核对。

## 二维地图

行：边际覆盖、群条件覆盖、逐点条件覆盖、风险控制。
列：可交换、协变量漂移、非可交换/时序、已知群。
每格：代表方法、需要的假设、代价、代表文献。

## 覆盖矩阵

比较本文与四篇已有综述：
Angelopoulos & Bates 2021、Fontana et al. 2023、Campos et al. 2024、Zhou et al. 2025。
维度：基础、分数、条件覆盖、风险控制、非可交换、语言模型、实现审计、双数据集实验。

## 产出

- refs/candidates_3c.json
- refs/screening_3c.csv
- refs/bib.json
- paper/tables/table1_map.md
- paper/tables/table9_coverage.md
