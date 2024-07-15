"""
URL configuration for loja project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from produto.views import ListaProduto, DetalheProduto, AdicionarAoCarrinho, RemoverDoCarrinho, Carrinho, ResumoDaCompra, Busca 
from perfil.views import Criar, Login, Logouth, BasePerfil
from pedido.views import Pagar, SalvarPedido, Detalhe, Lista

urlpatterns = [
    #Admin
    path('admin/', admin.site.urls),
    
    #Produto
    path('', ListaProduto.as_view(), name='Lista_produto'),
    path('<slug>', DetalheProduto.as_view(), name='Detalhe_produto'),
    path('adicionaraocarrinho/', AdicionarAoCarrinho.as_view(), name='adicionaraocarrinho'),
    path('removerdocarrinho/', RemoverDoCarrinho.as_view(), name='removerdocarrinho'),
    path('carrinho/', Carrinho.as_view(), name='Carrinho'),
    path('resumodacompra/', ResumoDaCompra.as_view(), name='resumodacompra'),
    path('busca/', Busca.as_view(), name='busca'),
    
    #Pedido
    path('pagar/<int:pk>', Pagar.as_view(), name='Pagar'),
    path('salvarpedido/', SalvarPedido.as_view(), name='salvarpedido'),
    path('lista/', Lista.as_view(), name='lista'),
    path('detalhe/<int:pk>', Detalhe.as_view(), name='detalhe'),
    
    #Perfil
    path('criarperfil/', Criar.as_view(), name='criar'),
    # path('atualizar/', Atualizar.as_view(), name='atualizar'),
    path('login/', Login.as_view(), name='login'),
    path('logouth/', Logouth.as_view(), name='logouth'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    