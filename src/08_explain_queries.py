from neo4j import GraphDatabase


URI = "bolt+s://db-a2703f17.databases.cognodb.com"
USERNAME = "cognodb"
PASSWORD = ""


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


def main():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        driver.verify_connectivity()

        print("=" * 70)
        print("WEXA AI - COGNODB QUERY PLAN ANALYSIS")
        print("=" * 70)

        with driver.session() as session:

            for name, query in QUERIES.items():

                print("\n")
                print("=" * 70)
                print(f"QUERY: {name}")
                print("=" * 70)

                explain_query = "EXPLAIN " + query

                result = session.run(
                    explain_query,
                    node_id=1891
                )

                summary = result.consume().plan

                print(summary)

    finally:

        driver.close()


if __name__ == "__main__":
    main()
