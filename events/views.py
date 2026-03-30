from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Q
from collections import OrderedDict
import locale

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

        qs = Event.objects.filter(community=community)\
            .prefetch_related('favorited_by')

        search = self.request.query_params.get("q")
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(short_description__icontains=search) |
                Q(long_description__icontains=search)
            )

        return qs.order_by("start_date")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        grouped_events = self._group_events_by_month(queryset)

        grouped_list = [
            {"month": month, "events": events}
            for month, events in grouped_events.items()
        ]

        # контекст с request — чтобы is_favorite работал
        serializer_context = self.get_serializer_context()

        page = self.paginate_queryset(grouped_list)
        if page is not None:
            for group in page:
                group["events"] = EventListSerializer(
                    group["events"], many=True, context=serializer_context
                ).data
            return self.get_paginated_response(page)

        for group in grouped_list:
            group["events"] = EventListSerializer(
                group["events"], many=True, context=serializer_context
            ).data
        return Response(grouped_list)

    def _group_events_by_month(self, queryset):
        grouped = OrderedDict()
        russian_months = {
            1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
            5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
            9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
        }
        for event in queryset:
            if event.start_date:
                date_obj = event.start_date
                month_name = russian_months.get(date_obj.month, 'Неизвестно')
                month_key = f"{month_name} {date_obj.year}"
            else:
                month_key = "Без даты"

            if month_key not in grouped:
                grouped[month_key] = []
            grouped[month_key].append(event)

        return grouped