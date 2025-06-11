from django.contrib import admin
from .models import AnalisisNutricional, HistorialMedico, RecursoEducativo

@admin.register(AnalisisNutricional)
class AnalisisNutricionalAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha', 'estado', 'ancho_rostro', 'ratio_ojos_rostro')
    list_filter = ('estado', 'fecha')
    search_fields = ('usuario__username', 'signos_detectados')
    readonly_fields = ('fecha',)
    ordering = ('-fecha',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('usuario', 'imagen', 'fecha', 'estado')
        }),
        ('Mediciones Faciales', {
            'fields': ('ancho_rostro', 'distancia_interpupilar', 'ratio_ojos_rostro', 
                      'ancho_mejillas', 'ratio_mejillas_ojos'),
            'classes': ('collapse',)
        }),
        ('Análisis y Recomendaciones', {
            'fields': ('signos_detectados', 'recomendaciones')
        }),
    )

@admin.register(HistorialMedico)
class HistorialMedicoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'analisis', 'fecha_seguimiento')
    list_filter = ('fecha_seguimiento', 'analisis__estado')
    search_fields = ('usuario__username', 'notas')
    ordering = ('-fecha_seguimiento',)
    
    fieldsets = (
        ('Información del Seguimiento', {
            'fields': ('usuario', 'analisis', 'fecha_seguimiento')
        }),
        ('Notas Médicas', {
            'fields': ('notas',)
        }),
    )

@admin.register(RecursoEducativo)
class RecursoEducativoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'fecha_publicacion')
    list_filter = ('categoria', 'fecha_publicacion')
    search_fields = ('titulo', 'descripcion')
    readonly_fields = ('fecha_publicacion',)
    ordering = ('-fecha_publicacion',)
    
    fieldsets = (
        ('Información del Recurso', {
            'fields': ('titulo', 'categoria', 'fecha_publicacion')
        }),
        ('Contenido', {
            'fields': ('descripcion', 'archivo')
        }),
    )