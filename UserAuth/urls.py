from django.contrib import admin
from django.urls import path, include

from restaurants.views import restaurant_detail_view
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('profile/', views.profile, name='profile'),
    path('restaurants/details/<str:place_id>', restaurant_detail_view, name='restaurant_detail_view')
]