from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render
from rest_framework import viewsets

from .models import (
    Articulo, Autor, Categoria, Comentario, Estado, Etiqueta, Favorito,
    HistorialEstado, Lectura, Pais, Perfil, Rol,
)
from .serializers import (
    ArticuloSerializer, AutorSerializer, CategoriaSerializer, ComentarioSerializer,
    EstadoSerializer, EtiquetaSerializer, FavoritoSerializer, HistorialEstadoSerializer,
    LecturaSerializer, PaisSerializer, PerfilSerializer, RolSerializer, UsuarioSerializer,
)


# --------------------------------------------------------- Pagina de inicio

def bienvenida(request):
    return render(request, 'noticias/bienvenida.html')


# ------------------------------------------------------ API REST (CRUD completo)
# Cada ModelViewSet entrega list, retrieve, create, update (PUT),
# partial_update (PATCH) y destroy (DELETE) sin escribir cada metodo a mano.

class PaisViewSet(viewsets.ModelViewSet):
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer


class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer


class EstadoViewSet(viewsets.ModelViewSet):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class EtiquetaViewSet(viewsets.ModelViewSet):
    queryset = Etiqueta.objects.all()
    serializer_class = EtiquetaSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by('id')
    serializer_class = UsuarioSerializer


class PerfilViewSet(viewsets.ModelViewSet):
    queryset = Perfil.objects.select_related('usuario', 'rol', 'pais')
    serializer_class = PerfilSerializer


class AutorViewSet(viewsets.ModelViewSet):
    queryset = Autor.objects.select_related('perfil__usuario')
    serializer_class = AutorSerializer


class ArticuloViewSet(viewsets.ModelViewSet):
    queryset = Articulo.objects.select_related('autor', 'categoria', 'estado').prefetch_related('etiquetas')
    serializer_class = ArticuloSerializer

    def _usuario(self):
        usuario = self.request.user
        return usuario if usuario.is_authenticated else None

    @transaction.atomic
    def perform_create(self, serializer):
        articulo = serializer.save()
        HistorialEstado.objects.create(
            articulo=articulo, estado_anterior=None, estado_nuevo=articulo.estado,
            usuario=self._usuario(), motivo='Creación del artículo',
        )

    @transaction.atomic
    def perform_update(self, serializer):
        estado_anterior = serializer.instance.estado
        articulo = serializer.save()
        if articulo.estado_id != estado_anterior.pk:  # auditoria de cambios de estado
            HistorialEstado.objects.create(
                articulo=articulo, estado_anterior=estado_anterior, estado_nuevo=articulo.estado,
                usuario=self._usuario(), motivo='Cambio de estado vía API',
            )


class HistorialEstadoViewSet(viewsets.ModelViewSet):
    queryset = HistorialEstado.objects.all()
    serializer_class = HistorialEstadoSerializer


class ComentarioViewSet(viewsets.ModelViewSet):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer


class LecturaViewSet(viewsets.ModelViewSet):
    queryset = Lectura.objects.all()
    serializer_class = LecturaSerializer


class FavoritoViewSet(viewsets.ModelViewSet):
    queryset = Favorito.objects.all()
    serializer_class = FavoritoSerializer
