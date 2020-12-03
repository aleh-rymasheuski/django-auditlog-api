from django.conf import settings
from rest_framework.pagination import LimitOffsetPagination

from auditlog_api.tools import limit_query_time


class TimeLimitedPagination(LimitOffsetPagination):
    @limit_query_time(
        getattr(settings, "AUDITLOG_PAGINATOR_TIMEOUT", 500), default=100000
    )
    def get_count(self, queryset):
        return super().get_count(queryset)
