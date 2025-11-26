from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from communities.models import Community, Membership
from communities.serializers import (
    CommunityListSerializer,
    CommunityDetailSerializer,
    CommunityCreateUpdateSerializer,
)
from communities.serializers.list import CommunityListShortSerializer
from communities.serializers.detail import MembershipSerializer


class CommunityPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all()
    lookup_field = "slug"
    pagination_class = CommunityPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_serializer_class(self):
        if self.action == "list":
            return CommunityListSerializer

        if self.action == "retrieve":
            return CommunityDetailSerializer

        if self.action in ("create", "update", "partial_update"):
            return CommunityCreateUpdateSerializer

        return CommunityDetailSerializer


    def get_queryset(self):
        qs = super().get_queryset()

        # Фильтр по тегу
        tag_slug = self.request.query_params.get('tag', '')
        if tag_slug and tag_slug != 'all':
            qs = qs.filter(community_tags__slug=tag_slug)

        # Поиск по названию или описанию
        search_query = self.request.query_params.get('q', '')
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(long_description__icontains=search_query)
            )

        return qs.distinct()  # distinct на случай ManyToMany дубли

    # -------------------------------------------------
    # 🔥 ACTION: получить все сообщества текущего юзера
    # -------------------------------------------------
    @action(detail=False, methods=["get"], url_path="my")
    def my(self, request):
        user = request.user
        community_ids = Membership.objects.filter(user=user).values_list("community_id", flat=True)
        communities = Community.objects.filter(id__in=community_ids)
        serializer = CommunityListShortSerializer(communities, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="members")
    def members(self, request, slug=None):
        community = self.get_object()
        memberships = Membership.objects.filter(
            community=community
        ).select_related('user')

        serializer = MembershipSerializer(memberships, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="join")
    def join(self, request, slug=None):
        print(request.user)
        obj = self.get_object()
        Membership.objects.create(user=request.user, community=obj)
        return Response(status=200)


def create(self, request, *args, **kwargs):
        print("=== REQUEST DATA ===")
        for key, value in request.data.items():
            print(f"{key}: {value}")

        serializer = self.get_serializer(data=request.data)

        # Временно убираем raise_exception чтобы увидеть ошибки
        # serializer.is_valid(raise_exception=True)
        if not serializer.is_valid():
            print("=== VALIDATION ERRORS ===")
            print(serializer.errors)
            return Response(serializer.errors, status=400)

        instance = serializer.save()

        print("=== SUCCESSFULLY CREATED ===")
        detail_serializer = CommunityDetailSerializer(instance, context=self.get_serializer_context())
        return Response(detail_serializer.data, status=201)
