from neo4j import GraphDatabase
from pathlib import Path
import csv
import time


# ============================================================
# CONFIGURATION
# ============================================================

URI = "bolt+s://db-a2703f17.databases.cognodb.com"
USERNAME = "cognodb"
PASSWORD = "dd030ff05a0acc853644b780d4f39df2"

BATCH_SIZE = 5_000


# ============================================================
# FILE PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RELATIONSHIPS_FILE = (
    PROJECT_ROOT
    / "data"
    / "benchmark"
    / "relationships.csv"
)


# ============================================================
# LOAD RELATIONSHIPS
# ============================================================

def load_relationships(driver):

    print("=" * 60)
    print("WEXA AI - COGNODB RELATIONSHIP LOADER")
    print("=" * 60)

    print("\nInput file:")
    print(RELATIONSHIPS_FILE)

    if not RELATIONSHIPS_FILE.exists():

        raise FileNotFoundError(
            f"File not found:\n{RELATIONSHIPS_FILE}"
        )

    total_loaded = 0
    start_time = time.perf_counter()

    with open(
        RELATIONSHIPS_FILE,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        batch = []

        for row in reader:

            batch.append(
                {
                    "source": int(row["source_id"]),
                    "target": int(row["target_id"])
                }
            )

            if len(batch) >= BATCH_SIZE:

                load_batch(driver, batch)

                total_loaded += len(batch)

                print(
                    f"Relationships loaded: "
                    f"{total_loaded:,}"
                )

                batch.clear()

        # Remaining rows
        if batch:

            load_batch(driver, batch)

            total_loaded += len(batch)

            print(
                f"Relationships loaded: "
                f"{total_loaded:,}"
            )

    elapsed = time.perf_counter() - start_time

    print("\n" + "=" * 60)
    print("RELATIONSHIP LOAD COMPLETE")
    print("=" * 60)

    print(
        f"Total relationships : "
        f"{total_loaded:,}"
    )

    print(
        f"Time taken          : "
        f"{elapsed:.2f} seconds"
    )

    if elapsed > 0:

        print(
            f"Throughput          : "
            f"{total_loaded / elapsed:,.0f} "
            f"relationships/sec"
        )


# ============================================================
# LOAD ONE BATCH
# ============================================================

def load_batch(driver, batch):

    query = """
    UNWIND $relationships AS rel

    MATCH (source:User {id: rel.source})
    MATCH (target:User {id: rel.target})

    CREATE (source)-[:FRIEND]->(target)
    """

    with driver.session() as session:

        session.run(
            query,
            relationships=batch
        ).consume()


# ============================================================
# MAIN
# ============================================================

def main():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        driver.verify_connectivity()

        print("Connected to CognoDB.")

        load_relationships(driver)

    finally:

        driver.close()


if __name__ == "__main__":
    main()