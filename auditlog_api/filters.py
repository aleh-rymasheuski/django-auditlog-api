from auditlog.models import LogEntry
from auditlog.registry import auditlog
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.functions import Cast
from django_filters.rest_framework import FilterSet, CharFilter
from rest_framework.filters import BaseFilterBackend


class ReverseChoiceFilter(CharFilter):
    choices = LogEntry.Action.choices

    def filter(self, qs, value):
        if not value:
            return qs
        reverse = dict((label, value) for value, label in self.choices)
        try:
            value = reverse[value]
        except KeyError as e:
            raise ValidationError(f"Unknown action {value}") from e
        return super().filter(qs, value)


class LogEntryFilterSet(FilterSet):
    action = ReverseChoiceFilter()

    class Meta:
        model = LogEntry
        fields = ["action", "object_id"]


class ChangedFieldsFilter(BaseFilterBackend):
    model_param = "model"
    fields_param = "changed_fields"

    def _get_tracked_models(self):
        return [
            "{}.{}".format(model._meta.app_label, model._meta.model_name)
            for model in auditlog.list()
        ]

    def _get_content_type(self, request):
        model = request.query_params.get(self.model_param, "")
        if not model:
            return None
        tracked_models = self._get_tracked_models()
        if model not in tracked_models:
            raise ValidationError(
                f"Not a tracked model: {model}. Allowed options: {', '.join(sorted(tracked_models))}"
            )
        return ContentType.objects.get_by_natural_key(*model.split("."))

    def _get_fields(self, request, content_type):
        fields = request.query_params.get(self.fields_param, "")
        if not fields:
            return []
        fields = fields.split(",")
        if not content_type:
            raise ValidationError("Can't filter by fields without filtering by model")
        Model = content_type.model_class()
        invalid_fields = set(fields) - set(field.name for field in Model._meta.fields)
        if invalid_fields:
            s = "s" if len(invalid_fields) > 1 else ""
            is_are = "are" if len(invalid_fields) > 1 else "is"
            raise ValidationError(
                f"Field{s} {', '.join(sorted(invalid_fields))} {is_are} not defined on {Model.__name__}"
            )
        return fields

    def filter_queryset(self, request, queryset, view):
        content_type = self._get_content_type(request)
        fields = self._get_fields(request, content_type)

        if content_type:
            queryset = queryset.filter(content_type=content_type)

        field_filter = Q()
        for field in fields:
            field_filter |= Q(**{f"changes_json__{field}__isnull": False})

        if field_filter:
            return queryset.annotate(changes_json=Cast("changes", JSONField())).filter(
                field_filter
            )
        return queryset
