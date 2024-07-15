from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from produto.models import Produto, Variacao
from perfil.models import Perfil
from django.contrib import messages
from django.db.models import Q



class ListaProduto(ListView):
    model = Produto
    # O banco de dados que será usado 
    template_name = 'produto/lista.html'
    # O template que será renderizado
    context_object_name = 'produtos'
    # context_object_name -> já faz a busca dos campos no banco de dados 
    paginate_by = 10
    ordering = ['-id']


class Busca(ListaProduto):
    '''
    Aqui fazemos a busca personalizada
    '''
    def get_queryset(self, *args, **kwargs):
        termo = self.request.GET.get('termo') or self.request.session['termo']
        qs = super().get_queryset(*args, **kwargs)
        
        if not termo:
            return qs
        
        self.request.session['termo'] = termo
        
        qs = qs.filter(
            Q(nome__icontains=termo) 
        )
        
        self.request.session.save()
        return qs
        '''
        Criar umas session foi importante para apenas mostrar os resultados relacionados na busca. Sem a session estavamos buscando um valor, porem ele estava sendo mostrado primeiro e logo em seguida valores que nao tinham correlação alguma. 
        '''


class DetalheProduto(DetailView):
    model = Produto
    # banco de dados que será usado 
    template_name = 'produto/detalhe.html'
    # template que será renderizado
    context_object_name = 'produto'
    # context_object_name -> já faz a busca dos campos no banco de dados
    slug_url_kwarg = 'slug'
    # busca o slug da classe que está na url
    


class AdicionarAoCarrinho(View):
    def get(self, *args, **kwargs):
        variacao_id = self.request.GET.get('vid')
        '''
        Neste código buscamos o id que está na url e jogamos na variavél 
        '''
        if not variacao_id:
            '''
            se na variavel não houver valor que no caso seria um id retornamos o usuário para a pagina principal e emitimos uma mensagem de erro. 
            
            Se não houver id na vid que dizer que não há produto, então o que resta é redirecionar o usuário a pagina princial 
            
            Esse id é buscado na variação, se um produto não tiver variações ele gerará um erro, todo produto deverá ter variações.
            '''
            messages.error(
                self.request,
                'Este produto não existe, tente novamente...'
            )
            return redirect(self.request.META['HTTP_REFERER'])
        
        variacao = get_object_or_404(Variacao, id=variacao_id)
        '''
        No código acima selecionamos o banco de dados e interligamos com o id passado na vid, caso haja um id na vid que corresponda a um id no banco de dados, tudo ok!, se o id que está na vid não corresponda o id que esta no banco de dados será levantado um error 404, como já diz no metodo get_object_or_404
        
        A variavel variacao tem o valor do banco de dados Variacao.
        '''

        variacao_estoque = variacao.estoque
        
        produto = variacao.produto 
        '''
        esta variavel esta sendo atribuida a ela o valor do model Produto que está linkado no model Variacao, por isso variacao.produto, para que se tenha acesso a varivel do banco de dados Produto.
        '''
 
        produto_id = produto.id
        produto_nome = produto.nome
        variacao_nome = variacao.nome or ''
        preco_unitario = variacao.preco
        preco_unitario_promocional = variacao.preco_promocional
        quantidade = 1
        slug = produto.slug
        imagem = produto.imagem
        
        if imagem:
            imagem = imagem.name
        else:
            imagem = ''
        
        if variacao.estoque < 1: 
            messages.error(
                self.request,
                'Produto esgotado!'
            )
            return redirect(self.request.META['HTTP_REFERER'])
        
        if not self.request.session.get('carrinho'):
            # Aqui criamos a sessão do carrinho, que é um dicionario
            self.request.session['carrinho'] = {} 
            self.request.session.save()
            
        carrinho = self.request.session['carrinho']
        
        if variacao_id in carrinho:
            quantidade_carrinho = carrinho[variacao_id]['quantidade']
            quantidade_carrinho += 1
            
            if variacao_estoque < quantidade_carrinho:
                messages.warning(
                    self.request,
                    f'Estoque insuficiente para {quantidade_carrinho}x do produto "{produto_nome}"'
                    f'Adicionamos {variacao_estoque}x no seu carrinho.'
                ) 
                quantidade_carrinho = variacao_estoque
            
            carrinho[variacao_id]['quantidade'] = quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo'] = preco_unitario * quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo_promocional'] = preco_unitario_promocional * quantidade_carrinho
        else:
            carrinho[variacao_id] = {
                    'produto_id': produto_id,
                    'produto_nome': produto_nome,
                    'variacao_nome': variacao_nome,
                    'variacao_id': variacao_id,
                    'preco_unitario': preco_unitario,
                    'preco_unitario_promocional': preco_unitario_promocional,
                    'preco_quantitativo': preco_unitario,
                    'preco_quantitativo_promocional': preco_unitario_promocional,
                    'quantidade': 1,
                    'slug': slug,
                    'imagem': imagem,
                    }
        '''
        Estas variaveis acima estão sendo atribuido a elas os valores que estão dentro do banco de dados, para melhor entendimento olhar o models. O model Produto está linkado ao model Variacao. A variavel variacao esta com o valor do model Variacao.
        '''
        self.request.session.save()
        # pprint(carrinho)

        messages.success(
            self.request,
            f'Produto {produto_nome} {variacao_nome} adicionado ao seu '
            f'carrinho {carrinho[variacao_id]["quantidade"]}x.'
        )

        return redirect('Lista_produto')
    
    

class RemoverDoCarrinho(View):
    def get(self, *args, **kwargs):
        variacao_id = self.request.GET.get('vid')
        if not variacao_id:
            '''
            aqui verificamos se o id do produto existe, se não redirecionamos o usuario para a pagina em que ela estava 
            '''
            return redirect(self.request.META['HTTP_REFERER'])
        
        if not self.request.session.get('carrinho'):
            '''
            aqui verificamos se self.request.session.get('carrinho') existe, se não redirecionamos o usuario para a pagina em que ela estava.
            '''
            return redirect(self.request.META['HTTP_REFERER'])
        
        if variacao_id not in self.request.session['carrinho']:
            '''
            aqui verificamos se o id do produto não está no carrinho, se não redirecionamos o usuario para a pagina que ele estava.
            '''
            return redirect(self.request.META['HTTP_REFERER'])
        
        carrinho = self.request.session['carrinho'][variacao_id]
        messages.success(
            self.request,
            f'Produto {carrinho['produto_nome']} {carrinho['variacao_nome']} removido com sucesso.'
        )
        
        del self.request.session['carrinho'][variacao_id]
        self.request.session.save()
        return redirect(self.request.META['HTTP_REFERER'])



class Carrinho(View):
    def get(self, *args, **kwargs):
        contexto = {
            'carrinho': self.request.session.get('carrinho', {})
        }
        return render(self.request, 'produto/carrinho.html', contexto)



class ResumoDaCompra(View):
    # Só poderam realizar pagamentos usuario que possuem cadastro
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            '''
            Se o usuario não estiver logado, ele não poderá fazer o pagamento, será redirecionado para a pagina de cadastro
            '''
            return redirect('criar')

        perfil = Perfil.objects.filter(usuario=self.request.user).exists()
        if not perfil:
            '''
            Aqui verificamos se o usuario existe, se não o usuario será redirecionado a pagaina de castro
            '''
            messages.error(
                self.request,
                'usuário sem perfil'
            )
            return redirect('criar')
        if not self.request.session.get('carrinho'):
            '''
            Verificamos se o carrinho possui algum produto, se não redireciona para a pagina principal 
            '''
            messages.error(
                self.request,
                'O carrinho não possui nenhum produto'
            )
            return redirect('Lista_produto')
        contexto = {
            'usuario': self.request.user,
            'carrinho': self.request.session['carrinho'],
        }
        return render(self.request, 'produto/resumodacompra.html', contexto)
