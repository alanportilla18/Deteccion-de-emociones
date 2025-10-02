# 🎭 Detección de Emociones con Deep Learning

Sistema avanzado de reconocimiento de emociones en tiempo real utilizando redes neuronales convolucionales (CNN) con arquitectura ResNet y mecanismos de atención CBAM.

## 🌟 Características Principales

- **Detección en tiempo real** de emociones faciales usando modelos de deep learning
- **Interfaz gráfica moderna** desarrollada con Tkinter
- **Múltiples modelos de IA** disponibles para diferentes casos de uso
- **Generación automática de reportes** en formato PDF
- **Métricas detalladas** de rendimiento y estadísticas
- **Configuración flexible** de intervalos de captura

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8 o superior
- Cámara web funcional
- Entorno virtual (recomendado)

### Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   cd "C:\Users\tu_usuario\Documents\GUI emotion"
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Uso de la Aplicación

### Ejecutar la aplicación
```bash
python app.py
```

### Flujo de trabajo
1. **Seleccionar modelo**: Elige uno de los 3 modelos disponibles
2. **Iniciar cámara**: Presiona "Iniciar Cámara" para comenzar
3. **Detección automática**: El sistema detectará emociones según el intervalo configurado
4. **Ver resultados**: Revisa métricas en tiempo real y genera reportes

## 🧪 Modelos Disponibles

El sistema incluye 3 modelos entrenados específicamente conservados:

- **`emotion_model.h5`**: Modelo base de detección de emociones
- **`prueba_nuevo_modelo_cnn.h5`**: CNN optimizada para precisión
- **`resnet_rapido.h5`**: Modelo ResNet optimizado para velocidad

## 📊 Funcionalidades

### Detección en Tiempo Real
- Procesamiento de video en vivo (~30 FPS)
- Clasificación de múltiples emociones
- Confidence score para cada predicción
- Intervalos de captura configurables

### Análisis y Reportes
- Historial completo de sesiones
- Estadísticas de emociones dominantes
- Métricas de rendimiento del sistema
- Exportación a PDF con gráficos

### Interfaz de Usuario
- Diseño moderno e intuitivo
- Estados visuales dinámicos
- Controles accesibles
- Feedback en tiempo real

## 📁 Estructura del Proyecto

```
GUI emotion/
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias del proyecto
├── README.md             # Esta documentación
├── models/               # Modelos de IA entrenados
│   ├── emotion_model.h5
│   ├── prueba_nuevo_modelo_cnn.h5
│   └── resnet_rapido.h5
├── utils/                # Utilidades del proyecto
│   ├── model_utils.py    # Funciones de carga y procesamiento de modelos
│   └── pdf_report.py     # Generación de reportes PDF
├── fer2013/              # Dataset de prueba
│   ├── test/            # Imágenes de prueba por emoción
│   └── train/           # Datos de entrenamiento
└── results/             # Reportes generados automáticamente
```

## 🔧 Configuración Avanzada

### Variables de Entorno
La aplicación se configura automáticamente, pero puedes personalizar:

- **Intervalo de captura**: Ajustable desde la interfaz (0.1 - 10 segundos)
- **Resolución de cámara**: Detectada automáticamente
- **Modelos**: Carga automática desde la carpeta `models/`

### Dependencias Principales
```
opencv-python>=4.8    # Procesamiento de video e imágenes
Pillow>=9.5          # Manipulación de imágenes
reportlab==3.6.0     # Generación de reportes PDF
tensorflow>=2.12     # Deep learning y modelos de IA
numpy>=1.23          # Operaciones numéricas
```

## 🐛 Solución de Problemas

### Error de cámara
- Verificar que la cámara no esté siendo usada por otra aplicación
- Revisar permisos de acceso a la cámara en Windows
- Reiniciar la aplicación si es necesario

### Error de modelo
- Verificar que los archivos `.h5` estén en la carpeta `models/`
- Comprobar que TensorFlow se instaló correctamente
- Usar el botón "Recargar" para actualizar la lista de modelos

### Problemas de rendimiento
- Aumentar el intervalo de captura si el sistema es lento
- Cerrar otras aplicaciones que usen mucha CPU
- Considerar usar el modelo `resnet_rapido.h5` para mejor rendimiento

## 📈 Métricas del Sistema

La aplicación monitorea automáticamente:
- **FPS de cámara**: Frames por segundo del video
- **Tiempo de procesamiento**: Latencia de cada predicción
- **Precisión del modelo**: Confidence score promedio
- **Emociones detectadas**: Distribución y frecuencia

## 🤝 Soporte

Para problemas técnicos o mejoras:
1. Revisar la sección de solución de problemas
2. Verificar los logs de la aplicación
3. Comprobar la instalación de dependencias

## 📝 Notas de Versión

**Versión actual**: Aplicación estable con interfaz moderna
- ✅ Detección en tiempo real optimizada
- ✅ 3 modelos de IA especializados
- ✅ Interfaz de usuario mejorada
- ✅ Generación automática de reportes
- ✅ Proyecto limpio y optimizado

---

*Desarrollado con Python, TensorFlow y OpenCV para detección de emociones en tiempo real.*