# 共形预测综述 · 完整材料包

生成日期：2026-11-05。包含原稿、实验数据、文献清单、图件、各期刊版本与全部构建脚本。
打包过程不修改工作区里的任何原文件。

## 01_原稿_未调整格式 ← 你要的「原稿」在这里

| 文件 | 说明 |
|---|---|
| 英文原稿_LaTeX源_Conformal_Prediction_Survey.tex | **最初的英文投稿源**，Elsevier CAS 模板，未按 Current Science / SAJS 改造 |
| 英文原稿_去格式纯文本.txt | 从上面那份 .tex 提取的纯文本：去掉 LaTeX 命令，保留章节、段落、公式、图表题注与参考文献，引用转成 [n]。方便自行排版或换模板 |
| 英文原稿_排版PDF.pdf | 该源编译出的 17 页 PDF |
| 英文原稿_Word版.docx | 该源转出的 Word 版（公式是原生可编辑对象） |
| 中文原稿_Markdown.md | 中文版内容源（去 AI 味改写后的定稿） |
| 中文课程报告.docx / 中文课程报告_新图版.docx | 中文成品；后者是图件重做后的版本 |
| 选题建议书.html | 立项阶段的选题建议书 |

注意：`.tex` 里含 CAS 模板标记，属于「未针对具体期刊二次调整格式」的原始稿；
若需要完全无标记的内容，用 `英文原稿_去格式纯文本.txt`。

## 02_实验数据与代码

`numbers.json` 是唯一数据源（81 KB），正文和表格里的每个数字都从它读出。
包含 dataset、base_accuracy、e1_summary/e1_raw、e2_summary/e2_raw、
e2_temperature、e2_wilcoxon、e3、e3_static_sliding、e3_adaptive_sliding。
`numbers_brief.txt` 是便于人工核对的摘要。

代码：`experiment.py`（原始实验）、`experiment_figstyle.py`（按终稿图宽重画）、
`make_schematics.py`（最初 4 张示意图）、`make_schematics_v2.py`（重设计的图1/图4）、
`make_fig10.py`（文献年份分布）。全部随机种子已固定。
数据用 scikit-learn 自带 digits，不需要外部下载。

## 03_文献清单与检索

- `refs.json` — 项目原始文献清单，**34 条**（保持原样）
- `refs_complete_35条.json` — 打包时补了一份完整清单，**35 条**

差异说明：正文 `egin{thebibliography}` 里有 35 条，其中 `Guo2017`（On Calibration
of Modern Neural Networks，温度缩放基线）没有进 `refs.json`。打包副本补上了这一条，
并在文件内写了 `_archive_note`。原文件未改动，因为 `make_fig10.py` 依赖它的 34 条
来生成年份分布图。

其余为检索与核验过程：`oa_scan.py`、`verify.py`、`refine.py` 等脚本，以及
`doi_resolved.json`、`arxiv_ids.json`、`targeted.json`、`verify_results.json`
等中间结果。全部条目带 DOI 或 arXiv 号，预印本在正文与清单里都标注了未经评审。

## 04_图件

`最终图_投稿用/`（13 个文件，含 PNG 与矢量 PDF）、`研究阶段图/`、
`CurrentScience_单独图件/`（10 张图各含 400dpi PNG + PDF）、`实验原始输出/`。

## 05_期刊版本与评估

Elsevier 投稿附件、Current Science 完整投稿包（含压缩后的
`CurrentScience_Manuscript.tex`）、SAJS 匹配度评估。这些是衍生版本，不是原稿。

## 06_构建脚本与模板

所有 .tex/.md → .docx 的生成器、校验脚本、OMML 公式模块 `_texmath.py`，
以及 Elsevier CAS 模板文件（cas-sc.cls 等）。

## 复现顺序

1. 跑 `_research/experiment.py` 生成 `numbers.json` 与实验图
2. 跑 `make_schematics_v2.py`、`make_fig10.py` 生成示意图
3. 用 `pdflatex` 编译 `Conformal_Prediction_Survey.tex`（两遍）得到 PDF
4. 用 `build_en_docx.py` / `build_zh_docx.py` / `build_cs_docx.py` 生成各版 Word
5. 用 `_verify_en_docx.py` / `_verify_cs.py` 做构建期校验

## 一点提醒

各期刊版本是按不同投稿要求从同一份内容派生的，正文经历过压缩与改写，
数字一致但措辞不同。若以「原稿」为准，请用 01 目录里的文件。
