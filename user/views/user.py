from rest_framework import viewsets, permissions
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from user.models import User

from user.serializers.create import  UserCreateSerializer
from user.serializers.user import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    from rest_framework.decorators import action

    def get_serializer_class(self):
        if self.action in ("create",):
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="my_comments", permission_classes=[permissions.IsAuthenticated])
    def my_comments(self, request):
        """
        GET /api/users/my_comments/
        Возвращает все комментарии текущего пользователя с инфой о посте и сообществе.
        """
        from posts.models import PostComment
        from posts.serializers import PostCommentWithContextSerializer

        qs = (
            PostComment.objects
            .filter(author=request.user)
            .select_related("post__community", "author")
            .prefetch_related("reactions")
            .order_by("-date")
        )
        serializer = PostCommentWithContextSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="my_communities", permission_classes=[permissions.IsAuthenticated])
    def my_communities(self, request):
        """
        GET /api/users/my_communities/
        Возвращает все сообщества текущего пользователя.
        """
        from communities.models import Community, Membership
        from communities.serializers.list import CommunityListSerializer

        community_ids = Membership.objects.filter(user=request.user).values_list("community_id", flat=True)
        qs = Community.objects.filter(id__in=community_ids)
        serializer = CommunityListSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


class UpdateUser(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer


    def get_object(self):
        return self.request.user

    # def update(self, request, *args, **kwargs):
    #     print(request.data)
    #     serializer = self.get_serializer(data=request.data)