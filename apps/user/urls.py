# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register_user, name='register_user'),
    path('login', views.login_user, name='login_user'),
    path('info', views.get_user_info, name='get_user_info'),
    path('logout', views.logout_user, name='logout_user'),
    path('getSession', views.get_session_info, name='get_session_info'),
    path('get_users', views.get_users, name='get_users'),
]
