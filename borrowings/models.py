from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, CheckConstraint, F

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="borrowings",
    )

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(borrow_date__gte=datetime.now().date()),
                name="borrow_date_gte_or_equal_today"
            ),
            CheckConstraint(
                check=Q(expected_return_date__gte=F("borrow_date")),
                name="expected_return_after_borrow"
            ),
            CheckConstraint(
                check=Q(
                    actual_return_date__gte=F("borrow_date"),
                    actual_return_date__lte=F("expected_return_date")
                ),
                name="actual_return_between_borrow_and_expected"
            ),
        ]

    @staticmethod
    def validate_book_inventory(book, error_to_raise):
        if book.inventory <= 0:
            raise error_to_raise(
                {"message": f"All books with name '{book.title}' borrowing."}
            )

    def clean(self):
        Borrowing.validate_book_inventory(self.book, ValidationError)

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        if self.pk is None:
            self.full_clean()
        return super(Borrowing, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self) -> str:
        return f"{self.user} borrowed {self.book.title}"
