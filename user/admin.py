from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import *

class UserAdmin(BaseUserAdmin):
    list_display = (
        'email',
        'full_name',
        'phone',
        'tg_username',
        'is_active',
        'date_joined',

    )
    ordering = ('id',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'full_name',
                'email',
                'password1',
                'password2',
            ), }),)
    search_fields = ('id','email', 'full_name', 'phone',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info',
         {'fields': (
             'is_active',
             'avatar',
             'full_name',
             'phone',
             'tg_username',
             'tg_id',

         )}
         ),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups',)}),)


admin.site.register(User,UserAdmin)







