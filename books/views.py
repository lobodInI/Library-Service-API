from rest_framework import viewsets

from books.models import Book
from books.serializers import BookSerializer
from books.permissions import IsAdminOrIfAuthenticatedReadOnly


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )
