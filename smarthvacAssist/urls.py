from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    
     # LOGIN / LOGOUT
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='assistente/login.html'),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    # APP
    path('', include('assistente.urls')),
]
