from django.db import models
from django.conf import settings
from pytils.translit import slugify
from django_ckeditor_5.fields import CKEditor5Field
import random
import string

User = settings.AUTH_USER_MODEL

class CommunityTag(models.Model):
    name = models.CharField("Название", max_length=255)
    slug = models.CharField('ЧПУ', max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def save(self, *args, **kwargs):
        base_slug = slugify(self.name)
        exist_cat = CommunityTag.objects.filter(slug=base_slug)
        if exist_cat.exists() and not self.slug:
            self.slug = f'{base_slug}-{"".join(random.choices(string.ascii_letters + string.digits, k=3))}'
        elif not self.slug:
            self.slug = base_slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Community(models.Model):
    name = models.CharField("Название", max_length=255)
    slug = models.CharField('ЧПУ', max_length=255, blank=True, null=True)
    cover = models.ImageField("Обложка", upload_to="communities/covers/", null=True, blank=True)
    community_tags = models.ManyToManyField(CommunityTag,blank=True, related_name='communities')
    short_description = models.CharField("Короткое описание", max_length=500, blank=True)
    long_description = CKEditor5Field("Длинное описание (HTML)", blank=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Сообщество"
        verbose_name_plural = "Сообщества"

    def save(self, *args, **kwargs):
        base_slug = slugify(self.name)
        exist_cat = Community.objects.filter(slug=base_slug)
        if exist_cat.exists() and not self.slug:
            self.slug = f'{base_slug}-{"".join(random.choices(string.ascii_letters + string.digits, k=3))}'
        elif not self.slug:
            self.slug = base_slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CommunityLink(models.Model):
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name="community_links",
        verbose_name="Сообщество",
    )
    title = models.CharField("Название ссылки", max_length=255)
    url = models.URLField("URL")

    class Meta:
        verbose_name = "Ссылка сообщества"
        verbose_name_plural = "Ссылки сообщества"

    def __str__(self):
        return f"{self.title} ({self.community})"


class CommunityPhoto(models.Model):
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name="community_photos",
        verbose_name="Сообщество",
    )
    image = models.ImageField("Фотография", upload_to="communities/photos/")

    class Meta:
        verbose_name = "Фото сообщества"
        verbose_name_plural = "Фотографии сообщества"

    def __str__(self):
        return f"Фото ({self.community})"


class Membership(models.Model):
    """Связь пользователь - сообщество с ролями"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="memberships",
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        verbose_name="Сообщество",
        related_name="members"
    )
    is_owner = models.BooleanField("Владелец?", default=False)
    joined_at = models.DateTimeField("Дата вступления/создания", auto_now_add=True)

    class Meta:
        verbose_name = "Член сообщества"
        verbose_name_plural = "Члены сообществ"
        unique_together = ("user", "community")

    def __str__(self):
        return f"{self.user} -> {self.community} ({'владелец' if self.is_owner else 'участник'})"
