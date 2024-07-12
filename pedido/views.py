from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from produto.models import Variacao


class Pagar(View):
    template_name = 'pedido/pagar.html'
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(
                self.request,
                'Você precisa fazer login.'
            )
            return redirect('criar')
        if not self.request.session.get('carrinho'):
            messages.error(
                self.request,
                'Carrinho não possui nenhum produto.'
            )
            
        '''
        Terminar e buscar um melhor entendimento desses codigos abaixo, e não esquecer de comentar detalhadamente cada um deles.
        '''
        carrinho = self.request.session.get('carrinho')
        print('Carrinho: ', carrinho)
        print()
        carrinho_variacao_ids = [v for v in carrinho]
        print('IDS: ', carrinho_variacao_ids)
        print()
        bd_varicoes = list(Variacao.objects.select_related('produto').filter(id__in=carrinho_variacao_ids))
        print(bd_varicoes)
        # for variacao in bd_varicoes:
            # vid = variacao.id 
            # estoque = variacao.estoque 
            # qtd_carrinho = carrinho[vid]['quantidade']
            # preco_unt = carrinho[vid]['preco_unitario']
            # preco_unt_promo = carrinho[vid]['preco_unitario_promocional']
            
        contexto = {
            
        }
        return render(self.request, self.template_name, contexto)


class SalvarPedido(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Fechar_Pedido')


class Detalhe(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Detalhe')