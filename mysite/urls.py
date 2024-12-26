"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from Dynasty_8.views import (
    index_page, create_adv, create_app,
    DistrictListCreateAPIView, ProfileListCreateAPIView,
    AdverSearchAPIView, AdverViewSet, ApartmentViewSet
)
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from Dynasty_8.views import AdverCreateView
from Dynasty_8.views import test_email_view

# Роутер для ViewSet
router = DefaultRouter()
router.register(r'adverts', AdverViewSet, basename='adverts')
router.register(r'apartments', ApartmentViewSet, basename='apartments')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_page, name='index_page'),
    path('create/', create_adv, name='create_adv'),
    path('new_app/', create_app, name='create_app'),

    # API маршруты
    path('api/districts/', DistrictListCreateAPIView.as_view(), name='api_districts'),
    path('api/profiles/', ProfileListCreateAPIView.as_view(), name='api_profiles'),
    path('api/adverts/search/', AdverSearchAPIView.as_view(), name='adver_search'),
    path('api/', include(router.urls)),

    # Добавление маршрутов из DefaultRouter с префиксом "api/"
    path('api/', include(router.urls)),

     # Схема API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Redoc (альтернативная документация)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('send-test-email/', test_email_view),

    path('class-create-adv/', AdverCreateView.as_view(), name='class_create_adv'),

    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
