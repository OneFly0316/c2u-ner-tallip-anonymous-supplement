import argparse
import csv
import json
import os
from collections import Counter, defaultdict

import torch
from tqdm.auto import tqdm
from transformers import AutoModelForTokenClassification, AutoTokenizer


LABELS = ["O", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]
ID2LABEL = {i: label for i, label in enumerate(LABELS)}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_gold(spans):
    return {(int(s["start"]), int(s["end"]), s["label"]) for s in spans}


def bio_to_char_spans(pred_ids, offsets, threshold_special=True):
    spans = []
    current = None

    def close_current():
        nonlocal current
        if current is not None:
            spans.append(tuple(current))
            current = None

    for pred_id, (start, end) in zip(pred_ids, offsets):
        if threshold_special and int(start) == int(end):
            continue

        label = ID2LABEL[int(pred_id)]
        if label == "O":
            close_current()
            continue

        prefix, ent_type = label.split("-", 1)
        start, end = int(start), int(end)

        if prefix == "B":
            close_current()
            current = [start, end, ent_type]
        elif prefix == "I":
            if current is not None and current[2] == ent_type:
                current[1] = max(current[1], end)
            else:
                current = [start, end, ent_type]

    close_current()
    return set(spans)


def score_counts(gold_items, pred_items):
    tp = len(gold_items & pred_items)
    fp = len(pred_items - gold_items)
    fn = len(gold_items - pred_items)
    return tp, fp, fn


def tolerant_match(gold_item, pred_item, tolerance):
    gs, ge, gt = gold_item
    ps, pe, pt = pred_item
    return gt == pt and abs(gs - ps) <= tolerance and abs(ge - pe) <= tolerance


def tolerant_score_counts(gold_items, pred_items, tolerance):
    if tolerance <= 0:
        return score_counts(gold_items, pred_items)

    matched_gold = set()
    matched_pred = set()
    for pred_idx, pred_item in enumerate(sorted(pred_items)):
        candidates = [
            (abs(gold_item[0] - pred_item[0]) + abs(gold_item[1] - pred_item[1]), gold_idx, gold_item)
            for gold_idx, gold_item in enumerate(sorted(gold_items))
            if gold_idx not in matched_gold and tolerant_match(gold_item, pred_item, tolerance)
        ]
        if candidates:
            _, gold_idx, _ = min(candidates)
            matched_gold.add(gold_idx)
            matched_pred.add(pred_idx)

    tp = len(matched_pred)
    fp = len(pred_items) - tp
    fn = len(gold_items) - tp
    return tp, fp, fn


def prf(tp, fp, fn):
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def classify_errors(gold, pred):
    gold_by_type = defaultdict(list)
    pred_by_type = defaultdict(list)
    for s, e, t in gold:
        gold_by_type[t].append((s, e))
    for s, e, t in pred:
        pred_by_type[t].append((s, e))

    errors = Counter()
    for ps, pe, pt in pred - gold:
        if any(max(ps, gs) < min(pe, ge) for gs, ge in gold_by_type[pt]):
            errors["boundary_fp"] += 1
        elif any(max(ps, gs) < min(pe, ge) for gt, spans in gold_by_type.items() if gt != pt for gs, ge in spans):
            errors["type_confusion_fp"] += 1
        else:
            errors["spurious_fp"] += 1

    for gs, ge, gt in gold - pred:
        if any(max(gs, ps) < min(ge, pe) for ps, pe in pred_by_type[gt]):
            errors["boundary_fn"] += 1
        elif any(max(gs, ps) < min(ge, pe) for pt, spans in pred_by_type.items() if pt != gt for ps, pe in spans):
            errors["type_confusion_fn"] += 1
        else:
            errors["missed_fn"] += 1
    return errors


def evaluate(args):
    data = load_json(args.test_file)
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer_path or args.checkpoint, use_fast=True)
    model = AutoModelForTokenClassification.from_pretrained(args.checkpoint)
    device = torch.device(args.device if args.device else ("cuda" if torch.cuda.is_available() else "cpu"))
    model.to(device)
    model.eval()

    total = Counter()
    per_type = {t: Counter() for t in ["PER", "LOC", "ORG"]}
    error_counts = Counter()
    cases = []

    with torch.no_grad():
        for item in tqdm(data, desc=os.path.basename(args.checkpoint)):
            enc = tokenizer(
                item["text"],
                truncation=True,
                max_length=args.max_length,
                return_offsets_mapping=True,
                return_tensors="pt",
            )
            offsets = enc.pop("offset_mapping")[0].tolist()
            enc = {k: v.to(device) for k, v in enc.items()}
            pred_ids = model(**enc).logits.argmax(-1)[0].cpu().tolist()

            gold = normalize_gold(item.get("char_spans", []))
            pred = bio_to_char_spans(pred_ids, offsets)

            tp, fp, fn = tolerant_score_counts(gold, pred, args.boundary_tolerance)
            total.update({"tp": tp, "fp": fp, "fn": fn})
            for ent_type in per_type:
                g_t = {x for x in gold if x[2] == ent_type}
                p_t = {x for x in pred if x[2] == ent_type}
                t_tp, t_fp, t_fn = tolerant_score_counts(g_t, p_t, args.boundary_tolerance)
                per_type[ent_type].update({"tp": t_tp, "fp": t_fp, "fn": t_fn})

            errs = classify_errors(gold, pred)
            error_counts.update(errs)
            if (fp or fn) and len(cases) < args.max_cases:
                cases.append(
                    {
                        "id": item.get("id"),
                        "text": item["text"],
                        "text_zh": item.get("text_zh"),
                        "gold": sorted(list(gold)),
                        "pred": sorted(list(pred)),
                        "errors": dict(errs),
                    }
                )

    p, r, f1 = prf(total["tp"], total["fp"], total["fn"])
    rows = [{
        "name": args.name or os.path.basename(os.path.dirname(args.checkpoint)),
        "checkpoint": args.checkpoint,
        "scope": "char_span_exact" if args.boundary_tolerance == 0 else f"char_span_tol_{args.boundary_tolerance}",
        "precision": f"{p:.6f}",
        "recall": f"{r:.6f}",
        "f1": f"{f1:.6f}",
        "tp": total["tp"],
        "fp": total["fp"],
        "fn": total["fn"],
    }]
    for ent_type, c in per_type.items():
        t_p, t_r, t_f1 = prf(c["tp"], c["fp"], c["fn"])
        rows.append({
            "name": args.name or os.path.basename(os.path.dirname(args.checkpoint)),
            "checkpoint": args.checkpoint,
            "scope": ent_type,
            "precision": f"{t_p:.6f}",
            "recall": f"{t_r:.6f}",
            "f1": f"{t_f1:.6f}",
            "tp": c["tp"],
            "fp": c["fp"],
            "fn": c["fn"],
        })

    os.makedirs(os.path.dirname(args.output_csv) or ".", exist_ok=True)
    exists = os.path.exists(args.output_csv)
    with open(args.output_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if not exists:
            writer.writeheader()
        writer.writerows(rows)

    if args.error_json:
        os.makedirs(os.path.dirname(args.error_json) or ".", exist_ok=True)
        with open(args.error_json, "w", encoding="utf-8") as f:
            json.dump({"error_counts": dict(error_counts), "cases": cases}, f, ensure_ascii=False, indent=2)

    print(json.dumps({"overall": rows[0], "errors": dict(error_counts)}, ensure_ascii=False, indent=2))


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate NER checkpoints with exact original character spans.")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--tokenizer_path")
    parser.add_argument("--test_file", default="data/UG/dataset_for_ner_final_v3/test.json")
    parser.add_argument("--output_csv", default="reports/char_span_evaluation_v3.csv")
    parser.add_argument("--error_json")
    parser.add_argument("--name")
    parser.add_argument("--device")
    parser.add_argument("--max_length", type=int, default=512)
    parser.add_argument("--max_cases", type=int, default=80)
    parser.add_argument("--boundary_tolerance", type=int, default=0)
    return parser.parse_args()


if __name__ == "__main__":
    evaluate(parse_args())
