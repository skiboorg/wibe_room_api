# views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from django.db.models import Q
from communities.models import Community
from .models import InfoProduct
from .serializers import (
    InfoProductListSerializer,
    InfoProductDetailSerializer,
    InfoProductCreateUpdateSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class GroupInfoProductViewSet(viewsets.ModelViewSet):

    lookup_field = "slug"
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return InfoProductCreateUpdateSerializer
        elif self.action == "retrieve":
            return InfoProductDetailSerializer
        return InfoProductListSerializer

    def get_queryset(self):
        group_slug = self.kwargs.get("community_slug")
        community = Community.objects.filter(slug=group_slug).first()
        if not community:
            return InfoProduct.objects.none()

        qs = InfoProduct.objects.filter(community=community)

        # Фильтр по основным продуктам
        is_main = self.request.query_params.get("is_main")
        if is_main and is_main.lower() in ['true', '1']:
            qs = qs.filter(is_main=True)

        # Поиск по названию и описанию
        search = self.request.query_params.get("q")
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(short_description__icontains=search)
            )

        # Сортировка: основные сверху, потом по названию
        qs = qs.order_by("-is_main", "title")

        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Отдельно основные продукты
        main_products = queryset.filter(is_main=True)
        other_products = queryset.filter(is_main=False)

        # Пагинация только для обычных продуктов
        page = self.paginate_queryset(other_products)
        serializer_page = self.get_serializer(page, many=True)
        main_serializer = self.get_serializer(main_products, many=True)

        return Response({
            "main_products": main_serializer.data,
            "products": serializer_page.data,
            "count": self.paginator.page.paginator.count if page else len(other_products),
            "next": self.paginator.get_next_link() if page else None,
            "previous": self.paginator.get_previous_link() if page else None,
        })

    def retrieve(self, request, *args, **kwargs):
        """Получение одного продукта (без product_info_structure)"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Добавляем community к данным перед сохранением
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Обновление продукта по ID"""
        print('update')
        instance = self.get_object()
        print(instance)
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def edit_data(self, request, community_slug=None, slug=None):
        """Получение всех данных продукта для редактирования (с product_info_structure)"""
        print('Edit data called')
        instance = self.get_object()
        serializer = InfoProductCreateUpdateSerializer(instance)
        return Response(serializer.data)
