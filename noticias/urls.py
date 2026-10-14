from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "noticias"

# El router crea solo las rutas de lista/detalle de cada ViewSet.
enrutador = routers.DefaultRouter()
enrutador.register(r'paises', views.PaisViewSet)
enrutador.register(r'roles', views.RolViewSet)
enrutador.register(r'estados', views.EstadoViewSet)
enrutador.register(r'categorias', views.CategoriaViewSet)
enrutador.register(r'etiquetas', views.EtiquetaViewSet)
enrutador.register(r'usuarios', views.UsuarioViewSet)
enrutador.register(r'perfiles', views.PerfilViewSet)
enrutador.register(r'autores', views.AutorViewSet)
enrutador.register(r'articulos', views.ArticuloViewSet)
enrutador.register(r'historial-estados', views.HistorialEstadoViewSet)
enrutador.register(r'comentarios', views.ComentarioViewSet)
enrutador.register(r'lecturas', views.LecturaViewSet)
enrutador.register(r'favoritos', views.FavoritoViewSet)

urlpatterns = [
    path('', views.bienvenida, name='bienvenida'),
    path('api/', include(enrutador.urls)),
]
