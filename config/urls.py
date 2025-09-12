from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework.authtoken import views as drf_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'api/v1/api-token-auth/',
        drf_views.obtain_auth_token,
        name='api-token-auth',
    ),
    path('api/v1/', include('payments.urls')),
    path('api/v1/', include('collects.urls')),
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/v1/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
]
