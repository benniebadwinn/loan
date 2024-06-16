# your_app/tasks.py
from celery import shared_task
from .models import Blacklist, Loan
from django.utils import timezone
from datetime import timedelta

@shared_task
def check_and_update_defaulters():
    print("Checking for defaulters...")
    loans = Loan.objects.filter(due_date__lte=timezone.now())
    for loan in loans:
        print(f"Loan ID: {loan.id} is overdue.")
        # Add logic here to update the database accordingly
    print("Defaulters check complete.")
