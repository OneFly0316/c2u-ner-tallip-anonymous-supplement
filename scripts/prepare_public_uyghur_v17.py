import argparse
import json
import random
import signal
import traceback
from datetime import datetime
from pathlib import Path

from prepare_public_ner_datasets import (
    SPLIT_ALIASES,
    convert_records,
    infer_label_names,
    split_single_records,
    write_json,
    write_reports,
)


ROOT = Path("/home/ubuntu/GYF/LLM_NER")
REPORTS = ROOT / "reports"
PUBLIC_ROOT = ROOT / "data" / "public"
OUT_JSON = REPORTS / "public_uyghur_fetch_status_v17.json"
OUT_MD = REPORTS / "PUBLIC_UYGHUR_FETCH_STATUS_v17.md"


DATASETS = [
    {
        "dataset_id": "wikiann_ug_per_org_loc",
        "source": "unimelb-nlp/wikiann",
        "config": "ug",
        "fallbacks": [("wikiann", "ug")],
        "output_dir": PUBLIC_ROOT / "wikiann_ug_per_org_loc",
        "authority": "tier1",
        "split_policy": "use_existing",
        "role": "authoritative public Uyghur PAN-X/WikiANN validation",
        "local_dir": "wikiann_ug",
        "label_names": ["O", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"],
        "local_patterns": {
            "train": ["**/ug/train*.parquet", "**/train*.parquet"],
            "validation": ["**/ug/validation*.parquet", "**/validation*.parquet", "**/dev*.parquet"],
            "test": ["**/ug/test*.parquet", "**/test*.parquet"],
        },
    },
    {
        "dataset_id": "codemurt_uyghur_ner_per_org_loc",
        "source": "codemurt/uyghur_ner_dataset",
        "config": "",
        "fallbacks": [],
        "output_dir": PUBLIC_ROOT / "codemurt_uyghur_ner_per_org_loc",
        "authority": "tier2",
        "split_policy": "split_if_missing_eval",
        "role": "additional public Uyghur validation after normalization",
        "local_dir": "codemurt_uyghur_ner_dataset",
        "label_names": ["O", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"],
        "local_patterns": {
            "train": ["**/data/train*.parquet", "**/train*.parquet"],
            "extra": ["**/data/extra*.parquet", "**/extra*.parquet"],
            "validation": ["**/data/validation*.parquet", "**/validation*.parquet", "**/dev*.parquet"],
            "test": ["**/data/test*.parquet", "**/test*.parquet"],
        },
    },
]


class FetchTimeout(RuntimeError):
    pass


def _timeout_handler(_signum, _frame):
    raise FetchTimeout("dataset fetch exceeded the configured timeout")


class timeout_guard:
    def __init__(self, seconds):
        self.seconds = int(seconds or 0)
        self.previous = None

    def __enter__(self):
        if self.seconds > 0:
            self.previous = signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(self.seconds)

    def __exit__(self, exc_type, exc, tb):
        if self.seconds > 0:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, self.previous)
        return False


def load_hf_dataset(source, config):
    from datasets import load_dataset

    if config:
        return load_dataset(source, config)
    return load_dataset(source)


def plain_value(value):
    if hasattr(value, "tolist"):
        return plain_value(value.tolist())
    if isinstance(value, tuple):
        return [plain_value(item) for item in value]
    if isinstance(value, list):
        return [plain_value(item) for item in value]
    if isinstance(value, dict):
        return {key: plain_value(item) for key, item in value.items()}
    return value


def read_parquet_records(paths):
    import pandas as pd

    rows = []
    for path in paths:
        frame = pd.read_parquet(path)
        for record in frame.to_dict("records"):
            rows.append({key: plain_value(value) for key, value in record.items()})
    return rows


def dedupe_paths(paths):
    seen = set()
    unique = []
    for path in paths:
        resolved = str(path.resolve())
        if resolved not in seen:
            unique.append(path)
            seen.add(resolved)
    return unique


def local_search_roots(raw_root, spec):
    raw_root = Path(raw_root)
    preferred = raw_root / spec["local_dir"]
    if preferred.exists():
        return [preferred]
    return [raw_root] if raw_root.exists() else []


def load_local_download(raw_root, spec):
    split_paths = {}
    for root in local_search_roots(raw_root, spec):
        for split, patterns in spec["local_patterns"].items():
            matches = []
            for pattern in patterns:
                matches.extend(root.glob(pattern))
            matches = dedupe_paths([path for path in matches if path.is_file()])
            if matches:
                split_paths.setdefault(split, []).extend(matches)

    split_paths = {split: dedupe_paths(paths) for split, paths in split_paths.items()}
    if not split_paths:
        raise FileNotFoundError(
            f"No local parquet files found for {spec['dataset_id']} under {Path(raw_root) / spec['local_dir']}"
        )

    raw = {}
    for split, paths in split_paths.items():
        raw[split] = read_parquet_records(paths)
    local_files = {split: [str(path) for path in paths] for split, paths in split_paths.items()}
    return raw, local_files


def first_label_names(raw_splits, tags_field=None):
    for split in raw_splits.values():
        names = infer_label_names(split, tags_field)
        if names:
            return names
    return None


def normalize_splits(raw_splits, split_policy, seed):
    normalized = {}
    for split, records in raw_splits.items():
        split_name = SPLIT_ALIASES.get(split, split)
        normalized[split_name] = list(records)

    has_eval = "dev" in normalized and "test" in normalized
    if split_policy == "split_if_missing_eval" and not has_eval:
        merged = []
        for rows in normalized.values():
            merged.extend(rows)
        return split_single_records(merged, seed)
    return normalized


def convert_one(spec, seed, timeout_seconds=0, raw_root=None):
    attempts = [(spec["source"], spec["config"])] + spec.get("fallbacks", [])
    errors = []
    raw = None
    source_name = None
    local_files = None
    if raw_root:
        try:
            raw, local_files = load_local_download(raw_root, spec)
            source_name = f"local:{Path(raw_root) / spec['local_dir']}"
        except Exception as exc:
            errors.append(
                {
                    "source": f"local:{Path(raw_root) / spec['local_dir']}",
                    "config": "",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "traceback_tail": traceback.format_exc(limit=2),
                }
            )
    for source, config in attempts:
        if raw is not None:
            break
        try:
            with timeout_guard(timeout_seconds):
                raw = load_hf_dataset(source, config)
            source_name = f"{source}/{config}" if config else source
            break
        except Exception as exc:
            errors.append(
                {
                    "source": source,
                    "config": config,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "traceback_tail": traceback.format_exc(limit=2),
                }
            )
    if raw is None:
        return {
            "dataset_id": spec["dataset_id"],
            "status": "failed",
            "output_dir": str(spec["output_dir"]),
            "authority": spec["authority"],
            "role": spec["role"],
            "errors": errors,
        }

    label_names = first_label_names(raw) or spec.get("label_names")
    raw_by_split = normalize_splits(raw, spec["split_policy"], seed)
    converted = {}
    for split, records in raw_by_split.items():
        converted[split] = convert_records(
            list(records),
            split,
            spec["dataset_id"],
            label_names=label_names,
        )

    for required in ("train", "dev", "test"):
        converted.setdefault(required, [])

    output_dir = spec["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    for split in ("train", "dev", "test"):
        write_json(output_dir / f"{split}.json", converted[split])
    write_reports(output_dir, spec["dataset_id"], source_name, converted)

    return {
        "dataset_id": spec["dataset_id"],
        "status": "done",
        "source_name": source_name,
        "output_dir": str(output_dir),
        "authority": spec["authority"],
        "role": spec["role"],
        "splits": {split: len(converted[split]) for split in ("train", "dev", "test")},
        "local_files": local_files,
        "errors": errors,
    }


def existing_status(spec):
    output_dir = spec["output_dir"]
    exists = all((output_dir / f"{split}.json").exists() for split in ("train", "dev", "test"))
    return {
        "dataset_id": spec["dataset_id"],
        "status": "exists" if exists else "missing",
        "output_dir": str(output_dir),
        "authority": spec["authority"],
        "role": spec["role"],
    }


def write_status(results):
    REPORTS.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "results": results,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Public Uyghur Fetch Status v17",
        "",
        f"- Generated: {payload['generated']}",
        "- Purpose: fetch and normalize real public Uyghur NER datasets for paper validation.",
        "",
        "| Dataset | Authority | Status | Role | Output |",
        "|---|---|---|---|---|",
    ]
    for row in results:
        lines.append(
            f"| {row['dataset_id']} | {row['authority']} | {row['status']} | {row['role']} | `{row['output_dir']}` |"
        )
    lines.extend(["", "## Notes", ""])
    for row in results:
        if row.get("errors"):
            lines.append(f"### {row['dataset_id']}")
            for err in row["errors"]:
                lines.append(
                    f"- `{err['source']}` config `{err['config']}` failed with `{err['error_type']}`: {err['error']}"
                )
            lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(OUT_MD)
    print(OUT_JSON)


def main():
    parser = argparse.ArgumentParser(description="Fetch and normalize public Uyghur NER datasets for v17 validation.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dry_run", action="store_true", help="Only report whether normalized files already exist.")
    parser.add_argument("--timeout_seconds", type=int, default=60, help="Maximum seconds to spend loading each HF dataset attempt.")
    parser.add_argument("--dataset", choices=[spec["dataset_id"] for spec in DATASETS], action="append")
    parser.add_argument(
        "--raw_root",
        default="",
        help="Optional local download root. Expected subdirs: wikiann_ug/ and codemurt_uyghur_ner_dataset/.",
    )
    args = parser.parse_args()

    selected = DATASETS
    if args.dataset:
        selected = [spec for spec in DATASETS if spec["dataset_id"] in set(args.dataset)]

    results = []
    for spec in selected:
        if args.dry_run:
            results.append(existing_status(spec))
        else:
            results.append(
                convert_one(
                    spec,
                    args.seed,
                    timeout_seconds=args.timeout_seconds,
                    raw_root=args.raw_root or None,
                )
            )
    write_status(results)


if __name__ == "__main__":
    main()
