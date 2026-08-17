import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

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


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("WEXA AI - NEO4J NODE VERIFICATION")
    print("=" * 60)

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        driver.verify_connectivity()

        with driver.session(database=DATABASE) as session:

            # ------------------------------------------------
            # Total nodes
            # ------------------------------------------------

            result = session.run("""
                MATCH (u:User)
                RETURN count(u) AS total_nodes
            """).single()

            total_nodes = result["total_nodes"]

            # ------------------------------------------------
            # Nodes with ID
            # ------------------------------------------------

            result = session.run("""
                MATCH (u:User)
                WHERE u.id IS NOT NULL
                RETURN count(u) AS nodes_with_id
            """).single()

            nodes_with_id = result["nodes_with_id"]

            # ------------------------------------------------
            # Unique IDs
            # ------------------------------------------------

            result = session.run("""
                MATCH (u:User)
                WHERE u.id IS NOT NULL
                RETURN count(DISTINCT u.id) AS unique_ids
            """).single()

            unique_ids = result["unique_ids"]

            # ------------------------------------------------
            # Relationships
            # ------------------------------------------------

            result = session.run("""
                MATCH ()-[r]->()
                RETURN count(r) AS relationships
            """).single()

            relationships = result["relationships"]

            # ------------------------------------------------
            # Results
            # ------------------------------------------------

            print(f"\nTotal User nodes       : {total_nodes:,}")
            print(f"Nodes with ID          : {nodes_with_id:,}")
            print(f"Unique IDs             : {unique_ids:,}")
            print(f"Relationships          : {relationships:,}")

            print("\n" + "=" * 60)

            if (
                total_nodes == 397769
                and nodes_with_id == 397769
                and unique_ids == 397769
                and relationships == 0
            ):
                print("NODE VERIFICATION PASSED")
            else:
                print("NODE VERIFICATION FAILED")

            print("=" * 60)

    finally:

        driver.close()


if __name__ == "__main__":
    main()