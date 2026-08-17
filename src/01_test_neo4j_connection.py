import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


if not URI or not USERNAME or not PASSWORD:
    raise RuntimeError(
        "Missing Neo4j environment variables. "
        "Check your .env file."
    )


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

        with driver.session(database=DATABASE) as session:

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