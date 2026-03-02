from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('menu/', views.menu_principal, name='menu_principal'),
    path('empleados/', views.modulo_empleados, name='modulo_empleados'),
    path('rol-pagos/', views.modulo_rol_pagos, name='modulo_rol_pagos'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('meme/', views.meme, name='meme'),
]
