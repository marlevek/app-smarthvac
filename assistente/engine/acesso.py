from assistente.models import UsuarioAutorizado 


def usuario_autorizado(user):
    if not user.is_authenticated:
        return False 
    
    email = user.email or user.username
    
    return UsuarioAutorizado.objects.filter(
        email = email,
        ativo = True
    ).exists()