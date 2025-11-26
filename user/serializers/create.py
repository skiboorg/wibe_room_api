from rest_framework import serializers
from user.models import User

from djoser.conf import settings
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, transaction
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    default_error_messages = {
        "cannot_create_user": settings.CONSTANTS.messages.CANNOT_CREATE_USER_ERROR
    }

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            "email",
            "full_name",
            'password',
        )

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")


        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            print(e)
            raise serializers.ValidationError(
                {"password": serializer_error["non_field_errors"]}
            )

        return attrs

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")
        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            token = default_token_generator.make_token(user)
            user.is_active = True
            user.activate_token = token
            user.save(update_fields=["is_active"])


        return user
