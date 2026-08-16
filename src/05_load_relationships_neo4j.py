import csv
import time
from neo4j import GraphDatabase


URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = ""

RELATIONSHIPS_FILE = (
    r"C:\Users\Lenovo\Documents\wexa-cognodb-benchmark"
    r"\data\benchmark\relationships.csv"
)

BATCH_SIZE = 5000


def load_relationships(driver):

    print("=" * 60)
    print("WEXA AI - NEO4J RELATIONSHIP LOADER")
    print("=" * 60)

    print("\nInput file:")
    print(RELATIONSHIPS_FILE)

    start_time = time.time()
    total_loaded = 0

    with open(
        RELATIONSHIPS_FILE,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        print(f"CSV columns: {reader.fieldnames}")

        batch = []

        with driver.session(database="neo4j") as session:

            for row in reader:

                batch.append({
                    "source": int(row["source_id"]),
                    "target": int(row["target_id"])
                })

                if len(batch) >= BATCH_SIZE:

                    session.run(
                        """
                        UNWIND $rows AS row

                        MATCH (source:User {id: row.source})
                        MATCH (target:User {id: row.target})

                        MERGE (source)-[:FRIEND]->(target)
                        """,
                        rows=batch
                    ).consume()

                    total_loaded += len(batch)

                    print(
                        f"Relationships loaded: "
                        f"{total_loaded:,}"
                    )

                    batch.clear()

            if batch:

                session.run(
                    """
                    UNWIND $rows AS row

                    MATCH (source:User {id: row.source})
                    MATCH (target:User {id: row.target})

                    MERGE (source)-[:FRIEND]->(target)
                    """,
                    rows=batch
                ).consume()

                total_loaded += len(batch)

                print(
                    f"Relationships loaded: "
                    f"{total_loaded:,}"
                )

    elapsed = time.time() - start_time

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


def main():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        driver.verify_connectivity()

        print("Connected to Neo4j.")

        load_relationships(driver)

    finally:

        driver.close()


if __name__ == "__main__":
    main()
