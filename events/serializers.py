from rest_framework import serializers
from communities.models import Community
from .models import Event


class EventListSerializer(serializers.ModelSerializer):
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'start_date', 'time_text', 'title',
            'slug', 'cover', 'short_description', 'is_favorite'
        ]
        read_only_fields = ['id', 'community']

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        from favorites.models import Favorite
        return Favorite.objects.filter(user=request.user, event_id=obj.pk).exists()


class EventDetailSerializer(serializers.ModelSerializer):
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'start_date', 'time_text', 'title',
            'slug', 'cover', 'short_description', 'long_description', 'is_favorite'
        ]
        read_only_fields = ['id', 'community']

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        from favorites.models import Favorite
        return Favorite.objects.filter(user=request.user, event_id=obj.pk).exists()


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    community = serializers.PrimaryKeyRelatedField(queryset=Community.objects.all())

    class Meta:
        model = Event
        fields = [
            'community', 'start_date', 'time_text', 'title',
            'cover', 'short_description', 'long_description'
        ]

    def validate_title(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError('Название события не может быть пустым')
        return value.strip()