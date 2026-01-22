# 🌐 Scalable Website Crawling & Analytics Pipeline

An **end-to-end, scalable data engineering pipeline** that crawls multiple websites, extracts structured content, aggregates analytics, and visualizes insights through a professional Streamlit dashboard — all orchestrated using **Apache Airflow** and **Docker**.

---

##  Project Overview

This project demonstrates how to design and implement a **production-style data pipeline** with clear separation of concerns:

- **Config-driven ingestion** (scale from 1 → N websites)
- **Modular crawling & extraction logic**
- **Airflow-based orchestration**
- **Aggregation layer for analytics**
- **Decoupled visualization layer**
- **Fully Dockerized setup**

The system is designed to be **scalable, extensible, and interview-ready**.

---

## 🧠 Architecture

```text
Config (YAML)
   ↓
Airflow DAG
   ↓
Crawling → Extraction → Transformation
   ↓
Aggregation (metrics)
   ↓
Data Contract (summary.json)
   ↓
Streamlit Analytics Dashboard
```

## Project Structure
```bash
Data_Eng_Task/
├── dags/
│   └── website_crawler_dag.py
├── src/
│   ├──__init__.py
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
├── streamlit_app/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── logs/
├── docker-compose.yaml
├── requirements.txt
├── .gitignore 
└── README.md
```

## Technology Stack
| Layer            | Technology                      |
| ---------------- | ------------------------------- |
| Orchestration    | Apache Airflow                  |
| Crawling         | Python, Requests, BeautifulSoup |
| Processing       | Pandas                          |
| Analytics        | Streamlit, Plotly               |
| Configuration    | YAML                            |
| Containerization | Docker, Docker Compose          |


## ▶️ How to Run the Project

This project is fully containerized using **Docker Compose**. Follow the steps below to run the complete end-to-end pipeline locally.

---

###  Prerequisites

Make sure the following are installed on your system:

- Docker (v20+ recommended)
- Docker Compose (v2+)
- At least **4 GB RAM** allocated to Docker

---

###  Clone the Repository

```bash
git clone https://github.com/AtharSayed/CrawlFlow.git
cd CrawlFlow

```

###  Build and Start All Services

```bash
docker compose up -d --build

```

### Accessing the Applications 

| Service             | URL                                            |
| ------------------- | ---------------------------------------------- |
| Airflow UI          | [http://localhost:8080](http://localhost:8080) |
| Streamlit Dashboard | [http://localhost:8501](http://localhost:8501) |


### Airflow Login Credentials 

```bash
docker exec -it data_eng_task_airflow airflow users create `
  --role Admin `
  --username admin `
  --email admin@example.com `
  --firstname admin `
  --lastname user `
  --password admin

```
After running this command the airflow will create a admin user with its credentials 

```bash
Username: admin
Password: admin
```

### Triggering the Pipeline 

1) Open Airflow UI

2) Navigate to DAGs

3) Enable website_crawler_dag

4) Click Trigger DAG ▶️

5) Wait for all tasks to complete successfully

6) The pipeline will:

7) Crawl configured websites

8) Extract and process content

9) Generate analytics in summary.json


### View Analytics 

Once the DAG completes successfully:

Open http://localhost:8501

The Streamlit dashboard will automatically load analytics

Refresh the page after each pipeline run to see updated insights
