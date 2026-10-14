"""Serializadores: convierten los modelos a JSON y validan los datos que llegan por la API."""
import copy

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError as ErrorDjango
from django.utils import timezone
from rest_framework import serializers

from .models import (
    Articulo, Autor, Categoria, Comentario, Estado, Etiqueta, Favorito,
    HistorialEstado, Lectura, Pais, Perfil, Rol,
)


class ModeloValidadoSerializer(serializers.ModelSerializer):
    """Base que ejecuta el clean() del modelo, para que la API respete las mismas
    reglas de negocio que el panel de administracion."""

    def validate(self, attrs):
        attrs = super().validate(attrs)
        modelo = self.Meta.model
        nombres_m2m = {campo.name for campo in modelo._meta.many_to_many}
        datos = {k: v for k, v in attrs.items() if k not in nombres_m2m}
        if self.instance is not None:
            instancia = copy.copy(self.instance)
            for campo, valor in datos.items():
                setattr(instancia, campo, valor)
        else:
            instancia = modelo(**datos)
        try:
            instancia.clean()
        except ErrorDjango as error:
            raise serializers.ValidationError(
                error.message_dict if hasattr(error, 'error_dict') else error.messages
            )
        return attrs


# ---------------------------------------------------------------- Catalogos

class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = '__all__'


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = '__all__'


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ('slug',)  # se genera sola a partir del nombre


class EtiquetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etiqueta
        fields = '__all__'
        read_only_fields = ('slug',)


# ----------------------------------------------------------------- Personas

class UsuarioSerializer(serializers.ModelSerializer):
    """Usuario de Django. La clave solo se escribe: nunca se devuelve y se guarda cifrada."""
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'is_active', 'date_joined')
        read_only_fields = ('date_joined',)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'Este campo es obligatorio.'})
        return User.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        usuario = super().update(instance, validated_data)
        if password:
            usuario.set_password(password)
            usuario.save()
        return usuario


class PerfilSerializer(ModeloValidadoSerializer):
    class Meta:
        model = Perfil
        fields = '__all__'


class AutorSerializer(ModeloValidadoSerializer):
    class Meta:
        model = Autor
        fields = '__all__'


# ----------------------------------------------------------------- Contenido

class ArticuloSerializer(ModeloValidadoSerializer):
    class Meta:
        model = Articulo
        fields = '__all__'
        read_only_fields = ('slug',)

    def validate(self, attrs):
        # Si el estado es publico y no se indico fecha, se publica ahora.
        estado = attrs.get('estado') or (self.instance.estado if self.instance else None)
        fecha = attrs.get('fecha_publicacion', self.instance.fecha_publicacion if self.instance else None)
        if estado and estado.visible_publicamente and fecha is None:
            attrs['fecha_publicacion'] = timezone.now()
        return super().validate(attrs)


# ------------------------------------------------ Auditoria e indicadores

class HistorialEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialEstado
        fields = '__all__'


class ComentarioSerializer(ModeloValidadoSerializer):
    class Meta:
        model = Comentario
        fields = '__all__'


class LecturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lectura
        fields = '__all__'


class FavoritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorito
        fields = '__all__'
