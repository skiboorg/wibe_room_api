from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Q
from collections import OrderedDict
import locale
from datetime import datetime

# Устанавливаем локаль для русских названий месяцев
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')
    except:
        pass

from .models import Event, Community
from .serializers import EventListSerializer, EventDetailSerializer, EventCreateUpdateSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class EventViewSet(viewsets.ModelViewSet):
    lookup_field = "slug"
    #pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == "list":
            return EventListSerializer
        elif self.action == "retrieve":
            return EventDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return EventCreateUpdateSerializer
        return EventListSerializer

    def get_queryset(self):
        group_slug = self.kwargs.get("community_slug")
        community = Community.objects.filter(slug=group_slug).first()
        if not community:
            return Event.objects.none()

        qs = Event.objects.filter(community=community)

        # Поиск по названию и описанию
        search = self.request.query_params.get("q")
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(short_description__icontains=search) |
                Q(long_description__icontains=search)
            )

        # Сортировка по дате начала
        qs = qs.order_by("start_date")

        return qs

    # def perform_create(self, serializer):
    #     """Автоматически привязываем событие к сообществу"""
    #     group_slug = self.kwargs.get("slug")
    #     community = Community.objects.filter(slug=group_slug).first()
    #     if community:
    #         serializer.save(community=community)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Группируем события по месяцам
        grouped_events = self._group_events_by_month(queryset)

        # Преобразуем в список для пагинации
        grouped_list = [
            {"month": month, "events": events}
            for month, events in grouped_events.items()
        ]

        page = self.paginate_queryset(grouped_list)
        if page is not None:
            # Сериализуем события для каждой группы
            for group in page:
                group["events"] = EventListSerializer(group["events"], many=True).data
            return self.get_paginated_response(page)

        # Если пагинация не используется
        for group in grouped_list:
            group["events"] = EventListSerializer(group["events"], many=True).data
        return Response(grouped_list)

    def _group_events_by_month(self, queryset):
        """Группирует события по месяцам в формате 'Сентябрь 2024'"""
        grouped = OrderedDict()

        # Русские названия месяцев
        russian_months = {
            1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
            5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
            9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
        }

        for event in queryset:
            if event.start_date:
                # start_date уже является datetime.date объектом
                date_obj = event.start_date
                month_name = russian_months.get(date_obj.month, 'Неизвестно')
                month_key = f"{month_name} {date_obj.year}"
            else:
                # События без даты
                month_key = "Без даты"

            if month_key not in grouped:
                grouped[month_key] = []
            grouped[month_key].append(event)

        return grouped