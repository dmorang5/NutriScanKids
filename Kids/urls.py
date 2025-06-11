from django.urls import path
from . import views
from .views import HistorialMedicoListView
urlpatterns = [
    path('', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('', views.dashboard, name='dashboard'),
    path('analisis/', views.analisis_nutricional, name='analisis'),
    path('analisis/<int:analisis_id>/', views.detalle_analisis, name='detalle_analisis'),
    path('guardar-historial/', views.guardar_en_historial, name='guardar_historial'),
    path('historial/', HistorialMedicoListView.as_view(), name='historial'),

    path('recursos/', views.recursos_educativos, name='recursos'),
]

    #path('historial/', views.historial, name='historial'),
