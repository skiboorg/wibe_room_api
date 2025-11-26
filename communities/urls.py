from rest_framework.routers import DefaultRouter
from django.urls import path, include
from communities.views.community import CommunityViewSet
from communities.views.tag import TagViewSet

router = DefaultRouter()
router.register("communities", CommunityViewSet, basename="communities")
router.register(r'communities_tags', TagViewSet, basename='tags')

urlpatterns = [
    path("", include(router.urls)),
]
