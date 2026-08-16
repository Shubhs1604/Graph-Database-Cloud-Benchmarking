from neo4j import GraphDatabase
from pathlib import Path
import csv
import time


# ============================================================
# CONFIGURATION
# ============================================================

URI = "bolt+s://db-a2703f17.databases.cognodb.com"
USERNAME = "cognodb"
PASSWORD = ""

BATCH_SIZE = 5_000


# ============================================================
# FILE PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

NODES_FILE = (
    PROJECT_ROOT
    / "data"
    / "benchmark"
    / "nodes.csv"
)


# ============================================================
# LOAD NODES
# ============================================================

def load_nodes(driver):

    print("=" * 60)
    print("WEXA AI - COGNODB NODE LOADER")
    print("=" * 60)

    print(f"\nInput file:")
    print(NODES_FILE)

    if not NODES_FILE.exists():

        raise FileNotFoundError(
            f"File not found:\n{NODES_FILE}"
        )

    total_loaded = 0
    start_time = time.perf_counter()

    with open(
        NODES_FILE,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        batch = []

        for row in reader:

            batch.append(
                {
                    "id": int(row["node_id"]),
                    "gender": int(row["gender"]),
                    "age": int(row["age"])
                }
            )

            if len(batch) >= BATCH_SIZE:

                load_batch(driver, batch)

                total_loaded += len(batch)

                print(
                    f"Nodes loaded: "
                    f"{total_loaded:,}"
                )

                batch.clear()

        # Load remaining rows
        if batch:

            load_batch(driver, batch)

            total_loaded += len(batch)

            print(
                f"Nodes loaded: "
                f"{total_loaded:,}"
            )

    elapsed = time.perf_counter() - start_time

    print("\n" + "=" * 60)
    print("NODE LOAD COMPLETE")
    print("=" * 60)

    print(
        f"Total nodes loaded : "
        f"{total_loaded:,}"
    )

    print(
        f"Time taken         : "
        f"{elapsed:.2f} seconds"
    )

    if elapsed > 0:

        print(
            f"Throughput         : "
            f"{total_loaded / elapsed:,.0f} nodes/sec"
        )


# ============================================================
# LOAD ONE BATCH
# ============================================================

def load_batch(driver, batch):

    query = """
    UNWIND $nodes AS node

    MERGE (u:User {id: node.id})

    SET
        u.gender = node.gender,
        u.age = node.age
    """

    with driver.session() as session:

        session.run(
            query,
            nodes=batch
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

        load_nodes(driver)

    finally:

        driver.close()


if __name__ == "__main__":
    main()
