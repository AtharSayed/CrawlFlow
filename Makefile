# ================================
# Project: CrawlFlow – Website Crawler Analytics
# Author: Athar Sayed
# ================================

PROJECT_NAME = crawlflow
DOCKER_COMPOSE = docker compose
AIRFLOW_CONTAINER = airflow
STREAMLIT_CONTAINER = streamlit

.DEFAULT_GOAL := help

# ----------------
# HELP
# ----------------
help:
	@echo "Available commands:"
	@echo ""
	@echo "🔹 Setup & Build"
	@echo "  make build              Build all Docker images"
	@echo "  make up                 Start all services"
	@echo "  make down               Stop all services"
	@echo "  make restart            Restart all services"
	@echo ""
	@echo "🔹 Airflow Commands"
	@echo "  make airflow-logs       Show Airflow logs"
	@echo "  make airflow-shell      Open shell inside Airflow container"
	@echo "  make dags               List Airflow DAGs"
	@echo "  make dags-refresh       Reserialize Airflow DAGs"
	@echo ""
	@echo "🔹 Streamlit Commands"
	@echo "  make streamlit-logs     Show Streamlit logs"
	@echo "  make streamlit-shell    Open shell inside Streamlit container"
	@echo ""
	@echo "🔹 Maintenance"
	@echo "  make clean              Remove containers, volumes, and orphans"
	@echo "  make prune              Docker system prune"
	@echo ""

# ----------------
# DOCKER
# ----------------
build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

restart:
	$(DOCKER_COMPOSE) down && $(DOCKER_COMPOSE) up -d

clean:
	$(DOCKER_COMPOSE) down -v --remove-orphans

prune:
	docker system prune -f

# ----------------
# AIRFLOW
# ----------------
airflow-logs:
	$(DOCKER_COMPOSE) logs -f $(AIRFLOW_CONTAINER)

airflow-shell:
	$(DOCKER_COMPOSE) exec $(AIRFLOW_CONTAINER) bash

dags:
	$(DOCKER_COMPOSE) exec $(AIRFLOW_CONTAINER) airflow dags list

dags-refresh:
	$(DOCKER_COMPOSE) exec $(AIRFLOW_CONTAINER) airflow dags reserialize

# ----------------
# STREAMLIT
# ----------------
streamlit-logs:
	$(DOCKER_COMPOSE) logs -f $(STREAMLIT_CONTAINER)

streamlit-shell:
	$(DOCKER_COMPOSE) exec $(STREAMLIT_CONTAINER) bash
