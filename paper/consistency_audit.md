# Consistency audit

Date: 2026-11-06. Scope: paper/main.md, 10,343 words; Tables 1-10; Figures 1-5;
refs/bib.json (69-entry pool, 26 cited in prose).

## Checks performed

1. Section structure: Sections 1-7 plus Data and code availability. Word counts
   recorded per section.
2. Table references: Table 1 through Table 10 are referenced; all ten table files
   exist in paper/tables/.
3. Figure references: Figure 1 through Figure 5 are referenced; all five figure
   files exist in paper/figures/ (fig1_pipeline, fig2_equivalence, fig3_forcing,
   fig4_aci, fig5_regime).
4. Citations: 26 unique citation keys in prose, all present in refs/bib.json. No
   missing keys.
5. Key numbers: the abstract, Section 1.2, Section 4.1-4.3, Section 4.4, Section
   5.2-5.6 and Section 6 were checked against Tables 2-8 and the JSON results.
6. Cross-references: Section 2.2 references Figure 1; Section 4.1 references
   Tables 2 and 5 and Figure 2; 4.2 references Tables 3 and 6 and Figure 3; 4.3
   references Tables 4 and 7 and Figure 4; 5.5 references Figure 5; 5.1 references
   Table 10.

## Confirmed issues and fixes

| issue | fix |
|---|---|
| Abstract said "up to 9.5 points" without the alpha qualifier, while the grid contains a 0.318 maximum at alpha = 0.30 | qualified as "up to 9.7 points at alpha = 0.10"; the 9.7 is the digits maximum at that level, the 9.5 is CIFAR |
| Section 1.2 and 5.6 used 9.5 and 8.4 without saying which setting | replaced with "at alpha = 0.10, 9.7 on digits and 9.5 on CIFAR-10" |
| Section 4.2 stated the digits maximum only through the 8.4 smallest-model cell | added "the largest cell is 9.7 points at 224 training points" |
| Figure 1 was listed but did not exist | created fig1_pipeline and referenced it in 2.2 |
| Table list T3/T4 pointed to JSON, order was T1-T4, F1-F5, T5-T10 | reordered T1-T10 then F1-F5, sources corrected to Markdown tables |
| Section 1.5 claimed "a curated set of 69 references" while the prose cites 26 | changed to "a curated pool ... the cited subset is what the argument needs" |
| Section 2.2 repeated "the construction has three stages" after the Figure 1 sentence | removed the repetition |

## Numbers checked, with sources

- Raw threshold, digits smallest model: empty 0.701, coverage 0.294, forced 0.833
  (Table 2).
- Raw threshold, CIFAR 30k: empty 0.244, coverage 0.716, forced 0.855, accuracy
  0.855 (Table 5).
- Max-probability calibration, CIFAR: 0.668 / 0.762 / 0.771 / 0.810 (Table 5).
- Post-processing, digits: mean delta 0.077, max 0.318; per-score means 0.041 /
  0.080 / 0.108 / 0.078 (Table 3, results/postprocess_digits.json).
- Post-processing, CIFAR: APS randomized 1.0-3.7 percent empty; APS deterministic
  6.9-9.5 percent empty; 5k cell 0.994 coverage and size 6.08 (Table 6).
- MAPIE: 0.9457 default, 0.8998 randomized, 0.8284 False; 4.6-point gap
  (results/mapie_empty.json, Table 8).
- ACI, digits linear: static 0.666; fixed 0.836 / size 3.44; buggy 0.869 / size
  4.58; near-trivial 10.8 to 24.4 percent (Table 4).
- ACI, CIFAR: static 0.272; fixed 0.677 / size 5.13; buggy 0.801 / size 6.39;
  near-trivial 4.6 to 12.9 percent (Table 7).
- ACI divergence: two of five seeds above 0.69, one at 0.998; coverage 0.436 and
  0.162; seed SD 0.205 vs 0.046 (results/aci_digits.json).

## Remaining issues, not fixed

1. Reference list. The manuscript cites 26 keys in prose. The map table adds CRC,
   NonExchgCRC and Combes2026 as plain keys. The software audit adds six entries
   (MAPIE, TorchCP, puncc, crepes, coverforest, AdaptiveConformal). The 69-entry
   bib.json pool is not the reference list; the final list should be the cited
   subset plus software, about 35 entries.
2. Preprint marking. Aguru2026, Mehrtens2025, Gauthier2025 and Boman2026 are
   preprints. The prose now says preprints are marked in the reference list; the
   list must actually mark them.
3. Data and code availability. The repository URL is a placeholder.
4. Working notes. The block after the final "---" (Tables and figures, Claims
   ledger) is a working artifact and must be excluded from the submission build.
5. Length. 10,343 words. Current Science has a 6,000-word limit; a condensed
   version is a separate writing task, not a deletion pass.

## Not verified

- A full numeric sweep of every decimal in the manuscript against the JSON. The
  key claims were checked; the tables are generated from the JSON, and the text
  numbers were written from the tables. A scripted full sweep is a useful next
  step before submission.
- The bibliography metadata of the recent entries (some author strings come from
  OpenAlex and need a Crossref pass).


## Reference list update (2026-11-06)

The reference list is built as paper/references.md: 36 entries, 30 papers and 6
software entries. The cited-key set is the union of the prose citations (27 keys),
the keys used in Table 1 (15 keys), and the software entries (6 keys). Item 1 of
the remaining issues is resolved.

Four metadata errors were fixed during the build:

| entry | fix |
|---|---|
| Angelopoulos2021intro | cited as the 2023 Foundations and Trends version (16(4), 494-591, DOI 10.1561/2200000101), not the 2021 preprint |
| Campos2024 | pages corrected to 1497-1516 (Crossref) |
| Hore2024 | issue year set to 2025, matching volume 87 and the Gibbs 2025 entry |
| Mehrtens2025 | book-chapter DOI removed; the entry is the 2025 arXiv preprint (2506.18162), marked preprint |

Preprints are marked in the list. The remaining list-level issues are:

1. Vovk2012 has no DOI or arXiv identifier; it uses the PMLR URL. This is a
   persistent identifier but not the DOI/arXiv rule in the protocol.
2. The software entries use organisational authors (MAPIE contributors, TorchCP
   contributors, and so on). A journal may require the package authors.
3. The HTML key comments in paper/references.md must be stripped in the
   submission build.
4. The citation keys in the manuscript are still [@key] placeholders. They must be
   converted to the target journal's numeric or author-year style.
