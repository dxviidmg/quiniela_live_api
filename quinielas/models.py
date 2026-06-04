from django.db import models
from django.utils.text import slugify
from datetime import datetime


class Quiniela(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    numero_participantes = models.PositiveIntegerField()
    aporte_participante = models.DecimalField(max_digits=10, decimal_places=2)
    total_premio = models.DecimalField(max_digits=12, decimal_places=2)
    primer_premio = models.DecimalField(max_digits=12, decimal_places=2)
    segundo_premio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tercer_premio = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.slug = slugify(f"{self.nombre}-{timestamp}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
