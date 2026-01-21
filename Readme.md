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
