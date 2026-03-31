import datetime
from airflow.sdk import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s

# Configuration
GIT_REPO = "https://github.com/techiescamp/mlops-for-devops-dev.git"
GIT_BRANCH = "main"
DVC_DATA_FILE = "phase-1-local-dev/datasets/employee_attrition.csv"
DVC_IMAGE = "techiescamp/airflow-dvc-worker:v2.0.0"

GIT_SECRET = k8s.V1EnvFromSource(
    secret_ref=k8s.V1SecretEnvSource(name="git-credentials")
)

RESOURCES = k8s.V1ResourceRequirements(
    requests={"memory": "256Mi", "cpu": "100m"},
    limits={"memory": "512Mi", "cpu": "500m"},
)

SHARED_VOLUME = k8s.V1Volume(
    name="shared-data",
    persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(
        claim_name="airflow-shared-pvc"
    )
)

SHARED_VOLUME_MOUNT = k8s.V1VolumeMount(
    name="shared-data",
    mount_path="/shared"
)

COMMON_ENV = {
    "GIT_REPO": GIT_REPO,
    "GIT_BRANCH": GIT_BRANCH,
    "DVC_DATA_FILE": DVC_DATA_FILE,
    "SHARED_DIR": "/shared/repo",
    "RUN_DATE": "{{ ds }}",
}

# =============================================================================
# TASK 1: Clone repo + DVC Pull
# =============================================================================
TASK1_SCRIPT = '''
import os, subprocess, shutil

GIT_REPO     = os.environ["GIT_REPO"]
GIT_BRANCH   = os.environ["GIT_BRANCH"]
SHARED_DIR   = os.environ["SHARED_DIR"]
GIT_USERNAME = os.environ["GIT_SYNC_USERNAME"]
GIT_TOKEN    = os.environ["GIT_SYNC_PASSWORD"]
CSV_SOURCE   = os.environ["DVC_DATA_FILE"]

def run(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout); print(result.stderr)
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    if result.stdout.strip(): print(result.stdout.strip())
    return result

def dvc_cmd(*args, cwd=None):
    import sys
    run([sys.executable, "-m", "dvc"] + list(args), cwd=cwd)

print("=== Task 1: Clone + DVC Pull ===")

# Clean shared mount from previous runs
SHARED_MOUNT = "/shared"
for item in os.listdir(SHARED_MOUNT):
    item_path = os.path.join(SHARED_MOUNT, item)
    shutil.rmtree(item_path) if os.path.isdir(item_path) else os.remove(item_path)

# Clone repo
repo_url = GIT_REPO.replace("https://", f"https://{GIT_USERNAME}:{GIT_TOKEN}@")
run(["git", "clone", "-b", GIT_BRANCH, repo_url, SHARED_DIR])
run(["git", "config", "user.email", "airflow@devopscube.com"], cwd=SHARED_DIR)
run(["git", "config", "user.name", "Airflow"], cwd=SHARED_DIR)

# DVC pull
print("Pulling DVC data...")
dvc_cmd("pull", cwd=SHARED_DIR)

# Verify CSV exists
src = os.path.join(SHARED_DIR, CSV_SOURCE)
if not os.path.exists(src):
    raise FileNotFoundError(f"CSV not found at {src}")
print(f"CSV ready at: {src}")

print("=== Task 1 Complete ===")
'''

# =============================================================================
# TASK 2: Modify CSV
# =============================================================================
TASK2_SCRIPT = '''
import os, pandas as pd, random

DVC_DATA_FILE = os.environ["DVC_DATA_FILE"]
SHARED_DIR    = os.environ["SHARED_DIR"]

print("=== Task 2: Modify Data ===")
data_path = f"{SHARED_DIR}/{DVC_DATA_FILE}"
df = pd.read_csv(data_path)
print(f"Current rows: {len(df)}")

new_employee = {
    "Employee ID": int(df["Employee ID"].max()) + 1,
    "Age": random.randint(22, 55),
    "Gender": random.choice(["Male", "Female"]),
    "Years at Company": random.randint(0, 25),
    "Job Role": random.choice(["Education", "Sales", "Manager", "Healthcare", "Media"]),
    "Monthly Income": random.randint(3000, 15000),
    "Work-Life Balance": random.choice(["Poor", "Good", "Excellent"]),
    "Job Satisfaction": random.choice(["Low", "Medium", "High"]),
    "Performance Rating": random.choice(["Average", "High"]),
    "Number of Promotions": random.randint(0, 5),
    "Overtime": random.choice(["Yes", "No"]),
    "Distance from Home": random.randint(1, 50),
    "Education Level": random.choice(["High School", "Associate Degree", "Bachelor", "Master", "PhD"]),
    "Marital Status": random.choice(["Single", "Married", "Divorced"]),
    "Number of Dependents": random.randint(0, 4),
    "Job Level": random.choice(["Entry", "Mid", "Senior"]),
    "Company Size": random.choice(["Small", "Medium", "Large"]),
    "Company Tenure": random.randint(1, 100),
    "Remote Work": random.choice(["Yes", "No"]),
    "Leadership Opportunities": random.choice(["Yes", "No"]),
    "Innovation Opportunities": random.choice(["Yes", "No"]),
    "Company Reputation": random.choice(["Poor", "Good", "Excellent"]),
    "Employee Recognition": random.choice(["Low", "Medium", "High"]),
    "Attrition": random.choice(["Stayed", "Left"]),
    "dataset_type": "train"
}

df = pd.concat([df, pd.DataFrame([new_employee])], ignore_index=True)
df.to_csv(data_path, index=False)
print(f"Added employee ID {new_employee['Employee ID']}, total rows: {len(df)}")

print("=== Task 2 Complete ===")
'''

# =============================================================================
# TASK 3: DVC Push + Git Commit + Cleanup PVC
# =============================================================================
TASK3_SCRIPT = '''
import os, subprocess, sys, shutil

DVC_DATA_FILE = os.environ["DVC_DATA_FILE"]
SHARED_DIR    = os.environ["SHARED_DIR"]
RUN_DATE      = os.environ["RUN_DATE"]
GIT_BRANCH    = os.environ["GIT_BRANCH"]

def run(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout); print(result.stderr)
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    if result.stdout.strip(): print(result.stdout.strip())
    return result

def dvc_cmd(*args, cwd=None):
    run([sys.executable, "-m", "dvc"] + list(args), cwd=cwd)

print("=== Task 3: DVC Push + Git Commit ===")

# DVC add and push to S3
dvc_cmd("add", DVC_DATA_FILE, cwd=SHARED_DIR)
dvc_cmd("push", cwd=SHARED_DIR)

# Git commit and push
run(["git", "add", "."], cwd=SHARED_DIR)

diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=SHARED_DIR)
if diff.returncode != 0:
    run(["git", "commit", "-m", f"Data version: {RUN_DATE}"], cwd=SHARED_DIR)
    run(["git", "pull", "--rebase", "origin", GIT_BRANCH], cwd=SHARED_DIR)
    run(["git", "push", "origin", GIT_BRANCH], cwd=SHARED_DIR)
    print(f"Committed: {RUN_DATE}")
else:
    print("No changes to commit")

# Cleanup: Remove all data from shared PVC
print("Cleaning up shared volume...")
SHARED_MOUNT = "/shared"
for item in os.listdir(SHARED_MOUNT):
    item_path = os.path.join(SHARED_MOUNT, item)
    shutil.rmtree(item_path) if os.path.isdir(item_path) else os.remove(item_path)
print("Cleanup complete")

print("=== Task 3 Complete ===")
'''

# =============================================================================
# DAG Definition
# =============================================================================
with DAG(
    dag_id="dataset_pipeline",
    start_date=datetime.datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    tags=["dvc", "employee-attrition", "shared-pvc"],
) as dag:

    task_pull = KubernetesPodOperator(
        task_id="pull_data",
        name="dvc-pull",
        namespace="airflow",
        image=DVC_IMAGE,
        image_pull_policy="Always",
        service_account_name="airflow-dvc-sa",
        container_resources=RESOURCES,
        env_from=[GIT_SECRET],
        env_vars=COMMON_ENV,
        volumes=[SHARED_VOLUME],
        volume_mounts=[SHARED_VOLUME_MOUNT],
        cmds=["python", "-c"],
        arguments=[TASK1_SCRIPT],
        get_logs=True,
        do_xcom_push=False,
        on_finish_action="keep_pod",
        log_events_on_failure=True,
        in_cluster=True,
        config_file=None,
    )

    task_modify = KubernetesPodOperator(
        task_id="modify_data",
        name="dvc-modify",
        namespace="airflow",
        image=DVC_IMAGE,
        image_pull_policy="Always",
        service_account_name="airflow-dvc-sa",
        container_resources=RESOURCES,
        env_vars=COMMON_ENV,
        volumes=[SHARED_VOLUME],
        volume_mounts=[SHARED_VOLUME_MOUNT],
        cmds=["python", "-c"],
        arguments=[TASK2_SCRIPT],
        get_logs=True,
        do_xcom_push=False,
        on_finish_action="keep_pod",
        log_events_on_failure=True,
        in_cluster=True,
        config_file=None,
    )

    task_push = KubernetesPodOperator(
        task_id="push_data",
        name="dvc-push",
        namespace="airflow",
        image=DVC_IMAGE,
        image_pull_policy="Always",
        service_account_name="airflow-dvc-sa",
        container_resources=RESOURCES,
        env_from=[GIT_SECRET],
        env_vars=COMMON_ENV,
        volumes=[SHARED_VOLUME],
        volume_mounts=[SHARED_VOLUME_MOUNT],
        cmds=["python", "-c"],
        arguments=[TASK3_SCRIPT],
        get_logs=True,
        do_xcom_push=False,
        on_finish_action="keep_pod",
        log_events_on_failure=True,
        in_cluster=True,
        config_file=None,
    )

    task_pull >> task_modify >> task_push