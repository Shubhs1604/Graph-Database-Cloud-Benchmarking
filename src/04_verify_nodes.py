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
        print("WEXA AI - COGNODB NODE VERIFICATION")
        print("=" * 60)

        with driver.session() as session:

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
            # Count nodes with properties
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

        print("\n" + "=" * 60)

        if (
            node_count == 397769
            and nodes_with_id == 397769
            and relationship_count == 0
            and duplicate_ids == 0
        ):

            print("NODE VERIFICATION PASSED ✅")

        else:

            print("NODE VERIFICATION NEEDS REVIEW ⚠️")

        print("=" * 60)

    finally:

        driver.close()


if __name__ == "__main__":
    main()
