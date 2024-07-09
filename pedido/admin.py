from django.contrib import admin
from pedido.models import Pedido, itemPedido


class ItemPedidoInline(admin.TabularInline):
    model = itemPedido
    extra = 1
    

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    inlines = [
        ItemPedidoInline
    ]
