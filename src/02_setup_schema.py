from neo4j import GraphDatabase


URI = "bolt+s://db-a2703f17.databases.cognodb.com"
USERNAME = "cognodb"
PASSWORD = "dd030ff05a0acc853644b780d4f39df2"


def main():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:
        driver.verify_connectivity()

        with driver.session() as session:

            print("Creating User ID index...")

            session.run(
                """
                CREATE INDEX user_id_index IF NOT EXISTS
                FOR (u:User)
                ON (u.id)
                """
            )

            print("Index creation command completed.")

            result = session.run(
                """
                SHOW INDEXES
                """
            )

            print("\nCurrent indexes:")

            for record in result:
                print(
                    record.get("name"),
                    "|",
                    record.get("state"),
                    "|",
                    record.get("type")
                )

        print("\nSchema setup complete.")

    finally:
        driver.close()


if __name__ == "__main__":
    main()