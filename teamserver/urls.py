# urls.py
from django.urls import path
from .views import (
    ListenerView,
    ListenerDetailView,
    ImplantsView,
    ImplantsDetailView,
    ImplantsTaskView,
    UIListenersView,
    UIImplantsView
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
    path('api/listeners/', ListenerView.as_view(), name='listener_view'),
    path('api/listeners/<int:id>', ListenerDetailView.as_view(), name='listener_detail'),
    path('api/implants/', ImplantsView.as_view(), name='implant_view'),
    path('api/implants/<int:id>', ImplantsDetailView.as_view(), name='implant_detail'),
    path('api/implants/<int:id>/tasks', ImplantsTaskView.as_view(), name='implant_task'),
    path('listeners/', UIListenersView.as_view(), name='manage_listeners'),
    path('implants/', UIImplantsView.as_view(), name='manage_implants'),
]