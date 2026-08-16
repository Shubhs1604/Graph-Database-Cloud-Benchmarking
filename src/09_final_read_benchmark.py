from neo4j import GraphDatabase
from pathlib import Path
import random
import statistics
import time
import csv


# ============================================================
# CONFIGURATION
# ============================================================

URI = "bolt+s://db-a2703f17.databases.cognodb.com"
USERNAME = "cognodb"
PASSWORD = ""

ITERATIONS = 100
WARMUP_RUNS = 10
RANDOM_SEED = 42


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

NODES_FILE = (
    PROJECT_ROOT
    / "data"
    / "benchmark"
    / "nodes.csv"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
)

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


OUTPUT_FILE = (
    RESULTS_DIR
    / "cognodb_final_read_benchmark.csv"
)


# ============================================================
# QUERIES
# ============================================================

QUERIES = {

    # --------------------------------------------------------
    # 1-HOP
    # --------------------------------------------------------

    "1_hop": """
        MATCH (u:User {id: $node_id})
              -[:FRIEND]->
              (friend)
        RETURN friend.id AS id
    """,

    # --------------------------------------------------------
    # 2-HOP
    # --------------------------------------------------------

    "2_hop": """
        MATCH (u:User {id: $node_id})
              -[:FRIEND]->
              (f1)
              -[:FRIEND]->
              (f2)
        RETURN DISTINCT f2.id AS id
    """,

    # --------------------------------------------------------
    # 3-HOP
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # POINT LOOKUP
    # --------------------------------------------------------

    "point_lookup": """
        MATCH (u:User {id: $node_id})
        RETURN u.id AS id
    """,

    # --------------------------------------------------------
    # INDEXED LOOKUP
    # --------------------------------------------------------

    "indexed_lookup": """
        MATCH (u:User {id: $node_id})
        RETURN
            u.id AS id,
            u.gender AS gender,
            u.age AS age
    """,

    # --------------------------------------------------------
    # AGGREGATION
    # --------------------------------------------------------

    "aggregation": """
        MATCH (u:User)
        RETURN
            u.gender AS gender,
            count(*) AS total
        ORDER BY gender
    """
}


# ============================================================
# PERCENTILE FUNCTION
# ============================================================

def percentile(values, p):

    values = sorted(values)

    if not values:
        return 0.0

    position = (
        (len(values) - 1)
        * p
        / 100
    )

    lower = int(position)

    upper = min(
        lower + 1,
        len(values) - 1
    )

    fraction = position - lower

    return (
        values[lower]
        +
        (
            values[upper]
            -
            values[lower]
        )
        * fraction
    )


# ============================================================
# LOAD RANDOM NODE IDS FROM LOCAL CSV
# ============================================================

def get_random_nodes():

    print()
    print(
        "Reading node IDs from:"
    )
    print(NODES_FILE)

    if not NODES_FILE.exists():

        raise FileNotFoundError(
            f"\nNodes file not found:\n"
            f"{NODES_FILE}"
        )

    node_ids = []

    with open(
        NODES_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        # Skip CSV header
        header = next(file).strip()

        print(
            f"CSV header: {header}"
        )

        for line in file:

            line = line.strip()

            if not line:
                continue

            # nodes.csv:
            # node_id,gender,age

            parts = line.split(",")

            if len(parts) < 1:
                continue

            try:

                node_id = int(
                    parts[0]
                )

                node_ids.append(
                    node_id
                )

            except ValueError:

                continue

    if len(node_ids) < ITERATIONS:

        raise RuntimeError(
            f"Only {len(node_ids)} valid "
            f"nodes found. Need at least "
            f"{ITERATIONS}."
        )

    # Reproducible random selection
    random.seed(
        RANDOM_SEED
    )

    selected_nodes = random.sample(
        node_ids,
        ITERATIONS
    )

    print()
    print(
        f"Total available nodes : "
        f"{len(node_ids):,}"
    )

    print(
        f"Random benchmark nodes : "
        f"{len(selected_nodes):,}"
    )

    print(
        f"Random seed            : "
        f"{RANDOM_SEED}"
    )

    return selected_nodes


# ============================================================
# EXECUTE QUERY
# ============================================================

def execute_query(
    driver,
    query,
    node_id=None
):

    start_time = (
        time.perf_counter()
    )

    with driver.session() as session:

        if node_id is None:

            result = session.run(
                query
            )

        else:

            result = session.run(
                query,
                node_id=node_id
            )

        records = list(result)

    end_time = (
        time.perf_counter()
    )

    elapsed_ms = (
        end_time
        - start_time
    ) * 1000

    return (
        elapsed_ms,
        len(records)
    )


# ============================================================
# BENCHMARK NORMAL QUERY
# ============================================================

def benchmark_query(
    driver,
    workload,
    query,
    node_ids
):

    print()
    print("=" * 60)
    print(
        f"WORKLOAD: {workload}"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # WARM-UP
    # --------------------------------------------------------

    print(
        f"Warm-up runs: "
        f"{WARMUP_RUNS}"
    )

    for i in range(
        WARMUP_RUNS
    ):

        node_id = node_ids[
            i % len(node_ids)
        ]

        execute_query(
            driver,
            query,
            node_id
        )

    # --------------------------------------------------------
    # ACTUAL BENCHMARK
    # --------------------------------------------------------

    print(
        f"Benchmark runs: "
        f"{ITERATIONS}"
    )

    latencies = []
    row_counts = []

    for i in range(
        ITERATIONS
    ):

        node_id = node_ids[i]

        latency_ms, rows = (
            execute_query(
                driver,
                query,
                node_id
            )
        )

        latencies.append(
            latency_ms
        )

        row_counts.append(
            rows
        )

        if (
            (i + 1) % 10 == 0
        ):

            print(
                f"Completed "
                f"{i + 1}/{ITERATIONS}"
            )

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    result = {

        "workload":
            workload,

        "iterations":
            ITERATIONS,

        "warmup_runs":
            WARMUP_RUNS,

        "min_ms":
            min(latencies),

        "max_ms":
            max(latencies),

        "mean_ms":
            statistics.mean(
                latencies
            ),

        "p50_ms":
            percentile(
                latencies,
                50
            ),

        "p95_ms":
            percentile(
                latencies,
                95
            ),

        "avg_result_rows":
            statistics.mean(
                row_counts
            )
    }

    return result


# ============================================================
# AGGREGATION BENCHMARK
# ============================================================

def benchmark_aggregation(
    driver
):

    print()
    print("=" * 60)
    print(
        "WORKLOAD: aggregation"
    )
    print("=" * 60)

    query = QUERIES[
        "aggregation"
    ]

    # --------------------------------------------------------
    # WARM-UP
    # --------------------------------------------------------

    print(
        f"Warm-up runs: "
        f"{WARMUP_RUNS}"
    )

    for _ in range(
        WARMUP_RUNS
    ):

        execute_query(
            driver,
            query
        )

    # --------------------------------------------------------
    # ACTUAL BENCHMARK
    # --------------------------------------------------------

    print(
        f"Benchmark runs: "
        f"{ITERATIONS}"
    )

    latencies = []
    row_counts = []

    for i in range(
        ITERATIONS
    ):

        latency_ms, rows = (
            execute_query(
                driver,
                query
            )
        )

        latencies.append(
            latency_ms
        )

        row_counts.append(
            rows
        )

        if (
            (i + 1) % 10 == 0
        ):

            print(
                f"Completed "
                f"{i + 1}/{ITERATIONS}"
            )

    return {

        "workload":
            "aggregation",

        "iterations":
            ITERATIONS,

        "warmup_runs":
            WARMUP_RUNS,

        "min_ms":
            min(latencies),

        "max_ms":
            max(latencies),

        "mean_ms":
            statistics.mean(
                latencies
            ),

        "p50_ms":
            percentile(
                latencies,
                50
            ),

        "p95_ms":
            percentile(
                latencies,
                95
            ),

        "avg_result_rows":
            statistics.mean(
                row_counts
            )
    }


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(
    results
):

    fieldnames = [

        "workload",

        "iterations",

        "warmup_runs",

        "min_ms",

        "max_ms",

        "mean_ms",

        "p50_ms",

        "p95_ms",

        "avg_result_rows"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            results
        )


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(
    results
):

    print()
    print("=" * 75)
    print(
        "FINAL READ BENCHMARK SUMMARY"
    )
    print("=" * 75)

    print(
        f"{'Workload':<22}"
        f"{'p50(ms)':>12}"
        f"{'p95(ms)':>12}"
        f"{'Mean(ms)':>14}"
    )

    print("-" * 60)

    for result in results:

        print(
            f"{result['workload']:<22}"
            f"{result['p50_ms']:>12.3f}"
            f"{result['p95_ms']:>12.3f}"
            f"{result['mean_ms']:>14.3f}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print(
        "WEXA AI - FINAL COGNODB READ BENCHMARK"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # CREATE DRIVER
    # --------------------------------------------------------

    driver = GraphDatabase.driver(
        URI,
        auth=(
            USERNAME,
            PASSWORD
        )
    )

    try:

        # ----------------------------------------------------
        # TEST CONNECTION
        # ----------------------------------------------------

        driver.verify_connectivity()

        print()
        print(
            "CognoDB connection: OK"
        )

        print(
            f"Iterations: "
            f"{ITERATIONS}"
        )

        print(
            f"Warm-up: "
            f"{WARMUP_RUNS}"
        )

        # ----------------------------------------------------
        # SELECT RANDOM NODES LOCALLY
        # ----------------------------------------------------

        print()
        print(
            "Selecting random benchmark nodes..."
        )

        # IMPORTANT:
        # No driver argument here.
        #
        # This fixes:
        #
        # TypeError:
        # get_random_nodes() takes 0 positional
        # arguments but 1 was given

        node_ids = (
            get_random_nodes()
        )

        # ----------------------------------------------------
        # RUN BENCHMARKS
        # ----------------------------------------------------

        results = []

        workloads = [

            "1_hop",

            "2_hop",

            "3_hop",

            "point_lookup",

            "indexed_lookup"
        ]

        for workload in workloads:

            result = benchmark_query(

                driver,

                workload,

                QUERIES[
                    workload
                ],

                node_ids
            )

            results.append(
                result
            )

        # ----------------------------------------------------
        # AGGREGATION
        # ----------------------------------------------------

        aggregation_result = (
            benchmark_aggregation(
                driver
            )
        )

        results.append(
            aggregation_result
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        save_results(
            results
        )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        print_summary(
            results
        )

        # ----------------------------------------------------
        # OUTPUT LOCATION
        # ----------------------------------------------------

        print()
        print(
            "Results saved to:"
        )

        print(
            OUTPUT_FILE
        )

        print()
        print("=" * 60)
        print(
            "FINAL READ BENCHMARK COMPLETE"
        )
        print("=" * 60)

    finally:

        driver.close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
