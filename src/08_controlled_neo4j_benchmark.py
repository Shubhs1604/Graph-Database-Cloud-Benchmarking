import os
import csv
import statistics
import time
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
# NEO4J CONFIGURATION
# ============================================================

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


if not URI:
    raise RuntimeError(
        "Missing NEO4J_URI in .env file."
    )

if not USERNAME:
    raise RuntimeError(
        "Missing NEO4J_USERNAME in .env file."
    )

if not PASSWORD:
    raise RuntimeError(
        "Missing NEO4J_PASSWORD in .env file."
    )


# ============================================================
# BENCHMARK CONFIGURATION
# ============================================================

BENCHMARK_NODE = 1891

WARMUP_RUNS = 10

BENCHMARK_RUNS = 100


# ============================================================
# RESULTS
# ============================================================

RESULTS_DIR = PROJECT_ROOT / "results"

OUTPUT_FILE = (
    RESULTS_DIR
    / "neo4j_controlled_benchmark.csv"
)


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
    """
}


# ============================================================
# PERCENTILE
# ============================================================

def percentile(values, p):

    values = sorted(values)

    if not values:
        return 0.0

    index = (
        (p / 100)
        * (len(values) - 1)
    )

    lower = int(index)

    upper = min(
        lower + 1,
        len(values) - 1
    )

    weight = index - lower

    return (
        values[lower] * (1 - weight)
        +
        values[upper] * weight
    )


# ============================================================
# RUN ONE QUERY
# ============================================================

def run_query(session, query):

    start = time.perf_counter()

    result = session.run(
        query,
        node_id=BENCHMARK_NODE
    )

    # Consume the complete result.
    records = list(result)

    elapsed = (
        time.perf_counter() - start
    ) * 1000

    return elapsed, len(records)


# ============================================================
# BENCHMARK ONE WORKLOAD
# ============================================================

def benchmark_workload(
    session,
    workload,
    query
):

    print("\n" + "=" * 60)

    print(
        f"WORKLOAD: {workload}"
    )

    print("=" * 60)

    print(
        f"Benchmark node: "
        f"{BENCHMARK_NODE}"
    )

    print(
        f"Warm-up runs: "
        f"{WARMUP_RUNS}"
    )

    print(
        f"Benchmark runs: "
        f"{BENCHMARK_RUNS}"
    )


    # ========================================================
    # WARM-UP
    # ========================================================

    print("\nRunning warm-up...")

    for _ in range(WARMUP_RUNS):

        run_query(
            session,
            query
        )


    # ========================================================
    # BENCHMARK
    # ========================================================

    print("\nRunning benchmark...")

    latencies = []

    row_counts = []


    for i in range(BENCHMARK_RUNS):

        elapsed, rows = run_query(
            session,
            query
        )

        latencies.append(
            elapsed
        )

        row_counts.append(
            rows
        )


        if (i + 1) % 10 == 0:

            print(
                f"Completed "
                f"{i + 1}/{BENCHMARK_RUNS}"
            )


    # ========================================================
    # STATISTICS
    # ========================================================

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
        row_counts
    )


    # ========================================================
    # PRINT RESULTS
    # ========================================================

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

        "workload": workload,

        "benchmark_node": BENCHMARK_NODE,

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
        "WEXA AI - CONTROLLED NEO4J BENCHMARK"
    )

    print("=" * 60)


    print(
        f"\nBenchmark node: "
        f"{BENCHMARK_NODE}"
    )

    print(
        f"Iterations: "
        f"{BENCHMARK_RUNS}"
    )

    print(
        f"Warm-up: "
        f"{WARMUP_RUNS}"
    )


    # ========================================================
    # CONNECTION
    # ========================================================

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


        # ====================================================
        # OPEN SESSION
        # ====================================================

        with driver.session(
            database=DATABASE
        ) as session:


            # ================================================
            # VERIFY BENCHMARK NODE
            # ================================================

            print(
                "\nChecking benchmark node..."
            )


            result = session.run(
                """
                MATCH (u:User {id: $node_id})

                RETURN
                    u.id AS id,
                    u.gender AS gender,
                    u.age AS age
                """,
                node_id=BENCHMARK_NODE
            )


            record = result.single()


            if record is None:

                raise RuntimeError(
                    f"Benchmark node "
                    f"{BENCHMARK_NODE} "
                    f"does not exist."
                )


            print(
                "\nBenchmark node found:"
            )

            print(
                f"ID     : "
                f"{record['id']}"
            )

            print(
                f"Gender : "
                f"{record['gender']}"
            )

            print(
                f"Age    : "
                f"{record['age']}"
            )


            # ================================================
            # RUN WORKLOADS
            # ================================================

            results = []


            for workload, query in QUERIES.items():

                result = benchmark_workload(
                    session,
                    workload,
                    query
                )

                results.append(
                    result
                )


        # ====================================================
        # CREATE RESULTS DIRECTORY
        # ====================================================

        RESULTS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )


        # ====================================================
        # SAVE CSV
        # ====================================================

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
                    "benchmark_node",
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


        # ====================================================
        # FINAL SUMMARY
        # ====================================================

        print(
            "\n"
            + "=" * 75
        )

        print(
            "CONTROLLED NEO4J BENCHMARK SUMMARY"
        )

        print(
            "=" * 75
        )


        print(
            f"{'Workload':<15}"
            f"{'Rows':>10}"
            f"{'p50(ms)':>14}"
            f"{'p95(ms)':>14}"
            f"{'Mean(ms)':>14}"
        )


        print(
            "-" * 67
        )


        for result in results:

            print(
                f"{result['workload']:<15}"
                f"{result['median_rows']:>10.0f}"
                f"{result['p50_ms']:>14.3f}"
                f"{result['p95_ms']:>14.3f}"
                f"{result['mean_ms']:>14.3f}"
            )


        print(
            "\nResults saved to:"
        )

        print(
            OUTPUT_FILE
        )


        print(
            "\n"
            + "=" * 60
        )

        print(
            "CONTROLLED NEO4J BENCHMARK COMPLETE"
        )

        print(
            "=" * 60
        )


    except Exception as e:

        print(
            "\n"
            + "=" * 60
        )

        print(
            "NEO4J BENCHMARK FAILED"
        )

        print(
            "=" * 60
        )

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