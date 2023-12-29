from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_id",
            "user_id",
        )


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )
        read_only_fields = fields


class BorrowingCreateSerializer(BorrowingSerializer):
    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs=attrs)
        Borrowing.validate_book_inventory(attrs["book"], ValidationError)

        return data

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
        )

    def create(self, validated_data):
        with transaction.atomic():
            borrowing = Borrowing.objects.create(**validated_data)

            book = validated_data.get("book")
            book.inventory -= 1
            book.save()

            return borrowing
