import os
import csv
import random
import statistics
import time
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# CONFIGURATION
# ============================================================

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


if not URI or not USERNAME or not PASSWORD:
    raise RuntimeError(
        "Missing Neo4j environment variables. "
        "Check your .env file."
    )


RANDOM_SEED = 42
RANDOM_NODES = 100
WARMUP_RUNS = 10
BENCHMARK_RUNS = 100