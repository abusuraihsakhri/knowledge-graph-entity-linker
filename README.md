# Knowledge Graph Entity Linker

> **Domain:** Clinical Decision Support & Biomedical Computing
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Knowledge Graph Entity Linker** is an advanced analytical and computational platform implementing continuous clinical named entity extraction, multi-worker consensus evaluation, and RDF/property graph building.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine:** Strict compliance with standard reference formulations and thresholds.
- **Risk & Urgency Classification:** Multi-tier categorization with automated clinical/operational action recommendations.
- **Validation & Guardrails:** Rigorous input bounds checking and anomaly detection.
- **Multi-Worker Consensus:** Three specialized workers (InvariantQC, SafetyEscalation, ProtocolConformance) evaluate each task.
- **Enrichment Suite:** Confidence scoring, entity deduplication, history tracking, graph export, and statistics dashboard.

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/knowledge-graph-entity-linker.git
cd knowledge-graph-entity-linker

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# Set the audit signing key (minimum 16 characters)
export AUDIT_SECRET_KEY="your-strong-random-key-here"
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --task-id <value> --target <value> --primary <value> --secondary <value>
```

### 3. CLI Subcommands

#### Audit (single task evaluation)
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

#### Chat (supervisory query)
```bash
python cli.py chat "What is the system status?"
```

#### Batch (CSV processing)
```bash
python cli.py batch -i sample.csv -o results.csv
```

#### Verify Audit Trail
```bash
python cli.py verify-audit
```

#### Serve (FastAPI REST server)
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Specifies input measurement or parameter value.
- `--target`: Specifies input measurement or parameter value.
- `--primary`: Specifies input measurement or parameter value (float).
- `--secondary`: Specifies input measurement or parameter value (float).
- `--critical`: Triggers emergency escalation flag.
- `--status`: Status descriptor (e.g., NOMINAL, DISCORDANT, ANOMALY).

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Parameter / observation metric | Required |
| `target_identifier` | Parameter / observation metric | Required |
| `primary_metric` | Parameter / observation metric | Required |
| `secondary_metric` | Parameter / observation metric | Required |
| `is_critical_flag` | Parameter / observation metric | Required |
| `status_descriptor` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers. PHI is also automatically redacted from outbound text.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition. Requires a persistent `AUDIT_SECRET_KEY` environment variable (minimum 16 characters).
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).
* **Path Traversal Protection:** All CLI file operations resolve and validate paths against the working directory.

---

## 🔐 Environment Variables

| Variable | Required | Description |
|:---------|:---------|:------------|
| `AUDIT_SECRET_KEY` | Recommended | HMAC-SHA256 audit signing key (min 16 chars). If unset, an ephemeral key is generated with a warning. |
| `MODEL_PROVIDER` | No | LLM provider: `mock` (default), `ollama`, `claude`, `openai` |

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env to set AUDIT_SECRET_KEY and MODEL_PROVIDER

# Build and run
docker compose up --build
```

Or manually:

```bash
docker build -t knowledge-graph-entity-linker .
docker run -p 8000:8000 --env-file .env knowledge-graph-entity-linker
```

---

## 📁 Project Structure

```
knowledge-graph-entity-linker/
├── agents/                  # Core analytical workers & security
│   ├── api.py               # FastAPI REST endpoints
│   ├── base.py              # PHI guard, HMAC audit trail
│   ├── models.py            # Pydantic data models
│   ├── supervisor.py        # Multi-worker orchestrator
│   ├── workers.py           # Specialized evaluation workers
│   ├── llm_factory.py       # LLM provider factory
│   ├── learning.py          # Bayesian calibration engine
│   ├── metrics.py           # Prometheus metrics collector
│   └── streamer.py          # WebSocket telemetry broadcaster
├── graph_linker/            # Alternative frontend engine
│   ├── agents.py            # Sub-agent hierarchy
│   ├── engine.py            # Domain evaluation engine
│   ├── models.py            # Dataclass models
│   ├── cli.py               # Alternative CLI
│   └── server.py            # FastAPI app factory
├── tests/                   # Pytest test suite
├── web/                     # Operations console (HTML)
├── cli.py                   # Main CLI entry point
├── enrichment.py            # Enrichment feature suite
├── simulator.py             # High-throughput stress tester
├── sample.csv               # Sample batch input
├── sample_payload.json      # Sample API payload
├── Dockerfile               # Container build
├── docker-compose.yml       # Container orchestration
└── pyproject.toml           # Project metadata
```

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
