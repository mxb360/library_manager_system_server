"""libaray_manage_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from library_app import views

urlpatterns = [
    path('bookmanager/index', views.index),
    path('bookmanager/login', views.login),
    path('bookmanager/logout', views.logout),
    path('bookmanager/user_info', views.user_info),
    path('bookmanager/add_user', views.add_user),
    path('bookmanager/change_password', views.change_password),
    path('bookmanager/get_user_info', views.get_user_info),
    path('bookmanager/change_user_info', views.change_user_info),
    path('bookmanager/remove_user', views.remove_user),
    path('bookmanager/search_user', views.search_user),
    path('bookmanager/get_category', views.get_category),
    path('bookmanager/remove_category', views.remove_category),
    path('bookmanager/change_category', views.change_category),
    path('bookmanager/add_category', views.add_category),
    path('bookmanager/add_book', views.add_book),
    path('bookmanager/get_book', views.get_book),
    path('bookmanager/change_book', views.change_book),
    path('bookmanager/remove_book', views.remove_book),
    path('bookmanager/search_book', views.search_book),
]
