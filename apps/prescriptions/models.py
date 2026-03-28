import uuid
from django.db import models
from apps.users.models import Doctor
from apps.patients.models import Patient
from apps.drugs.models import Drug


class Prescription(models.Model):
    patient    = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='prescriptions')
    doctor     = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name='prescriptions')
    diagnosis  = models.TextField()
    notes      = models.TextField(blank=True)
    share_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Prescription #{self.pk} — {self.patient.full_name}'

    @property
    def prescription_number(self):
        return f'RX-{self.created_at.strftime("%Y%m")}-{self.pk:04d}'


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    drug = models.ForeignKey(Drug, on_delete=models.PROTECT)
    dosage = models.CharField(max_length=255)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.drug.name} — {self.dosage}'
