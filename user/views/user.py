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


class UpdateUser(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer


    def get_object(self):
        return self.request.user

    # def update(self, request, *args, **kwargs):
    #     print(request.data)
    #     serializer = self.get_serializer(data=request.data)