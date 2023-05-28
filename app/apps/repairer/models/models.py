from django.db import models

from apps.iiko.models import Storage

from . import managers


class Malfunction(models.Model):
    STATUS_CHOICES = [
        (0, 'Не исправлено'),
        (1, 'Исправлено'),
        (2, 'Одобрено')
    ]

    date_at = models.DateTimeField(auto_now=True)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True)
    photo = models.ImageField(upload_to='malfunction_photos')
    fault_object = models.CharField(max_length=64)
    description = models.TextField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)
    comment = models.CharField(max_length=128, null=True)

    objects = managers.MalfunctionManager()
