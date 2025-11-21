from django.urls import path
from . import views
urlpatterns = [
    path('register/', views.register, name='register'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('history/', views.history, name='history'),
    path('summary/<int:pk>/', views.get_summary, name='get_summary'),
    path('generate_pdf/<int:pk>/', views.generate_pdf, name='generate_pdf'),
]
