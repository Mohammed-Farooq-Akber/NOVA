from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('hello/', hello, name='hello'),
    path('generate_map/', generate_map, name='generate_map'),
    path('calculate/', calculate, name='calculate'),
    path('cart/', cart, name='cart'),
    path('spline/',spline, name='spline')
]
