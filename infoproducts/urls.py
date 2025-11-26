# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupInfoProductViewSet


router = DefaultRouter()
# Регистрируем инфопродукты группы
router.register(
    r'communities/(?P<community_slug>[-\w]+)/infoproducts',
    GroupInfoProductViewSet,
    basename='group-infoproducts'
)

urlpatterns = [
    path('', include(router.urls)),
]