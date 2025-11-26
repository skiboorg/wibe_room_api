from rest_framework import viewsets, permissions
from rest_framework.response import Response
from communities.models import Community
from .models import Tag
from .serializers import TagSerializer, PostSerializer, PostCreateUpdateSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from django.db.models import Q
from .models import Post


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class GroupTagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer

    def get_queryset(self):
        group_slug = self.kwargs.get("slug")
        community = Community.objects.filter(slug=group_slug).first()
        if not community:
            return Tag.objects.none()
        return Tag.objects.filter(community=community)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # Добавляем искусственный тег "Все" в начало
        all_tag = {
            "id": 0,
            "name": "Все",
            "slug": "all"
        }
        data.insert(0, all_tag)

        return Response(data)



class GroupPostViewSet(viewsets.ModelViewSet):
    lookup_field = "id"
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PostCreateUpdateSerializer
        return PostSerializer

    def get_queryset(self):
        group_slug = self.kwargs.get("slug")
        community = Community.objects.filter(slug=group_slug).first()
        if not community:
            return Post.objects.none()

        qs = Post.objects.filter(community=community)

        # Фильтр по тегу
        tag_slug = self.request.query_params.get("tag")
        print(tag_slug)
        if tag_slug and tag_slug != 'all':
            qs = qs.filter(post_tags__slug=tag_slug)

        # Поиск по содержанию
        search = self.request.query_params.get("q")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(text__icontains=search))

        # Сортировка по дате, свежие сверху
        qs = qs.order_by("-date")

        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Отдельно "прикреплённые" посты
        pinned_posts = queryset.filter(is_pinned=True)
        unpinned_posts = queryset.filter(is_pinned=False)

        # Пагинация только для обычных постов
        page = self.paginate_queryset(unpinned_posts)
        serializer_page = self.get_serializer(page, many=True)
        pinned_serializer = self.get_serializer(pinned_posts, many=True)

        # Возвращаем данные: pinned вне пагинации, posts с пагинацией
        return Response({
            "pinned": pinned_serializer.data,
            "posts": serializer_page.data,
            "count": self.paginator.page.paginator.count if page else len(unpinned_posts),
            "next": self.paginator.get_next_link() if page else None,
            "previous": self.paginator.get_previous_link() if page else None,
        })