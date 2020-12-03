from auditlog.models import LogEntry
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import GenericViewSet

from auditlog_api.filters import ChangedFieldsFilter, LogEntryFilterSet
from auditlog_api.serializers import LogEntrySerializer
from auditlog_api.pagination import TimeLimitedPagination


class LogEntryViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = LogEntry.objects.select_related("actor", "content_type")
    pagination_class = TimeLimitedPagination
    serializer_class = LogEntrySerializer
    filter_backends = [
        DjangoFilterBackend,
        ChangedFieldsFilter,
        OrderingFilter,
    ]
    filterset_class = LogEntryFilterSet
    ordering_fields = ["id", "timestamp"]
