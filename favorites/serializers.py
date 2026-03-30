from rest_framework import serializers
from .models import Favorite
from infoproducts.serializers import InfoProductListSerializer
from events.serializers import EventListSerializer


class FavoriteProductSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    community_slug = serializers.SerializerMethodField()
    community_name = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ('id', 'product', 'community_slug', 'community_name', 'created_at')

    def get_product(self, obj):
        return InfoProductListSerializer(obj.product, context=self.context).data

    def get_community_slug(self, obj):
        return obj.product.community.slug if obj.product else None

    def get_community_name(self, obj):
        return obj.product.community.name if obj.product else None


class FavoriteEventSerializer(serializers.ModelSerializer):
    event = serializers.SerializerMethodField()
    community_slug = serializers.SerializerMethodField()
    community_name = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ('id', 'event', 'community_slug', 'community_name', 'created_at')

    def get_event(self, obj):
        return EventListSerializer(obj.event, context=self.context).data

    def get_community_slug(self, obj):
        return obj.event.community.slug if obj.event else None

    def get_community_name(self, obj):
        return obj.event.community.name if obj.event else None