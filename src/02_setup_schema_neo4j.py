from neo4j import GraphDatabase


URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = ""


def main():

    print("=" * 60)
    print("WEXA AI - NEO4J SCHEMA SETUP")
    print("=" * 60)

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:
        driver.verify_connectivity()

        with driver.session(database="neo4j") as session:

            print("\nCreating User ID index...")

            session.run("""
                CREATE INDEX user_id_index IF NOT EXISTS
                FOR (u:User)
                ON (u.id)
            """).consume()

            print("Index creation command completed.")

            print("\nCurrent indexes:")

            result = session.run("SHOW INDEXES")

            for record in result:
                print(
                    f"{record['name']} | "
                    f"{record['type']} | "
                    f"{record['state']}"
                )

        print("\n" + "=" * 60)
        print("SCHEMA SETUP COMPLETE")
        print("=" * 60)

    except Exception as e:
        print("\nSchema setup failed:")
        print(e)

    finally:
        driver.close()


if __name__ == "__main__":
    main()
