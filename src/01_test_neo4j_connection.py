from neo4j import GraphDatabase


URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"

# Put your Neo4j password here locally.
# DO NOT share it with me or commit it to GitHub.
PASSWORD = "Shubhu@7666"


def main():
    print("=" * 60)
    print("WEXA AI - NEO4J CONNECTION TEST")
    print("=" * 60)

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:
        driver.verify_connectivity()
        print("\nNeo4j connection: SUCCESS")

        with driver.session(database="neo4j") as session:
            result = session.run("RETURN 1 AS test")
            record = result.single()

            print(f"Test query result: {record['test']}")

            result = session.run(
                "MATCH (n) RETURN count(n) AS nodes"
            )
            record = result.single()

            print(f"Current node count: {record['nodes']}")

        print("\n" + "=" * 60)
        print("NEO4J CONNECTION TEST PASSED")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print("NEO4J CONNECTION TEST FAILED")
        print("=" * 60)
        print("\nError:")
        print(e)

    finally:
        driver.close()


if __name__ == "__main__":
    main()