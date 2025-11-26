from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "community", "start_date", "time_text")
    search_fields = ("title", "community__name")
