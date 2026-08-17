# Graph Database Cloud Benchmarking

A graph database benchmarking project designed to evaluate **CognoDB Cloud** against **Neo4j** using a real-world social-network dataset derived from the **Pokec Slovakian social network dataset**.

The project focuses on graph data ingestion, schema/index configuration, graph validation, traversal queries, query-plan analysis, and controlled performance benchmarking.

---

## 🚀 Project Overview

This project creates a reproducible graph benchmark containing:

* **397,769 unique User nodes**
* **300,000 FRIEND relationships**
* Zero duplicate relationships
* Zero self-loop relationships
* Zero invalid relationship endpoints

The same benchmark structure is used across:

* **CognoDB Cloud**
* **Neo4j**

The goal is to compare graph database behavior for common graph workloads such as:

* Indexed node lookup
* 1-hop traversal
* 2-hop traversal
* 3-hop traversal
* Query-plan analysis
* Controlled latency benchmarking

---

## 🏗️ Architecture

```text
Pokec Dataset
     │
     ├── soc-pokec-relationships.txt
     │
     └── soc-pokec-profiles.txt
              │
              ▼
       Data Preparation
              │
              ▼
      Benchmark Dataset
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
    Neo4j         CognoDB
       │             │
       └──────┬──────┘
              │
              ▼
       Graph Validation
              │
              ▼
       Query Benchmarking
              │
              ▼
       Performance Results
```

---

## 📊 Benchmark Dataset

The benchmark dataset was generated from the Pokec social-network data.

### Dataset statistics

| Metric                  |    Value |
| ----------------------- | -------: |
| Total User Nodes        |  397,769 |
| Total Relationships     |  300,000 |
| Relationship Type       | `FRIEND` |
| Self-loops              |        0 |
| Duplicate Relationships |        0 |
| Invalid Relationships   |        0 |

### Node properties

Each `User` node contains:

```text
User
 ├── id
 ├── gender
 └── age
```

Example:

```text
(:User {
    id: 1891,
    gender: 1,
    age: 25
})
```

### Relationship structure

```text
(User)-[:FRIEND]->(User)
```

Example:

```text
(1891)-[:FRIEND]->(2345)
```

---

## 🔍 Graph Model

The benchmark uses a simple social-network graph.

```text
        ┌────────────┐
        │   User     │
        │            │
        │ id         │
        │ gender     │
        │ age        │
        └─────┬──────┘
              │
           FRIEND
              │
              ▼
        ┌────────────┐
        │   User     │
        └────────────┘
```

This structure allows the benchmark to test graph traversal depth.

### 1-Hop

```text
User → Friend
```

### 2-Hop

```text
User → Friend → Friend
```

### 3-Hop

```text
User → Friend → Friend → Friend
```

---

## ⚡ Indexing

A `User` ID index is created for efficient node lookup.

```cypher
CREATE INDEX user_id_index IF NOT EXISTS
FOR (u:User)
ON (u.id)
```

This allows queries such as:

```cypher
MATCH (u:User {id: $node_id})
RETURN u.id, u.gender, u.age
```

The benchmark uses node ID `1891` as the controlled benchmark node.

---

## 📥 Data Loading

The loading process is divided into separate stages.

### Step 1 — Load Nodes

The node loader:

1. Reads `nodes.csv`
2. Processes records in batches
3. Uses `UNWIND`
4. Creates/updates `User` nodes
5. Stores `id`, `gender`, and `age`

Example:

```cypher
UNWIND $nodes AS node

MERGE (u:User {id: node.id})

SET
    u.gender = node.gender,
    u.age = node.age
```

Batch size:

```text
5,000 records
```

---

### Step 2 — Load Relationships

Relationships are loaded from:

```text
relationships.csv
```

The loader matches source and target nodes before creating the relationship.

```cypher
UNWIND $relationships AS rel

MATCH (source:User {id: rel.source})
MATCH (target:User {id: rel.target})

CREATE (source)-[:FRIEND]->(target)
```

This ensures relationships are connected to existing `User` nodes.

---

## 🧪 Graph Validation

After loading, the graph is validated using several checks.

### Node validation

Checks:

* Total nodes
* Nodes containing IDs
* Duplicate IDs
* Relationship count

### Relationship validation

Checks:

* Total relationships
* Self-loops
* Duplicate relationships
* Invalid endpoints

Expected result:

```text
Total nodes              : 397,769
Total relationships      : 300,000
Self-loop relationships  : 0
Duplicate relationships  : 0
Invalid relationships    : 0
```

Expected status:

```text
GRAPH VALIDATION PASSED
```

---

# 🔎 Query Benchmarking

The project benchmarks several graph workloads.

## 1. Indexed Lookup

Retrieves a single user by ID.

```cypher
MATCH (u:User {id: $node_id})
RETURN u.id, u.gender, u.age
```

This measures point lookup performance using the user ID index.

---

## 2. 1-Hop Traversal

Finds direct friends.

```cypher
MATCH (u:User {id: $node_id})
      -[:FRIEND]->
      (friend:User)
RETURN friend.id
```

Conceptually:

```text
1891
 │
 ├── Friend A
 ├── Friend B
 └── Friend C
```

---

## 3. 2-Hop Traversal

Finds friends-of-friends.

```cypher
MATCH (u:User {id: $node_id})
      -[:FRIEND]->
      ()
      -[:FRIEND]->
      (friend:User)
RETURN DISTINCT friend.id
```

Conceptually:

```text
1891
 │
 ├── A
 │    ├── C
 │    └── D
 │
 └── B
      ├── E
      └── F
```

---

## 4. 3-Hop Traversal

Finds nodes three relationships away.

```cypher
MATCH (u:User {id: $node_id})
      -[:FRIEND]->
      ()
      -[:FRIEND]->
      ()
      -[:FRIEND]->
      (friend:User)
RETURN DISTINCT friend.id
```

Conceptually:

```text
User
 │
 └── Friend
      │
      └── Friend
           │
           └── Friend
```

---

# 📈 Controlled Benchmark

To make the comparison more consistent, the project includes a controlled Neo4j benchmark.

### Benchmark configuration

```text
Benchmark node : 1891
Warm-up runs   : 10
Benchmark runs : 100
```

For each workload, the benchmark calculates:

* p50 latency
* p95 latency
* Mean latency
* Median result rows

### Why p50 and p95?

**p50** represents typical query latency.

**p95** shows the latency experienced by slower queries and helps identify performance variability.

---

## 🔬 Query Plan Analysis

The project also uses Cypher `EXPLAIN` to inspect query execution plans.

Example:

```cypher
EXPLAIN
MATCH (u:User {id: $node_id})
      -[:FRIEND]->
      (friend)
RETURN friend.id
```

This helps analyze how the database plans:

* Node lookup
* Index usage
* Relationship expansion
* Graph traversal

---

# 🗂️ Project Structure

```text
Graph-Database-Cloud-Benchmarking/
│
├── data/
│   ├── raw/
│   │   ├── soc-pokec-profiles.txt
│   │   └── soc-pokec-relationships.txt
│   │
│   └── benchmark/
│       ├── nodes.csv
│       └── relationships.csv
│
├── results/
│   ├── benchmark_results.csv
│   ├── neo4j_query_benchmark.csv
│   └── neo4j_controlled_benchmark.csv
│
├── src/
│   ├── 01_cognodb_smoke_test.py
│   ├── 01_test_neo4j_connection.py
│   │
│   ├── 02_setup_schema.py
│   ├── 02_setup_schema_neo4j.py
│   │
│   ├── 03_load_nodes.py
│   ├── 03_load_nodes_neo4j.py
│   │
│   ├── 04_verify_nodes.py
│   ├── 04_verify_nodes_neo4j.py
│   │
│   ├── 05_load_relationships.py
│   ├── 05_load_relationships_neo4j.py
│   │
│   ├── 06_validate_graph_neo4j.py
│   ├── 06_verify_graph.py
│   │
│   ├── 07_benchmark.py
│   ├── 07_neo4j_query_benchmark.py
│   │
│   ├── 08_controlled_neo4j_benchmark.py
│   ├── 08_explain_queries.py
│   │
│   └── 09_final_read_benchmark.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 🔐 Environment Variables

Credentials are **not stored directly in the source code**.

Create a local `.env` file:

```env
COGNODB_URI=bolt+s://your-cognodb-instance
COGNODB_USERNAME=cognodb
COGNODB_PASSWORD=your-password

NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
```

The `.env` file should remain local and must **not** be committed to Git.

A `.env.example` file is provided as a template.

---

# 📦 Installation

Clone the repository:

```bash
git clone https://github.com/Shubhs1604/Graph-Database-Cloud-Benchmarking.git
```

Move into the project:

```bash
cd Graph-Database-Cloud-Benchmarking
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your local environment file:

```text
.env
```

and configure the required credentials.

---

# ▶️ Running the Project

The scripts are organized as a sequential workflow.

### 1. Test connections

```bash
python src/01_cognodb_smoke_test.py
python src/01_test_neo4j_connection.py
```

### 2. Configure indexes/schema

```bash
python src/02_setup_schema.py
python src/02_setup_schema_neo4j.py
```

### 3. Load nodes

```bash
python src/03_load_nodes.py
python src/03_load_nodes_neo4j.py
```

### 4. Verify nodes

```bash
python src/04_verify_nodes.py
python src/04_verify_nodes_neo4j.py
```

### 5. Load relationships

```bash
python src/05_load_relationships.py
python src/05_load_relationships_neo4j.py
```

### 6. Validate graph

```bash
python src/06_validate_graph_neo4j.py
python src/06_verify_graph.py
```

### 7. Run benchmarks

```bash
python src/07_benchmark.py
python src/07_neo4j_query_benchmark.py
```

### 8. Run controlled benchmark

```bash
python src/08_controlled_neo4j_benchmark.py
```

### 9. Analyze query plans

```bash
python src/08_explain_queries.py
```

### 10. Final read benchmark

```bash
python src/09_final_read_benchmark.py
```

---

# 🛠️ Technologies Used

* Python
* Cypher
* Neo4j
* CognoDB Cloud
* Neo4j Python Driver
* CSV
* Pokec Social Network Dataset
* Graph Database Indexing
* Graph Traversal
* Query Plan Analysis
* Performance Benchmarking

---

# 🎯 Key Engineering Concepts Demonstrated

This project demonstrates practical experience with:

### Graph Modeling

```text
Nodes
Relationships
Properties
Labels
```

### Graph Indexing

```text
User ID → Index → Fast node lookup
```

### Batch Data Loading

```text
CSV
 ↓
Python
 ↓
Batch
 ↓
UNWIND
 ↓
Graph Database
```

### Graph Traversal

```text
1-hop
2-hop
3-hop
```

### Data Validation

```text
Node count
Relationship count
Duplicate detection
Self-loop detection
Endpoint validation
```

### Performance Engineering

```text
Warm-up
 ↓
Repeated queries
 ↓
Latency collection
 ↓
p50 / p95 / mean
 ↓
Benchmark results
```

---

# 📌 Benchmark Philosophy

The project intentionally keeps the graph model simple so that database behavior can be evaluated under controlled conditions.

The same logical graph is loaded into both database systems:

```text
397,769 Users
        +
300,000 FRIEND relationships
```

This allows query workloads to focus on graph traversal and lookup behavior rather than application complexity.

---

# 🔒 Security

Credentials should never be committed to Git.

The project uses:

```text
.env
```

for local credentials and:

```text
.env.example
```

for documenting the required configuration.

The actual `.env` file should be excluded using `.gitignore`.

**Important:** If credentials were ever exposed in Git history, they should be rotated even after removing them from the current source files.

---

# 📚 Purpose of the Project

The primary purpose of this project is to build a reproducible benchmark for understanding how graph databases behave with:

* Large node counts
* Relationship traversal
* Indexed lookups
* Multi-hop queries
* Query planning
* Repeated read workloads
* Latency measurements

It also provides a practical foundation for evaluating **cloud graph database performance against a local Neo4j deployment**.

---

# 👨‍💻 Author

**Shubham Pawar**

Data Engineer | Python | SQL | PySpark | AWS | Databricks | Graph Databases

GitHub:

https://github.com/Shubhs1604
