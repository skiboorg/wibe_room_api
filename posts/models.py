from django.db import models
from django.conf import settings
from communities.models import Community
from pytils.translit import slugify
from django_ckeditor_5.fields import CKEditor5Field
import random
import string

User = settings.AUTH_USER_MODEL

class Tag(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, verbose_name="Группа", related_name="tags")
    name = models.CharField("Тэг", max_length=100)
    slug = models.CharField('ЧПУ', max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        base_slug = slugify(self.name)
        exist_cat = Tag.objects.filter(slug=base_slug)
        if exist_cat.exists() and not self.slug:
            self.slug = f'{base_slug}-{"".join(random.choices(string.ascii_letters + string.digits, k=3))}'
        elif not self.slug:
            self.slug = base_slug

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return f"{self.name} ({self.community})"

class Post(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, verbose_name="ID группы", related_name="posts")
    post_tags = models.ManyToManyField(Tag, verbose_name="Теги", blank=True)
    date = models.DateTimeField("Дата", auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Кто добавил", related_name="added_posts")
    title = models.CharField("Заголовок", max_length=255)
    vk_video_link = models.CharField("Ссылка на ВК видео", max_length=255, blank=True, null=True)
    text = CKEditor5Field("Текст")
    is_pinned = models.BooleanField(default=False, null=False)

    class Meta:
        verbose_name = "Запись на стене"
        verbose_name_plural = "Записи на стене"

    def __str__(self):
        return f"{self.title} ({self.community})"

class PostPhoto(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="photos", verbose_name="Фото")
    image = models.ImageField("Фото", upload_to="posts/photos/")

class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="Комментарий")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Автор")
    text = models.TextField("Текст")
    date = models.DateTimeField("Дата", auto_now_add=True)

class ReactionType(models.TextChoices):
    LIKE = "like", "Лайк"
    LOVE = "love", "Люблю"
    WOW = "wow", "Вау"
    SAD = "sad", "Печаль"
    ANGRY = "angry", "Злой"

class PostReaction(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions", verbose_name="Реакция")
    reaction = models.CharField("Реакция", max_length=20, choices=ReactionType.choices)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Автор")
