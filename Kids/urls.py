from django.urls import path
from . import views
from .views import HistorialMedicoListView
urlpatterns = [
    path('', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
    # dashboard
    path('', views.dashboard, name='dashboard'),
    path('analisis/', views.analisis_nutricional, name='analisis'),
    path('analisis/<int:analisis_id>/', views.detalle_analisis, name='detalle_analisis'),

    #historial
    path('guardar-historial/', views.guardar_en_historial, name='guardar_historial'),
    path('historial/', HistorialMedicoListView.as_view(), name='historial'),

    # recursos
    path('recursos/', views.recursos_educativos, name='recursos'),
    path('recursos/crear/', views.crear_recurso, name='crear_recurso'),
]