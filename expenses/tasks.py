from celery import shared_task
from django.core.mail import send_mail
from django.db.models import Sum  # Import Sum from django.db.models
from .models import Balance, User
from celery import Celery
from celery.schedules import crontab
from celery.task import periodic_task

@shared_task
def send_weekly_email():
    # Get a list of users with non-zero balances
    users_with_balances = User.objects.filter(balance__gt=0)

    for user in users_with_balances:
        # Get the total amount owed to the user
        total_amount_owed = Balance.objects.filter(to_user=user).aggregate(total_amount=Sum('amount'))['total_amount']

        # Send email to the user
        subject = 'Weekly Balance Update'
        message = f'Hello {user.name},\n\nYou have a total owe balance of Rs {total_amount_owed:.2f}.\n\nBest regards,\nYour Expense Sharing App Team'
        from_email = 'testmailinator0105@gmail.com'  # Set your sender email

        send_mail(subject, message, from_email, [user.email])


@periodic_task(run_every=crontab(minute=0, hour=0, day_of_week='monday'))
def send_weekly_email_task():
    send_weekly_email.delay()
