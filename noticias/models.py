"""Modelo de datos de la Plataforma de Noticias.

Tablas:
  Catalogos : Pais, Rol, Estado, Categoria, Etiqueta
  Personas  : Perfil (extiende al User de Django), Autor
  Contenido : Articulo (+ tabla intermedia articulo-etiqueta que crea Django)
  Auditoria e indicadores : HistorialEstado, Comentario, Lectura, Favorito
"""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.text import slugify

# Roles que pueden tener un perfil de autor (deben existir en el fixture de roles).
ROLES_CON_AUTORIA = ('Administrador', 'Editor', 'Autor')


def generar_slug_unico(modelo, texto, instancia=None):
    """Convierte `texto` en slug y agrega -2, -3... si ya existe en la tabla."""
    largo = modelo._meta.get_field('slug').max_length
    base = slugify(texto)[:largo - 8] or 'sin-titulo'
    slug = base
    contador = 2
    existentes = modelo.objects.all()
    if instancia is not None and instancia.pk:
        existentes = existentes.exclude(pk=instancia.pk)
    while existentes.filter(slug=slug).exists():
        slug = f'{base}-{contador}'
        contador += 1
    return slug


class RegistroBase(models.Model):
    """Campos comunes: borrado logico (habilitado) y fechas de creacion/modificacion."""
    habilitado = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ---------------------------------------------------------------- Catalogos

class Pais(RegistroBase):
    codigo = models.CharField(max_length=3, unique=True, help_text='Codigo ISO de 3 letras, ej: CHL')
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table_comment = 'Paises de origen de los usuarios'
        verbose_name = 'país'
        verbose_name_plural = 'países'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Rol(RegistroBase):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table_comment = 'Perfiles de acceso: administrador, editor, autor y lector'
        verbose_name = 'rol'
        verbose_name_plural = 'roles'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Estado(RegistroBase):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, blank=True)
    visible_publicamente = models.BooleanField(
        default=False,
        help_text='Si es True, los articulos en este estado pueden mostrarse a los lectores.',
    )

    class Meta:
        db_table_comment = 'Estados del flujo editorial de un articulo'
        verbose_name = 'estado'
        verbose_name_plural = 'estados'
        ordering = ['id']

    def __str__(self):
        return self.nombre


class Categoria(RegistroBase):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        db_table_comment = 'Secciones tematicas del medio (politica, deportes, etc.)'
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['nombre']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generar_slug_unico(Categoria, self.nombre, self)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Etiqueta(RegistroBase):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        db_table_comment = 'Etiquetas libres para clasificar articulos'
        verbose_name = 'etiqueta'
        verbose_name_plural = 'etiquetas'
        ordering = ['nombre']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generar_slug_unico(Etiqueta, self.nombre, self)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


# ----------------------------------------------------------------- Personas

class Perfil(RegistroBase):
    """Datos del medio asociados a un usuario de Django (login, clave, permisos)."""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, related_name='perfiles')
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, null=True, blank=True, related_name='perfiles')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True, help_text='Dato privado: no se muestra publicamente.')
    es_publico = models.BooleanField(default=True, help_text='Si es False, solo el propio usuario ve su perfil.')

    class Meta:
        db_table_comment = 'Perfil de cada usuario: rol, pais y datos publicos o privados'
        verbose_name = 'perfil'
        verbose_name_plural = 'perfiles'
        ordering = ['usuario__username']

    def clean(self):
        if self.fecha_nacimiento and self.fecha_nacimiento > timezone.localdate():
            raise ValidationError({'fecha_nacimiento': 'La fecha de nacimiento no puede ser futura.'})

    def __str__(self):
        return f'{self.usuario.username} ({self.rol})'


class Autor(RegistroBase):
    perfil = models.OneToOneField(Perfil, on_delete=models.PROTECT, related_name='autor')
    seudonimo = models.CharField(max_length=100, blank=True)
    biografia = models.TextField(blank=True)
    sitio_web = models.URLField(blank=True)

    class Meta:
        db_table_comment = 'Periodistas que pueden firmar articulos'
        verbose_name = 'autor'
        verbose_name_plural = 'autores'
        ordering = ['perfil__usuario__username']

    def clean(self):
        # Regla de negocio: un lector no puede ser autor.
        if self.perfil_id and self.perfil.rol.nombre not in ROLES_CON_AUTORIA:
            raise ValidationError({'perfil': 'Solo administradores, editores y autores pueden tener perfil de autor.'})

    def __str__(self):
        return self.seudonimo or self.perfil.usuario.get_full_name() or self.perfil.usuario.username


# ----------------------------------------------------------------- Contenido

class Articulo(RegistroBase):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    resumen = models.CharField(max_length=300, blank=True)
    contenido = models.TextField()
    imagen_url = models.URLField(blank=True)
    autor = models.ForeignKey(Autor, on_delete=models.PROTECT, related_name='articulos')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='articulos')
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name='articulos')
    etiquetas = models.ManyToManyField(Etiqueta, blank=True, related_name='articulos')
    es_publico = models.BooleanField(default=True, help_text='Si es False, solo lo ven usuarios registrados.')
    fecha_publicacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table_comment = 'Articulos periodisticos del medio'
        verbose_name = 'artículo'
        verbose_name_plural = 'artículos'
        ordering = ['-fecha_publicacion', '-created_at']
        indexes = [
            models.Index(fields=['estado', 'fecha_publicacion'], name='art_estado_fecha_idx'),
            models.Index(fields=['categoria', 'fecha_publicacion'], name='art_categoria_fecha_idx'),
        ]

    @property
    def esta_visible(self):
        """True si un lector puede ver el articulo hoy."""
        return bool(
            self.habilitado
            and self.estado.visible_publicamente
            and self.fecha_publicacion
            and self.fecha_publicacion <= timezone.now()
        )

    def clean(self):
        # Regla de negocio: un articulo en estado publico necesita fecha de publicacion.
        if self.estado_id and self.estado.visible_publicamente and not self.fecha_publicacion:
            raise ValidationError({'fecha_publicacion': 'Un artículo publicado debe tener fecha de publicación.'})

    def cambiar_estado(self, nuevo_estado, usuario=None, motivo=''):
        """Cambia el estado y deja el registro en HistorialEstado (todo o nada)."""
        if nuevo_estado.pk == self.estado_id:
            raise ValidationError('El artículo ya se encuentra en ese estado.')
        with transaction.atomic():
            HistorialEstado.objects.create(
                articulo=self,
                estado_anterior=self.estado,
                estado_nuevo=nuevo_estado,
                usuario=usuario,
                motivo=motivo,
            )
            self.estado = nuevo_estado
            if nuevo_estado.visible_publicamente and self.fecha_publicacion is None:
                self.fecha_publicacion = timezone.now()
            self.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generar_slug_unico(Articulo, self.titulo, self)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo


# ------------------------------------------------ Auditoria e indicadores

class HistorialEstado(models.Model):
    """Registro inmutable de cada cambio de estado de un articulo."""
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.ForeignKey(Estado, on_delete=models.PROTECT, null=True, blank=True, related_name='+')
    estado_nuevo = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name='+')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cambios_de_estado')
    motivo = models.TextField(blank=True)
    fecha = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table_comment = 'Auditoria de cambios de estado de los articulos'
        verbose_name = 'historial de estado'
        verbose_name_plural = 'historial de estados'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.articulo} -> {self.estado_nuevo} ({self.fecha:%d-%m-%Y})'


class Comentario(RegistroBase):
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='comentarios')
    lector = models.ForeignKey(Perfil, on_delete=models.PROTECT, related_name='comentarios')
    respuesta_a = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='respuestas')
    texto = models.TextField()

    class Meta:
        db_table_comment = 'Comentarios de los lectores, con respuestas anidadas'
        verbose_name = 'comentario'
        verbose_name_plural = 'comentarios'
        ordering = ['created_at']

    def clean(self):
        # Una respuesta debe pertenecer al mismo articulo que el comentario original.
        if self.respuesta_a_id and self.respuesta_a.articulo_id != self.articulo_id:
            raise ValidationError({'respuesta_a': 'La respuesta debe ser del mismo artículo.'})

    def __str__(self):
        return f'Comentario de {self.lector} en {self.articulo}'


class Lectura(models.Model):
    """Cada visita a un articulo; sirve para los indicadores de gestion."""
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='lecturas')
    lector = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True, related_name='lecturas')
    fecha = models.DateTimeField(default=timezone.now, editable=False)
    duracion_segundos = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table_comment = 'Visitas a articulos para medir tendencias y comportamiento'
        verbose_name = 'lectura'
        verbose_name_plural = 'lecturas'
        ordering = ['-fecha']
        indexes = [models.Index(fields=['articulo', 'fecha'], name='lectura_art_fecha_idx')]

    def __str__(self):
        return f'{self.articulo} - {self.fecha:%d-%m-%Y %H:%M}'


class Favorito(models.Model):
    lector = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='favoritos')
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='favoritos')
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table_comment = 'Articulos guardados por cada lector'
        verbose_name = 'favorito'
        verbose_name_plural = 'favoritos'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['lector', 'articulo'], name='favorito_unico_por_lector_articulo'),
        ]

    def __str__(self):
        return f'{self.lector} guardó {self.articulo}'
