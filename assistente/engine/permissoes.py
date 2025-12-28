def tem_plano_pro(user):
   try:
       return user.perfil.plano == 'pro'
   except:
       return False