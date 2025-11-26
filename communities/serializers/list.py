from rest_framework import serializers
from communities.models import Community



class CommunityListSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    class Meta:
        model = Community
        fields = [
            "id",
            "name",
            "slug",
            "cover",
            "short_description",
            "created_at",
            "members_count"
        ]

    def get_members_count(self, obj):
        return obj.members.count()


class CommunityListShortSerializer(CommunityListSerializer):
    class Meta:
        model = Community
        fields = [
            "name",
            "slug",
            "cover",
            "members_count"
        ]
