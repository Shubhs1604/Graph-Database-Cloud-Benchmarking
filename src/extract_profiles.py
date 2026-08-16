from pathlib import Path
import csv


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RELATIONSHIPS_FILE = (
    PROJECT_ROOT
    / "data"
    / "benchmark"
    / "relationships.csv"
)

PROFILES_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "soc-pokec-profiles.txt"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "benchmark"
    / "nodes.csv"
)


# ============================================================
# PROFILE COLUMNS
# ============================================================

# Based on the Pokec profile file structure we inspected:
#
# Column 0 = user_id
# Column 1 = gender
# Column 2 = age
#
# We will only use these three properties for the benchmark.


# ============================================================
# STEP 1: GET NODE IDS FROM RELATIONSHIPS
# ============================================================

def load_required_node_ids():

    print("=" * 60)
    print("STEP 1 - READING BENCHMARK RELATIONSHIPS")
    print("=" * 60)

    if not RELATIONSHIPS_FILE.exists():

        raise FileNotFoundError(
            f"Relationships file not found:\n"
            f"{RELATIONSHIPS_FILE}"
        )

    required_nodes = set()

    with open(
        RELATIONSHIPS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            source_id = row["source_id"]
            target_id = row["target_id"]

            required_nodes.add(source_id)
            required_nodes.add(target_id)

    print(
        f"Unique nodes required : {len(required_nodes):,}"
    )

    return required_nodes


# ============================================================
# STEP 2: EXTRACT PROFILES
# ============================================================

def extract_profiles(required_nodes):

    print("\n" + "=" * 60)
    print("STEP 2 - EXTRACTING POKEC PROFILES")
    print("=" * 60)

    if not PROFILES_FILE.exists():

        raise FileNotFoundError(
            f"Profile file not found:\n"
            f"{PROFILES_FILE}"
        )

    profiles_found = 0
    invalid_rows = 0

    # Keep track of IDs we found
    found_nodes = set()

    with open(
        PROFILES_FILE,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as infile, open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as outfile:

        writer = csv.writer(outfile)

        # CSV header
        writer.writerow(
            [
                "node_id",
                "gender",
                "age"
            ]
        )

        for line_number, line in enumerate(infile, start=1):

            line = line.rstrip("\n\r")

            if not line:
                continue

            # Pokec profile file is TAB separated
            parts = line.split("\t")

            # We need at least:
            # user_id
            # gender
            # age

            if len(parts) < 3:

                invalid_rows += 1
                continue

            user_id = parts[0].strip()
            gender = parts[1].strip()
            age = parts[2].strip()

            # Only keep users present in our benchmark graph
            if user_id not in required_nodes:
                continue

            # Prevent duplicate profiles
            if user_id in found_nodes:
                continue

            writer.writerow(
                [
                    user_id,
                    gender,
                    age
                ]
            )

            found_nodes.add(user_id)
            profiles_found += 1

            # Progress every 100,000 matching profiles
            if profiles_found % 100_000 == 0:

                print(
                    f"Profiles extracted: "
                    f"{profiles_found:,}"
                )

    return profiles_found, found_nodes, invalid_rows


# ============================================================
# STEP 3: REPORT MISSING PROFILES
# ============================================================

def report_results(
    required_nodes,
    found_nodes,
    profiles_found,
    invalid_rows
):

    missing_nodes = required_nodes - found_nodes

    print("\n" + "=" * 60)
    print("PROFILE EXTRACTION RESULTS")
    print("=" * 60)

    print(
        f"Graph nodes required     : "
        f"{len(required_nodes):,}"
    )

    print(
        f"Profiles found           : "
        f"{profiles_found:,}"
    )

    print(
        f"Profiles missing         : "
        f"{len(missing_nodes):,}"
    )

    print(
        f"Invalid profile rows     : "
        f"{invalid_rows:,}"
    )

    print(
        f"\nOutput file:"
    )

    print(OUTPUT_FILE)

    if len(missing_nodes) == 0:

        print(
            "\nSUCCESS: Profile found for every "
            "benchmark node."
        )

    else:

        print(
            "\nNOTE: Some graph nodes do not have "
            "matching profile records."
        )

        print(
            "We will handle those nodes explicitly "
            "in the benchmark."
        )

    print("\n" + "=" * 60)
    print("PROFILE EXTRACTION COMPLETE")
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

def main():

    required_nodes = load_required_node_ids()

    profiles_found, found_nodes, invalid_rows = (
        extract_profiles(required_nodes)
    )

    report_results(
        required_nodes,
        found_nodes,
        profiles_found,
        invalid_rows
    )


if __name__ == "__main__":
    main()