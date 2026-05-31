# TALLIP Risk Remediation Checklist

This checklist converts reviewer-style concerns into concrete manuscript and supplement actions.

## Completed in the Current Draft

| Risk | Current mitigation |
|---|---|
| Manuscript overclaims model novelty | IBP/TBR/TBRK are framed as an error-driven diagnostic baseline chain rather than the main algorithmic contribution. |
| CINO backbone choice unclear | The manuscript now includes same-protocol CINO/XLM-R/Glot500 comparison and explains why CINO is fixed for boundary experiments. |
| TBRK may look like ordinary filtering | A seed2024 filtering baseline and threshold ablation table compares IBP, TBR, default TBRK, and dev-selected TBRK. |
| IDD looks like a black box | Supplement includes prompt summaries, JSON schema, audit pseudocode, conflict rules, threshold notes, and retention-rate definition. |
| External validation overclaim | The text uses “consistent trend under a unified protocol” rather than SOTA or unconditional generalization language. |
| Data/code availability too vague | Anonymous supplement repository structure is created locally and excludes restricted raw text. |

## Author-side Items Still Requiring Factual Fill-in

| Item | Needed evidence | Where to fill |
|---|---|---|
| Double-review Uyghur manual audit | Reviewer A/B judgments, adjudication, pass rates, Cohen's kappa, error-type counts | Manuscript Table 6; data card; final supplement |
| People's Daily source version and license | Exact release URL or file, download/access date, license terms, redistribution permission | Manuscript Table 3; source license template; data availability |
| Anonymous GitHub URL | Repository URL created under an anonymized account or organization | Data availability statement; README |
| Final archive DOI | Zenodo/OSF/institutional archive after acceptance or preprint release | Data availability statement |

## Recommended Final Wording Rules

- Do not call C2U-NER a fully manually annotated dataset unless the manual audit is completed and reported.
- Do not use “state-of-the-art” unless a complete, fair, public benchmark comparison is added.
- Do not equate “publicly circulated 1998 People's Daily resource” with unrestricted redistribution.
- Keep the contribution order as: resource construction, audit/evaluation protocol, then diagnostic baseline experiments.
- Report external validation as evidence of trend consistency, not proof of universal generalization.

