from django.db import models
from communities.models import Community
from pytils.translit import slugify
from django_ckeditor_5.fields import CKEditor5Field
import random
import string

class InfoProduct(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, verbose_name="ID группы", related_name="infoproducts")
    is_main = models.BooleanField("Основной", default=False)
    title = models.CharField("Название", max_length=255)
    slug = models.CharField('ЧПУ', max_length=255, blank=True, null=True)
    cover = models.ImageField("Обложка", upload_to="infoproducts/covers/", null=True, blank=True)
    short_description = models.CharField("Короткое описание", max_length=500, blank=True)
    price = models.DecimalField("Стоимость", max_digits=10, decimal_places=2, null=True, blank=True)
    product_info = CKEditor5Field("Большое описание (HTML)", blank=True, null=True)
    product_info_structure = models.JSONField("Сруктура html", blank=True,  null=True)

    class Meta:
        verbose_name = "Инфопродукт"
        verbose_name_plural = "Инфопродукты"

    def save(self, *args, **kwargs):

        obj = InfoProduct.objects.filter(slug=slugify(self.title))
        if obj.exists():
            self.slug = f'{slugify(self.title)}-{"".join(random.choices(string.ascii_letters + string.digits, k=3))}'
        else:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.community})"

class InfoFile(models.Model):
    product = models.ForeignKey(InfoProduct, on_delete=models.CASCADE, related_name="files")
    file = models.FileField("Файл", upload_to="infoproducts/files/")
    name = models.CharField("Название файла", max_length=255, blank=True)



