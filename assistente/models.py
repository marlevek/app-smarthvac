from django.db import models
from django.utils import timezone


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
    