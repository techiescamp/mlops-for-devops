import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator

with DAG(
    dag_id="etl_workflow",
    start_date=datetime.datetime(2021, 1, 1),
    schedule="@daily",
):
    start = EmptyOperator(task_id="start")
    extract = EmptyOperator(task_id="extract")
    load = EmptyOperator(task_id="load")

    start >> extract >> load
