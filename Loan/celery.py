# celery.py

import os
from celery import Celery
from celery.schedules import crontab  # Import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Loan.settings')

app = Celery('Loan')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Define the schedule for the task
app.conf.beat_schedule = {
    # Run the task every 5 seconds
    'check-and-update-defaulters': {
        'task': 'loans.tasks.check_and_update_defaulters',
        'schedule': 5.0,
    },
}
