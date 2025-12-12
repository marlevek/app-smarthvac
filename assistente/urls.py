from django.urls import path 
from . import views 

urlpatterns = [
    path('assistente/', views.tela_assistente, name='tela_assistente'),
]