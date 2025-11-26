from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views.user import UserViewSet

router = DefaultRouter()
router.register(r"", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
]