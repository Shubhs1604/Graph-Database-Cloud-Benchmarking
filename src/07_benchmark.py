from neo4j import GraphDatabase
from pathlib import Path
import statistics
import time
import csv


# ============================================================
# CONFIGURATION
# ============================================================

URI = "bolt+s://db-a2703f17.databases.cognodb.com"
USERNAME = "cognodb"
PASSWORD = "dd030ff05a0acc853644b780d4f39df2"

RUNS = 20

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_DIR = PROJECT_ROOT / "results"

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# BENCHMARK QUERIES
# ============================================================

QUERIES = {

    "1_hop": """
        MATCH (u:User {id: $node_id})
              -[:FRIEND]->
              (friend)
        RETURN friend.id AS id
    """,

    "2_hop": """
        MATCH (u:User {id: $node_id})
              -[:FRIEND]->
              (f1)
              -[:FRIEND]->
              (f2)
        RETURN DISTINCT f2.id AS id
    """,

    "3_hop": """
        MATCH (u:User {id: $node_id})
              -[:FRIEND]->
              (f1)
              -[:FRIEND]->
              (f2)
              -[:FRIEND]->
              (f3)
        RETURN DISTINCT f3.id AS id
    """,

    "indexed_lookup": """
        MATCH (u:User {id: $node_id})
        RETURN u.id AS id,
               u.gender AS gender,
               u.age AS age
    """
}


# ============================================================
# SELECT BENCHMARK NODE
# ============================================================

def get_benchmark_node(driver):

    query = """
        MATCH (u:User)
        WHERE u.id = 1891
        RETURN u.id AS id
    """

    with driver.session() as session:

        record = session.run(query).single()

        if record is None:

            raise RuntimeError(
                "Benchmark node 1891 was not found."
            )

        return record["id"]


# ============================================================
# RUN ONE QUERY
# ============================================================

def run_query(
    driver,
    query,
    node_id
):

    start = time.perf_counter()

    with driver.session() as session:

        result = session.run(
            query,
            node_id=node_id
        )

        # Consume the complete result.
        records = list(result)

    end = time.perf_counter()

    latency_ms = (
        end - start
    ) * 1000

    return latency_ms, len(records)


# ============================================================
# PERCENTILE
# ============================================================

def percentile(
    values,
    percentile_value
):

    values = sorted(values)

    if not values:

        return None

    index = (
        (len(values) - 1)
        * percentile_value
        / 100
    )

    lower = int(index)

    upper = min(
        lower + 1,
        len(values) - 1
    )

    fraction = index - lower

    return (
        values[lower]
        + (
            values[upper]
            - values[lower]
        )
        * fraction
    )


# ============================================================
# BENCHMARK ONE WORKLOAD
# ============================================================

def benchmark_workload(
    driver,
    workload_name,
    query,
    node_id
):

    print(
        f"\nRunning: {workload_name}"
    )

    latencies = []

    result_rows = []

    for run_number in range(
        1,
        RUNS + 1
    ):

        latency_ms, rows = run_query(
            driver,
            query,
            node_id
        )

        latencies.append(
            latency_ms
        )

        result_rows.append(
            rows
        )

        print(
            f"  Run {run_number:02d}: "
            f"{latency_ms:.3f} ms "
            f"({rows} rows)"
        )

    return {
        "workload": workload_name,
        "node_id": node_id,
        "runs": RUNS,
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "mean_ms": statistics.mean(latencies),
        "p50_ms": percentile(
            latencies,
            50
        ),
        "p95_ms": percentile(
            latencies,
            95
        ),
        "avg_result_rows": statistics.mean(
            result_rows
        )
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("WEXA AI - COGNODB QUERY BENCHMARK")
    print("=" * 60)

    driver = GraphDatabase.driver(
        URI,
        auth=(
            USERNAME,
            PASSWORD
        )
    )

    results = []

    try:

        driver.verify_connectivity()

        print(
            "\nCognoDB connection: OK"
        )

        node_id = get_benchmark_node(
            driver
        )

        print(
            f"Benchmark node: "
            f"{node_id}"
        )

        # ----------------------------------------------------
        # Run workloads
        # ----------------------------------------------------

        for workload_name, query in QUERIES.items():

            result = benchmark_workload(
                driver,
                workload_name,
                query,
                node_id
            )

            results.append(result)

        # ----------------------------------------------------
        # Save results
        # ----------------------------------------------------

        output_file = (
            RESULTS_DIR
            / "benchmark_results.csv"
        )

        with open(
            output_file,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            fieldnames = [
                "workload",
                "node_id",
                "runs",
                "min_ms",
                "max_ms",
                "mean_ms",
                "p50_ms",
                "p95_ms",
                "avg_result_rows"
            ]

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()

            writer.writerows(
                results
            )

        # ----------------------------------------------------
        # Print summary
        # ----------------------------------------------------

        print("\n")
        print("=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)

        for result in results:

            print(
                f"\n{result['workload']}"
            )

            print(
                f"  p50 : "
                f"{result['p50_ms']:.3f} ms"
            )

            print(
                f"  p95 : "
                f"{result['p95_ms']:.3f} ms"
            )

            print(
                f"  mean: "
                f"{result['mean_ms']:.3f} ms"
            )

        print("\n")
        print(
            f"Results saved to:\n"
            f"{output_file}"
        )

        print("\n" + "=" * 60)
        print("BENCHMARK COMPLETE")
        print("=" * 60)

    finally:

        driver.close()


if __name__ == "__main__":

    main()