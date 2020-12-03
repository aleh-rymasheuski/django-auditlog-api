import json

from auditlog.models import LogEntry
from rest_framework.serializers import SerializerMethodField, ModelSerializer


_ACTIONS = dict(LogEntry.Action.choices)


class LogEntrySerializer(ModelSerializer):
    action = SerializerMethodField()
    actor = SerializerMethodField()
    changes = SerializerMethodField()
    model = SerializerMethodField()

    def get_action(self, obj):
        return _ACTIONS[obj.action]

    def get_actor(self, obj):
        if not obj.actor:
            return None
        return {
            "id": obj.actor.id,
            "email": obj.actor.email,
            "full_name": obj.actor.full_name,
        }

    def get_changes(self, obj):
        return json.loads(obj.changes)

    def get_model(self, obj):
        content_type = obj.content_type
        return f"{content_type.app_label}.{content_type.model}"

    class Meta:
        model = LogEntry
        fields = ["id", "object_id", "action", "actor", "changes", "model"]
