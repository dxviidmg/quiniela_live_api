from django.db import models
from django.utils.text import slugify
from datetime import datetime


DIVISORES_48 = [2, 3, 4, 6, 8, 12, 16, 24, 48]

class Seleccion(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


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
    sorteada = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.slug = slugify(f"{self.nombre}-{timestamp}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Participante(models.Model):
    quiniela = models.ForeignKey(Quiniela, on_delete=models.CASCADE, related_name='participantes')
    nombre = models.CharField(max_length=100)
    selecciones = models.ManyToManyField(Seleccion, blank=True)
    fecha_union = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.quiniela.nombre}"
