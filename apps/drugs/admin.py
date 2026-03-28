from django.contrib import admin
from .models import Drug


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ('name', 'generic_name', 'category', 'is_active', 'created_at')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'generic_name', 'description')
    list_editable = ('is_active',)
    ordering = ('name',)
    fieldsets = (
        ('Drug Information', {
            'fields': ('name', 'generic_name', 'category', 'is_active')
        }),
        ('Details', {
            'fields': ('description', 'dosage_info', 'side_effects')
        }),
    )
