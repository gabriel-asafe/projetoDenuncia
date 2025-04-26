from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator


class User(AbstractUser):

    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return self.get_full_name() or self.username


class StatusDenuncia(models.Model):
    nome_status = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True, null=True)
    cor = models.CharField(max_length=7, default='#FFFFFF', help_text="Cor em hexadecimal (ex: #FF0000 para vermelho)")
    
    class Meta:
        verbose_name = 'Status de Denúncia'
        verbose_name_plural = 'Status de Denúncias'
    
    def __str__(self):
        return self.nome_status

class Denuncia(models.Model):
    BAIRROS_CHOICES = [
        ('Abaíra', 'Abaíra'),
        ('Andaraí', 'Andaraí'),
        ('Barra da Estiva', 'Barra da Estiva'),
        ('Boninal', 'Boninal'),
        ('Bonito', 'Bonito'),
        ('Ibicoara', 'Ibicoara'),
        ('Ibitiara', 'Ibitiara'),
        ('Iramaia', 'Iramaia'),
        ('Iraquara', 'Iraquara'),
        ('Itaetê', 'Itaetê'),
        ('Jussiape', 'Jussiape'),
        ('Lençóis', 'Lençóis'),
        ('Marcionílio Souza', 'Marcionílio Souza'),
        ('Morro do Chapéu', 'Morro do Chapéu'),
        ('Mucugê', 'Mucugê'),
        ('Nova Redenção', 'Nova Redenção'),
        ('Novo Horizonte', 'Novo Horizonte'),
        ('Palmeiras', 'Palmeiras'),
        ('Piatã', 'Piatã'),
        ('Rio de Contas', 'Rio de Contas'),
        ('Seabra', 'Seabra'),
        ('Souto Soares', 'Souto Soares'),
        ('Utinga', 'Utinga'),
        ('Wagner', 'Wagner')
    ]

    TIPO_CRIME_CHOICES = [
        ('desmatamento', 'Desmatamento'),
        ('queimada', 'Queimada'),
        ('poluicao', 'Poluição'),
        ('caca_ilegal', 'Caça Ilegal'),
        ('pesca_predatoria', 'Pesca Predatória'),
        ('outro', 'Outro'),
    ]

    tipo = models.CharField(max_length=100, choices=TIPO_CRIME_CHOICES)
    descricao = models.TextField()
    data_ocorrencia = models.DateField()
    hora_ocorrencia = models.TimeField()
    data_denuncia = models.DateTimeField(auto_now_add=True)
    
    bairro = models.CharField(max_length=100, choices=BAIRROS_CHOICES)
    bairro_outro = models.CharField(max_length=100, blank=True, null=True)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    
    
    contato_email = models.EmailField(blank=True, null=True)
    
    imagem = models.ImageField(
        upload_to='denuncias/imagens/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]
    )
    video = models.FileField(
        upload_to='denuncias/videos/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['mp4', 'avi', 'mov', 'mpeg'])]
    )
    
    status = models.ForeignKey(
        StatusDenuncia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=1 
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='denuncias'
    )
    
 
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Denúncia'
        verbose_name_plural = 'Denúncias'
        ordering = ['-data_denuncia']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.bairro} ({self.data_ocorrencia})"
    
    def save(self, *args, **kwargs):
            if not self.status_id:
                self.status = StatusDenuncia.objects.get(nome_status='Pendente')
            super().save(*args, **kwargs)