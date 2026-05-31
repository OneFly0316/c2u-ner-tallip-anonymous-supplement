#!/usr/bin/env python3
"""Create a v25 manifest for the C2U-NER TALLIP Chinese submission package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "submission_manifest_v25"


FILES = [
    ("manuscript", "reports/C2U_NER_中文论文修改稿_v25_TALLIP中文润色定稿候选.md", "public_draft"),
    ("manuscript", "word/C2U_NER_中文论文修改稿_v25_TALLIP中文润色定稿候选.docx", "public_draft"),
    ("manuscript_render", "tmp/docs/v25_final_candidate_check/C2U_NER_中文论文修改稿_v25_TALLIP中文润色定稿候选.pdf", "public_draft"),
    ("manuscript", "reports/C2U_NER_中文论文修改稿_v26_TALLIP投稿前要求对齐版.md", "public_draft"),
    ("manuscript", "word/C2U_NER_中文论文修改稿_v26_TALLIP投稿前要求对齐版.docx", "public_draft"),
    ("manuscript_render", "tmp/docs/v26_tallip_check/C2U_NER_中文论文修改稿_v26_TALLIP投稿前要求对齐版.pdf", "public_draft"),
    ("manuscript_acm_template", "word/C2U_NER_中文论文修改稿_v26_TALLIP_ACM模板版.docx", "public_draft"),
    ("manuscript_acm_template_render", "tmp/docs/v26_acm_template_check/C2U_NER_中文论文修改稿_v26_TALLIP_ACM模板版.pdf", "public_draft"),
    ("manuscript", "reports/C2U_NER_中文论文修改稿_v27_TALLIP正式中文稿.md", "public_draft"),
    ("manuscript", "word/C2U_NER_中文论文修改稿_v27_TALLIP正式中文稿.docx", "public_draft"),
    ("manuscript_render", "tmp/docs/v27_tallip_check/C2U_NER_中文论文修改稿_v27_TALLIP正式中文稿.pdf", "public_draft"),
    ("manuscript_acm_template", "word/C2U_NER_中文论文修改稿_v27_TALLIP_ACM模板版.docx", "public_draft"),
    ("manuscript_acm_template_render", "tmp/docs/v27_acm_template_check/C2U_NER_中文论文修改稿_v27_TALLIP_ACM模板版.pdf", "public_draft"),
    ("manuscript", "reports/C2U_NER_中文论文修改稿_v28_TALLIP摘要标题合规版.md", "public_draft"),
    ("manuscript", "word/C2U_NER_中文论文修改稿_v28_TALLIP摘要标题合规版.docx", "public_draft"),
    ("manuscript_render", "tmp/docs/v28_tallip_check/C2U_NER_中文论文修改稿_v28_TALLIP摘要标题合规版.pdf", "public_draft"),
    ("manuscript_acm_template", "word/C2U_NER_中文论文修改稿_v28_TALLIP_ACM模板版.docx", "public_draft"),
    ("manuscript_acm_template_render", "tmp/docs/v28_acm_template_check/C2U_NER_中文论文修改稿_v28_TALLIP_ACM模板版.pdf", "public_draft"),
    ("manuscript", "reports/C2U_NER_中文论文修改稿_v29_TALLIP完整性审计版.md", "public_draft"),
    ("manuscript", "word/C2U_NER_中文论文修改稿_v29_TALLIP完整性审计版.docx", "public_draft"),
    ("manuscript_render", "tmp/docs/v29_tallip_check/C2U_NER_中文论文修改稿_v29_TALLIP完整性审计版.pdf", "public_draft"),
    ("manuscript_acm_template", "word/C2U_NER_中文论文修改稿_v29_TALLIP_ACM模板版.docx", "public_draft"),
    ("manuscript_acm_template_render", "tmp/docs/v29_acm_template_check/C2U_NER_中文论文修改稿_v29_TALLIP_ACM模板版.pdf", "public_draft"),
    ("manuscript_final", "reports/C2U_NER_TALLIP_中文正式稿_FINAL.md", "public_draft"),
    ("manuscript_final", "word/C2U_NER_TALLIP_中文正式稿_FINAL.docx", "public_draft"),
    ("manuscript_final_render", "tmp/docs/C2U_NER_TALLIP_中文正式稿_FINAL.pdf", "public_draft"),
    ("manuscript_final_acm_template", "word/C2U_NER_TALLIP_中文正式稿_ACM模板_FINAL.docx", "public_draft"),
    ("manuscript_final_acm_template_render", "tmp/docs/C2U_NER_TALLIP_中文正式稿_ACM模板_FINAL.pdf", "public_draft"),
    ("final_delivery_note", "reports/C2U_NER_TALLIP_中文正式稿_FINAL_交付说明.md", "public_draft"),
    ("manuscript", "reports/C2U_NER_TALLIP_中文正式稿_v30_声明附录调整版.md", "public_draft"),
    ("manuscript", "word/C2U_NER_TALLIP_中文正式稿_v30_声明附录调整版.docx", "public_draft"),
    ("manuscript_render", "tmp/docs/v30_tallip_check/C2U_NER_TALLIP_中文正式稿_v30_声明附录调整版.pdf", "public_draft"),
    ("manuscript_acm_template", "word/C2U_NER_TALLIP_中文正式稿_ACM模板_v30_声明附录调整版.docx", "public_draft"),
    ("manuscript_acm_template_render", "tmp/docs/v30_acm_template_check/C2U_NER_TALLIP_中文正式稿_ACM模板_v30_声明附录调整版.pdf", "public_draft"),
    ("supplement", "reports/C2U_NER_TALLIP_复现材料说明_SUPPLEMENT.md", "public_draft"),
    ("english_translation", "reports/C2U_NER_TALLIP_English_translation_v1.md", "public_draft"),
    ("english_translation", "word/C2U_NER_TALLIP_English_translation_v1.docx", "public_draft"),
    ("english_translation_render", "tmp/docs/english_v1_check/C2U_NER_TALLIP_English_translation_v1.pdf", "public_draft"),
    ("english_polished", "reports/C2U_NER_TALLIP_English_polished_v2.md", "public_draft"),
    ("english_polished", "word/C2U_NER_TALLIP_English_polished_v2.docx", "public_draft"),
    ("english_polished_render", "tmp/docs/english_v2_check/C2U_NER_TALLIP_English_polished_v2.pdf", "public_draft"),
    ("package_index", "reports/C2U_NER_TALLIP_中文投稿包索引_v25.md", "internal"),
    ("author_form", "reports/TALLIP_作者需补信息表_v25.md", "internal"),
    ("author_form", "reports/TALLIP_作者侧信息采集表_v26.md", "internal"),
    ("review_risk_audit", "reports/TALLIP_审稿风险审计_v25.md", "internal"),
    ("submission_checklist", "reports/C2U_NER_TALLIP_ACM_对齐自检表_v25.md", "internal"),
    ("completion_audit", "reports/C2U_NER_TALLIP_v25_完成度审计.md", "internal"),
    ("requirements_audit", "reports/TALLIP_官方要求对齐审计_v26.md", "internal"),
    ("requirements_audit", "reports/TALLIP_v28_官方要求逐项审计.md", "internal"),
    ("integrity_audit", "reports/TALLIP_v29_完整性一致性审计.md", "internal"),
    ("final_fill_form", "reports/TALLIP_v29_最终回填总表.md", "internal"),
    ("completion_audit", "reports/TALLIP_v29_中文稿完成度审计.md", "internal"),
    ("structure_audit", "reports/TALLIP_v30_声明附录调整审计.md", "internal"),
    ("risk_mitigation_report", "reports/TALLIP_投稿前风险整改完成报告_FINAL.md", "internal"),
    ("revision_record", "reports/ARS_TALLIP_中文稿整改记录_v23.md", "internal"),
    ("data_card", "reports/C2U_NER_数据卡_v24.md", "public_draft"),
    ("data_card", "reports/C2U_NER_数据卡_v26.md", "public_draft"),
    ("data_card", "reports/C2U_NER_数据卡_FINAL.md", "public_draft"),
    ("source_license_template", "reports/C2U_NER_源端数据许可回填模板_v26.md", "internal"),
    ("manual_audit_template", "reports/C2U_NER_人工复核结果回填模板_v26.md", "internal"),
    ("source_data", "reports/C2U_NER_图表源数据说明_v24.md", "public_draft"),
    ("manual_audit_protocol", "reports/C2U_NER_抽样人工复核协议_v15.md", "public_draft"),
    ("manual_audit_sample", "reports/C2U_NER_人工复核抽样说明_v21.md", "public_draft"),
    ("manual_audit_sample", "reports/manual_audit_v21/C2U_NER_manual_audit_sample_v21.csv", "controlled_until_source_license_confirmed"),
    ("manual_audit_sample", "reports/manual_audit_v21/C2U_NER_manual_audit_sample_v21.jsonl", "controlled_until_source_license_confirmed"),
    ("figure_plan", "reports/C2U_NER_TALLIP_图件设计说明_v19.md", "public_draft"),
    ("data_availability", "reports/C2U_NER_数据与代码可用性声明_v24.md", "internal"),
    ("script", "tools/build_submission_manifest_v25.py", "public_code"),
    ("script", "tools/build_submission_manifest_v24.py", "public_code"),
    ("script", "tools/build_manual_audit_sample_v21.py", "public_code"),
    ("script", "tools/render_c2u_manuscript_docx.py", "public_code"),
    ("script", "tools/render_c2u_acm_template_docx.py", "public_code"),
    ("script", "tools/evaluate_char_spans.py", "public_code"),
    ("script", "tools/prepare_public_uyghur_v17.py", "public_code"),
    ("script", "tools/build_public_bootstrap_summary_v20.py", "public_code"),
    ("script", "tools/bootstrap_error_json_ci.py", "public_code"),
    ("script", "tools/build_error_driven_model_story_v12.py", "public_code"),
    ("script", "tools/build_strict_experiment_package_v11.py", "public_code"),
    ("script", "tools/run_backbone_selection_char_exact.py", "public_code"),
    ("script", "scripts/run_backbone_selection_multigpu_v23.py", "public_code"),
    ("result", "reports/backbone_comparison_v23.md", "public_result"),
    ("result", "reports/backbone_ibp_comparison_v23.csv", "public_result"),
    ("result", "reports/backbone_selection_v23_with_token_f1.csv", "public_result"),
    ("result", "reports/paper_multiseed_strict_summary_v11.csv", "public_result"),
    ("result", "reports/public_uyghur_results_v17.csv", "public_result"),
    ("result", "reports/PUBLIC_UYGHUR_BOOTSTRAP_SUMMARY_v20.md", "public_result"),
    ("result", "reports/ERROR_DRIVEN_MODEL_STORY_v12.md", "public_result"),
    ("figure", "reports/figures/fig1_idd_pipeline_final.png", "public_draft"),
    ("figure", "reports/figures/fig2_c2u_entity_distribution.png", "public_draft"),
    ("figure", "reports/figures/fig3_model_chain_final.png", "public_draft"),
    ("figure", "reports/figures/fig4_main_public_f1.png", "public_draft"),
    ("figure", "reports/figures/fig5_error_counts.png", "public_draft"),
    ("figure_english", "reports/figures/fig1_idd_pipeline_final_en.png", "public_draft"),
    ("figure_english", "reports/figures/fig2_c2u_entity_distribution_en.png", "public_draft"),
    ("figure_english", "reports/figures/fig3_model_chain_final_en.png", "public_draft"),
    ("figure_english", "reports/figures/fig4_main_public_f1_en.png", "public_draft"),
    ("derived_dataset", "data/UG/dataset_for_ner_final_v3/train.json", "restricted_pending_source_license"),
    ("derived_dataset", "data/UG/dataset_for_ner_final_v3/dev.json", "restricted_pending_source_license"),
    ("derived_dataset", "data/UG/dataset_for_ner_final_v3/test.json", "restricted_pending_source_license"),
    ("external_dataset_summary", "data/public/finer_ug_per_org_loc/dataset_card.json", "public_result"),
    ("external_dataset_summary", "data/public/wikiann_ug_per_org_loc/dataset_card.json", "public_result"),
    ("external_dataset_summary", "data/public/codemurt_uyghur_ner_per_org_loc/dataset_card.json", "public_result"),
]


ACCESS_NOTES = {
    "public_draft": "可作为论文草稿、图表或补充说明公开；投稿前仍需作者确认作者信息和许可口径",
    "public_code": "可进入匿名复现仓库的代码",
    "public_result": "可公开的汇总结果、统计表、数据卡或分析报告",
    "controlled_until_source_license_confirmed": "含源端或目标端文本，需源端许可确认后再公开",
    "restricted_pending_source_license": "C2U-NER 派生数据全文，暂不公开，等待源端许可和发布策略确认",
    "internal": "内部投稿准备材料，不建议原样提交给审稿人",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for category, rel_path, access_route in FILES:
        path = ROOT / rel_path
        rows.append(
            {
                "category": category,
                "path": rel_path,
                "exists": path.exists(),
                "bytes": path.stat().st_size if path.exists() else "",
                "sha256": sha256(path) if path.exists() else "",
                "access_route": access_route,
                "access_note": ACCESS_NOTES[access_route],
            }
        )
    return rows


def write_manifest(rows: list[dict[str, object]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / "C2U_NER_submission_manifest_v25.csv"
    json_path = OUT_DIR / "C2U_NER_submission_manifest_v25.json"
    md_path = ROOT / "reports" / "C2U_NER_匿名审稿材料清单_v25.md"

    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    missing = [r for r in rows if not r["exists"]]
    md = [
        "# C2U-NER 匿名审稿材料清单与哈希（v25）",
        "",
        "## 用途",
        "",
        "本清单用于准备 TALLIP 匿名审稿材料、数据可用性声明和后续归档仓库。清单以 v25 中文润色定稿候选为中心，记录支撑论文主要结论的正文、图表、数据卡、人工复核材料、脚本、结果表、外部数据摘要和受限派生数据文件，并给出 SHA-256 哈希。",
        "",
        "## 机器可读清单",
        "",
        "- CSV：`reports/submission_manifest_v25/C2U_NER_submission_manifest_v25.csv`",
        "- JSON：`reports/submission_manifest_v25/C2U_NER_submission_manifest_v25.json`",
        "",
        "## 访问路线说明",
        "",
        "| access_route | 含义 |",
        "|---|---|",
    ]
    for key, value in ACCESS_NOTES.items():
        md.append(f"| {key} | {value} |")

    md.extend(
        [
            "",
            "## 文件清单",
            "",
            "| 类别 | 路径 | 大小(bytes) | SHA-256 | 访问路线 |",
            "|---|---|---:|---|---|",
        ]
    )
    for row in rows:
        size = row["bytes"] if row["exists"] else "MISSING"
        digest = str(row["sha256"])[:16] + "..." if row["sha256"] else ""
        md.append(f"| {row['category']} | `{row['path']}` | {size} | `{digest}` | {row['access_route']} |")

    md.extend(
        [
            "",
            "## 建议匿名审稿仓库结构",
            "",
            "```text",
            "c2u-ner-anonymous/",
            "  README.md",
            "  manuscript/",
            "    C2U_NER_中文润色定稿候选.md",
            "  data_card/",
            "    C2U_NER_数据卡.md",
            "    图表源数据说明.md",
            "  scripts/",
            "    evaluate_char_spans.py",
            "    build_manual_audit_sample.py",
            "    prepare_public_uyghur.py",
            "    bootstrap_error_json_ci.py",
            "    run_backbone_selection_char_exact.py",
            "  results/",
            "    backbone_ibp_comparison.csv",
            "    paper_multiseed_strict_summary.csv",
            "    public_uyghur_results.csv",
            "    public_bootstrap_summary.md",
            "    error_driven_model_story.md",
            "  figures/",
            "    fig1_idd_pipeline_final.png",
            "    fig2_c2u_entity_distribution.png",
            "    fig3_model_chain_final.png",
            "    fig4_main_public_f1.png",
            "    fig5_error_counts.png",
            "  manual_audit/",
            "    人工复核抽样说明.md",
            "    C2U_NER_manual_audit_sample.csv  # 若许可允许；否则只提供字段说明和哈希",
            "  manifest/",
            "    C2U_NER_submission_manifest_v25.csv",
            "```",
            "",
            "## 数据发布边界",
            "",
            "1. C2U-NER 派生数据全文在确认源端人民日报中文 NER 标注资源许可后再公开。",
            "2. 若源端许可不允许再分发原文或派生文本，可公开数据卡、构建脚本、审计脚本、汇总统计、哈希、复现实验命令和不含受限文本的派生摘要。",
            "3. `whoisjones/fiNERweb`、WikiANN/PAN-X 和 `codemurt/uyghur_ner_dataset` 等外部验证来源以原始公开数据链接和处理脚本方式引用，不重新声明为本文原创数据。",
            "4. 人工复核 CSV/JSONL 含中文源句和维吾尔语目标句，发布前同样受源端许可约束；当前复核判断列为空，只能作为抽样清单和字段模板。",
            "",
            "## 缺失项",
            "",
        ]
    )
    if missing:
        md.extend(f"- `{row['path']}`" for row in missing)
    else:
        md.append("- 当前清单内文件均存在。")

    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(csv_path)
    print(json_path)
    print(md_path)
    print(f"files={len(rows)} missing={len(missing)}")


def main() -> None:
    write_manifest(build_rows())


if __name__ == "__main__":
    main()
