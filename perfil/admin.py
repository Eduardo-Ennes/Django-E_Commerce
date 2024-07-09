from django.contrib import admin
from perfil.models import Perfil


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = 'id', 'usuario', 'cpf', 'bairro', 'endereco', 'numero', 'cidade',
    
