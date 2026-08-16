from pathlib import Path
import random
import csv


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "soc-pokec-relationships.txt"
)

BENCHMARK_DIR = PROJECT_ROOT / "data" / "benchmark"

OUTPUT_FILE = BENCHMARK_DIR / "relationships.csv"


# ============================================================
# CONFIGURATION
# ============================================================

TARGET_RELATIONSHIPS = 300_000

# Fixed seed = reproducible dataset
RANDOM_SEED = 42


# ============================================================
# RESERVOIR SAMPLING
# ============================================================

def create_sample():

    print("=" * 60)
    print("WEXA AI - REPRODUCIBLE POKEC SAMPLING")
    print("=" * 60)

    if not RAW_FILE.exists():
        print("\nERROR: Raw dataset not found:")
        print(RAW_FILE)
        return

    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)

    random.seed(RANDOM_SEED)

    reservoir = []

    total_valid_lines = 0

    print("\nReading raw dataset...")
    print("This may take a little while because the file is ~404 MB.\n")

    with open(
        RAW_FILE,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as infile:

        for line in infile:

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            if len(parts) < 2:
                continue

            source = parts[0]
            target = parts[1]

            total_valid_lines += 1

            relationship = (source, target)

            # Fill reservoir first
            if len(reservoir) < TARGET_RELATIONSHIPS:

                reservoir.append(relationship)

            else:

                # Reservoir sampling
                random_index = random.randint(
                    0,
                    total_valid_lines - 1
                )

                if random_index < TARGET_RELATIONSHIPS:

                    reservoir[random_index] = relationship

    print("\nRaw valid relationships found:")
    print(f"{total_valid_lines:,}")

    print("\nSample size:")
    print(f"{len(reservoir):,}")

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    unique_relationships = list(set(reservoir))

    print("\nAfter duplicate removal:")
    print(f"{len(unique_relationships):,}")

    # ========================================================
    # WRITE CSV
    # ========================================================

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as outfile:

        writer = csv.writer(outfile)

        writer.writerow(
            ["source_id", "target_id"]
        )

        for source, target in unique_relationships:

            writer.writerow(
                [source, target]
            )

    # ========================================================
    # SUMMARY
    # ========================================================

    unique_nodes = set()

    for source, target in unique_relationships:

        unique_nodes.add(source)
        unique_nodes.add(target)

    print("\n" + "=" * 60)
    print("FINAL SAMPLE")
    print("=" * 60)

    print(
        f"Relationships : {len(unique_relationships):,}"
    )

    print(
        f"Unique nodes  : {len(unique_nodes):,}"
    )

    print(
        f"Output file   : {OUTPUT_FILE}"
    )

    print(
        f"Random seed   : {RANDOM_SEED}"
    )

    print("\nSampling completed successfully.")


if __name__ == "__main__":
    create_sample()