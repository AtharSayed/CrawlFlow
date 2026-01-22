# 🌐 Scalable Website Crawling & Analytics Pipeline

A **production-ready, end-to-end data engineering pipeline** that crawls multiple websites, extracts structured content, aggregates analytics, and visualizes insights through a professional **Streamlit dashboard**, orchestrated using **Apache Airflow** and fully **Dockerized**.

This project is designed to demonstrate **real-world data engineering practices**, clean system architecture, and scalability-first thinking.

---

## Project Highlights

- Config-driven website crawling (scale from 1 → N websites)
- Dynamic task mapping using Apache Airflow
- Modular, maintainable Python codebase
- Aggregation layer producing analytics-ready metrics
- Decoupled Streamlit analytics dashboard
- Fully Dockerized and reproducible setup
- Developer-friendly workflow with Makefile

---

##  System Architecture

```text
websites.yaml (Config)
        ↓
Apache Airflow DAG
        ↓
Crawling → Extraction → Transformation
        ↓
Aggregation Layer
        ↓
summary.json (Data Contract)
        ↓
Streamlit Analytics Dashboard
```

### Key Design Principles
- Loose coupling between ETL and analytics
- Stable file-based data contract
- Config-based scalability (no code changes required)
- Independent service deployment

---

##  Project Structure

```text
Data_Eng_Task/
├── dags/
│   └── website_crawler_dag.py
├── src/
│   ├── __init__.py
│   ├── crawler.py
│   ├── extractor.py
│   ├── transformer.py
│   ├── aggregator.py
│   └── utils.py
├── config/
│   └── websites.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   └── metrics/
│       └── summary.json
├── streamlit_analytics/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── logs/
├── docker-compose.yaml
├── Makefile
├── requirements.txt
└── README.md
```

---

##  Technology Stack

| Layer | Technology |
|-----|-----------|
| Orchestration | Apache Airflow |
| Crawling | Python, Requests |
| Parsing | BeautifulSoup |
| Processing | Pandas |
| Analytics | Streamlit, Plotly |
| Configuration | YAML |
| Containerization | Docker, Docker Compose |

---

##  Airflow Pipeline Workflow

1. Load website configuration from `websites.yaml`
2. Dynamically crawl each website
3. Extract structured content (homepage, navbar, footer, case studies)
4. Transform and clean extracted data
5. Aggregate analytics and metrics
6. Persist output to `summary.json`

---

##  Analytics Dashboard (Streamlit)

The Streamlit application:

- Consumes `summary.json`
- Displays KPI cards and charts
- Provides section-wise content statistics
- Shows pipeline metadata for traceability

The analytics layer is **read-only and decoupled**, making it easy to replace or scale independently.

---

##  Dockerized Architecture

The system runs as two independent services:

### Airflow Service
- Scheduler and webserver
- Executes the crawling and aggregation pipeline

### Streamlit Service
- Serves analytics dashboard
- Reads shared output from `data/metrics/summary.json`

Both services communicate via a shared Docker volume.

---

##  How to Run the Project

### Prerequisites
- Docker (v20+)
- Docker Compose (v2+)
- Minimum 4 GB RAM allocated to Docker

---

### Clone the Repository

```bash
git clone https://github.com/AtharSayed/CrawlFlow.git
cd CrawlFlow
```

---

### Build and Start Services

```bash
docker compose up -d --build
```

---

### Access the Applications

| Service | URL |
|------|----|
| Airflow UI | http://localhost:8080 |
| Streamlit Dashboard | http://localhost:8501 |

**Airflow Credentials**
```
Username: admin
Password: admin
```

---

### Trigger the Pipeline

1. Open the Airflow UI
2. Enable `website_crawler_dag`
3. Trigger the DAG manually
4. Wait for all tasks to complete successfully
5. Refresh the Streamlit dashboard to view analytics

---

### Stop the Services

```bash
docker compose down
```

---

##  Makefile Commands

This project includes a Makefile for simplified operations.

| Command | Description |
|------|------------|
| `make build` | Build Docker images |
| `make up` | Start all services |
| `make down` | Stop all services |
| `make restart` | Restart services |
| `make dags-refresh` | Refresh Airflow DAGs |
| `make airflow-logs` | View Airflow logs |
| `make streamlit-logs` | View Streamlit logs |
| `make clean` | Remove containers and volumes |

---

##  Configuration

Edit `config/websites.yaml` to add or remove websites:

```yaml
websites:
  - https://www.apple.com
  - https://www.microsoft.com
  - https://www.amazon.com

rate_limit:
  requests_per_minute: 60
```

No code changes are required when scaling.

---

## Scalability & Extensibility

- Replace `summary.json` with PostgreSQL, DuckDB, or S3 + Parquet
- Replace Streamlit with Superset, Metabase, or Power BI
- Add alerting, historical metrics, or anomaly detection

The core pipeline remains unchanged.

---

##  Author

**Athar Sayed**  
MTech (Artificial Intelligence) | Data & AI Engineering  
Focused on building scalable, production-grade data and AI systems
---

## 📜 License

This project is intended for educational and portfolio use.
