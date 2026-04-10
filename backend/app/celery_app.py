from celery import Celery

from app.config import settings

celery = Celery("feedy")
celery.conf.broker_url = settings.redis_url
celery.conf.result_backend = settings.redis_url
celery.conf.task_serializer = "json"
celery.conf.result_serializer = "json"
celery.conf.include = ["app.tasks.feed_tasks"]
celery.conf.beat_schedule = {
    "refresh-feeds-every-5-min": {
        "task": "feedy.refresh_due_feeds",
        "schedule": 300.0,  # check every 5 minutes
    },
}
