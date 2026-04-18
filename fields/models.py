from django.db import models
from django.conf import settings
from django.utils import timezone

class Field(models.Model):
    PLANTED = 'PLANTED'
    GROWING = 'GROWING'
    READY = 'READY'
    HARVESTED = 'HARVESTED'

    STAGE_CHOICES = [
        (PLANTED, 'Planted'),
        (GROWING, 'Growing'),
        (READY, 'Ready'),
        (HARVESTED, 'Harvested'),
    ]

    name = models.CharField(max_length=200)
    crop_type = models.CharField(max_length=100)
    planting_date = models.DateField()
    stage = models.CharField(
        max_length=20,
        choices=STAGE_CHOICES,
        default=PLANTED
    )
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_fields',
        limit_choices_to={'role': 'AGENT'},  # only agents appear in dropdowns
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def status(self):
        if self.stage == self.HARVESTED:
            return 'completed'
        days_stale = (timezone.now() - self.updated_at).days
        if self.stage == self.READY and days_stale > 14:
            return 'at_risk'
        if days_stale > 7:
            return 'at_risk'
        return 'active'

    @property
    def status_label(self):
        return {
            'active': 'Active',
            'at_risk': 'At Risk',
            'completed': 'Completed',
        }[self.status]

    @property
    def days_since_planted(self):
        return (timezone.now().date() - self.planting_date).days

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.crop_type})"


class FieldUpdate(models.Model):
    field = models.ForeignKey(Field,on_delete=models.CASCADE,related_name='updates',)
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='field_updates'
    )
    stage = models.CharField(max_length=20, choices=Field.STAGE_CHOICES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.field.name} → {self.stage} on {self.created_at:%Y-%m-%d}"