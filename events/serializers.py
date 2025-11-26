from rest_framework import serializers
from django.utils import timezone
from datetime import datetime
from communities.models import Community
from .models import Event


class EventListSerializer(serializers.ModelSerializer):
    """Сериализатор для получения событий"""

    class Meta:
        model = Event
        fields = [
            'id',
            'start_date',
            'time_text',
            'title',
            'slug',
            'cover',
            'short_description',
        ]
        read_only_fields = ['id', 'community']


class EventDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для получения одного события"""

    class Meta:
        model = Event
        fields = [
            'id',
            'start_date',
            'time_text',
            'title',
            'slug',
            'cover',
            'short_description',
            'long_description'
        ]
        read_only_fields = ['id', 'community']


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и редактирования событий"""
    community = serializers.PrimaryKeyRelatedField(
        queryset=Community.objects.all()
    )

    class Meta:
        model = Event
        fields = [
            'community',
            'start_date',
            'time_text',
            'title',
            'cover',
            'short_description',
            'long_description'
        ]

    def validate_title(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("Название события не может быть пустым")
        return value.strip()