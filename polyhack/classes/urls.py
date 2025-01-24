from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    path('create/', views.create_class, name='create_class'),
    path('', views.list_classes, name='list_classes'),
    path('list/', views.class_list, name='class_list'),
    path('<int:pk>/', views.class_detail, name='class_detail'),
    path('<int:pk>/enroll/', views.enroll_student, name='enroll_student'),
    path('<int:pk>/attendance/', views.manage_attendance, name='manage_attendance'),
    path('<int:pk>/attendance/mark/', views.mark_attendance, name='mark_attendance'),
    path('<int:pk>/attendance/new-session/', views.new_session, name='new_session'),
    path('<int:pk>/attendance/active/', views.active_session, name='active_session'),
    path('<int:pk>/attendance/end/', views.end_session, name='end_session'),
    path('<int:pk>/attendance/cancel/', views.cancel_session, name='cancel_session'),
    path('<int:pk>/process_handwriting/', views.process_handwriting, name='process_handwriting'),
    
] 