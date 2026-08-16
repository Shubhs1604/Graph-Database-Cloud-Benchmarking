from neo4j import GraphDatabase


# ============================================================
# COGNODB CONNECTION
# ============================================================

URI = "bolt+s://db-a2703f17.databases.cognodb.com"
USERNAME = "cognodb"

# IMPORTANT:
# Replace this with the password shown/provided by CognoDB.
PASSWORD = "dd030ff05a0acc853644b780d4f39df2"


def test_connection():

    print("=" * 60)
    print("WEXA AI - COGNODB CONNECTION TEST")
    print("=" * 60)

    driver = None

    try:

        print("\nConnecting to CognoDB...")

        driver = GraphDatabase.driver(
            URI,
            auth=(USERNAME, PASSWORD)
        )

        # Verify that the database is reachable
        driver.verify_connectivity()

        print("Connection successful!")

        # Run a very small test query
        with driver.session() as session:

            result = session.run(
                "RETURN 1 AS test"
            )

            record = result.single()

            print(
                f"Test query result: {record['test']}"
            )

        print("\n" + "=" * 60)
        print("COGNODB CONNECTION TEST PASSED")
        print("=" * 60)

    except Exception as e:

        print("\n" + "=" * 60)
        print("COGNODB CONNECTION TEST FAILED")
        print("=" * 60)

        print(f"\nError:\n{e}")

    finally:

        if driver is not None:
            driver.close()


if __name__ == "__main__":
    test_connection()