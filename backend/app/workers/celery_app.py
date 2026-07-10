from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "loci",
    broker=settings.redis_dsn,
    backend=settings.redis_dsn,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
)
