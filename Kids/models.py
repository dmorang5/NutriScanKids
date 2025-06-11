from django.db import models
from django.contrib.auth.models import User

class AnalisisNutricional(models.Model):
    STATUS_CHOICES = [
        ('normal', 'Normal'),
        ('riesgo', 'Riesgo'),
        ('alerta', 'Alerta'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    imagen = models.ImageField(upload_to='analisis/')
    fecha = models.DateTimeField(auto_now_add=True)
    ancho_rostro = models.FloatField(null=True, blank=True)
    distancia_interpupilar = models.FloatField(null=True, blank=True)
    ratio_ojos_rostro = models.FloatField(null=True, blank=True)
    ancho_mejillas = models.FloatField(null=True, blank=True)
    ratio_mejillas_ojos = models.FloatField(null=True, blank=True)
    signos_detectados = models.TextField(blank=True)
    estado = models.CharField(max_length=10, choices=STATUS_CHOICES)
    recomendaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"Análisis de {self.usuario.username} - {self.fecha}"

class HistorialMedico(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    analisis = models.ForeignKey(AnalisisNutricional, on_delete=models.CASCADE)
    notas = models.TextField(blank=True)
    fecha_seguimiento = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Historial de {self.usuario.username} - {self.analisis.fecha}"

class RecursoEducativo(models.Model):
    CATEGORIA_CHOICES = [
        ('alimentacion', 'Alimentación Saludable'),
        ('monitoreo', 'Monitoreo del Crecimiento'),
        ('recetas', 'Recetas Nutritivas'),
        ('signos', 'Signos de Alerta'),
    ]
    
    titulo = models.CharField(max_length=200)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    descripcion = models.TextField()
    archivo = models.FileField(upload_to='recursos/')
    fecha_publicacion = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.titulo