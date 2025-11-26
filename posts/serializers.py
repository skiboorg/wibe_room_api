from rest_framework import serializers

from communities.models import Membership, Community
from .models import Tag, Post, PostPhoto, PostComment, PostReaction, ReactionType

from django.contrib.auth import get_user_model

from pytils.translit import slugify

User = get_user_model()

class UserShortSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()  # новое поле

    class Meta:
        model = User
        fields = ["id", "avatar", "full_name", "is_admin"]

    def get_is_admin(self, obj):
        """
        Проверяем, является ли пользователь админом сообщества.
        В объекте `context` должен быть передан `community`.
        """
        community = self.context.get("community")

        if not community:
            return False

        return Membership.objects.filter(
            user=obj, community=community, is_owner=True
        ).exists()

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")

class PostPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostPhoto
        fields = ("id", "image")

class PostCommentSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)
    class Meta:
        model = PostComment
        fields = ("id", "post", "author", "text", "date")
        read_only_fields = ("date",)

class PostReactionSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)
    class Meta:
        model = PostReaction
        fields = ("id", "post", "reaction", "author")

class PostSerializer(serializers.ModelSerializer):
    photos = PostPhotoSerializer(many=True, read_only=True)
    #comments = PostCommentSerializer(many=True, read_only=True)
    reactions = PostReactionSerializer(many=True, read_only=True)
    post_tags = TagSerializer(many=True, read_only=True)
    added_by = UserShortSerializer(read_only=True)
    is_own = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = (
            "id",
            "community",
            "post_tags",
            "date",
            "added_by",
            "title",
            "text",
            "is_pinned",
            "photos",
            "vk_video_link",
            "is_own",
            "reactions")
        read_only_fields = ("date", "added_by")

    def get_is_own(self, obj):
        # Получаем пользователя из контекста
        user = self.context.get('request').user if self.context.get('request') else None

        # Альтернативно: получаем из дополнительного контекста
        if not user and 'user' in self.context:
            user = self.context['user']

        if user and user.is_authenticated:
            return obj.added_by == user
        return False

    def to_representation(self, instance):
        # Передаем community вложенному сериализатору added_by
        self.fields['added_by'].context['community'] = instance.community
        return super().to_representation(instance)




class PostCreateUpdateSerializer(serializers.ModelSerializer):
    post_tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False
    )
    new_tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False
    )
    photos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    community = serializers.PrimaryKeyRelatedField(
        queryset=Community.objects.all()
    )
    added_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'community',
            'post_tags',
            'vk_video_link',
            'text',
            'is_pinned',
            'new_tags',
            'photos',
            'added_by'
        ]
        read_only_fields = ['id', 'date']

    def create(self, validated_data):
        # Извлекаем данные для новых тегов и фото
        new_tags_data = validated_data.pop('new_tags', [])
        photos_data = validated_data.pop('photos', [])
        post_tags = validated_data.pop('post_tags', [])

        # Создаем пост
        post = Post.objects.create(**validated_data)

        # Добавляем существующие теги
        if post_tags:
            post.post_tags.set(post_tags)

        # Создаем новые теги
        for tag_name in new_tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_name.strip(),
                community=post.community,
                defaults={'slug': slugify(tag_name.strip())}
            )
            post.post_tags.add(tag)

        # Создаем фото
        for photo_data in photos_data:
            PostPhoto.objects.create(post=post, image=photo_data)

        return post

    def update(self, instance, validated_data):
        # Обработка обновления поста
        new_tags_data = validated_data.pop('new_tags', [])
        photos_data = validated_data.pop('photos', [])
        post_tags = validated_data.pop('post_tags', [])

        # Обновляем основные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Обновляем теги
        if post_tags is not None:
            instance.post_tags.set(post_tags)

        # Добавляем новые теги
        for tag_name in new_tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_name.strip(),
                community=instance.community,
                defaults={'slug': slugify(tag_name.strip())}
            )
            instance.post_tags.add(tag)

        # Добавляем новые фото (если нужно)
        for photo_data in photos_data:
            PostPhoto.objects.create(post=instance, image=photo_data)

        return instance

    def to_representation(self, instance):
        # При чтении возвращаем полное представление
        from .serializers import PostSerializer  # Импортируем здесь чтобы избежать циклического импорта
        return PostSerializer(instance, context=self.context).data