# C2U-NER 复现材料说明（补充材料）

为便于匿名评审和后续归档，本文将复现材料划分为正文、数据说明、脚本、结果、图件、人工复核和受限数据六类。匿名评审阶段提供不暴露作者身份且不违反源端许可的材料；论文接收或预印本发布后，再补充归档 DOI、最终许可证和可公开数据文件。当前本地匿名补充材料目录为 `submission/C2U_NER_TALLIP_anon_supplement/`，可在 GitHub CLI 登录后推送为匿名审稿仓库。

## 复现包结构

复现仓库包含 `manuscript/`、`data_card/`、`scripts/`、`results/`、`figures/`、`manual_audit/`、`docs/` 和 `manifest/` 八个目录。`manuscript/` 放置匿名正文；`data_card/` 放置 C2U-NER 数据卡、图表源数据说明和数据可用性声明；`scripts/` 放置字符级评价、公开数据转换、manifest 生成和 GitHub 推送脚本；`results/` 放置主实验、骨干对比、外部验证、阈值消融、bootstrap 和错误分析汇总；`figures/` 放置图1-图5；`manual_audit/` 放置红acted 复核表 schema；`docs/` 放置源端许可回填模板、TALLIP 风险整改清单和 GitHub 推送说明；`manifest/` 放置文件级哈希清单。若人工复核样本或 C2U-NER 全文数据受许可限制，`manual_audit/` 和受限数据目录只发布字段说明、哈希和不含文本的统计摘要。

## 复现实验顺序

复现流程按三层执行。第一层是数据审计：运行公开数据转换脚本和 C2U-NER span 审计脚本，验证标签空间、实体文本切片、坏 span 数和实体规模。第二层是模型训练与解码：在固定随机种子 42、2024 和 3407 下训练 IBP-CINO、TBR-IBP-CINO 和 TBRK-IBP-CINO，并在验证集选择阈值后报告测试集严格字符级结果。第三层是统计与图表：用统一预测文件复现 bootstrap 置信区间、过滤基线、阈值消融、错误类型分解、图2、图4、图5 和表7-表12。每一层均提供关键中间数值作为校验点，避免只依赖最终 F1。

## IDD 提示模板摘要

为避免把自动构建流程写成不可复现的黑箱，补充材料记录三类提示模板。正式匿名仓库中可用真实字段名和伪样例替代受限文本。

### 零样本汉维翻译

输入字段包括 `sample_id`、`zh_text` 和 `zh_entities`。提示目标是生成自然维吾尔语句子，并保留人名、地名和机构名的核心语义。模板摘要如下：

```text
任务：将中文新闻句子翻译为自然维吾尔语。
约束：保留 PER/LOC/ORG 实体的核心语义；不要输出解释、列表或注释；只输出一个维吾尔语句子。
输入：{zh_text}
实体提示：{zh_entities}
输出：{ug_text}
```

### 形态感知软对齐

输入字段包括中文句子、维吾尔语句子、源端实体、实体类型、已占用 span 和硬对齐失败原因。输出必须是可解析 JSON：

```json
{
  "entity_id": "source entity id",
  "target_text": "目标端连续片段",
  "start": 0,
  "end": 0,
  "reason": "alignment rationale for diagnosis only"
}
```

系统只使用 `target_text`、`start` 和 `end` 参与审计；`reason` 仅用于错误诊断。若 `start/end` 与 `target_text` 不一致，以目标句中可唯一定位的 `target_text` 为候选；若无法唯一定位，则拒绝该输出。

### 生成式实体回填

输入字段包括当前维吾尔语译文、已接受实体 span、缺失源端实体和实体类型。提示要求模型在不改变已接受实体的前提下修复译文，使缺失实体以自然形式出现。修复后样本重新执行全量 span 解析、占用冲突检查和类型一致性检查；若已接受实体消失或产生类型冲突，则回退到修复前版本。

## 数据字段 schema

C2U-NER 的每条样本建议采用如下字段。若源端许可限制文本公开，可发布字段说明、哈希和不含原文的统计摘要。

| 字段 | 类型 | 说明 |
|---|---|---|
| `sample_id` | string | 样本唯一标识 |
| `zh_text` | string | 源端中文句子；受许可约束 |
| `ug_text` | string | 目标端维吾尔语句子；受许可约束 |
| `entities` | list | 目标端实体列表 |
| `entities[].start` | integer | 目标端字符起点，闭区间 |
| `entities[].end` | integer | 目标端字符终点，开区间 |
| `entities[].label` | string | PER、LOC 或 ORG |
| `entities[].text` | string | `ug_text[start:end]` |
| `entities[].source_text` | string | 对应源端实体文本 |
| `entities[].stage` | string | hard、soft、repair 或 bootstrap |
| `entities[].confidence` | float/null | 判别式自举或候选过滤置信度 |
| `audit.bad_span` | boolean | 是否存在越界、空 span 或切片不一致 |
| `audit.overlap_conflict` | boolean | 是否存在非法重叠 |
| `audit.label_valid` | boolean | 标签是否属于目标标签空间 |

## 审计伪代码

```text
for sample in dataset:
    assert sample.ug_text is not empty
    occupied = []
    for ent in sample.entities:
        check ent.label in {PER, LOC, ORG}
        check 0 <= ent.start < ent.end <= len(sample.ug_text)
        check sample.ug_text[ent.start:ent.end] == ent.text
        check ent does not partially overlap any accepted span
        if duplicate span with conflicting label:
            keep source-side label and log conflict
        add ent span to occupied
    if any check fails:
        mark sample as bad_span and exclude or send to manual audit pool
```

## 阈值与负样本摘要

判别式自举正例来自前四阶段通过所有审计的实体 span。负例来自三类候选：同句非实体片段、实体邻近偏移片段和空样本候选片段。推理阶段只接受最高预测类型属于 PER、LOC 或 ORG、置信度超过验证集阈值且通过 span 审计的候选。TBR 默认 refine 阈值为 0.55，TBRK 默认 keep 阈值为 0.50；dev-selected 结果在验证集上选择 refine 和 keep 阈值，再在测试集一次性报告。
