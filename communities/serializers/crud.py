import json

from rest_framework import serializers
from communities.models import Community, CommunityPhoto, CommunityLink, CommunityTag, Membership


class CommunityCreateUpdateSerializer(serializers.ModelSerializer):
    community_tags = serializers.PrimaryKeyRelatedField(
        queryset=CommunityTag.objects.all(),
        many=True,
        required=False
    )
    community_photos = serializers.ListField(
        child=serializers.ImageField(write_only=True),
        required=False,
        write_only=True
    )
    community_links = serializers.ListField(
        child=serializers.CharField(),  # ✅ Изменили на CharField
        required=False,
        write_only=True
    )

    photos_to_delete = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )

    class Meta:
        model = Community
        fields = [
            "name",
            "slug",
            "cover",
            "community_tags",
            "short_description",
            "long_description",
            "community_photos",
            "community_links",
            "photos_to_delete",
        ]

    def validate_community_links(self, value):
        """Парсим JSON строки в словари для дальнейшей обработки"""
        if not value:
            return value

        parsed_links = []
        for link_json in value:
            if isinstance(link_json, dict):
                # Если уже словарь - оставляем как есть
                parsed_links.append(link_json)
            elif isinstance(link_json, str):
                try:
                    link_data = json.loads(link_json)
                    if isinstance(link_data, dict):
                        parsed_links.append(link_data)
                except json.JSONDecodeError:
                    # Пропускаем некорректные JSON
                    continue
        return parsed_links

    def create(self, validated_data):
        community_photos = validated_data.pop("community_photos", [])
        community_links = validated_data.pop("community_links", [])  # Теперь это уже словари
        community_tags = validated_data.pop("community_tags", [])

        community = Community.objects.create(**validated_data)

        # Добавляем теги
        community.community_tags.set(community_tags)

        # Создаем фотографии
        for photo in community_photos:
            CommunityPhoto.objects.create(community=community, image=photo)

        # Создаем ссылки - теперь community_links уже словари
        for link_data in community_links:
            CommunityLink.objects.create(
                community=community,
                title=link_data.get("title"),
                url=link_data.get("url")
            )

        # Создаем membership для создателя
        Membership.objects.create(
            user=self.context['request'].user,
            community=community,
            is_owner=True
        )

        return community

    def update(self, instance, validated_data):
        photos_to_delete = validated_data.pop("photos_to_delete", [])
        community_photos = validated_data.pop("community_photos", None)
        community_links = validated_data.pop("community_links", None)
        community_tags = validated_data.pop("community_tags", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        if photos_to_delete:
            CommunityPhoto.objects.filter(id__in=photos_to_delete).delete()

        if community_tags is not None:
            instance.community_tags.set(community_tags)

        if community_photos is not None:
            # instance.community_photos.all().delete()
            for photo in community_photos:
                CommunityPhoto.objects.create(community=instance, image=photo)

        # if community_links is not None:
        instance.community_links.all().delete()
        if community_links is not None:
            for link_data in community_links:
                CommunityLink.objects.create(
                    community=instance,
                    title=link_data.get("title"),
                    url=link_data.get("url")
                )

        return instance