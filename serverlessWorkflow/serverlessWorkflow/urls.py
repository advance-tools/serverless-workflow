from django.contrib import admin
from django.urls import path, include, re_path

from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

read_me = ""

with open("serverlessWorkflow/DocsHeader.md", encoding='utf-8') as f:
    read_me = f.read()

schema_view = get_schema_view(
    openapi.Info(
        title="ServerLess Workflow API",
        default_version='v0.1',
        description=read_me,
        contact=openapi.Contact(email="priyanshu@advancedware.in"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('task_services.urls')),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
