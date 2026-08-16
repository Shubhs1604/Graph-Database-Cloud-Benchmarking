from pathlib import Path
import csv
from collections import Counter

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "benchmark" / "relationships.csv"


def validate_dataset():

    print("=" * 60)
    print("WEXA AI - DATASET VALIDATION")
    print("=" * 60)

    if not INPUT_FILE.exists():
        print(f"\nERROR: File not found:")
        print(INPUT_FILE)
        return

    total_rows = 0
    valid_rows = 0
    invalid_rows = 0

    unique_nodes = set()
    unique_relationships = set()

    duplicate_relationships = 0
    self_loops = 0

    source_counts = Counter()
    target_counts = Counter()

    with open(INPUT_FILE, "r", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for row in reader:

            total_rows += 1

            source = row.get("source_id")
            target = row.get("target_id")

            # Validate missing values
            if not source or not target:
                invalid_rows += 1
                continue

            valid_rows += 1

            # Track nodes
            unique_nodes.add(source)
            unique_nodes.add(target)

            # Track source/target frequency
            source_counts[source] += 1
            target_counts[target] += 1

            # Detect self-loop
            if source == target:
                self_loops += 1

            # Detect duplicate relationship
            relationship = (source, target)

            if relationship in unique_relationships:
                duplicate_relationships += 1
            else:
                unique_relationships.add(relationship)

    unique_sources = len(source_counts)
    unique_targets = len(target_counts)

    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)

    print(f"Total rows              : {total_rows:,}")
    print(f"Valid relationships     : {valid_rows:,}")
    print(f"Invalid rows            : {invalid_rows:,}")

    print(f"\nUnique nodes            : {len(unique_nodes):,}")
    print(f"Unique source nodes     : {unique_sources:,}")
    print(f"Unique target nodes     : {unique_targets:,}")

    print(f"\nDuplicate relationships : {duplicate_relationships:,}")
    print(f"Self-loop relationships : {self_loops:,}")

    print("\n" + "=" * 60)
    print("TOP 10 SOURCE NODES")
    print("=" * 60)

    for node, count in source_counts.most_common(10):
        print(f"{node:<15} {count:,} relationships")

    print("\n" + "=" * 60)
    print("TOP 10 TARGET NODES")
    print("=" * 60)

    for node, count in target_counts.most_common(10):
        print(f"{node:<15} {count:,} relationships")

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    validate_dataset()