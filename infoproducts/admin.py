from django.contrib import admin
from .models import InfoProduct, InfoFile

class InfoFileInline(admin.TabularInline):
    model = InfoFile
    extra = 0


@admin.register(InfoProduct)
class InfoProductAdmin(admin.ModelAdmin):
    list_display = ("title", "community", "is_main", "price")
    inlines = [InfoFileInline]
