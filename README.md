# 🎯 Detector de Emociones v2.0# 🎭 Detección de Emociones con Deep Learning



Una aplicación moderna y modular de detección de emociones en tiempo real usando Computer Vision y Deep Learning.Sistema avanzado de reconocimiento de emociones en tiempo real utilizando redes neuronales convolucionales (CNN) con arquitectura ResNet y mecanismos de atención CBAM.



## 🚀 Características Principales## 🌟 Características Principales



- **🎨 Interfaz Moderna**: Diseño clean y responsivo con componentes personalizados- **Detección en tiempo real** de emociones faciales usando modelos de deep learning

- **🔄 Arquitectura Modular**: Código organizado en módulos especializados- **Interfaz gráfica moderna** desarrollada con Tkinter

- **📹 Detección en Tiempo Real**: Análisis continuo usando cámara web- **Múltiples modelos de IA** disponibles para diferentes casos de uso

- **🤖 Múltiples Modelos**: Soporte para diferentes arquitecturas de IA- **Generación automática de reportes** en formato PDF

- **📊 Reportes Automáticos**: Generación de PDFs con estadísticas detalladas- **Métricas detalladas** de rendimiento y estadísticas

- **⏱️ Timer Configurable**: Control preciso de intervalos de captura- **Configuración flexible** de intervalos de captura

- **📈 Métricas Avanzadas**: Estadísticas en tiempo real y análisis de sesiones

## 🚀 Instalación y Configuración

## 🏗️ Arquitectura Modular

### Prerrequisitos

### Nueva Estructura del Proyecto- Python 3.8 o superior

```- Cámara web funcional

GUI-emotion/- Entorno virtual (recomendado)

├── 📄 app.py                    # Coordinador principal (simplificado)

├── 📄 app_original.py           # Respaldo del código original### Instalación

├── 📄 requirements.txt          # Dependencias Python

├── 📄 README.md                 # Documentación1. **Clonar o descargar el proyecto**

├── 📁 src/                      # Código fuente modular   ```bash

│   ├── 📄 __init__.py           # Inicialización del paquete   cd "C:\Users\tu_usuario\Documents\GUI emotion"

│   ├── 📄 config.py             # Configuraciones centralizadas   ```

│   ├── 📁 core/                 # Lógica de negocio

│   │   ├── 📄 __init__.py2. **Crear entorno virtual**

│   │   ├── 📄 camera.py         # Manejo de cámara y video   ```bash

│   │   ├── 📄 emotion_detector.py # Modelos de IA y predicción   python -m venv .venv

│   │   └── 📄 session_manager.py  # Sesiones y estadísticas   .venv\Scripts\activate

│   └── 📁 ui/                   # Interfaz de usuario   ```

│       ├── 📄 __init__.py

│       ├── 📄 components.py     # Widgets personalizados3. **Instalar dependencias**

│       └── 📄 interface.py      # Interfaz principal   ```bash

├── 📁 models/                   # Modelos de IA (.h5, .keras)   pip install -r requirements.txt

├── 📁 results/                  # Reportes PDF generados   ```

├── 📁 utils/                    # Utilidades (PDF, modelos)

│   ├── 📄 model_utils.py        # Funciones de modelo## 🎮 Uso de la Aplicación

│   └── 📄 pdf_report.py         # Generación de reportes

├── 📁 fer2013/                  # Dataset de entrenamiento### Ejecutar la aplicación

└── 📁 graficas/                 # Visualizaciones y gráficas```bash

```python app.py

```

### Módulos Principales

### Flujo de trabajo

#### 🔧 `src/config.py` - Configuración Centralizada1. **Seleccionar modelo**: Elige uno de los 3 modelos disponibles

- **AppConfig**: Configuración general de la aplicación2. **Iniciar cámara**: Presiona "Iniciar Cámara" para comenzar

- **Colors**: Paleta de colores del diseño3. **Detección automática**: El sistema detectará emociones según el intervalo configurado

- **Fonts**: Tipografías y tamaños4. **Ver resultados**: Revisa métricas en tiempo real y genera reportes

- **EmotionConfig**: Configuración de emociones y etiquetas

- **UIStyles**: Estilos de componentes UI## 🧪 Modelos Disponibles



#### 📹 `src/core/camera.py` - Gestión de CámaraEl sistema incluye 3 modelos entrenados específicamente conservados:

- **CameraManager**: Captura de video en threading

- **FrameProcessor**: Detección facial y procesamiento de imágenes- **`emotion_model.h5`**: Modelo base de detección de emociones

- **`prueba_nuevo_modelo_cnn.h5`**: CNN optimizada para precisión

#### 🤖 `src/core/emotion_detector.py` - Inteligencia Artificial- **`resnet_rapido.h5`**: Modelo ResNet optimizado para velocidad

- **EmotionModel**: Carga y manejo de modelos TensorFlow

- **ModelManager**: Gestión de múltiples modelos## 📊 Funcionalidades



#### 📊 `src/core/session_manager.py` - Sesiones y Estadísticas### Detección en Tiempo Real

- **SessionManager**: Control de sesiones de detección- Procesamiento de video en vivo (~30 FPS)

- **SessionStatistics**: Análisis y métricas avanzadas- Clasificación de múltiples emociones

- **EmotionDetection**: Representación de detecciones individuales- Confidence score para cada predicción

- Intervalos de captura configurables

#### 🎨 `src/ui/components.py` - Componentes UI

- **RoundedButton**: Botones modernos con esquinas redondeadas### Análisis y Reportes

- **ModernCard**: Tarjetas con sombra y bordes suaves- Historial completo de sesiones

- **StatusIndicator**: Indicadores de estado con colores- Estadísticas de emociones dominantes

- **ProgressBar**: Barras de progreso personalizadas- Métricas de rendimiento del sistema

- Exportación a PDF con gráficos

#### 🖥️ `src/ui/interface.py` - Interfaz Principal

- **EmotionDetectionInterface**: Ventana principal de la aplicación### Interfaz de Usuario

- Integración de todos los módulos- Diseño moderno e intuitivo

- Manejo de eventos y actualizaciones en tiempo real- Estados visuales dinámicos

- Controles accesibles

## 📋 Requisitos del Sistema- Feedback en tiempo real



- **Python**: 3.7+ (recomendado 3.8+)## 📁 Estructura del Proyecto

- **Sistema Operativo**: Windows 10+, macOS 10.14+, Linux Ubuntu 18.04+

- **Hardware**: Cámara web, 4GB RAM mínimo```

- **Dependencias**: Ver `requirements.txt`GUI emotion/

├── app.py                 # Aplicación principal

## 🛠️ Instalación y Configuración├── requirements.txt       # Dependencias del proyecto

├── README.md             # Esta documentación

### 1. Clonar el Repositorio├── models/               # Modelos de IA entrenados

```bash│   ├── emotion_model.h5

git clone https://github.com/alanportilla18/Detecci-n-de-emociones.git│   ├── prueba_nuevo_modelo_cnn.h5

cd Detecci-n-de-emociones│   └── resnet_rapido.h5

```├── utils/                # Utilidades del proyecto

│   ├── model_utils.py    # Funciones de carga y procesamiento de modelos

### 2. Configurar Entorno Virtual│   └── pdf_report.py     # Generación de reportes PDF

```bash├── fer2013/              # Dataset de prueba

# Crear entorno virtual│   ├── test/            # Imágenes de prueba por emoción

python -m venv .venv│   └── train/           # Datos de entrenamiento

└── results/             # Reportes generados automáticamente

# Activar entorno virtual```

# Windows PowerShell:

.venv\Scripts\Activate.ps1## 🔧 Configuración Avanzada

# Windows CMD:

.venv\Scripts\activate.bat### Variables de Entorno

# Linux/macOS:La aplicación se configura automáticamente, pero puedes personalizar:

source .venv/bin/activate

```- **Intervalo de captura**: Ajustable desde la interfaz (0.1 - 10 segundos)

- **Resolución de cámara**: Detectada automáticamente

### 3. Instalar Dependencias- **Modelos**: Carga automática desde la carpeta `models/`

```bash

pip install -r requirements.txt### Dependencias Principales

``````

opencv-python>=4.8    # Procesamiento de video e imágenes

### 4. Verificar InstalaciónPillow>=9.5          # Manipulación de imágenes

```bashreportlab==3.6.0     # Generación de reportes PDF

python app.pytensorflow>=2.12     # Deep learning y modelos de IA

```numpy>=1.23          # Operaciones numéricas

```

## 🎮 Guía de Uso

## 🐛 Solución de Problemas

### Inicio Rápido

1. **Ejecutar**: `python app.py`### Error de cámara

2. **Seleccionar Modelo**: Elegir de la lista desplegable- Verificar que la cámara no esté siendo usada por otra aplicación

3. **Configurar**: Ajustar intervalo y umbral de confianza- Revisar permisos de acceso a la cámara en Windows

4. **Iniciar**: Presionar "Iniciar Cámara"- Reiniciar la aplicación si es necesario

5. **Monitorear**: Ver métricas en tiempo real

6. **Detener**: Presionar "Detener Cámara" para generar reporte### Error de modelo

- Verificar que los archivos `.h5` estén en la carpeta `models/`

### Configuraciones Avanzadas- Comprobar que TensorFlow se instaló correctamente

- Usar el botón "Recargar" para actualizar la lista de modelos

#### Intervalos de Captura

- **Rango**: 0.1 - 60.0 segundos### Problemas de rendimiento

- **Recomendado**: 2.0 - 5.0 segundos para balance entre precisión y performance- Aumentar el intervalo de captura si el sistema es lento

- Cerrar otras aplicaciones que usen mucha CPU

#### Umbral de Confianza- Considerar usar el modelo `resnet_rapido.h5` para mejor rendimiento

- **Rango**: 0.0 - 1.0

- **Recomendado**: 0.5 - 0.7 para filtrar detecciones de baja calidad## 📈 Métricas del Sistema



#### Modelos SoportadosLa aplicación monitorea automáticamente:

- **FER2013 (5 clases)**: Enojado, Asco, Feliz, Miedo, Triste- **FPS de cámara**: Frames por segundo del video

- **Extendido (6 clases)**: + Neutral- **Tiempo de procesamiento**: Latencia de cada predicción

- **Completo (7 clases)**: + Sorpresa- **Precisión del modelo**: Confidence score promedio

- **Avanzado (8 clases)**: + Otro- **Emociones detectadas**: Distribución y frecuencia



## 📊 Funcionalidades Avanzadas## 🤝 Soporte



### Análisis de SesionesPara problemas técnicos o mejoras:

- **Detecciones Totales**: Contador en tiempo real1. Revisar la sección de solución de problemas

- **Duración**: Cronómetro de sesión2. Verificar los logs de la aplicación

- **Emoción Dominante**: Más frecuente en la sesión3. Comprobar la instalación de dependencias

- **Distribución**: Porcentajes por emoción

- **Confianza Promedio**: Calidad de las detecciones## 📝 Notas de Versión

- **Tasa de Detección**: Detecciones por minuto

**Versión actual**: Aplicación estable con interfaz moderna

### Reportes PDF- ✅ Detección en tiempo real optimizada

Los reportes incluyen:- ✅ 3 modelos de IA especializados

- 📈 **Gráficas de distribución** de emociones- ✅ Interfaz de usuario mejorada

- ⏰ **Línea de tiempo** de la sesión- ✅ Generación automática de reportes

- 📋 **Estadísticas detalladas** y métricas- ✅ Proyecto limpio y optimizado

- 🔍 **Análisis de calidad** de detecciones

- 📅 **Metadatos** de sesión (fecha, duración, configuración)---



### Temporizador Visual*Desarrollado con Python, TensorFlow y OpenCV para detección de emociones en tiempo real.*
- **Countdown**: Cuenta regresiva visual
- **Estados de Color**: Verde → Naranja → Rojo según proximidad
- **Indicadores**: Estado textual del timer
- **Sincronización**: Perfecta con intervalos configurados

## 🔧 Configuración Técnica

### Variables de Entorno (config.py)
```python
# Configuración de cámara
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Configuración de detección
DEFAULT_CAPTURE_INTERVAL = 5.0
DEFAULT_CONFIDENCE_THRESHOLD = 0.5

# Configuración de interfaz
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
```

### Personalización de Colores
```python
class Colors:
    PRIMARY = "#16a04d"      # Verde principal
    SECONDARY = "#ecf0f1"    # Gris claro  
    ACCENT = "#3498db"       # Azul
    SUCCESS = "#27ae60"      # Verde éxito
    WARNING = "#f39c12"      # Naranja
    DANGER = "#e74c3c"       # Rojo
```

## 🐛 Solución de Problemas

### Errores Comunes

#### 1. Error de Importación de Módulos
```bash
Error importando módulos: No module named 'src'
```
**Solución**: Verificar que esté ejecutando desde el directorio raíz del proyecto.

#### 2. Error de Cámara
```bash
[CAMERA ERROR] No se pudo abrir la cámara
```
**Solución**: 
- Verificar que la cámara no esté siendo usada por otra aplicación
- Probar cambiar el índice de cámara en configuración
- Verificar permisos de cámara del sistema

#### 3. Error de Modelo
```bash
[MODEL ERROR] Error cargando modelo
```
**Solución**:
- Verificar que el archivo `.h5` esté completo y no corrupto
- Verificar compatibilidad con versión de TensorFlow
- Verificar permisos de lectura del archivo

#### 4. Error de PDF
```bash
[SESSION ERROR] Error guardando reporte
```
**Solución**:
- Verificar permisos de escritura en carpeta `results/`
- Verificar espacio disponible en disco
- Verificar instalación de ReportLab

### Logs y Debugging
Los mensajes de debug incluyen prefijos para fácil identificación:
- `[CAMERA]`: Eventos de cámara
- `[MODEL]`: Carga y predicciones de modelo  
- `[SESSION]`: Manejo de sesiones
- `[TIMER]`: Eventos del temporizador
- `[UI]`: Eventos de interfaz
- `[APP]`: Estados generales de la aplicación

## 🚀 Desarrollo y Extensión

### Agregar Nuevos Modelos
1. Colocar archivo `.h5` o `.keras` en carpeta `models/`
2. El sistema detectará automáticamente el número de clases
3. Configurar etiquetas en `EmotionConfig` si es necesario

### Crear Nuevos Componentes UI
```python
# En src/ui/components.py
class CustomWidget(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        # Implementación del widget
```

### Extender Funcionalidad Core
```python
# En src/core/
class NewModule:
    def __init__(self):
        # Inicialización
        pass
```

### Modificar Configuraciones
Editar `src/config.py` para cambiar:
- Colores y temas
- Configuraciones por defecto
- Textos de interfaz
- Límites y validaciones

## 📈 Performance y Optimización

### Recomendaciones
- **FPS objetivo**: 30 FPS para video fluido
- **Intervalo de captura**: ≥2s para evitar sobrecarga
- **Resolución**: 640x480 balance óptimo calidad/performance
- **Umbral confianza**: ≥0.5 para filtrar falsos positivos

### Monitoreo
La aplicación incluye métricas de performance:
- FPS real de cámara
- Tiempo de carga de modelo
- Tasa de éxito de predicciones
- Uso de memoria (historial limitado)

## 📄 Licencia

Este proyecto está licenciado bajo MIT License.

## 👥 Contribución

### Cómo Contribuir
1. Fork del repositorio
2. Crear branch para nueva funcionalidad
3. Desarrollar siguiendo la arquitectura modular
4. Agregar tests si es necesario
5. Crear Pull Request

### Estándares de Código
- **Documentación**: Docstrings en español para todas las funciones
- **Tipado**: Type hints donde sea apropiado
- **Estilo**: Seguir convenciones PEP 8
- **Modularidad**: Mantener separación de responsabilidades

## 📞 Soporte

### Reportar Issues
Crear issue en GitHub incluyendo:
- Descripción del problema
- Pasos para reproducir
- Logs relevantes
- Información del sistema

### Contacto
- **GitHub**: [alanportilla18](https://github.com/alanportilla18)
- **Proyecto**: [Detecci-n-de-emociones](https://github.com/alanportilla18/Detecci-n-de-emociones)

---

**🎯 Detector de Emociones v2.0** - Una aplicación moderna, modular y escalable para detección de emociones en tiempo real.