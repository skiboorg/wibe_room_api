from rest_framework import serializers
from communities.models import Community, CommunityPhoto, CommunityLink, Membership
from django.contrib.auth import get_user_model



User = get_user_model()

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "avatar"]

class UserFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'avatar',
            'tg_username',
            'full_name',
            'comment',
            'last_login',
            'date_joined',
        ]

class CommunityPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityPhoto
        fields = ["id", "image"]


class CommunityLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityLink
        fields = ["id", "title", "url"]




class CommunityDetailSerializer(serializers.ModelSerializer):

    community_photos = CommunityPhotoSerializer(many=True, read_only=True)
    community_links = CommunityLinkSerializer(many=True, read_only=True)
    community_tags = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()
    first_members = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = [
            "id",
            "name",
            "slug",
            "cover",
            "short_description",
            "long_description",
            "community_photos",
            "community_links",
            "community_tags",
            "members_count",
            "first_members",
            "is_owner",
            "is_member",
            "created_at",
        ]

    def get_community_tags(self, obj):
        from communities.serializers import CommunityTagSerializer
        return CommunityTagSerializer(obj.community_tags.all(), many=True).data

    def get_members_count(self, obj):
        return obj.members.count()

    def get_first_members(self, obj):
        memberships = obj.members.select_related("user")[:6]
        return UserShortSerializer([m.user for m in memberships], many=True).data

    # --------------------------
    # Текущий пользователь — владелец?
    # --------------------------
    def get_is_owner(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        membership = obj.members.filter(user=request.user).first()
        return membership.is_owner if membership else False

    # --------------------------
    # Текущий пользователь — участник?
    # --------------------------
    def get_is_member(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        return obj.members.filter(user=request.user).exists()



# Или если хотите переименовать поле
class MembershipSerializer(serializers.ModelSerializer):
    user = UserFullSerializer(read_only=True)  # source указывает на связь

    class Meta:
        model = Membership
        fields = [
            'user',
            'is_owner',
            'joined_at'
        ]
