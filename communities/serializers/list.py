from rest_framework import serializers
from communities.models import Community



class CommunityListSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    class Meta:
        model = Community
        fields = [
            "id",
            "name",
            "slug",
            "cover",
            "short_description",
            "created_at",
            "members_count",
            "is_member"
        ]

    def get_members_count(self, obj):
        return obj.members.count()



    def get_is_member(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        return obj.members.filter(user=request.user).exists()

class CommunityListShortSerializer(CommunityListSerializer):
    class Meta:
        model = Community
        fields = [
            "name",
            "slug",
            "cover",
            "members_count"
        ]
