from django.db import models
from communities.models import Community
from pytils.translit import slugify
from django_ckeditor_5.fields import CKEditor5Field
import random
import string

class Event(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, verbose_name="ID группы", related_name="events")
    start_date = models.DateField("Дата начала", blank=True, null=True)
    time_text = models.CharField("Время проведения", max_length=100, blank=True, null=True)
    title = models.CharField("Название", max_length=255, blank=True, null=True)
    slug = models.CharField( max_length=255, blank=True, null=True)
    cover = models.ImageField("Обложка", upload_to="events/covers/", null=True, blank=True)
    short_description = models.CharField("Короткое описание", max_length=500, blank=True, null=True)
    long_description = CKEditor5Field("Длинное описание (HTML)", blank=True, null=True)

    class Meta:
        verbose_name = "Ивент"
        verbose_name_plural = "Ивенты"

    def __str__(self):
        return f"{self.title} ({self.community})"

    def save(self, *args, **kwargs):
        base_slug = slugify(self.title)
        exist_cat = Event.objects.filter(slug=base_slug)
        if exist_cat.exists() and not self.slug:
            self.slug = f'{base_slug}-{"".join(random.choices(string.ascii_letters + string.digits, k=3))}'
        elif not self.slug:
            self.slug = base_slug

        super().save(*args, **kwargs)