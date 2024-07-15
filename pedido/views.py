from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, DetailView
from django.views import View 
from django.http import HttpResponse
from django.contrib import messages
from produto.models import Variacao
from utils import utils
from pedido.models import Pedido, itemPedido




class DispatchLoginRequired(View):
    def dispatch(self, *args, **kwargs):
        '''
        É um metodo que direcina para uma url.
        '''
        if not self.request.user.is_authenticated:
            '''  
            Se o usuario for anonimo ira ser redirecionado para a pagina principal.
            '''
            return redirect('criar')
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self, *args, **kwargs):
        '''
        Aqui definimos que o usuario so poderá acessar coisas relacionadas ao seu usuario, apenas seus produtos, compras e histórico de suas compras. 
        '''
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(usuario=self.request.user)
        return qs


class Pagar(DispatchLoginRequired, DetailView):
    template_name = 'pedido/pagar.html'
    model = Pedido
    pk_url_kwarg = 'pk'
    context_object_name = 'pedido'  


class SalvarPedido(View):
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
        Buscar um melhor entendimento desses codigos abaixo, e não esquecer de comentar detalhadamente cada um deles.
        '''
        carrinho = self.request.session.get('carrinho')
        print('Carrinho: ', carrinho)
        print()
        carrinho_variacao_ids = [v for v in carrinho]
        print('IDS: ', carrinho_variacao_ids)
        print()
        bd_varicoes = list(Variacao.objects.select_related('produto').filter(id__in=carrinho_variacao_ids))
        print(bd_varicoes)
        
        for variacao in bd_varicoes:
            vid = str(variacao.id) 
            estoque = variacao.estoque 
            qtd_carrinho = carrinho[vid]['quantidade']
            preco_unt = carrinho[vid]['preco_unitario']
            preco_unt_promo = carrinho[vid]['preco_unitario_promocional']
            
            error_msg_estoque = ''
            
            if estoque < qtd_carrinho:
                '''
                Essa verificação provavelmete nunca irá acontecer, quando adicionamos a quantidade de produtos para colocar no carrinho já fazemos a verificação da quantidade em estoque. Deixarei este codigo por segurança.  
                '''
                carrinho[vid]['quantidade'] = estoque
                carrinho[vid]['preco_quantitativo'] = estoque * preco_unt
                carrinho[vid]['preco_quantitativo_promocional'] = estoque * preco_unt_promo
                
                error_msg_estoque = 'Estoque insuficiente para alguns produtos do seu carrinho'
                
        if error_msg_estoque:
            messages.error(
                self.request,
                error_msg_estoque
            )
            self.request.session.save()
            return redirect('Carrinho')
        
        qtd_total_carrinho = utils.cart_total_qtd(carrinho)
        valor_total_carrinho = utils.soma_total(carrinho)
        
        # Daqui para baixo apenas estamos salvando as informações no banco de dados 
        pedido = Pedido(
            usuario=self.request.user,
            total=valor_total_carrinho,
            qtd_total=qtd_total_carrinho,
            status='C',
        )
        
        pedido.save()
        
        itemPedido.objects.bulk_create(
            [
                itemPedido(
                    pedido=pedido,
                    produto=v['produto_nome'],
                    produto_id=v['produto_id'],
                    variacao=v['variacao_nome'],
                    variacao_id=v['variacao_id'],
                    preco=v['preco_quantitativo'],
                    preco_promocional=v['preco_quantitativo_promocional'],
                    quantidade=v['quantidade'],
                    imagem=v['imagem'], 
                ) for v in carrinho.values()
            ]
        )
            
        
        contexto = {}
        # Quando finalizada a compra apagamos o carrinho
        del self.request.session['carrinho']
        # Em seguida redirecionamos para a area de pagamento com o id especifico do pedido 
        return redirect(
            reverse(
                'Pagar',
                kwargs={
                    'pk': pedido.pk
                }))


class Detalhe(DispatchLoginRequired, DetailView):
    model = Pedido
    context_object_name = 'pedido'
    template_name = 'pedido/detalhe.html'
    pk_url_kwarg = 'pk'
    
    
    
class Lista(DispatchLoginRequired, ListView):
    model = Pedido
    context_object_name = 'pedidos'
    template_name = 'pedido/lista.html'
    paginate_by = 10
    ordering = ['-id']
    
    '''
    DispatchLoginRequired -> tem uma função que limita o usuario apenas para ver coisas relacionadas a seu usuario, por isso, no meu pedidos irá mostrar apenas pedidos do usuario.
    '''