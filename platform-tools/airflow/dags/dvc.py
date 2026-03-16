import datetime
import subprocess
import os
import sys

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator

RAW_BUCKET    = "devopscube-data-lake"
RAW_KEY       = "employee_attrition.csv"
GIT_REPO      = "github.com/techiescamp/mlops-for-devops-development.git"
GIT_BRANCH    = "main"
CLONE_DIR     = "/tmp/dvc-repo"
WORK_DIR      = "/tmp/dvc-repo/airflow"
DVC_DATA_FILE = "data/employee_attrition.csv"


def run(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed:\n{result.stderr}")
    if result.stdout.strip():
        print(result.stdout.strip())


def dvc_cmd(*args, cwd=None):
    run([sys.executable, "-m", "dvc"] + list(args), cwd=cwd)


def s3_to_dvc(**context):
    import boto3
    run_date = context["ds"]

    # Install DVC if not available
    try:
        import dvc
    except ImportError:
        print("Installing DVC...")
        run([sys.executable, "-m", "pip", "install", "dvc", "dvc-s3", "--quiet"])

    # 1. Clone repo
    if os.path.exists(CLONE_DIR):
        subprocess.run(["rm", "-rf", CLONE_DIR])

    github_token = os.environ.get("GITHUB_TOKEN", "")
    github_user = os.environ.get("GITHUB_USER", "")
    repo_url = f"https://{github_user}:{github_token}@{GIT_REPO}"
    run(["git", "clone", "-b", GIT_BRANCH, repo_url, CLONE_DIR])

    # 2. Download CSV directly into airflow/data/
    os.makedirs(f"{WORK_DIR}/data", exist_ok=True)
    boto3.client("s3").download_file(
        RAW_BUCKET, RAW_KEY, f"{WORK_DIR}/{DVC_DATA_FILE}"
    )
    print(f"Downloaded {RAW_KEY} into repo")

    # 3. Git config (set at repo root)
    run(["git", "config", "user.email", "airflow@devopscube.com"], cwd=CLONE_DIR)
    run(["git", "config", "user.name", "Airflow"], cwd=CLONE_DIR)

    # 4. DVC add + push (run from airflow/ where .dvc/ lives)
    dvc_cmd("add", DVC_DATA_FILE, cwd=WORK_DIR)
    dvc_cmd("push", cwd=WORK_DIR)
    print("DVC pushed to S3")

    # 5. Git commit + push (from repo root)
    run(["git", "add", "."], cwd=CLONE_DIR)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=CLONE_DIR)
    if diff.returncode != 0:
        run(["git", "commit", "-m", f"Data version: {run_date}"], cwd=CLONE_DIR)
        run(["git", "push", "origin", GIT_BRANCH], cwd=CLONE_DIR)
        print(f"New version committed: {run_date}")
    else:
        print("No data changes, skipping commit")


with DAG(
    dag_id="dvc_pipeline",
    start_date=datetime.datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["s3", "dvc", "employee-attrition"],
) as dag:

    PythonOperator(
        task_id="s3_to_dvc",
        python_callable=s3_to_dvc,
    )