import csv
import random
import statistics
import time
from pathlib import Path

from neo4j import GraphDatabase


# ============================================================
# CONFIGURATION
# ============================================================

URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = ""

DATABASE = "neo4j"

PROJECT_ROOT = Path(
    r"C:\Users\Lenovo\Documents\wexa-cognodb-benchmark"
)

NODES_FILE = (
    PROJECT_ROOT
    / "data"
    / "benchmark"
    / "nodes.csv"
)

RESULTS_DIR = PROJECT_ROOT / "results"

OUTPUT_FILE = (
    RESULTS_DIR
    / "neo4j_query_benchmark.csv"
)

RANDOM_SEED = 42

RANDOM_NODES = 100

WARMUP_RUNS = 10

BENCHMARK_RUNS = 100


# ============================================================
# QUERIES
# ============================================================

QUERIES = {

    "1_hop": """
        MATCH (u:User {id: $node_id})
              -[:FRIEND]->(friend:User)
        RETURN friend.id AS node_id
    """,

    "2_hop": """
        MATCH (u:User {id: $node_id})
              -[:FRIEND]->()
              -[:FRIEND]->(friend:User)
        RETURN DISTINCT friend.id AS node_id
    """,

    "3_hop": """
        MATCH (u:User {id: $node_id})
              -[:FRIEND]->()
              -[:FRIEND]->()
              -[:FRIEND]->(friend:User)
        RETURN DISTINCT friend.id AS node_id
    """,

    "point_lookup": """
        MATCH (u:User {id: $node_id})
        RETURN u.id, u.gender, u.age
    """,

    "indexed_lookup": """
        MATCH (u:User)
        WHERE u.id = $node_id
        RETURN u.id
    """,

    "aggregation": """
        MATCH (u:User)
        RETURN u.gender AS gender,
               count(*) AS user_count
        ORDER BY gender
    """
}


# ============================================================
# READ NODE IDs
# ============================================================

def get_random_nodes():

    print("\nReading node IDs from:")

    print(NODES_FILE)

    node_ids = []

    with open(
        NODES_FILE,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        print(
            f"CSV header: "
            f"{reader.fieldnames}"
        )

        for row in reader:

            node_ids.append(
                int(row["node_id"])
            )

    print(
        f"\nTotal available nodes : "
        f"{len(node_ids):,}"
    )

    random.seed(RANDOM_SEED)

    selected = random.sample(
        node_ids,
        RANDOM_NODES
    )

    print(
        f"Random benchmark nodes : "
        f"{len(selected):,}"
    )

    print(
        f"Random seed            : "
        f"{RANDOM_SEED}"
    )

    return selected


# ============================================================
# EXECUTE ONE QUERY
# ============================================================

def execute_query(
    session,
    query,
    node_id=None
):

    start = time.perf_counter()

    result = session.run(
        query,
        node_id=node_id
    )

    records = list(result)

    elapsed = (
        time.perf_counter() - start
    ) * 1000

    return elapsed, len(records)


# ============================================================
# STATISTICS
# ============================================================

def percentile(values, percentile):

    sorted_values = sorted(values)

    index = (
        percentile / 100
    ) * (len(sorted_values) - 1)

    lower = int(index)

    upper = min(
        lower + 1,
        len(sorted_values) - 1
    )

    weight = index - lower

    return (
        sorted_values[lower]
        * (1 - weight)
        +
        sorted_values[upper]
        * weight
    )


# ============================================================
# BENCHMARK WORKLOAD
# ============================================================

def run_workload(
    session,
    workload_name,
    query,
    node_ids
):

    print("\n" + "=" * 60)

    print(
        f"WORKLOAD: "
        f"{workload_name}"
    )

    print("=" * 60)

    print(
        f"Warm-up runs: "
        f"{WARMUP_RUNS}"
    )

    print(
        f"Benchmark runs: "
        f"{BENCHMARK_RUNS}"
    )

    # --------------------------------------------------------
    # Warm-up
    # --------------------------------------------------------

    for i in range(WARMUP_RUNS):

        node_id = (
            node_ids[
                i % len(node_ids)
            ]
            if workload_name != "aggregation"
            else None
        )

        execute_query(
            session,
            query,
            node_id
        )

    # --------------------------------------------------------
    # Benchmark
    # --------------------------------------------------------

    latencies = []

    result_rows = []

    for i in range(BENCHMARK_RUNS):

        node_id = (
            node_ids[
                i % len(node_ids)
            ]
            if workload_name != "aggregation"
            else None
        )

        elapsed, rows = execute_query(
            session,
            query,
            node_id
        )

        latencies.append(
            elapsed
        )

        result_rows.append(
            rows
        )

        if (
            (i + 1) % 10 == 0
        ):

            print(
                f"Completed "
                f"{i + 1}/{BENCHMARK_RUNS}"
            )

    p50 = percentile(
        latencies,
        50
    )

    p95 = percentile(
        latencies,
        95
    )

    mean = statistics.mean(
        latencies
    )

    median_rows = statistics.median(
        result_rows
    )

    print("\nResults:")

    print(
        f"p50          : "
        f"{p50:.3f} ms"
    )

    print(
        f"p95          : "
        f"{p95:.3f} ms"
    )

    print(
        f"Mean         : "
        f"{mean:.3f} ms"
    )

    print(
        f"Median rows  : "
        f"{median_rows}"
    )

    return {
        "workload": workload_name,
        "p50_ms": p50,
        "p95_ms": p95,
        "mean_ms": mean,
        "median_rows": median_rows
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)

    print(
        "WEXA AI - NEO4J QUERY BENCHMARK"
    )

    print("=" * 60)

    print("\nConnecting to Neo4j...")

    driver = GraphDatabase.driver(
        URI,
        auth=(
            USERNAME,
            PASSWORD
        )
    )

    try:

        driver.verify_connectivity()

        print(
            "Neo4j connection: OK"
        )

        print(
            f"Iterations: "
            f"{BENCHMARK_RUNS}"
        )

        print(
            f"Warm-up: "
            f"{WARMUP_RUNS}"
        )

        # ----------------------------------------------------
        # Select benchmark nodes
        # ----------------------------------------------------

        node_ids = get_random_nodes()

        results = []

        # ----------------------------------------------------
        # Run workloads
        # ----------------------------------------------------

        with driver.session(
            database=DATABASE
        ) as session:

            for workload_name, query in QUERIES.items():

                result = run_workload(
                    session,
                    workload_name,
                    query,
                    node_ids
                )

                results.append(
                    result
                )

        # ----------------------------------------------------
        # Save results
        # ----------------------------------------------------

        RESULTS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            OUTPUT_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "workload",
                    "p50_ms",
                    "p95_ms",
                    "mean_ms",
                    "median_rows"
                ]
            )

            writer.writeheader()

            writer.writerows(
                results
            )

        # ----------------------------------------------------
        # Final summary
        # ----------------------------------------------------

        print("\n" + "=" * 75)

        print(
            "NEO4J QUERY BENCHMARK SUMMARY"
        )

        print("=" * 75)

        print(
            f"{'Workload':<20}"
            f"{'p50(ms)':>12}"
            f"{'p95(ms)':>12}"
            f"{'Mean(ms)':>14}"
        )

        print("-" * 60)

        for result in results:

            print(
                f"{result['workload']:<20}"
                f"{result['p50_ms']:>12.3f}"
                f"{result['p95_ms']:>12.3f}"
                f"{result['mean_ms']:>14.3f}"
            )

        print("\nResults saved to:")

        print(OUTPUT_FILE)

        print("\n" + "=" * 60)

        print(
            "NEO4J QUERY BENCHMARK COMPLETE"
        )

        print("=" * 60)

    finally:

        driver.close()


if __name__ == "__main__":
    main()
