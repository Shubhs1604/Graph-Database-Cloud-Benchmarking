import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")
DATABASE = os.getenv("COGNODB_DATABASE")


if not URI or not USERNAME or not PASSWORD:
    raise RuntimeError(
        "Missing CognoDB environment variables. "
        "Check your .env file."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("WEXA AI - COGNODB NODE VERIFICATION")
    print("=" * 60)

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        driver.verify_connectivity()

        print("\nCognoDB connection: SUCCESS")

        # Use database only if specified
        if DATABASE:
            session = driver.session(database=DATABASE)
        else:
            session = driver.session()

        with session:

            # ------------------------------------------------
            # Count total User nodes
            # ------------------------------------------------

            result = session.run(
                """
                MATCH (u:User)
                RETURN count(u) AS node_count
                """
            )

            node_count = result.single()["node_count"]

            print(
                f"\nTotal User nodes : "
                f"{node_count:,}"
            )

            # ------------------------------------------------
            # Count nodes with IDs
            # ------------------------------------------------

            result = session.run(
                """
                MATCH (u:User)
                WHERE u.id IS NOT NULL
                RETURN count(u) AS nodes_with_id
                """
            )

            nodes_with_id = result.single()["nodes_with_id"]

            print(
                f"Nodes with ID    : "
                f"{nodes_with_id:,}"
            )

            # ------------------------------------------------
            # Count relationships
            # ------------------------------------------------

            result = session.run(
                """
                MATCH ()-[r]->()
                RETURN count(r) AS relationship_count
                """
            )

            relationship_count = (
                result.single()["relationship_count"]
            )

            print(
                f"Relationships     : "
                f"{relationship_count:,}"
            )

            # ------------------------------------------------
            # Check duplicate IDs
            # ------------------------------------------------

            result = session.run(
                """
                MATCH (u:User)
                WITH u.id AS id, count(*) AS cnt
                WHERE cnt > 1
                RETURN count(*) AS duplicate_ids
                """
            )

            duplicate_ids = (
                result.single()["duplicate_ids"]
            )

            print(
                f"Duplicate IDs     : "
                f"{duplicate_ids:,}"
            )

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        print("\n" + "=" * 60)

        if (
            node_count == 397769
            and nodes_with_id == 397769
            and relationship_count == 0
            and duplicate_ids == 0
        ):

            print("NODE VERIFICATION PASSED")

        else:

            print("NODE VERIFICATION NEEDS REVIEW")

        print("=" * 60)

    finally:

        driver.close()


if __name__ == "__main__":
    main()