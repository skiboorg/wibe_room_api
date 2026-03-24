from rest_framework import serializers

from communities.models import Membership, Community
from .models import Tag, Post, PostPhoto, PostComment, PostReaction, CommentReaction, ReactionType

from django.contrib.auth import get_user_model
from pytils.translit import slugify

User = get_user_model()


class UserShortSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "avatar", "full_name", "is_admin"]

    def get_is_admin(self, obj):
        community = self.context.get("community")
        if not community:
            return False
        return Membership.objects.filter(user=obj, community=community, is_owner=True).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class PostPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostPhoto
        fields = ("id", "image")


# ──────────────────────────────────────────────
# Реакции на комментарий
# ──────────────────────────────────────────────

class CommentReactionSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)

    class Meta:
        model = CommentReaction
        fields = ("id", "comment", "reaction", "author")


# ──────────────────────────────────────────────
# Комментарии (с вложенными ответами и реакциями)
# ──────────────────────────────────────────────

class PostCommentReplySerializer(serializers.ModelSerializer):
    """Сериализатор для ответов на комментарий (без рекурсии)."""
    author = UserShortSerializer(read_only=True)
    reactions = CommentReactionSerializer(many=True, read_only=True)
    reactions_count = serializers.SerializerMethodField()
    my_reaction = serializers.SerializerMethodField()
    is_own = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = ("id", "post", "parent", "author", "text", "image", "date",
                  "reactions", "reactions_count", "my_reaction", "is_own")
        read_only_fields = ("date",)

    def get_reactions_count(self, obj):
        counts = {}
        for r in obj.reactions.all():
            counts[r.reaction] = counts.get(r.reaction, 0) + 1
        return counts

    def get_my_reaction(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            r = obj.reactions.filter(author=request.user).first()
            return r.reaction if r else None
        return None

    def get_is_own(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False


class PostCommentSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)
    replies = PostCommentReplySerializer(many=True, read_only=True)
    reactions = CommentReactionSerializer(many=True, read_only=True)
    reactions_count = serializers.SerializerMethodField()
    my_reaction = serializers.SerializerMethodField()
    is_own = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = ("id", "post", "parent", "author", "text", "image", "date",
                  "replies", "reactions", "reactions_count", "my_reaction", "is_own")
        read_only_fields = ("date",)

    def get_reactions_count(self, obj):
        counts = {}
        for r in obj.reactions.all():
            counts[r.reaction] = counts.get(r.reaction, 0) + 1
        return counts

    def get_my_reaction(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            r = obj.reactions.filter(author=request.user).first()
            return r.reaction if r else None
        return None

    def get_is_own(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False


class PostCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = ("id", "post", "parent", "text", "image", "date")
        read_only_fields = ("date",)


# ──────────────────────────────────────────────
# Реакции на пост
# ──────────────────────────────────────────────

class PostReactionSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)

    class Meta:
        model = PostReaction
        fields = ("id", "post", "reaction", "author")


# ──────────────────────────────────────────────
# Посты
# ──────────────────────────────────────────────

class PostSerializer(serializers.ModelSerializer):
    photos = PostPhotoSerializer(many=True, read_only=True)
    reactions = PostReactionSerializer(many=True, read_only=True)
    post_tags = TagSerializer(many=True, read_only=True)
    added_by = UserShortSerializer(read_only=True)
    is_own = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()
    my_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id", "community", "post_tags", "date", "added_by",
            "title", "text", "is_pinned", "photos", "vk_video_link",
            "is_own", "reactions", "reactions_count", "my_reaction",
            "comments_count", "views",
        )
        read_only_fields = ("date", "added_by")

    def get_is_own(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if not user and 'user' in self.context:
            user = self.context['user']
        if user and user.is_authenticated:
            return obj.added_by == user
        return False

    def get_comments_count(self, obj):
        # только корневые комментарии (без ответов)
        return obj.comments.filter(parent__isnull=True).count()

    def get_reactions_count(self, obj):
        counts = {}
        for r in obj.reactions.all():
            counts[r.reaction] = counts.get(r.reaction, 0) + 1
        return counts

    def get_my_reaction(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            r = obj.reactions.filter(author=request.user).first()
            return r.reaction if r else None
        return None

    def to_representation(self, instance):
        self.fields['added_by'].context['community'] = instance.community
        return super().to_representation(instance)


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    post_tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=False
    )
    new_tags = serializers.ListField(
        child=serializers.CharField(max_length=100), write_only=True, required=False
    )
    photos = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    community = serializers.PrimaryKeyRelatedField(queryset=Community.objects.all())
    added_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'community', 'post_tags', 'vk_video_link',
            'text', 'is_pinned', 'new_tags', 'photos', 'added_by'
        ]
        read_only_fields = ['id', 'date']

    def create(self, validated_data):
        new_tags_data = validated_data.pop('new_tags', [])
        photos_data = validated_data.pop('photos', [])
        post_tags = validated_data.pop('post_tags', [])

        post = Post.objects.create(**validated_data)

        if post_tags:
            post.post_tags.set(post_tags)

        for tag_name in new_tags_data:
            tag, _ = Tag.objects.get_or_create(
                name=tag_name.strip(),
                community=post.community,
                defaults={'slug': slugify(tag_name.strip())}
            )
            post.post_tags.add(tag)

        for photo_data in photos_data:
            PostPhoto.objects.create(post=post, image=photo_data)

        return post

    def update(self, instance, validated_data):
        new_tags_data = validated_data.pop('new_tags', [])
        photos_data = validated_data.pop('photos', [])
        post_tags = validated_data.pop('post_tags', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if post_tags is not None:
            instance.post_tags.set(post_tags)

        for tag_name in new_tags_data:
            tag, _ = Tag.objects.get_or_create(
                name=tag_name.strip(),
                community=instance.community,
                defaults={'slug': slugify(tag_name.strip())}
            )
            instance.post_tags.add(tag)

        for photo_data in photos_data:
            PostPhoto.objects.create(post=instance, image=photo_data)

        return instance

    def to_representation(self, instance):
        return PostSerializer(instance, context=self.context).data


class PostShortSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import Post
        model = Post
        fields = ("id", "title")


class CommunityShortSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    cover = serializers.ImageField()


class PostCommentWithContextSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)
    reactions_count = serializers.SerializerMethodField()
    my_reaction = serializers.SerializerMethodField()
    post_title = serializers.SerializerMethodField()
    post_id = serializers.SerializerMethodField()
    community_name = serializers.SerializerMethodField()
    community_slug = serializers.SerializerMethodField()
    community_cover = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = (
            "id", "text", "image", "date", "author",
            "reactions_count", "my_reaction",
            "post_id", "post_title",
            "community_name", "community_slug", "community_cover",
        )

    def get_reactions_count(self, obj):
        counts = {}
        for r in obj.reactions.all():
            counts[r.reaction] = counts.get(r.reaction, 0) + 1
        return counts

    def get_my_reaction(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            r = obj.reactions.filter(author=request.user).first()
            return r.reaction if r else None
        return None

    def get_post_id(self, obj):
        return obj.post_id

    def get_post_title(self, obj):
        return obj.post.title or obj.post.text[:20]

    def get_community_name(self, obj):
        return obj.post.community.name

    def get_community_slug(self, obj):
        return obj.post.community.slug

    def get_community_cover(self, obj):
        request = self.context.get("request")
        cover = obj.post.community.cover
        if cover and request:
            return request.build_absolute_uri(cover.url)
        return None