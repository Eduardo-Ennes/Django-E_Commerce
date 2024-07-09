from django import forms 
from . import models
from django.contrib.auth.models import User



class PerfilForm(forms.ModelForm):
    class Meta:
        model = models.Perfil
        fields = '__all__'
        exclude = ('usuario',)
        # exclude = ('usuario',) -> está excluindo o usuário que esta no banco de dados 



class UserForm(forms.ModelForm):
    password = forms.CharField(required=False, 
                               widget=forms.PasswordInput(), 
                               label='Senha')
    
    password2 = forms.CharField(required=False, 
                               widget=forms.PasswordInput(), 
                               label='Confirmação da senha')
    
    def __init__(self, usuario=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.usuario = usuario
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password', 'password2', 'email')
        # esses campos selecionados é o que serão utilizados pelo usuario, para registrar e atualizar. Se não selecionarmos os campos o usuario que se cadastrar ira se registrar como owner.  
        
    def clean(self, *args, **kwargs):
        data = self.data 
        cleaned = self.cleaned_data
        # na variavel "cleaned" estamos acessando as informações dos campos que estão no formulario cadastro
        validation_error_msgs = {}
        # esta variavel é para escrever as mensagens que serão exibidas caso haja excessão
        # ------------------------------------------------------------------
        usuario_data = cleaned.get('username')
        password_data = cleaned.get('password')
        password2_data = cleaned.get('password2')
        email_data = cleaned.get('email')
        # Estas variaveis acima estão pegando os valores dos campos do formulario
        
        usuario_db = User.objects.filter(username=usuario_data).first()
        email_db = User.objects.filter(email=email_data).first()
        
        error_msg_user_exists = 'Este usuário já está em uso'
        error_msg_email_exists = 'Este e-mail já está em uso'
        error_msg_password_match = 'As duas senhas não conferem'
        error_msg_password_short = 'Sua senha deve conter no mínimo 6 caracteres'
        validation_error_required_msgs = 'Este campo é obrigatório'
        # mensagens de error para as exceções 
        
        if self.usuario:
            '''
            Essas validações é caso o usuário esteja logado, que será as validações do campo de atualização.
            '''
            if password_data:
                if password_data != password2_data:
                    validation_error_msgs['password'] = error_msg_password_match
                    validation_error_msgs['password2'] = error_msg_password_match  
                    
                if len(password_data) < 2:
                    validation_error_msgs['password'] = error_msg_password_short
                    
            if email_db:
                if email_data != email_db.email:  
                    validation_error_msgs['email'] = error_msg_email_exists         
        else:
            '''
            Nesta condição é caso o usuário não esteja logado, que será a validação do cadastro.
            '''
            if usuario_db:
                validation_error_msgs['username'] = error_msg_user_exists
            
            if email_db:
                validation_error_msgs['email'] = error_msg_email_exists
                
            if not password_data:
                validation_error_msgs['password'] = validation_error_required_msgs
                
            if not password2_data:
                validation_error_msgs['password2'] = validation_error_required_msgs
                
            if password_data != password2_data:
                validation_error_msgs['password'] = error_msg_password_match
                validation_error_msgs['password2'] = error_msg_password_match
            
        if validation_error_msgs:
            raise(forms.ValidationError(validation_error_msgs))
        