from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingDetailSerializer,
    BorrowingSerializer,
)
from books.tests.test_book_api import sample_book

BORROWING_URL = reverse("borrowing:borrowing-list")
BORROWING_DATE = datetime.now().date()
EXPECTED_RETURN_DATE = BORROWING_DATE + timedelta(days=10)


def sample_borrowing(**params):
    book = sample_book()

    defaults = {
        "borrow_date": BORROWING_DATE,
        "expected_return_date": EXPECTED_RETURN_DATE,
        "book": book,
        "user_id": 1,
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


def sample_user(**params):
    defaults = {
        "email": "user@test.com",
        "password": "passwordtest",
    }
    defaults.update(params)

    return get_user_model().objects.create_user(**defaults)


def detail_url(borrowing_id: int):
    return reverse("borrowing:borrowing-detail", args=[borrowing_id])


def return_url(borrowing_id: int):
    """Return URL for recipe borrowing return"""
    return reverse("borrowing:borrowing-return-borrowing", args=[borrowing_id])


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        result = self.client.get(BORROWING_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)

    def test_list_borrowings(self):
        sample_borrowing()
        sample_borrowing()

        result = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingSerializer(borrowings, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_borrowing_detail(self):
        borrowing = sample_borrowing()

        url = detail_url(borrowing.id)
        result = self.client.get(url)

        serializer = BorrowingDetailSerializer(borrowing)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_create_borrowing(self):
        book = sample_book()
        payload = {
            "expected_return_date": EXPECTED_RETURN_DATE,
            "book": book.id,
        }

        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_borrowing_decreases_book_inventory_by_1(self):
        book = sample_book()
        expected_book_inventory = book.inventory - 1
        payload = {
            "expected_return_date": EXPECTED_RETURN_DATE,
            "book": book.id,
        }

        self.client.post(BORROWING_URL, payload)

        db_book = Book.objects.get(pk=book.id)
        actual_book_inventory = db_book.inventory

        self.assertEqual(expected_book_inventory, actual_book_inventory)

    def test_create_borrowing_attach_the_current_user(self):
        book = sample_book()
        payload = {
            "expected_return_date": EXPECTED_RETURN_DATE,
            "book": book.id,
        }

        result = self.client.post(BORROWING_URL, payload)
        borrowing = Borrowing.objects.get(pk=result.data["id"])

        self.assertEqual(borrowing.user, self.user)

    def test_filter_borrowings_by_current_user(self):
        user = sample_user(email="test1@test.com")
        sample_borrowing(user_id=user.id)
        sample_borrowing(user_id=self.user.id)

        result = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.filter(user_id=self.user.id)
        serializer = BorrowingSerializer(borrowings, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_return_borrowing(self):
        borrowing = sample_borrowing()

        self.client.post(return_url(borrowing.id))

        instance = Borrowing.objects.get(pk=borrowing.id)
        actual_time = datetime.now()
        actual_date = actual_time.date()

        self.assertEqual(instance.actual_return_date, actual_date)

    def test_return_borrowing_limited(self):
        borrowing = sample_borrowing()

        self.client.post(return_url(borrowing.id))
        result = self.client.post(return_url(borrowing.id))

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_1_to_book_inventory_on_returning(self):
        borrowing = sample_borrowing()
        book = borrowing.book
        inventory_expected = book.inventory + 1

        self.client.post(return_url(borrowing.id))

        instance = Book.objects.get(pk=book.id)
        inventory_actual = instance.inventory

        self.assertEqual(inventory_actual, inventory_expected)


class AdminBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com", "passwordtest", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_list_all_existing_borrowings(self):
        user = sample_user()

        sample_borrowing(user_id=user.id)
        sample_borrowing(user_id=user.id)
        sample_borrowing(user_id=self.user.id)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingSerializer(borrowings, many=True)

        result = self.client.get(BORROWING_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, result.data)

    def test_filter_borrowings_by_user_id(self):
        user = sample_user()

        borrowing_1 = sample_borrowing(user_id=user.id)
        borrowing_2 = sample_borrowing(user_id=user.id)
        borrowing_3 = sample_borrowing(user_id=self.user.id)

        result = self.client.get(BORROWING_URL, {"user_id": user.id})

        serializer_1 = BorrowingSerializer(borrowing_1)
        serializer_2 = BorrowingSerializer(borrowing_2)
        serializer_3 = BorrowingSerializer(borrowing_3)

        self.assertIn(serializer_1.data, result.data)
        self.assertIn(serializer_2.data, result.data)
        self.assertNotIn(serializer_3.data, result.data)

    def test_filter_borrowings_by_parameter_is_active(self):
        borrowing_1 = sample_borrowing()
        borrowing_2 = sample_borrowing()
        borrowing_3 = sample_borrowing()

        serializer_1 = BorrowingSerializer(borrowing_1)
        serializer_2 = BorrowingSerializer(borrowing_2)
        serializer_3 = BorrowingSerializer(borrowing_3)

        self.client.post(return_url(borrowing_3.id))
        res = self.client.get(BORROWING_URL, {"is_active": True})

        self.assertIn(serializer_1.data, res.data)
        self.assertIn(serializer_2.data, res.data)
        self.assertNotIn(serializer_3.data, res.data)
