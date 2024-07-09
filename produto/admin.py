from django.contrib import admin
from produto.models import Produto, Variacao


class VaricaoInline(admin.TabularInline):
    model = Variacao
    extra = 1


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    inlines = [ VaricaoInline ]
    list_display = 'id', 'nome', 'get_preco_formatato', 'get_preco_format', 'tipo',
    list_display_links = 'id',
    search_fields = 'id', 'nome',
    list_editable = 'nome', 'tipo',
    list_per_page = 10
    ordering = ['-id',]
    
    

    
    
    

