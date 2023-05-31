from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('task_services.urls')),

    # Documentation OpenAPI 3.x
    path('', RedirectView.as_view(url='api/schema/redoc', permanent=False), name='index'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
