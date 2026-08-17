import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

BENCHMARK_NODE = int(
    os.getenv("BENCHMARK_NODE", "1891")
)


# ============================================================
# VALIDATE ENVIRONMENT VARIABLES
# ============================================================

if not URI:
    raise RuntimeError(
        "Missing COGNODB_URI in .env"
    )

if not USERNAME:
    raise RuntimeError(
        "Missing COGNODB_USERNAME in .env"
    )

if not PASSWORD:
    raise RuntimeError(
        "Missing COGNODB_PASSWORD in .env"
    )


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
# EXPLAIN ONE QUERY
# ============================================================

def explain_query(
    session,
    query_name,
    query,
    node_id
):

    print("\n")
    print("=" * 70)
    print(f"QUERY PLAN: {query_name}")
    print("=" * 70)

    explain_query_text = (
        "EXPLAIN " + query
    )

    try:

        result = session.run(
            explain_query_text,
            node_id=node_id
        )

        summary = result.consume()

        plan = summary.plan

        if plan is None:

            print(
                "\nNo execution plan returned."
            )

            return

        print("\nExecution Plan:")
        print("-" * 70)

        print(plan)

    except Exception as e:

        print("\nQuery plan analysis failed.")

        print(
            f"\nError: {e}"
        )


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
        f"Connecting to: "
        f"{URI}"
    )

    driver = GraphDatabase.driver(
        URI,
        auth=(
            USERNAME,
            PASSWORD
        )
    )

    try:

        # ----------------------------------------------------
        # Verify connection
        # ----------------------------------------------------

        driver.verify_connectivity()

        print(
            "\nCognoDB connection: OK"
        )

        # ----------------------------------------------------
        # Open session
        # ----------------------------------------------------

        with driver.session() as session:

            # ------------------------------------------------
            # Verify benchmark node
            # ------------------------------------------------

            result = session.run(
                """
                MATCH (u:User {id: $node_id})
                RETURN u.id AS id
                """,
                node_id=BENCHMARK_NODE
            )

            record = result.single()

            if record is None:

                raise RuntimeError(
                    f"Benchmark node "
                    f"{BENCHMARK_NODE} "
                    f"was not found in CognoDB."
                )

            print(
                f"Benchmark node {BENCHMARK_NODE}: FOUND"
            )

            # ------------------------------------------------
            # Explain all queries
            # ------------------------------------------------

            for query_name, query in QUERIES.items():

                explain_query(
                    session,
                    query_name,
                    query,
                    BENCHMARK_NODE
                )

        print("\n" + "=" * 70)

        print(
            "QUERY PLAN ANALYSIS COMPLETE"
        )

        print("=" * 70)

    except Exception as e:

        print("\n" + "=" * 70)

        print(
            "COGNODB QUERY PLAN ANALYSIS FAILED"
        )

        print("=" * 70)

        print(
            f"\nError: {e}"
        )

    finally:

        driver.close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()