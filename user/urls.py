from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('base', base, name='base'),
    path('test', test, name='test'),
    path('', upload_image_and_voice_input, name='upload_image_and_voice_input'),
    path('dashboard', dashboard, name='dashboard'),
    path('recipee_slider', recipee_slider, name='recipee_slider'),
    path('rotting_index', rotting_index, name='rotting_index'),
    path('video_feed/', video_feed, name='video_feed'),
    path('community/', community, name='community'),
    path('fruit_detect', index1, name='index1'),
    path('video_feed1', video_feed1, name='video_feed1'),
    path('get_detections1', get_detections1, name='get_detections1'),
]
