from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
import re
from utils.validacpf import valida_cpf


class Perfil(models.Model):
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    '''
    Este campo deve ser OneToOneField, para que a busca feita na view resumodacompra funcionasse.
    Antes era ForeignKey.
    '''
    idade = models.PositiveIntegerField()
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=11)
    endereco = models.CharField(max_length=50)
    numero = models.CharField(max_length=5)
    complemento = models.CharField(max_length=30)
    bairro = models.CharField(max_length=30)
    cep = models.CharField(max_length=8)
    cidade = models.CharField(max_length=30)
    estado = models.CharField(
        max_length=2,
        default='RJ',
        choices=(
            ('AC', 'Acre'),
            ('AL', 'Alagoas'),
            ('AP', 'Amapá'),
            ('AM', 'Amazonas'),
            ('BA', 'Bahia'),
            ('CE', 'Ceará'),
            ('DF', 'Distrito Federal'),
            ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'),
            ('MA', 'Maranhão'),
            ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'),
            ('PA', 'Pará'),
            ('PB', 'Paraíba'),
            ('PR', 'Paraná'),
            ('PE', 'Pernambuco'),
            ('PI', 'Piauí'),
            ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondônia'),
            ('RR', 'Roraima'),
            ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'),
            ('SE', 'Sergipe'),
            ('TO', 'Tocantins'),
        )
    )
    
    def __str__(self):
        return f'{self.usuario}'
    
    def clean(self):
        '''
        Nesta função validamos os campos cpf e cep. No campo cpf usamos uma função que está no utils/validacpf.py, lá temos uma função que valida cpfs e pode ser reutilizada em outros prpjetos. 
        '''
        error_messages = {}
        
        '''-----------------------------------------------------'''
        # Codigo para tornar o cpf unico na base de dados
        cpf_enviado = self.cpf or None
        cpf_salvo = None
        perfil = Perfil.objects.filter(cpf=cpf_enviado).first()
        
        if perfil:
            cpf_salvo = perfil.cpf
            if cpf_salvo is not None and self.pk != perfil.pk:
                error_messages['cpf'] = 'CPF inválido!'
        '''-----------------------------------------------------'''
        
        if not valida_cpf(self.cpf):
            error_messages['cpf'] = 'Digite um cpf válido!'
            
        if re.search(r'[^0-9]', self.cep) or len(self.cep) < 8:
            error_messages['cep'] = 'CEP inválido! digite apenas números e o campo deve conter 8 números.'
            
        if error_messages:
            raise ValidationError(error_messages)
    