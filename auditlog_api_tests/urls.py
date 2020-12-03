from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from auditlog_api.views import LogEntryViewSet

router = routers.DefaultRouter()
router.register("logentries", LogEntryViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
]
