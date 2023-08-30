import subprocess


def start_celery_worker():
    worker_command = "celery -A celery_tasks worker -P gevent --loglevel=INFO"
    worker_process = subprocess.Popen(worker_command, shell=True)
    return worker_process


def start_celery_beat():
    beat_command = "celery -A celery_tasks beat"
    beat_process = subprocess.Popen(beat_command, shell=True)
    return beat_process


def create_migrations(migration_name='migration'):
    model_changes_revision_command = f'alembic revision --autogenerate -m "{migration_name}"'
    subprocess.Popen(model_changes_revision_command, shell=True)


def apply_migrations():
    apply_migrations_command = "alembic upgrade heads"
    subprocess.Popen(apply_migrations_command, shell=True)


if __name__ == "__main__":
    start_celery_worker()
    start_celery_beat()
