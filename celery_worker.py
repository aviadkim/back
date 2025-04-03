# file: celery_worker.py
import os
from celery import Celery
from config import Config

# Initialize Celery
# The first argument is the name of the current module,
# the second is the broker keyword argument specifying the URL of the message broker
# the third is the backend keyword argument specifying the result backend
celery_app = Celery(
    'tasks',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=['tasks']  # Specify the module where tasks are defined (we'll create this next)
)

# Optional configuration, see the application user guide.
celery_app.conf.update(
    result_expires=3600, # How long results should be kept (1 hour)
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)

if __name__ == '__main__':
    celery_app.start()