from neo4j import GraphDatabase


URI = "bolt+s://db-a2703f17.databases.cognodb.com"
USERNAME = "cognodb"
PASSWORD = ""


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

        with driver.session() as session:

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
            # 5. RELATIONSHIPS WITH MISSING SOURCE/TARGET
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

            print("\n✅ GRAPH VALIDATION PASSED")

        else:

            print("\n⚠️ GRAPH VALIDATION NEEDS REVIEW")

        print("=" * 60)

    finally:

        driver.close()


if __name__ == "__main__":
    main()
