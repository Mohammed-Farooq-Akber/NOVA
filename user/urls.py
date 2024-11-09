from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('base', base, name='base'),
    path('test', test, name='test'),

]
