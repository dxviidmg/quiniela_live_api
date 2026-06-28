from django.contrib import admin
from .models import Seleccion, Quiniela, Participante

@admin.register(Seleccion)
class SeleccionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'nombre', 'fase', 'eliminado')
    list_filter = ('fase', 'eliminado')
admin.site.register(Quiniela)
admin.site.register(Participante)
