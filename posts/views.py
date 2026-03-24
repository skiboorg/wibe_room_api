from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, F
from django.shortcuts import get_object_or_404

from communities.models import Community
from .models import Tag, Post, PostComment, PostReaction, CommentReaction, ReactionType
from .serializers import (
    TagSerializer,
    PostSerializer,
    PostCreateUpdateSerializer,
    PostCommentSerializer,
    PostCommentCreateSerializer,
    PostReactionSerializer,
    CommentReactionSerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


# ──────────────────────────────────────────────
# Теги группы
# ──────────────────────────────────────────────

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
        data.insert(0, {"id": 0, "name": "Все", "slug": "all"})
        return Response(data)


# ──────────────────────────────────────────────
# Посты группы
# ──────────────────────────────────────────────

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

        tag_slug = self.request.query_params.get("tag")
        if tag_slug and tag_slug != 'all':
            qs = qs.filter(post_tags__slug=tag_slug)

        search = self.request.query_params.get("q")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(text__icontains=search))

        return qs.order_by("-date")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        pinned_posts = queryset.filter(is_pinned=True)
        unpinned_posts = queryset.filter(is_pinned=False)

        page = self.paginate_queryset(unpinned_posts)
        serializer_page = self.get_serializer(page, many=True)
        pinned_serializer = self.get_serializer(pinned_posts, many=True)

        return Response({
            "pinned": pinned_serializer.data,
            "posts": serializer_page.data,
            "count": self.paginator.page.paginator.count if page else len(unpinned_posts),
            "next": self.paginator.get_next_link() if page else None,
            "previous": self.paginator.get_previous_link() if page else None,
        })

    # ── Просмотры ─────────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="view")
    def track_view(self, request, slug=None, id=None):
        """
        POST /communities/{slug}/posts/{id}/view/
        Инкрементирует счётчик просмотров. Вызывается с фронта при открытии диалога.
        Не требует авторизации — считаем всех.
        """
        Post.objects.filter(pk=self.get_object().pk).update(views=F('views') + 1)
        return Response(status=204)

    # ── Реакции на пост ──────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="react", permission_classes=[permissions.IsAuthenticated])
    def react(self, request, slug=None, id=None):
        """
        POST /communities/{slug}/posts/{id}/react/
        Body: { "reaction": "like" }
        Повторный запрос с той же реакцией — снимает её (toggle).
        Другая реакция — заменяет.
        """
        post = self.get_object()
        reaction_type = request.data.get("reaction")

        if reaction_type not in ReactionType.values:
            return Response({"detail": f"Допустимые реакции: {ReactionType.values}"}, status=400)

        existing = PostReaction.objects.filter(post=post, author=request.user).first()

        if existing:
            if existing.reaction == reaction_type:
                # toggle off
                existing.delete()
                return Response({"detail": "Реакция снята"}, status=200)
            else:
                # сменить реакцию
                existing.reaction = reaction_type
                existing.save()
                return Response(PostReactionSerializer(existing).data, status=200)
        else:
            r = PostReaction.objects.create(post=post, reaction=reaction_type, author=request.user)
            return Response(PostReactionSerializer(r).data, status=201)

    # ── Комментарии к посту ──────────────────────────────────────

    @action(detail=True, methods=["get"], url_path="comments")
    def comments(self, request, slug=None, id=None):
        """
        GET /communities/{slug}/posts/{id}/comments/
        Возвращает только корневые комментарии (parent=null) с вложенными replies.
        """
        post = self.get_object()
        qs = post.comments.filter(parent__isnull=True).order_by("date") \
            .prefetch_related("replies__reactions", "replies__author", "reactions", "author")
        serializer = PostCommentSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="comments/add", permission_classes=[permissions.IsAuthenticated])
    def add_comment(self, request, slug=None, id=None):
        """
        POST /communities/{slug}/posts/{id}/comments/add/
        Body: multipart/form-data  { text, parent (optional), image (optional) }
        """
        post = self.get_object()
        serializer = PostCommentCreateSerializer(data={
            "post": post.id,
            "text": request.data.get("text", ""),
            "parent": request.data.get("parent") or None,
            "image": request.FILES.get("image"),
        })
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(author=request.user)
        return Response(PostCommentSerializer(comment, context={"request": request}).data, status=201)


# ──────────────────────────────────────────────
# Комментарии (редактирование, удаление, реакции)
# ──────────────────────────────────────────────

class CommentViewSet(viewsets.GenericViewSet):
    """
    Маршруты:
      PATCH  /comments/{pk}/         — редактировать
      DELETE /comments/{pk}/         — удалить
      POST   /comments/{pk}/react/   — поставить/снять реакцию
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = PostComment.objects.all()

    def partial_update(self, request, pk=None):
        comment = get_object_or_404(PostComment, pk=pk)
        if comment.author != request.user:
            return Response({"detail": "Нет доступа"}, status=403)
        text = request.data.get("text")
        if not text:
            return Response({"detail": "Поле text обязательно"}, status=400)
        comment.text = text
        comment.save()
        return Response(PostCommentSerializer(comment, context={"request": request}).data)

    def destroy(self, request, pk=None):
        comment = get_object_or_404(PostComment, pk=pk)
        if comment.author != request.user and not request.user.is_staff:
            return Response({"detail": "Нет доступа"}, status=403)
        comment.delete()
        return Response(status=204)

    @action(detail=True, methods=["post"], url_path="react")
    def react(self, request, pk=None):
        """
        POST /comments/{pk}/react/
        Body: { "reaction": "like" }
        Toggle: та же реакция — снимает, другая — заменяет.
        """
        comment = get_object_or_404(PostComment, pk=pk)
        reaction_type = request.data.get("reaction")

        if reaction_type not in ReactionType.values:
            return Response({"detail": f"Допустимые реакции: {ReactionType.values}"}, status=400)

        existing = CommentReaction.objects.filter(comment=comment, author=request.user).first()

        if existing:
            if existing.reaction == reaction_type:
                existing.delete()
                return Response({"detail": "Реакция снята"}, status=200)
            else:
                existing.reaction = reaction_type
                existing.save()
                return Response(CommentReactionSerializer(existing).data, status=200)
        else:
            r = CommentReaction.objects.create(comment=comment, reaction=reaction_type, author=request.user)
            return Response(CommentReactionSerializer(r).data, status=201)