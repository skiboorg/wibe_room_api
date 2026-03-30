from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Favorite
from .serializers import FavoriteProductSerializer, FavoriteEventSerializer
from infoproducts.models import InfoProduct
from events.models import Event


class FavoriteViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='products')
    def my_products(self, request):
        """GET /api/favorites/products/ — избранные продукты"""
        qs = Favorite.objects.filter(user=request.user, product__isnull=False)\
            .select_related('product__community').order_by('-created_at')
        return Response(FavoriteProductSerializer(qs, many=True,context={'request': request}).data)

    @action(detail=False, methods=['get'], url_path='events')
    def my_events(self, request):
        """GET /api/favorites/events/ — избранные мероприятия"""
        qs = Favorite.objects.filter(user=request.user, event__isnull=False)\
            .select_related('event__community').order_by('-created_at')
        return Response(FavoriteEventSerializer(qs, many=True,context={'request': request}).data)

    @action(detail=False, methods=['post'], url_path='toggle_product')
    def toggle_product(self, request):
        """
        POST /api/favorites/toggle_product/  { product_id: N }
        Toggle: добавляет или убирает продукт из избранного.
        """
        product_id = request.data.get('product_id')
        product = get_object_or_404(InfoProduct, id=product_id)
        fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
        if not created:
            fav.delete()
            return Response({'is_favorite': False}, status=200)
        return Response({'is_favorite': True}, status=201)

    @action(detail=False, methods=['post'], url_path='toggle_event')
    def toggle_event(self, request):
        """
        POST /api/favorites/toggle_event/  { event_id: N }
        Toggle: добавляет или убирает мероприятие из избранного.
        """
        event_id = request.data.get('event_id')
        event = get_object_or_404(Event, id=event_id)
        fav, created = Favorite.objects.get_or_create(user=request.user, event=event)
        if not created:
            fav.delete()
            return Response({'is_favorite': False}, status=200)
        return Response({'is_favorite': True}, status=201)