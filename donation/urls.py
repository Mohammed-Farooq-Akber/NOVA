# Create your views here.
from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('donation_form', food_donation_form, name='food_donation_form'),
    path('food-donations/', food_donations_list, name='food_donations_list'),
    path('ngo_list', ngo_list, name='ngo_list'),
    path('route_optimize', index, name='index'),
    path('locations/',get_locations, name='locations'),
    path('route/', generate_route, name='generate_route'),
]