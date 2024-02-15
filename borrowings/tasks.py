from datetime import date

# from asgiref.sync import async_to_sync
from celery import shared_task

from borrowings.models import Borrowing
from borrowings.telegram_utils import send_message
from library_service_api import settings


@shared_task
def send_borrowing_notification(text):
    send_message(text=text)


@shared_task
def check_overdue_borrowings():
    today = date.today()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today, actual_return_date__isnull=True
    )

    if overdue_borrowings:
        for borrowing in overdue_borrowings:
            text = (f"Overdue borrowing: "
                    f"book - {borrowing.book.title}, "
                    f"user - {borrowing.user.email}")
            send_borrowing_notification(text=text)
    else:
        send_borrowing_notification("No borrowings overdue today!")
