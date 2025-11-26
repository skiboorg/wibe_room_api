from djoser.serializers import TokenCreateSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class CustomTokenCreateSerializer(TokenCreateSerializer):
    login = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)



    def validate(self, attrs):
        login = attrs.get("login")
        password = attrs.get("password")
        print(login, password)
        # ищем пользователя по email/username/телефону
        try:
            user = User.objects.get(email=login)
        except User.DoesNotExist:
            try:
                user = User.objects.get(phone=login)
            except User.DoesNotExist:
                raise serializers.ValidationError("User not found")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid password")
        print(user)

        self.user = user
        return attrs
