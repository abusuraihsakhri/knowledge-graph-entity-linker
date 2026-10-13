# Knowledge Graph Entity Linker

Deterministic entity-name matching and metric-audit utilities with a static browser interface, Python CLI tools, and a FastAPI service.

## Features

- **Browser entity linker:** Match user-supplied names and aliases against text; return mention offsets, entity IDs, unique nodes, and co-mention edges. Download results as JSON. The implementation is lexical and does not perform trained NER, entity disambiguation, ontology reasoning, or verified relationship extraction.
- **Browser metric audit:** Exercise the same basic thresholds as the Python `agents` workers locally, without a backend. These results are **unsigned**.
- **Python audit:** Evaluate numeric metrics and descriptor flags with three deterministic workers. Generate an in-memory HMAC-SHA256 audit chain.
- **CLI batch mode:** Process CSV tasks and export annotated CSV files.
- **FastAPI:** Expose `/health`, `/metrics`, `/api/audit`, `/api/chat`, and `/api/audit/logs`.

The project currently has two distinct Python implementations: `agents/` (the root `cli.py` and API) and `graph_linker/` (the installed CLI command). They have different thresholds and dossier schemas. Neither Python implementation performs the lexical entity linking shown in the browser.

## Browser use

Open `web/index.html` locally, or use the GitHub Pages deployment once it is enabled and verified. The app requires a modern browser with ES2018+ support. Enter text and a JSON array of vocabulary records:

```json
[
  {"id": "GENE-1", "label": "EGFR", "type": "Gene",
   "aliases": ["epidermal growth factor receptor"]},
  {"id": "DRUG-1", "label": "erlotinib", "type": "Drug"}
]
```

Select **Entity linking**, run the match, then **Export JSON**. Alternatively, select **Metric audit demo** to check the local deterministic thresholds. Co-mention edges mean only that both names appear in the supplied text.

All browser-side evaluation is performed in JavaScript; Pyodide and a Python server are not necessary for these workflows. The browser implementation does not implement the signed Python audit trail.

## Python installation

Requires Python 3.9 or newer.

```bash
git clone https://github.com/abusuraihsakhri/knowledge-graph-entity-linker.git
cd knowledge-graph-entity-linker
python -m pip install -e ".[server,test]"
```

### CLI and API

```bash
python cli.py audit --task-id T-001 --target SPECIMEN-01 --primary 28 --secondary 13
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py chat "system status"
python cli.py serve --host 127.0.0.1 --port 8000
```

The installed `knowledge-graph-entity-linker` command uses `graph_linker.cli`, whose evaluation criteria differ from the root `cli.py`.

The FastAPI service is exposed on port 8000. The `/metrics` endpoint returns JSON counters, not Prometheus exposition text. `/api/chat` uses a deterministic mock response and **does not** connect to Ollama or cloud LLM providers.

Set a random, persistent `AUDIT_SECRET_KEY` (at least 16 characters) when audit integrity must persist across restarts:

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

Without it, an ephemeral key is generated and logs cannot be verified across process restarts. The in-memory audit trail itself is not persistent storage.

### Container

```bash
cp .env.example .env
# Replace AUDIT_SECRET_KEY with a strong generated value.
docker compose up --build
```

## Tests

```bash
python -m pytest -q
node --check web/core.js
node --check web/app.js
node --test web/core.test.cjs
```

GitHub Actions runs the Python suite on Python 3.10–3.13 and checks the browser-side JavaScript.

## Privacy and limitations

- The browser UI does not submit text, vocabulary records, or audit data to a server. It does not use third-party scripts.
- Python API requests are processed by the server you run; do not expose it to the public internet without appropriate access controls and infrastructure.
- The identifier guard uses a limited set of regular-expression patterns. **It is not a validated de-identification tool**, and may miss protected health information.
- The numeric audit thresholds are software demonstration rules, **not medically validated reference values** or proof of CAP, CLSI, ISO, RDF, or OWL conformity.
- Treat co-mention edges as lexical observations only; no causal or biological relation is inferred.

## Technology and license

Python, Pydantic, FastAPI, pytest, vanilla JavaScript, HTML/CSS, and GitHub Actions. The static UI does not need a frontend build step. Licensed under [MIT](LICENSE).
