import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")


if not URI or not USERNAME or not PASSWORD:
    raise RuntimeError(
        "Missing CognoDB environment variables. "
        "Check your .env file."
    )


def main():

    print("=" * 60)
    print("WEXA AI - COGNODB SCHEMA SETUP")
    print("=" * 60)

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:
        driver.verify_connectivity()

        with driver.session() as session:

            print("\nCreating User ID index...")

            session.run(
                """
                CREATE INDEX user_id_index IF NOT EXISTS
                FOR (u:User)
                ON (u.id)
                """
            ).consume()

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

        print("\n" + "=" * 60)
        print("COGNODB SCHEMA SETUP COMPLETE")
        print("=" * 60)

    finally:
        driver.close()


if __name__ == "__main__":
    main()