from django.contrib import admin
from .models import Prescription, PrescriptionItem


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1
    fields = ('drug', 'dosage', 'duration', 'quantity', 'instructions')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('prescription_number', 'patient', 'doctor', 'diagnosis_short', 'created_at')
    list_filter = ('created_at', 'doctor')
    search_fields = ('patient__full_name', 'doctor__full_name', 'diagnosis')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PrescriptionItemInline]
    date_hierarchy = 'created_at'

    def diagnosis_short(self, obj):
        return obj.diagnosis[:60] + '...' if len(obj.diagnosis) > 60 else obj.diagnosis
    diagnosis_short.short_description = 'Diagnosis'

    def prescription_number(self, obj):
        return obj.prescription_number
    prescription_number.short_description = 'Rx #'


@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ('prescription', 'drug', 'dosage', 'duration', 'quantity')
    list_filter = ('drug',)
    search_fields = ('prescription__patient__full_name', 'drug__name')
