from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age', 'gender', 'phone_number', 'created_at')
    list_filter = ('gender', 'created_at')
    search_fields = ('full_name', 'phone_number', 'address')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('full_name', 'age', 'gender')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'address')
        }),
        ('Additional Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
