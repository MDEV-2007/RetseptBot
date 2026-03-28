from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(UserAdmin):
    list_display = ('telegram_id', 'full_name', 'username', 'specialty', 'is_active', 'is_staff', 'created_at')
    list_filter = ('is_active', 'is_staff', 'specialty')
    search_fields = ('telegram_id', 'full_name', 'username', 'phone')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('telegram_id', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'username', 'phone', 'specialty')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('telegram_id', 'full_name', 'password1', 'password2'),
        }),
    )
