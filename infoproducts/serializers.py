# serializers.py
from rest_framework import serializers
from .models import InfoProduct


class InfoProductListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка продуктов (без product_info и product_info_structure)"""

    class Meta:
        model = InfoProduct
        fields = [
            'id', 'is_main', 'title', 'slug',
            'cover', 'short_description', 'price'
        ]


class InfoProductDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра (без product_info_structure)"""

    class Meta:
        model = InfoProduct
        fields = [
            'id', 'is_main', 'title', 'slug',
            'cover', 'short_description', 'price', 'product_info'
        ]


class InfoProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/редактирования (все поля)"""

    class Meta:
        model = InfoProduct
        fields = [
            'id', 'is_main', 'title', 'slug',
            'community',
            'cover', 'short_description', 'price',
            'product_info', 'product_info_structure'
        ]
        read_only_fields = ['id', 'slug']

    def validate(self, attrs):
        title = attrs.get('title')
        community = self.context.get('community')  # Будет передан из view

        if community and title:
            # При создании проверяем уникальность
            if self.instance is None:  # Создание
                if InfoProduct.objects.filter(title=title, community=community).exists():
                    raise serializers.ValidationError({
                        'title': 'Продукт с таким названием уже существует в этой группе'
                    })
            else:  # Обновление
                if InfoProduct.objects.filter(
                        title=title,
                        community=community
                ).exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError({
                        'title': 'Продукт с таким названием уже существует в этой группе'
                    })

        return attrs

    # def create(self, validated_data):
    #     # Community передается из view
    #     community = self.context.get('community')
    #     if not community:
    #         raise serializers.ValidationError("Community is required")
    #
    #     validated_data['community'] = community
    #     return super().create(validated_data)