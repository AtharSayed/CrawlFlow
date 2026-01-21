from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

# ------------------------------------------------------------------------------
# Paths inside container
# ------------------------------------------------------------------------------
CONFIG_PATH = "/opt/airflow/config/websites.yaml"
RAW_DIR = "/opt/airflow/data/raw"
PROCESSED_DIR = "/opt/airflow/data/processed"
METRICS_DIR = "/opt/airflow/data/metrics"


# ------------------------------------------------------------------------------
# Task functions
# ------------------------------------------------------------------------------
def get_websites_list(**context):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

    from src.utils import load_websites, get_logger

    logger = get_logger("airflow.website_crawler_dag")
    websites = load_websites(CONFIG_PATH)

    logger.info(f"Loaded {len(websites)} websites")

    # REQUIRED for expand(op_kwargs=...)
    return [{"url": url} for url in websites]


def crawl_single(url, **context):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

    from src.crawler import crawl_website

    crawl_website(
        url=url,
        raw_base_dir=RAW_DIR,
        execution_date=context["execution_date"],
    )


def extract_single(url, **context):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

    from src.extractor import extract_and_tag

    extract_and_tag(
        url=url,
        raw_base_dir=RAW_DIR,
        execution_date=context["execution_date"],
    )


def transform_single(url, **context):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

    from src.transformer import transform_to_standard

    transform_to_standard(
        url=url,
        raw_base_dir=RAW_DIR,
        processed_base_dir=PROCESSED_DIR,
        execution_date=context["execution_date"],
    )


def aggregate_all(**context):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

    from src.aggregator import compute_and_save_metrics

    compute_and_save_metrics(
        processed_base_dir=PROCESSED_DIR,
        metrics_dir=METRICS_DIR,
        execution_date=context["execution_date"],
    )


# ------------------------------------------------------------------------------
# DAG
# ------------------------------------------------------------------------------
with DAG(
    dag_id="website_crawler_dag",
    description="Website content crawler pipeline",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "airflow",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["crawl", "etl"],
) as dag:

    # --------------------------------------------------------------------------
    # Tasks
    # --------------------------------------------------------------------------
    t0_get_list = PythonOperator(
        task_id="get_websites_list",
        python_callable=get_websites_list,
    )

    t1_crawl = PythonOperator.partial(
        task_id="crawl_website",
        python_callable=crawl_single,
    ).expand(op_kwargs=t0_get_list.output)

    t2_extract = PythonOperator.partial(
        task_id="extract_content",
        python_callable=extract_single,
    ).expand(op_kwargs=t0_get_list.output)

    t3_transform = PythonOperator.partial(
        task_id="transform_data",
        python_callable=transform_single,
    ).expand(op_kwargs=t0_get_list.output)

    t4_aggregate = PythonOperator(
        task_id="aggregate_metrics",
        python_callable=aggregate_all,
        trigger_rule=TriggerRule.ALL_DONE,  # IMPORTANT for mapped fan-in
    )

    # --------------------------------------------------------------------------
    # Dependencies (CORRECT)
    # --------------------------------------------------------------------------
    t0_get_list >> t1_crawl >> t2_extract >> t3_transform >> t4_aggregate
