from django.db import models
from PIL import Image
import os 
from django.conf import settings
from django.utils.text import slugify


class Produto(models.Model):
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
    
    nome = models.CharField(max_length=255)
    descricao_curta = models.TextField(max_length=255)
    descricao_longa = models.TextField()
    imagem = models.ImageField(upload_to='media/%y/%m/')
    slug = models.SlugField(unique=True, blank=True, null=True)
    preco_marketing = models.FloatField()
    preco_marketing_promocional = models.FloatField(default=0)
    tipo = models.CharField(default='V', max_length=1, choices=(
        ('V', 'Variação'),
        ('S', 'Simples'),
    ))

    '''
    get_preco_formatato e get_preco_format - são duas funções para formartar para o real brasileiro.
    '''
    def get_preco_formatato(self):
        return f'R${self.preco_marketing:.2f}'.replace('.', ',')
    get_preco_formatato.short_description = 'Preço'
    
    def get_preco_format(self):
        return f'R${self.preco_marketing_promocional:.2f}'.replace('.', ',')
    get_preco_format.short_description = 'Preço promocional'
    
    @staticmethod
    def resize_image(img, new_width=800):
        '''
        Estamos usando o pillow para o redimencionamento da imagem, o pillow deve ser instalado e importar sua biblioteca, sua importação está na linha 2
        
        Este metodo abaixo é para redimencionar imagens.
        
        em todos os projetos essa foi a melhor maneira que eu encontrei até agora para redimencionar imagens. 
        
        Este código pode ser reutilizado em outras aplicações.
        '''
        img_full_path = os.path.join(settings.MEDIA_ROOT, img.name)
        # img_full_path -> neste código fazemos uma busca até a imagem para redimensiona-las
        img_pil = Image.open(img_full_path)
        original_width, original_heigth = img_pil.size
        
        if original_width <= new_width:
            print('A imagem não pode ser redimencionada porque a largura e menor ou igual a nova largura.')
            img_pil.close()
            return
        
        new_heigth = round((new_width * original_heigth) / original_width)
        new_img = img_pil.resize((new_width, new_heigth), Image.LANCZOS)
        new_img.save(
            img_full_path,
            optimize=True, quality=50
        )
        print('A imagem foi redimencionada! ')
        # O códido de redimenção de imagens no metodo save abaixo.


    def save(self, *args, **kwargs):
        if not self.slug:
            '''
            Neste metodo usando o sligify que é um biblioteca que deverá ser importada, criamos uma slug para um produto que será cadastrado com o seu nome e pk.

            No projeto blog foi usado outro metodo para se criar uma slug. 
            
            Este metodo é mais simples de ser usado e usa-se a pk que é algo único e não gerará conflitos. Usar este metodo em outros projetos.
            '''
            slug = f'{slugify(self.nome)}'
            self.slug = slug
        super().save(*args, **kwargs)
        
        max_imagine_size = 800
        
        if self.imagem:
            self.resize_image(self.imagem, max_imagine_size)


    def __str__(self):
        return self.nome
    
    
    
class Variacao(models.Model):
    class Meta:
        verbose_name = 'Variação'
        verbose_name_plural = 'Variações'
    
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    nome = models.CharField(max_length=150, blank=True, null=True)
    preco = models.FloatField()
    preco_promocional = models.FloatField(default=0)
    estoque = models.PositiveIntegerField(default=1)
    
    def __str__(self) -> str:
        return self.nome or self.produto.nome
    