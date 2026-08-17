import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


# ============================================================
# CONFIGURATION
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

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        driver.verify_connectivity()

        print("=" * 60)
        print("WEXA AI - FINAL GRAPH VALIDATION")
        print("=" * 60)

        session_kwargs = {}

        if DATABASE:
            session_kwargs["database"] = DATABASE

        with driver.session(**session_kwargs) as session:

            # ==================================================
            # 1. TOTAL NODES
            # ==================================================

            result = session.run(
                """
                MATCH (u:User)
                RETURN count(u) AS count
                """
            )

            node_count = result.single()["count"]

            print(
                f"\nTotal nodes         : "
                f"{node_count:,}"
            )

            # ==================================================
            # 2. TOTAL RELATIONSHIPS
            # ==================================================

            result = session.run(
                """
                MATCH ()-[r:FRIEND]->()
                RETURN count(r) AS count
                """
            )

            relationship_count = result.single()["count"]

            print(
                f"Total relationships : "
                f"{relationship_count:,}"
            )

            # ==================================================
            # 3. SELF LOOPS
            # ==================================================

            result = session.run(
                """
                MATCH (a:User)-[:FRIEND]->(a)
                RETURN count(*) AS count
                """
            )

            self_loops = result.single()["count"]

            print(
                f"Self-loop relationships : "
                f"{self_loops:,}"
            )

            # ==================================================
            # 4. DUPLICATE RELATIONSHIPS
            # ==================================================

            result = session.run(
                """
                MATCH (a:User)-[:FRIEND]->(b:User)
                WITH a.id AS source,
                     b.id AS target,
                     count(*) AS cnt
                WHERE cnt > 1
                RETURN coalesce(sum(cnt - 1), 0) AS duplicates
                """
            )

            duplicates = result.single()["duplicates"]

            print(
                f"Duplicate relationships : "
                f"{duplicates:,}"
            )

            # ==================================================
            # 5. RELATIONSHIPS WITH MISSING SOURCE/TARGET ID
            # ==================================================

            result = session.run(
                """
                MATCH (a:User)-[:FRIEND]->(b:User)
                WHERE a.id IS NULL OR b.id IS NULL
                RETURN count(*) AS count
                """
            )

            invalid_relationships = result.single()["count"]

            print(
                f"Invalid relationships   : "
                f"{invalid_relationships:,}"
            )

        # ======================================================
        # FINAL RESULT
        # ======================================================

        print("\n" + "=" * 60)
        print("VALIDATION RESULT")
        print("=" * 60)

        if (
            node_count == 397769
            and relationship_count == 300000
            and self_loops == 0
            and duplicates == 0
            and invalid_relationships == 0
        ):

            print("\nGRAPH VALIDATION PASSED")

        else:

            print("\nGRAPH VALIDATION NEEDS REVIEW")

        print("=" * 60)

    finally:

        driver.close()


if __name__ == "__main__":
    main()