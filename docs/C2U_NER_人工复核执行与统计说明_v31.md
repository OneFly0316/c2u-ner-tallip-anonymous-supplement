# C2U-NER 双人维吾尔语人工复核执行与统计说明

## 当前证据状态

本地复核清单位于 `reports/manual_audit_v21/C2U_NER_manual_audit_sample_v21.csv`，包含 220 条样本、582 个实体和 37 条空样本。当前文件中的 `reviewer_a_pass`、`reviewer_b_pass`、`adjudicated_pass` 和 `error_types` 列均为空，因此不能据此报告真实通过率、Cohen's kappa 或错误类型比例。

## 复核流程

两名具备维吾尔语阅读能力和 NER 标注经验的复核者独立填写 `reviewer_a_pass/reviewer_b_pass` 和备注列。若两人判断不同，由仲裁者填写 `adjudicated_pass`、`error_types` 和 `final_notes`。错误类型建议使用以下受控词表：

| 错误类型 | 含义 |
|---|---|
| semantic_shift | 维吾尔语句子未保留源端核心语义 |
| missing_entity | 源端实体在目标端漏译或不可定位 |
| wrong_type | PER/LOC/ORG 类型错误 |
| under_extended_boundary | 实体边界欠扩展，漏掉必要后缀或修饰成分 |
| over_extended_boundary | 实体边界过扩展，吸收非实体成分 |
| discontinuous_entity | 目标端对应片段非连续 span |
| unnatural_translation | 译文明显不自然但实体仍可定位 |
| other | 其他需说明的问题 |

## 统计脚本

填完复核表后运行：

```bash
python3 tools/summarize_manual_audit.py \
  reports/manual_audit_v21/C2U_NER_manual_audit_sample_v21.csv
```

脚本会生成：

- `reports/manual_audit_v21/C2U_NER_manual_audit_summary.json`
- `reports/manual_audit_v21/C2U_NER_manual_audit_summary.md`

这些文件可直接用于回填正文表6、数据卡和补充材料。

## 投稿写法原则

在复核表未填写前，论文只能报告抽样设计和复核协议，不能报告通过率或一致性。自动审计坏 span 数为 0 只能说明字符区间合法，不能替代人工语义质量结论。

