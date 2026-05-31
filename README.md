# C2U-NER Anonymous Supplement

This repository is the anonymous review package for the manuscript **C2U-NER: Chinese-to-Uyghur Resource Construction and Character-level Boundary Evaluation for Low-resource Named Entity Recognition**.

The package is designed for ACM TALLIP review. It provides manuscript files, data documentation, reproducibility materials, result tables, figure files, scripts, and a redacted manual-audit template. It intentionally excludes author-identifying metadata and any source-side or target-side text that may be subject to redistribution restrictions.

## Repository Layout

| Directory | Contents |
|---|---|
| `manuscript/` | Chinese manuscript draft used for formatting and content review |
| `data_card/` | C2U-NER data card and release notes |
| `supplement/` | Reproducibility supplement, IDD prompts, schema, audit rules, thresholds |
| `results/` | Main experiment tables, threshold sweeps, bootstrap outputs, ablation summaries |
| `figures/` | Figure files used by the manuscript |
| `manual_audit/` | Redacted manual-audit schema and review protocol |
| `scripts/` | Character-level evaluation, public-data conversion, and manifest scripts |
| `docs/` | Source-data license audit template and author-side checklist |
| `manifest/` | File manifest from the local submission package |

## What Is Included

- C2U-NER statistics: 27,818 Uyghur sentences and 44,118 PER/LOC/ORG entities.
- IDD construction details: Hunyuan translation prompt, hard alignment, Qwen3 soft alignment JSON schema, generative repair constraints, XLM-R bootstrap description, and audit pseudocode.
- Evaluation protocol: strict character-level exact match with shared scripts and fixed random seeds.
- Experiment evidence: IBP/TBR/TBRK main results, public validation results, threshold sweeps, bootstrap tests, and diagnostic ablation evidence.
- Manual audit materials: a redacted 220-sample review schema. The non-redacted sheet should only be shared if source and derived text redistribution is permitted.

## What Is Not Included

- Full People's Daily source text.
- Full generated Uyghur text if redistribution is not cleared.
- Author-identifying metadata.
- API keys, model weights, or local checkpoint binaries.

## Data Release Policy

The source side is based on a publicly circulated 1998 People's Daily NER resource. Because redistributed versions may differ in license language and release terms, the manuscript separates public availability from redistribution permission. If the selected source version permits derived release, the final archive can include the Uyghur-side text and character spans. If not, the public archive should include scripts, schemas, hashes, aggregate statistics, predictions, and audit reports only.

## Reproducibility Entry Points

1. Read `supplement/C2U_NER_TALLIP_复现材料说明_SUPPLEMENT.md`.
2. Verify table-level numbers in `results/paper_main_strict_results_v11.csv`.
3. Inspect TBRK threshold behavior in `results/tbrk_threshold_sweep_focused_v10.csv`.
4. Use `scripts/evaluate_char_spans.py` for strict character-level matching.
5. Use `manual_audit/C2U_NER_manual_audit_sample_schema_redacted.csv` as the review-sheet schema.

## GitHub Setup

This directory can be pushed as an anonymous review repository after GitHub CLI authentication:

```bash
cd submission/C2U_NER_TALLIP_anon_supplement
bash scripts/create_github_repo.sh
```

If `gh` is not installed, install GitHub CLI first, then run `gh auth login`.

