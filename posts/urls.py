from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupTagViewSet, GroupPostViewSet, CommentViewSet

router = DefaultRouter()

# Теги группы
router.register(
    r'communities/(?P<slug>[-\w]+)/tags',
    GroupTagViewSet,
    basename='group-tags'
)

# Посты группы
router.register(
    r'communities/(?P<slug>[-\w]+)/posts',
    GroupPostViewSet,
    basename='group-posts'
)

# Операции с конкретным комментарием (редактирование, удаление, реакции)
router.register(
    r'comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('', include(router.urls)),
]