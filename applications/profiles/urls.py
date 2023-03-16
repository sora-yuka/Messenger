from django.urls import path, include
from rest_framework.routers import DefaultRouter

from applications.profiles.views import ProfileViewSet

router = DefaultRouter()
router.register('', ProfileViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
