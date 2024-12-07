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
from django.urls import path
from Dynasty_8.views import (
    index_page, create_adv, create_app,
    AdverListCreateAPIView, ApartmentListCreateAPIView,
    DistrictListCreateAPIView, ProfileListCreateAPIView,
    AdverSearchAPIView
)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_page, name='index_page'),
    path('create/', create_adv, name='create_adv'),
    path('new_app/', create_app, name='create_app'),
    
    # API маршруты
    path('api/adverts/', AdverListCreateAPIView.as_view(), name='api_adverts'),
    path('api/apartments/', ApartmentListCreateAPIView.as_view(), name='api_apartments'),
    path('api/districts/', DistrictListCreateAPIView.as_view(), name='api_districts'),
    path('api/profiles/', ProfileListCreateAPIView.as_view(), name='api_profiles'),
    path('api/adverts/search/', AdverSearchAPIView.as_view(), name='adver_search'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
