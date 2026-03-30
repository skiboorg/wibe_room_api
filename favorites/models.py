from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='Пользователь')

    # Один из двух — продукт или мероприятие (nullable)
    product = models.ForeignKey(
        'infoproducts.InfoProduct',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='favorited_by',
        verbose_name='Инфопродукт'
    )
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='favorited_by',
        verbose_name='Мероприятие'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        # один юзер не может добавить один и тот же объект дважды
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], condition=models.Q(product__isnull=False), name='unique_favorite_product'),
            models.UniqueConstraint(fields=['user', 'event'], condition=models.Q(event__isnull=False), name='unique_favorite_event'),
        ]

    def __str__(self):
        obj = self.product or self.event
        return f'{self.user} → {obj}'