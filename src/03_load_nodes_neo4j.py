import csv
import time
from neo4j import GraphDatabase


URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = ""

NODES_FILE = r"C:\Users\Lenovo\Documents\wexa-cognodb-benchmark\data\benchmark\nodes.csv"

BATCH_SIZE = 5000


def load_nodes(driver):

    print("=" * 60)
    print("WEXA AI - NEO4J NODE LOADER")
    print("=" * 60)

    print("\nInput file:")
    print(NODES_FILE)

    start_time = time.time()
    total_loaded = 0

    with open(
        NODES_FILE,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        batch = []

        with driver.session(database="neo4j") as session:

            for row in reader:

                batch.append({
                    "id": int(row["node_id"]),
                    "gender": int(row["gender"]),
                    "age": int(row["age"])
                })

                if len(batch) >= BATCH_SIZE:

                    session.run(
                        """
                        UNWIND $rows AS row

                        MERGE (u:User {id: row.id})

                        SET
                            u.gender = row.gender,
                            u.age = row.age
                        """,
                        rows=batch
                    ).consume()

                    total_loaded += len(batch)

                    print(f"Nodes loaded: {total_loaded:,}")

                    batch.clear()

            # Load remaining rows
            if batch:

                session.run(
                    """
                    UNWIND $rows AS row

                    MERGE (u:User {id: row.id})

                    SET
                        u.gender = row.gender,
                        u.age = row.age
                    """,
                    rows=batch
                ).consume()

                total_loaded += len(batch)

                print(f"Nodes loaded: {total_loaded:,}")

    elapsed = time.time() - start_time

    print("\n" + "=" * 60)
    print("NODE LOAD COMPLETE")
    print("=" * 60)

    print(f"Total nodes loaded : {total_loaded:,}")
    print(f"Time taken         : {elapsed:.2f} seconds")

    if elapsed > 0:
        print(
            f"Throughput         : "
            f"{total_loaded / elapsed:,.0f} nodes/sec"
        )


def main():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        driver.verify_connectivity()

        print("Connected to Neo4j.")

        load_nodes(driver)

    finally:

        driver.close()


if __name__ == "__main__":
    main()
