from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Count, Case, When, Value, IntegerField
from communities.models import CommunityTag
from communities.serializers import CommunityTagSerializer

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommunityTag.objects.all()
    serializer_class = CommunityTagSerializer

    def get_queryset(self):
        # Получаем обычные теги с подсчетом сообществ
        qs = CommunityTag.objects.annotate(
            communities_count=Count('communities')
        ).order_by('-communities_count')

        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()

        # Создаем искусственный тег "Все"
        all_tag = CommunityTag(
            id=0,  # фиктивный id
            name="Все",
            slug="all"
        )
        # Добавляем поле communities_count
        all_tag.communities_count = CommunityTag.objects.aggregate(
            total=Count('communities')
        )['total']

        # Сериализуем обычные теги
        serializer = self.get_serializer(qs, many=True)

        # Объединяем с искусственным тегом "Все"
        data = [{
            "id": all_tag.id,
            "name": all_tag.name,
            "slug": all_tag.slug,
            "count": all_tag.communities_count
        }] + serializer.data

        return Response(data)
