# 3C 筛选说明

## 数字

- 检索：10 组 query，OpenAlex 261 条，arXiv 182 条，原始 443 条，去重 337 条。
- 自动初筛：110 shortlist、77 borderline、150 reject。
- 最终判定：40 include、149 defer、148 exclude。
- 最终书目：69 条，其中 35 条旧稿种子、6 条经典补充、28 条近年工作。
- 29 条书目是已知条目种子，标题检索没有返回（书名或标题不含 conformal prediction），
  所以不在 337 条的筛选表里。

## 三个判定词

- include：进入 bib.json。
- defer：进了 shortlist 或 borderline，但没有逐条读完，也没有被否定。
- exclude：标题或摘要明显不相关，或不是方法学贡献。

## 必须承认的局限

1. 149 条 defer 不是“排除”，是“没读完”。这篇综述是 curated review，不是 PRISMA 式的
   系统综述。正文不能写“我们覆盖了全部文献”，只能写“在我们检索并阅读的范围内”。
2. 28 条近年工作是从 shortlist 顶部和已知方法学线索里选的，不是对 337 条的穷举阅读。
3. 标题检索会漏掉经典文献，所以用了 35 条旧稿种子加 6 条经典补充。这是已知条目检索，
   不是系统检索。
4. 2026 年的预印本较多，正文必须逐条标注 status=preprint。

## 如果要升级成系统综述

读掉 149 条 defer，补 Crossref 与 Semantic Scholar，做 PRISMA 流程图和双人 screening。
那是另一个量级的工作。当前版本的目标是 60 到 80 条的支持性书目，不是穷举。
