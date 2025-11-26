from rest_framework import serializers
from communities.models import CommunityTag

class CommunityTagSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    class Meta:
        model = CommunityTag
        fields = ["id", "name", "slug", "count"]

    def get_count(self, obj):
        return obj.communities.count()