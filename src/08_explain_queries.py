import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# COGNODB CONFIGURATION
# ============================================================

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")
DATABASE = os.getenv("COGNODB_DATABASE")


# ============================================================
# VALIDATE ENVIRONMENT VARIABLES
# ============================================================

if not URI:
    raise RuntimeError(
        "Missing COGNODB_URI in .env file."
    )

if not USERNAME:
    raise RuntimeError(
        "Missing COGNODB_USERNAME in .env file."
    )

if not PASSWORD:
    raise RuntimeError(
        "Missing COGNODB_PASSWORD in .env file."
    )


# ============================================================
# BENCHMARK NODE
# ============================================================

BENCHMARK_NODE = 1891


# ============================================================
# QUERIES
# ============================================================

QUERIES = {

    "indexed_lookup": """
        MATCH (u:User {id: $node_id})
        RETURN u.id, u.gender, u.age
    """,

    "1_hop": """
        MATCH (u:User {id: $node_id})
              -[:FRIEND]->
              (friend)
        RETURN friend.id
    """,

    "2_hop": """
        MATCH (u:User {id: $node_id})
              -[:FRIEND]->
              (f1)
              -[:FRIEND]->
              (f2)
        RETURN DISTINCT f2.id
    """,

    "3_hop": """
        MATCH (u:User {id: $node_id})
              -[:FRIEND]->
              (f1)
              -[:FRIEND]->
              (f2)
              -[:FRIEND]->
              (f3)
        RETURN DISTINCT f3.id
    """
}


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("WEXA AI - COGNODB QUERY PLAN ANALYSIS")
    print("=" * 70)

    print(
        f"\nBenchmark node: "
        f"{BENCHMARK_NODE}"
    )

    print(
        f"Database: "
        f"{DATABASE}"
    )

    # ========================================================
    # CREATE DRIVER
    # ========================================================

    driver = GraphDatabase.driver(
        URI,
        auth=(
            USERNAME,
            PASSWORD
        )
    )

    try:

        # ====================================================
        # VERIFY CONNECTION
        # ====================================================

        driver.verify_connectivity()

        print(
            "\nCognoDB connection: OK"
        )

        # ====================================================
        # CREATE SESSION
        # ====================================================

        session_kwargs = {}

        if DATABASE:
            session_kwargs["database"] = DATABASE

        with driver.session(**session_kwargs) as session:

            # ================================================
            # RUN EXPLAIN FOR EACH QUERY
            # ================================================

            for name, query in QUERIES.items():

                print("\n")
                print("=" * 70)
                print(
                    f"QUERY: {name}"
                )
                print("=" * 70)

                print(
                    "\nCypher:"
                )

                print(
                    query.strip()
                )

                print(
                    "\nQuery plan:"
                )

                explain_query = (
                    "EXPLAIN "
                    + query
                )

                result = session.run(
                    explain_query,
                    node_id=BENCHMARK_NODE
                )

                summary = result.consume().plan

                print(
                    summary
                )

        # ====================================================
        # COMPLETE
        # ====================================================

        print("\n")
        print("=" * 70)
        print(
            "QUERY PLAN ANALYSIS COMPLETE"
        )
        print("=" * 70)

    except Exception as e:

        print("\n")
        print("=" * 70)
        print(
            "COGNODB QUERY PLAN ANALYSIS FAILED"
        )
        print("=" * 70)

        print(
            f"\nError:\n{e}"
        )

        raise

    finally:

        driver.close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()