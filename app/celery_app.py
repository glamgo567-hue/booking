from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "booking",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.room_tasks"] 
)