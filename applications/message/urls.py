from django.urls import path, include
from rest_framework.routers import DefaultRouter
from applications.message.views import MessageViewSet

router = DefaultRouter()
router.register("", MessageViewSet)

urlpatterns = [
    path("", include(router.urls))
]