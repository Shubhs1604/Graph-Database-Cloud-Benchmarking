from neo4j import GraphDatabase


URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = ""


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

        with driver.session(database="neo4j") as session:

            result = session.run("""
                MATCH (u:User)
                RETURN count(u) AS total_nodes
            """).single()

            total_nodes = result["total_nodes"]

            result = session.run("""
                MATCH (u:User)
                WHERE u.id IS NOT NULL
                RETURN count(u) AS nodes_with_id
            """).single()

            nodes_with_id = result["nodes_with_id"]

            result = session.run("""
                MATCH (u:User)
                WHERE u.id IS NOT NULL
                RETURN count(DISTINCT u.id) AS unique_ids
            """).single()

            unique_ids = result["unique_ids"]

            result = session.run("""
                MATCH ()-[r]->()
                RETURN count(r) AS relationships
            """).single()

            relationships = result["relationships"]

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
