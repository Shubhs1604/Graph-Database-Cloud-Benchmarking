import os
import csv
import time
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")
DATABASE = os.getenv("COGNODB_DATABASE")

BATCH_SIZE = 5_000


if not URI or not USERNAME or not PASSWORD:
    raise RuntimeError(
        "Missing CognoDB environment variables. "
        "Check your .env file."
    )


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

        print(f"CSV columns: {reader.fieldnames}")

        batch = []

        with driver.session(
            database=DATABASE
        ) if DATABASE else driver.session() as session:

            for row in reader:

                batch.append(
                    {
                        "source": int(row["source_id"]),
                        "target": int(row["target_id"])
                    }
                )

                if len(batch) >= BATCH_SIZE:

                    session.run(
                        """
                        UNWIND $relationships AS rel

                        MATCH (source:User {id: rel.source})
                        MATCH (target:User {id: rel.target})

                        CREATE (source)-[:FRIEND]->(target)
                        """,
                        relationships=batch
                    ).consume()

                    total_loaded += len(batch)

                    print(
                        f"Relationships loaded: "
                        f"{total_loaded:,}"
                    )

                    batch.clear()

            # ------------------------------------------------
            # Remaining rows
            # ------------------------------------------------

            if batch:

                session.run(
                    """
                    UNWIND $relationships AS rel

                    MATCH (source:User {id: rel.source})
                    MATCH (target:User {id: rel.target})

                    CREATE (source)-[:FRIEND]->(target)
                    """,
                    relationships=batch
                ).consume()

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