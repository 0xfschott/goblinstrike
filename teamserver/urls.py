# urls.py
from django.urls import path
from .views import (
    ListenerCreateView,
    ListenerDeleteView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Goblinstrike API",
        default_version='v1'
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', ListenerCreateView.as_view(), name='listener_create'),
    path('<int:listener_id>', ListenerDeleteView.as_view(), name='listener_delete'),
]