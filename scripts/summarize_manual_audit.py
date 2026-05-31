#!/usr/bin/env python3
"""Summarize double-review manual audit results for C2U-NER.

Expected input columns:
  reviewer_a_pass, reviewer_b_pass, adjudicated_pass, error_types

Pass columns accept yes/no style values:
  1, 0, true, false, yes, no, pass, fail, y, n, 是, 否, 通过, 不通过
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd


TRUE_VALUES = {"1", "true", "yes", "y", "pass", "passed", "是", "通过", "合格"}
FALSE_VALUES = {"0", "false", "no", "n", "fail", "failed", "否", "不通过", "不合格"}


def parse_bool(value):
    if pd.isna(value):
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    if text in TRUE_VALUES:
        return True
    if text in FALSE_VALUES:
        return False
    raise ValueError(f"Unrecognized pass value: {value!r}")


def cohens_kappa(a_values, b_values):
    pairs = [(a, b) for a, b in zip(a_values, b_values) if a is not None and b is not None]
    if not pairs:
        return None
    n = len(pairs)
    observed = sum(a == b for a, b in pairs) / n
    a_counts = Counter(a for a, _ in pairs)
    b_counts = Counter(b for _, b in pairs)
    expected = sum((a_counts[v] / n) * (b_counts[v] / n) for v in {True, False})
    if expected == 1:
        return 1.0
    return (observed - expected) / (1 - expected)


def split_error_types(series):
    counter = Counter()
    for value in series.dropna():
        for item in str(value).replace("；", ";").replace("，", ";").replace(",", ";").split(";"):
            item = item.strip()
            if item:
                counter[item] += 1
    return dict(counter)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv")
    parser.add_argument("--output-json", default="reports/manual_audit_v21/C2U_NER_manual_audit_summary.json")
    parser.add_argument("--output-md", default="reports/manual_audit_v21/C2U_NER_manual_audit_summary.md")
    args = parser.parse_args()

    df = pd.read_csv(args.input_csv)
    required = ["reviewer_a_pass", "reviewer_b_pass", "adjudicated_pass", "error_types"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"Missing required columns: {missing}")

    a = [parse_bool(v) for v in df["reviewer_a_pass"]]
    b = [parse_bool(v) for v in df["reviewer_b_pass"]]
    adj = [parse_bool(v) for v in df["adjudicated_pass"]]

    reviewed_pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    adjudicated = [x for x in adj if x is not None]
    entity_total = int(df.get("entity_count", pd.Series([0] * len(df))).fillna(0).sum())
    entity_pass = (
        int(df.loc[[x is True for x in adj], "entity_count"].fillna(0).sum())
        if "entity_count" in df and adjudicated
        else None
    )

    summary = {
        "sample_count": int(len(df)),
        "entity_count": entity_total,
        "empty_sample_count": int((df.get("entity_count", pd.Series([0] * len(df))).fillna(0) == 0).sum()),
        "reviewer_pair_count": len(reviewed_pairs),
        "adjudicated_count": len(adjudicated),
        "sample_pass_rate": (sum(adjudicated) / len(adjudicated)) if adjudicated else None,
        "entity_pass_rate_approx": (entity_pass / entity_total) if entity_total and entity_pass is not None else None,
        "raw_agreement": (sum(x == y for x, y in reviewed_pairs) / len(reviewed_pairs)) if reviewed_pairs else None,
        "cohens_kappa": cohens_kappa(a, b),
        "error_types": split_error_types(df["error_types"]),
    }

    out_json = Path(args.output_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    def fmt(x):
        return "NA" if x is None else f"{x:.4f}" if isinstance(x, float) else str(x)

    md = [
        "# C2U-NER Manual Audit Summary",
        "",
        f"- Sample count: {summary['sample_count']}",
        f"- Entity count: {summary['entity_count']}",
        f"- Empty sample count: {summary['empty_sample_count']}",
        f"- Reviewer pair count: {summary['reviewer_pair_count']}",
        f"- Adjudicated count: {summary['adjudicated_count']}",
        f"- Sample pass rate: {fmt(summary['sample_pass_rate'])}",
        f"- Entity pass rate approximation: {fmt(summary['entity_pass_rate_approx'])}",
        f"- Raw agreement: {fmt(summary['raw_agreement'])}",
        f"- Cohen's kappa: {fmt(summary['cohens_kappa'])}",
        "",
        "## Error Types",
        "",
    ]
    if summary["error_types"]:
        md.extend(f"- {k}: {v}" for k, v in summary["error_types"].items())
    else:
        md.append("- NA")
    Path(args.output_md).write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
