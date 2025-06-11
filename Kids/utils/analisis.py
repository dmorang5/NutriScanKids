import cv2
import numpy as np
from scipy.spatial import distance as dist

def analizar_nutricion_facial(imagen):
    """Adapted from your Tkinter OpenCV code for Django"""
    try:
        # Cargar clasificadores
        detector_rostro = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        detector_ojos = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        if detector_rostro.empty() or detector_ojos.empty():
            return None
        
        # Convertir a escala de grises
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        
        # Detectar rostros
        rostros = detector_rostro.detectMultiScale(gris, scaleFactor=1.1, minNeighbors=5)
        
        if len(rostros) == 0:
            return None
        
        # Trabajar con el primer rostro
        x, y, w, h = rostros[0]
        
        # Región de interés (ROI) - Rostro
        roi_gris = gris[y:y+h, x:x+w]
        
        # Detectar ojos en el rostro
        ojos = detector_ojos.detectMultiScale(roi_gris, scaleFactor=1.1, minNeighbors=5)
        
        if len(ojos) < 2:
            return None
        
        # Ordenar ojos de izquierda a derecha
        ojos_ordenados = sorted(ojos, key=lambda ojo: ojo[0])
        
        # Si hay más de 2 ojos detectados, seleccionar los 2 más adecuados
        if len(ojos_ordenados) > 2:
            ojos_ordenados = sorted(ojos_ordenados, key=lambda ojo: ojo[2] * ojo[3], reverse=True)[:2]
            ojos_ordenados = sorted(ojos_ordenados, key=lambda ojo: ojo[0])
        
        ojo_izq = ojos_ordenados[0]
        ojo_der = ojos_ordenados[1]
        
        # Calcular centros de los ojos
        centro_ojo_izq = (x + int(ojo_izq[0] + ojo_izq[2]/2), y + int(ojo_izq[1] + ojo_izq[3]/2))
        centro_ojo_der = (x + int(ojo_der[0] + ojo_der[2]/2), y + int(ojo_der[1] + ojo_der[3]/2))
        
        # Calcular métricas
        distancia_interpupilar = dist.euclidean(centro_ojo_izq, centro_ojo_der)
        ancho_rostro = w
        ratio_ojos_rostro = distancia_interpupilar / ancho_rostro
        
        altura_mejillas = int(y + h * 2/3)
        pos_mejilla_izq = (x, altura_mejillas)
        pos_mejilla_der = (x + w, altura_mejillas)
        ancho_mejillas = dist.euclidean(pos_mejilla_izq, pos_mejilla_der)
        ratio_mejillas_ojos = ancho_mejillas / distancia_interpupilar
        
        # Crear imagen con resultados visuales
        imagen_resultado = imagen.copy()
        
        # Dibujar anotaciones
        cv2.rectangle(imagen_resultado, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        for (ex, ey, ew, eh) in ojos_ordenados:
            cv2.rectangle(imagen_resultado, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (0, 255, 0), 2)
        
        cv2.circle(imagen_resultado, centro_ojo_izq, 5, (0, 0, 255), -1)
        cv2.circle(imagen_resultado, centro_ojo_der, 5, (0, 0, 255), -1)
        cv2.line(imagen_resultado, centro_ojo_izq, centro_ojo_der, (0, 255, 255), 2)
        cv2.line(imagen_resultado, pos_mejilla_izq, pos_mejilla_der, (255, 255, 0), 2)
        
        # Definir umbrales
        umbral_ratio_ojos_rostro = 0.35
        umbral_ratio_mejillas_ojos = 3.0
        
        # Evaluación de posibles signos
        signos_desnutricion = []
        
        if ratio_ojos_rostro > umbral_ratio_ojos_rostro:
            signos_desnutricion.append("Rostro estrecho en proporción a los ojos")
        
        if ratio_mejillas_ojos < umbral_ratio_mejillas_ojos:
            signos_desnutricion.append("Posible hundimiento de mejillas")
        
        # Resultado final
        resultado = {
            "ancho_rostro": ancho_rostro,
            "distancia_interpupilar": distancia_interpupilar,
            "ratio_ojos_rostro": ratio_ojos_rostro,
            "ancho_mejillas": ancho_mejillas,
            "ratio_mejillas_ojos": ratio_mejillas_ojos,
            "signos_desnutricion": signos_desnutricion,
            "posible_desnutricion": len(signos_desnutricion) > 0,
            "imagen_resultado": imagen_resultado
        }
        
        return resultado
    
    except Exception as e:
        print(f"Error en el análisis: {str(e)}")
        return None