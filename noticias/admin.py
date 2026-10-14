from django.contrib import admin

from .models import (
    Articulo, Autor, Categoria, Comentario, Estado, Etiqueta, Favorito,
    HistorialEstado, Lectura, Pais, Perfil, Rol,
)


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'estado', 'es_publico', 'fecha_publicacion')
    list_filter = ('estado', 'categoria', 'es_publico')
    search_fields = ('titulo', 'resumen', 'contenido')
    filter_horizontal = ('etiquetas',)


admin.site.register(Pais)
admin.site.register(Rol)
admin.site.register(Estado)
admin.site.register(Categoria)
admin.site.register(Etiqueta)
admin.site.register(Perfil)
admin.site.register(Autor)
admin.site.register(HistorialEstado)
admin.site.register(Comentario)
admin.site.register(Lectura)
admin.site.register(Favorito)
