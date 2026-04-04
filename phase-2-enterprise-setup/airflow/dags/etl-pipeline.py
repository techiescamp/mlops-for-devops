import datetime
from airflow.sdk import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

with DAG(
    dag_id="etl_workflow",
    start_date=datetime.datetime(2021, 1, 1),
    schedule="@daily",
):
    extract = KubernetesPodOperator(
        task_id="extract",
        image="python:3.11",
        cmds=["python", "-c"],
        arguments=["print('Extracting data from source...')"],
    )

    transform = KubernetesPodOperator(
        task_id="transform",
        image="python:3.11",
        cmds=["python", "-c"],
        arguments=["print('Transforming data...')"],
    )

    load = KubernetesPodOperator(
        task_id="load",
        image="python:3.11",
        cmds=["python", "-c"],
        arguments=["print('Loading data into destination...')"],
    )