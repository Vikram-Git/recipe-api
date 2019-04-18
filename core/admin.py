from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']

    '''Django comes with default 'User' edit page, we will customize it'''
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (('Personal Info'), {'fields': ('name',)}),
        (
            ('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (('Important Dates'), {'fields': ('last_login',)})
    )

    '''admin comes with default fields to create user, we will customize it'''
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


admin.site.register(models.User, UserAdmin)