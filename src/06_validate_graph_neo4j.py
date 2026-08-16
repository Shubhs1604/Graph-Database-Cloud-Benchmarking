from neo4j import GraphDatabase


URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = ""


def main():

    print("=" * 60)
    print("WEXA AI - FINAL NEO4J GRAPH VALIDATION")
    print("=" * 60)

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        driver.verify_connectivity()

        with driver.session(database="neo4j") as session:

            # Total nodes
            result = session.run("""
                MATCH (u:User)
                RETURN count(u) AS total_nodes
            """).single()

            total_nodes = result["total_nodes"]

            # Total relationships
            result = session.run("""
                MATCH ()-[r:FRIEND]->()
                RETURN count(r) AS total_relationships
            """).single()

            total_relationships = result["total_relationships"]

            # Self-loops
            result = session.run("""
                MATCH (a:User)-[r:FRIEND]->(b:User)
                WHERE a.id = b.id
                RETURN count(r) AS self_loops
            """).single()

            self_loops = result["self_loops"]

            # Duplicate relationships
            result = session.run("""
                MATCH (a:User)-[:FRIEND]->(b:User)
                WITH a.id AS source, b.id AS target, count(*) AS cnt
                WHERE cnt > 1
                RETURN sum(cnt - 1) AS duplicates
            """).single()

            duplicates = result["duplicates"] or 0

            # Relationships with invalid endpoints
            result = session.run("""
                MATCH (a)-[r:FRIEND]->(b)
                WHERE NOT a:User OR NOT b:User
                RETURN count(r) AS invalid_relationships
            """).single()

            invalid_relationships = result["invalid_relationships"]

            print()
            print(f"Total nodes              : {total_nodes:,}")
            print(f"Total relationships      : {total_relationships:,}")
            print(f"Self-loop relationships  : {self_loops:,}")
            print(f"Duplicate relationships  : {duplicates:,}")
            print(f"Invalid relationships    : {invalid_relationships:,}")

            print("\n" + "=" * 60)

            if (
                total_nodes == 397769
                and total_relationships == 300000
                and self_loops == 0
                and duplicates == 0
                and invalid_relationships == 0
            ):
                print("VALIDATION RESULT")
                print("NEO4J GRAPH VALIDATION PASSED")
            else:
                print("VALIDATION RESULT")
                print("NEO4J GRAPH VALIDATION FAILED")

            print("=" * 60)

    finally:
        driver.close()


if __name__ == "__main__":
    main()
