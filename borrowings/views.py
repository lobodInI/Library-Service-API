from typing import Type

from django.db.models import QuerySet
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        return self.serializer_class

    def get_queryset(self) -> QuerySet:
        return self.filter_queryset(self.queryset)

    def filter_queryset(self, queryset) -> QuerySet:
        user = self.request.user
        is_active = self.request.query_params.get("is_active")

        if is_active:
            queryset = queryset.filter(actual_return_date__isnull=True)
        if not user.is_staff:
            queryset = queryset.filter(user=user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
