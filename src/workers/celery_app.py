
"""
Celery application configuration
"""
from celery import Celery
from src.core.config import settings

# Create Celery app
app = Celery(
    "mcp_analyzer",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["src.workers.tasks"]
)

# Configure Celery
app.conf.update(
    task_serializer = "json",
    accept_content = ["json"],
    result_serializer = "json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
    task_track_started=True,
    task_time_limit=settings.analysis_timeout,
    task_soft_time_limit=settings.analysis_timeout - 10,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Configure task routes
app.conf.task_routes = {
    "src.workers.tasks.analyze_project": {"queue": "analysis"},
    "src.workers.tasks.analyze_file": {"queue": "analysis"},
    "src.workers.tasks.generate_suggestion": {"queue": "ml"},
}

if __name__ == "__main__":
    app.start()