# therapy_bot_project/bot/urls.py
from django.urls import path
from . import views
app_name = 'bot'
urlpatterns = [
    path('', views.home, name='bot'),
    path('send_message/', views.send_message, name='send_message'),  # No leading slash here
    path('audio/<str:filename>/', views.serve_audio, name='serve_audio'),
]
