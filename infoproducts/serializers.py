# serializers.py
from rest_framework import serializers
from .models import InfoProduct,InfoFile

class InfoFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoFile
        fields = ['id', 'file', 'name']

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
    files = InfoFileSerializer(many=True, read_only=True)
    class Meta:
        model = InfoProduct
        fields = [
            'id', 'is_main', 'title', 'slug',
            'cover', 'short_description', 'price', 'product_info','files','main_link'
        ]




class InfoProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/редактирования (все поля)"""
    files = InfoFileSerializer(many=True, read_only=True)

    # Входящие данные из FormData
    _new_files = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)
    _new_files_names = serializers.ListField(child=serializers.CharField(allow_blank=True), write_only=True, required=False)
    _delete_file_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    _update_file_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    _update_file_names = serializers.ListField(child=serializers.CharField(allow_blank=True), write_only=True, required=False)

    class Meta:
        model = InfoProduct
        fields = [
            'id', 'is_main', 'title', 'slug',
            'community',
            'cover', 'short_description', 'price',
            'product_info', 'product_info_structure',
            'files',
            'main_link',
            '_new_files', '_new_files_names',
            '_delete_file_ids',
            '_update_file_ids', '_update_file_names',
        ]
        read_only_fields = ['id', 'slug']

    def validate(self, attrs):
        title = attrs.get('title')
        community = self.context.get('community')

        if community and title:
            if self.instance is None:
                if InfoProduct.objects.filter(title=title, community=community).exists():
                    raise serializers.ValidationError({
                        'title': 'Продукт с таким названием уже существует в этой группе'
                    })
            else:
                if InfoProduct.objects.filter(
                        title=title,
                        community=community
                ).exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError({
                        'title': 'Продукт с таким названием уже существует в этой группе'
                    })

        return attrs

    def _handle_files(self, instance, validated_data):
        # Создание новых файлов
        new_files = validated_data.pop('_new_files', [])
        new_files_names = validated_data.pop('_new_files_names', [])
        for i, file in enumerate(new_files):
            name = new_files_names[i] if i < len(new_files_names) else file.name
            InfoFile.objects.create(product=instance, file=file, name=name)

        # Удаление файлов
        delete_ids = validated_data.pop('_delete_file_ids', [])
        if delete_ids:
            InfoFile.objects.filter(product=instance, id__in=delete_ids).delete()

        # Обновление названий / замена файлов
        update_ids = validated_data.pop('_update_file_ids', [])
        update_names = validated_data.pop('_update_file_names', [])
        for i, file_id in enumerate(update_ids):
            try:
                info_file = InfoFile.objects.get(product=instance, id=file_id)
                if i < len(update_names):
                    info_file.name = update_names[i]
                info_file.save()
            except InfoFile.DoesNotExist:
                pass

    def create(self, validated_data):
        self._handle_files_data = {
            '_new_files': validated_data.pop('_new_files', []),
            '_new_files_names': validated_data.pop('_new_files_names', []),
            '_delete_file_ids': validated_data.pop('_delete_file_ids', []),
            '_update_file_ids': validated_data.pop('_update_file_ids', []),
            '_update_file_names': validated_data.pop('_update_file_names', []),
        }
        instance = super().create(validated_data)
        self._handle_files(instance, self._handle_files_data)
        return instance

    def update(self, instance, validated_data):
        self._handle_files_data = {
            '_new_files': validated_data.pop('_new_files', []),
            '_new_files_names': validated_data.pop('_new_files_names', []),
            '_delete_file_ids': validated_data.pop('_delete_file_ids', []),
            '_update_file_ids': validated_data.pop('_update_file_ids', []),
            '_update_file_names': validated_data.pop('_update_file_names', []),
        }
        instance = super().update(instance, validated_data)
        self._handle_files(instance, self._handle_files_data)
        return instance


class InfoProductCreateUpdateSerializer_old(serializers.ModelSerializer):
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