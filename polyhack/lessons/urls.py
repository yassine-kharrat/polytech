from django.urls import path
from . import views

app_name = 'lessons'

urlpatterns = [
    path('create/<int:class_pk>/', views.create_lesson, name='create_lesson'),
    path('<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('<int:pk>/generate-summary/', views.generate_summary, name='generate_summary'),
] 