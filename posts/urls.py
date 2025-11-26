from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupTagViewSet, GroupPostViewSet

router = DefaultRouter()
# Регистрируем теги группы
router.register(
    r'communities/(?P<slug>[-\w]+)/tags',
    GroupTagViewSet,
    basename='group-tags'
)
# Регистрируем посты группы
router.register(
    r'communities/(?P<slug>[-\w]+)/posts',
    GroupPostViewSet,
    basename='group-posts'
)

urlpatterns = [
    path('', include(router.urls)),
]
