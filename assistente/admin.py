from django.contrib import admin
from .models import UsuarioAutorizado,  PerfilUsuario



admin.site.register(PerfilUsuario)

admin.site.register(UsuarioAutorizado)


