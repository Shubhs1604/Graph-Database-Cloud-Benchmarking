from neo4j import GraphDatabase
import os


URI = "bolt+s://db-a2703f17.databases.cognodb.com"
USERNAME = "cognodb"
# Removed hard-coded password. Read from environment variable instead.
PASSWORD = os.environ.get("COGNODB_PASSWORD")
if not PASSWORD:
    raise EnvironmentError(
        "Environment variable COGNODB_PASSWORD is not set. Hard-coded passwords have been removed."
    )


def main():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        driver.verify_connectivity()

        print("=" * 60)
        print("COGNODB SMOKE TEST")
        print("=" * 60)

        with driver.session() as session:

            # ------------------------------------------------
            # 1. Create two temporary users
            # ------------------------------------------------

            session.run(
                """
                CREATE (a:User {id: 999999001, name: 'Test User A'})
                CREATE (b:User {id: 999999002, name: 'Test User B'})
                CREATE (a)-[:FRIEND]->(b)
                """
            )

            print("Test graph created.")

            # ------------------------------------------------
            # 2. Query the nodes
            # ------------------------------------------------

            result = session.run(
                """
                MATCH (u:User)
                WHERE u.id IN [999999001, 999999002]
                RETURN u.id AS id, u.name AS name
                ORDER BY u.id
                """
            )

            print("\nNodes:")

            for record in result:

                print(
                    f"ID={record['id']}, "
                    f"Name={record['name']}"
                )

            # ------------------------------------------------
            # 3. Query the relationship
            # ------------------------------------------------

            result = session.run(
                """
                MATCH (a:User {id: 999999001})
                      -[r:FRIEND]->
                      (b:User {id: 999999002})
                RETURN a.id AS source,
                       type(r) AS relationship,
                       b.id AS target
                """
            )

            record = result.single()

            print("\nRelationship:")

            print(
                f"{record['source']} "
                f"-[{record['relationship']}]-> "
                f"{record['target']}"
            )

            # ------------------------------------------------
            # 4. Cleanup test data
            # ------------------------------------------------

            session.run(
                """
                MATCH (u:User)
                WHERE u.id IN [999999001, 999999002]
                DETACH DELETE u
                """
            )

            print("\nTest data removed.")

        print("\n" + "=" * 60)
        print("COGNODB SMOKE TEST PASSED")
        print("=" * 60)

    finally:

        driver.close()


if __name__ == "__main__":
    main()
