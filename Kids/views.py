import datetime
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, UserRegistrationForm
from .forms import AnalisisForm, HistorialForm, RecursoEducativoForm
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import AnalisisNutricional, HistorialMedico, RecursoEducativo
from .utils.analisis import analizar_nutricion_facial
import cv2
import numpy as np
from PIL import Image
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from django.contrib import messages

# Vista basada en función para login o inicio de sesion
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, 
                                 username=cd['username'],
                                 password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Inicio exitososo')
                    return render(request, 'detector/base.html')
                else: 
                    #return HttpResponse('Autenticación negada')
                    messages.warning(request, "Autenticación negada")
                    return redirect('login')
            else:
                messages.warning(request, "Credenciales inválidas")
                return redirect('login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form':form})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Crear el nuevo usuario, pero sin guardar aún
            new_user = user_form.save(commit=False)
            # Asignar la contraseña
            new_user.set_password(user_form.cleaned_data['password'])
            # Guardar el usuario
            new_user.save()
            messages.success(request, f'Registro exitososo')
            return render(request, 'detector/base.html')
    else:
        user_form = UserRegistrationForm()  # si no es POST, crea un formulario vacío
    messages.warning(request, "Regsitro inválido")
    return render(request, 'account/registro.html', {'user_form': user_form})


@login_required
def dashboard(request):
    return render(request, 'detector/base.html')

@login_required
def analisis_nutricional(request):
    analisis = None
    mostrar_resultados = False
    if request.method == 'POST':
        form = AnalisisForm(request.POST, request.FILES)
        if form.is_valid():
            analisis = form.save(commit=False)
            analisis.usuario = request.user
            
            # Procesar imagen con OpenCV
            img = Image.open(analisis.imagen)
            img_array = np.array(img)
            
            # Convertir RGB a BGR si es necesario
            if img_array.shape[2] == 3:  # RGB
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            elif img_array.shape[2] == 4:  # RGBA
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
            
            # Analizar imagen
            resultado = analizar_nutricion_facial(img_array)
            
            if resultado:
                # Guardar resultados
                analisis.ancho_rostro = resultado['ancho_rostro']
                analisis.distancia_interpupilar = resultado['distancia_interpupilar']
                analisis.ratio_ojos_rostro = resultado['ratio_ojos_rostro']
                analisis.ancho_mejillas = resultado['ancho_mejillas']
                analisis.ratio_mejillas_ojos = resultado['ratio_mejillas_ojos']
                analisis.signos_detectados = "|".join(resultado['signos_desnutricion'])
                analisis.signos_lista = analisis.signos_detectados.split('|')

                if resultado['posible_desnutricion']:
                    analisis.estado = 'riesgo' if len(resultado['signos_desnutricion']) == 1 else 'alerta'
                else:
                    analisis.estado = 'normal'

                # Generar observaciones basadas en el estado
                if analisis.estado == 'normal':
                    observaciones = "Los parámetros evaluados se encuentran dentro de los rangos normales. Se recomienda mantener los hábitos alimenticios actuales."
                elif analisis.estado == 'riesgo':
                    observaciones = "Se detectan signos de posible desnutrición moderada. Se recomienda seguimiento periódico y consulta con especialista."
                elif analisis.estado == 'alerta':
                    observaciones = "Se detectan signos de desnutrición severa. Es necesaria atención médica inmediata y seguimiento especializado."
                else:
                    observaciones = "Estado no determinado. Se recomienda evaluación médica para determinar el estado nutricional."

                # Agregar observaciones al análisis
                analisis.signos_detectados = observaciones

                # Recomendaciones específicas según el estado
                if analisis.estado == 'normal':
                    recomendaciones = [
                        "Mantener una dieta balanceada con todos los grupos alimenticios",
                        "Realizar controles médicos periódicos",
                        "Mantener actividad física adecuada para la edad",
                        "Asegurar una hidratación adecuada"
                    ]
                elif analisis.estado == 'riesgo':
                    recomendaciones = [
                        "Consultar con un pediatra o nutricionista infantil lo antes posible",
                        "Aumentar la ingesta de proteínas de alta calidad en la dieta diaria",
                        "Incluir alimentos ricos en hierro y zinc como legumbres, carnes magras y verduras de hoja verde",
                        "Realizar un seguimiento del peso semanalmente",
                        "Implementar 5 comidas diarias para asegurar un aporte calórico adecuado"
                    ]
                elif analisis.estado == 'alerta':
                    recomendaciones = [
                        "Buscar atención médica inmediata",
                        "Consultar con un especialista en nutrición pediátrica",
                        "Implementar un plan nutricional supervisado",
                        "Monitoreo médico constante",
                        "Evaluación de posibles causas subyacentes"
                    ]
                else:
                    recomendaciones = [
                        "Consultar con un profesional de la salud",
                        "Realizar evaluación nutricional completa",
                        "Seguir las indicaciones médicas"
                    ]
                analisis.recomendaciones = "|".join(recomendaciones)
                analisis.recomendaciones_lista = analisis.recomendaciones.split('|')

                analisis.save()
                
                # Guardar imagen con anotaciones
                img_resultado = Image.fromarray(cv2.cvtColor(resultado['imagen_resultado'], cv2.COLOR_BGR2RGB))
                img_path = os.path.join(settings.MEDIA_ROOT, 'resultados', f'resultado_{analisis.id}.jpg')
                img_resultado.save(img_path)
                mostrar_resultados = True
                #return redirect('analisis', analisis_id=analisis.id)

            else: 
                messages.warning(request, 'No se pudo procesar la imagen. Intenta con otra fotografía.')
                print("No se pudo procesar la imagen. Intenta con otra fotografía.")
    else:
        form = AnalisisForm()
    
    return render(request, 'detector/analisis.html', {
        'form': form,
        'analisis': analisis,
        'mostrar_resultados': mostrar_resultados,
        'MEDIA_URL': settings.MEDIA_URL,})


@login_required
def detalle_analisis(request, analisis_id):
    analisis = AnalisisNutricional.objects.get(id=analisis_id, usuario=request.user)
    
    if request.method == 'POST':
        form = HistorialForm(request.POST)
        if form.is_valid():
            historial = form.save(commit=False)
            historial.usuario = request.user
            historial.analisis = analisis
            historial.save()
            return redirect('historial')
    else:
        form = HistorialForm()
    
    return render(request, 'includes/modal_detalle.html', {
        'analisis': analisis,
        'form': form
    })


class HistorialMedicoListView(LoginRequiredMixin, ListView):
    model = HistorialMedico
    template_name = 'detector/historial.html'
    context_object_name = 'historial'

    def get_queryset(self):
        queryset = HistorialMedico.objects.filter(usuario=self.request.user).order_by('-fecha_seguimiento')

        historial = []
        for item in queryset:
            analisis = item.analisis
            estado = analisis.estado

            if estado == 'normal':
                riesgo = "Sin riesgo"
                bg = "#4CAF50"
                fg = "white"
            elif estado == 'riesgo':
                riesgo = "Riesgo de Desnutrición Moderado"
                bg = "#FFC107"
                fg = "#333"
            elif estado == 'alerta':
                riesgo = "Riesgo de Desnutrición Alto"
                bg = "#F44336"
                fg = "white"
            else:
                riesgo = "Desconocido"
                bg = "#9E9E9E"
                fg = "white"
            
            #Procesar recomendaciones correctamente
            recomendaciones_text = ""
            if analisis.recomendaciones:
                # Dividir por '|' y crear string con saltos de línea
                recomendaciones_raw = analisis.recomendaciones.split('|')
                recomendaciones_list = [rec.strip() for rec in recomendaciones_raw if rec.strip()]
                # Convertir a string con numeración
                recomendaciones_text = '\n'.join([f"{i+1}. {rec}" for i, rec in enumerate(recomendaciones_list)])


            # Recomendaciones por defecto (puedes personalizarlas según el estado)
            recomendaciones_default = [
                "Consultar con un pediatra o nutricionista infantil lo antes posible",
                "Aumentar la ingesta de proteínas de alta calidad en la dieta diaria",
                "Incluir alimentos ricos en hierro y zinc como legumbres, carnes magras y verduras de hoja verde",
                "Realizar un seguimiento del peso semanalmente",
                "Implementar 5 comidas diarias para asegurar un aporte calórico adecuado"
            ]

            # Generar observaciones basadas en el estado
            if estado == 'normal':
                observaciones = "Los parámetros evaluados se encuentran dentro de los rangos normales. Se recomienda mantener los hábitos alimenticios actuales."
            elif estado == 'riesgo':
                observaciones = "Se detectan signos de posible desnutrición moderada. Se recomienda seguimiento periódico y consulta con especialista."
            elif estado == 'alerta':
                observaciones = "Se detectan signos de desnutrición severa. Es necesaria atención médica inmediata y seguimiento especializado."
            else:
                observaciones = "Estado no determinado. Se recomienda evaluación médica para determinar el estado nutricional."

            historial.append({
                'id': item.id,
                # 'fecha': item.fecha_seguimiento if item.fecha_seguimiento else analisis.fecha,
                'fecha': item.fecha_seguimiento,  # solo fecha (DateField)
                'fecha_analisis': analisis.fecha,  # con hora (DateTimeField)
                'riesgo': riesgo,
                'estado': estado,
                'color': bg,
                'texto_color': fg,
                'observaciones': observaciones,
                'imagen': analisis.imagen,
                'recomendaciones': recomendaciones_text,
                # 'recomendaciones': '\n'.join(recomendaciones_default)
            })

        return historial


@login_required
@csrf_exempt
def guardar_en_historial(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            analisis_id = data.get('analisis_id')
            
            # Obtener el análisis
            analisis = AnalisisNutricional.objects.get(id=analisis_id, usuario=request.user)
            
            # Verificar si ya existe en el historial
            historial_existente = HistorialMedico.objects.filter(
                usuario=request.user, 
                analisis=analisis
            ).first()
            
            if historial_existente:
                return JsonResponse({'success': False, 'message': 'Este análisis ya está en tu historial'})
            
            # Crear entrada en historial
            historial = HistorialMedico.objects.create(
                usuario=request.user,
                analisis=analisis,
                notas="Análisis guardado desde la vista de resultados",
                fecha_seguimiento=datetime.date.today()  
            )
            
            return JsonResponse({'success': True, 'message': 'Guardado en historial correctamente'})
            
        except AnalisisNutricional.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Análisis no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
def recursos_educativos(request):
    recursos = RecursoEducativo.objects.all().order_by('-fecha_publicacion')
    return render(request, 'detector/recursos.html', {'recursos': recursos})

@login_required
def crear_recurso(request):
    if request.method == 'POST':
        form = RecursoEducativoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Recurso creado exitosamente")
            return redirect('recursos') 
    else:
        form = RecursoEducativoForm()
    
    return render(request, 'detector/crear_recurso.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, f'Cierre exitososo')
    return redirect('login')

