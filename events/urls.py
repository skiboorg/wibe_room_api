from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet  # и другие вьюшки

router = DefaultRouter()
# Регистрируем события группы
router.register(
    r'communities/(?P<community_slug>[-\w]+)/events',
    EventViewSet,
    basename='group-events'
)

urlpatterns = [
    path('', include(router.urls)),
]