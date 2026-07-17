#!/usr/bin/env python3
"""Aggregate the released per-query family-source sensitivity table."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results/diagnostics/reference_family_source_per_query.tsv"


def main() -> None:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["family_source"]].append(row)
    if set(grouped) != {
        "controlled_relation",
        "public_metadata_title",
        "public_text_cluster",
    }:
        raise RuntimeError(f"unexpected family sources: {sorted(grouped)}")
    for family_source in sorted(grouped):
        members = grouped[family_source]
        if len(members) != 1686:
            raise RuntimeError(f"{family_source}: expected 1686 rows, got {len(members)}")
        values = [
            sum(float(row[field]) for row in members) / len(members)
            for field in ["recall_at_3", "hsr_at_3", "cleanhit_at_3"]
        ]
        print(f"{family_source}\t{len(members)}\t" + "\t".join(f"{v:.6f}" for v in values))


if __name__ == "__main__":
    main()
