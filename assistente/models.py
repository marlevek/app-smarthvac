from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User



class ChatConversa(models.Model):
    session_key = models.CharField(max_length=64, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField(db_index=True)
    
    def __str__(self):
        return f'Chatconversa({self.session_key})'
    
    
class ChatMensagem(models.Model):
    conversa = models.ForeignKey(ChatConversa, on_delete=models.CASCADE, related_name='mensagens')
    role = models.CharField(max_length=20)
    content = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['criado_em']
    
    def __str__(self):
        return f"{self.role} @ {self.criado_em: strftime('%d/%m/%Y %H:%M')}"


class UsuarioAutorizado(models.Model):
    email = models.EmailField(unique=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.email 
    

class UsoIA(models.Model):
    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='usos_ia'
    )
    data = models.DateField()
    total_chamadas = models.PositiveIntegerField(default=0)

    
    class Meta:
        unique_together = ('usuario', 'data')
        
    def __str__(self):
        return f"{self.usuario.email} - {self.data} - {self.total_chamadas}"


class PerfilUsuario(models.Model):
    PLANO_CHOICES = (
        ("basic", "Básico"),
        ("pro", "PRO"),
    )

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil"
    )
    plano = models.CharField(
        max_length=10,
        choices=PLANO_CHOICES,
        default="basic"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.email} ({self.plano})"
