from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from django.views import View
from django.http import HttpResponse
from perfil.models import Perfil
from perfil.forms import UserForm, PerfilForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
import copy


class BasePerfil(View):
    '''
    Revisar a forma que foi feita o formulario para melhor entendimento.
    '''
    template_name = 'perfil/criar.html'
    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        
        self.carrinho = copy.deepcopy(self.request.session.get('carrinho', {}))
        # Nesta variavel estamos pegando os valores do carrinho para que o usuario atualizar suas informações não perca od produtos que foram selecionados. Esta variavel será usada na class Criar logo abaixo.
        
        self.perfil = None
        
        if self.request.user.is_authenticated:
            # usuário logado 
            self.perfil = Perfil.objects.filter(usuario=self.request.user).first()
            self.context = {
                'userform': UserForm(data=self.request.POST or None, 
                                     usuario=self.request.user,
                                     instance=self.request.user,
                                     ),
                
                'perfilform': PerfilForm(data=self.request.POST or None,
                                         instance=self.perfil
                                         ),
            }
            '''
            'userform' -> formulario para o cadastro.
            
            se o usuário estiver logado, os campos do formulario do cadastro ja estarão preenchidos com as informações do usuario que estão no banco de dados. 
            as informções vieram por esse meio: usuario=self.request.user,
                                                instance=self.request.user
                                                
            'perfilform' -> formulario para login.
            '''
        else:
            # usuario não logado 
            self.context = {
                'userform': UserForm(data=self.request.POST or None),
                'perfilform': PerfilForm(data=self.request.POST or None),
            }
            
        self.userform = self.context['userform']
        self.perfilform = self.context['perfilform']
        '''
        Essas variaveis estão contento os formularios para que possamos fazer uma validação e logo salvar as informações no banco de dados. Variaveis que serão usadas na classe "CRIAR" logo abaixo.
        '''
        
        if self.request.user.is_authenticated:
            # se o usuario estiver logado será renderizada outra página.
            self.template_name = 'perfil/atualizar.html'
        
        self.renderizar = render(self.request, self.template_name, self.context)
        
    def get(self, *args, **kwargs):
        return self.renderizar


class Criar(BasePerfil):
    def post(self, *args, **kwargs):
        if not self.userform.is_valid() or not self.perfilform.is_valid():
            return self.renderizar
        
        username = self.userform.cleaned_data.get('username')
        password = self.userform.cleaned_data.get('password')
        email = self.userform.cleaned_data.get('email')
        first_name = self.userform.cleaned_data.get('first_name')
        last_name = self.userform.cleaned_data.get('last_name')
        '''
        Varivel password está armazenando o valor da senha que é passada no formulario "userform" para que possa salva-la criptografada
        '''
        
        if self.request.user.is_authenticated:
            '''
            Nesta exceção estmaos salvando o formulario dos usuários ja logados(existentes), seria o formulario de atualização dos dados 
            '''
            usuario = get_object_or_404(User, username=self.request.user.username)
            usuario.username = username
            
            if password:
                usuario.set_password(password)
                
            usuario.email = email
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.save()
            
            # Nestas condições abaixo estamos salvando as informações do 
            if not self.perfil:
                self.perfilform.cleaned_data['usuario'] = usuario
                perfil = Perfil(**self.perfilform.cleaned_data)
                perfil.save()
            else:
                perfil = self.perfilform.save(commit=False)
                perfil.usuario = usuario
                perfil.save()
        else:
            '''
            Nessa parte estamos salvando o formulario de usuários não logados, usuarios que desejam fazer o cadastro.
            '''
            # Userform
            usuario = self.userform.save(commit=False)
            # Aqui não salvamos as informações de imediato, por isso o commit=False
            usuario.set_password(password)
            # Logo após usamos esta função para que possa salvar a senha de forma criptografada, em seguida salvamos as informações no banco de dados.
            usuario.save()
            
            # Perfilform
            conta = self.perfilform.save(commit=False)
            conta.usuario = usuario
            conta.save()
        
        if password:
            autentica = authenticate(
                self.request,
                username=usuario,
                password=password
            )
            if autentica:
                '''
                Fazemos um processo de autenticação das informações do usuario, se autenticado o usuário em seguida será logado, porem o usuario não está autorizado a acessar a area admin. Não se perderá os produtos do carrinho que foram selecionados antes de se cadastrar, serão copiados e recolocados no carrinho. 
                '''
                login(self.request, user=usuario)
            
        self.request.session['carrinho'] = self.carrinho
        '''
        Aqui fazemos o processo para que o usuario não perca os produtos selecionados quando for realizado o login. Esta variavel está sendo chamada na classe BasePerfil
        '''
        self.request.session.save()
        
        messages.success(
            self.request,
            'Seu cadastro foi criado ou atualizado com sucesso!'
        )
        return redirect('criar')
        # Assim que o usuario concluir o cadastro logo em seguida já será redirecionado para a area de atualização de dados 
        return self.renderizar


class Atualizar(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Atualizar')


class Login(View):
    def post(self, *args, **kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        '''
        Aqui buscamos os names dos campos que estão lano html, consultar criar.html.
        '''
        
        if not username or not password:
            '''
            Aqui verificamos se os campos não condizem com o que está na base de dados
            '''
            messages.error(
                self.request,
                'Usuário ou senha inválido!'
            )
            return redirect('criar')
        
        usuario = authenticate(self.request, username=username, password=password)
        '''
        Se não houver nada de errado autenticamos os campos passados no login para realizar dar acesso ao usuario
        '''
        
        if not usuario:
            '''
            Verificação de não sei por qual cargas d`aguas as informções nao forem autenticadas irá acontecer esta exceção e o usuário não sera logado
            '''
            messages.error(
                self.request,
                'Usuário ou senha inválido!'
            )
            return redirect('criar')
        
        login(self.request, user=usuario)
        '''
        Aqui logamos o usuario caso esteja tudo correto.
        Temos outro exemplo de login na classe Criar. Pode ajudar para um melhor entendimento para logar um usuario.
        '''
        messages.success(
            self.request,
            'Você realizou o seu login e agora pode finalizar as suas compras!'
        )
        return redirect('Carrinho')


class Logouth(View):
    def get(self, *args, **kwargs):
        carrinho = copy.deepcopy(self.request.session.get('carrinho'))
        '''
        Aqui fazemos o mesmo procedimento para salvar a informações do carrinho para que o usuario não perca as informações que ja estavam nele. o codigo termina mais abaixo.
        '''
        logout(self.request)
        # logout serve para deslogar o usuario, para que ele saia do acesso do site
        self.request.session['carrinho'] = carrinho
        self.request.session.save()
        return redirect('Lista_produto')