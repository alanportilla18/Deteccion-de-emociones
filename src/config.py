#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 CONFIGURACIÓN DEL DETECTOR DE EMOCIONES
Configuración centralizada para la aplicación de detección de emociones
"""

import os
from pathlib import Path

# 🔧 CONFIGURACIÓN DE LA APLICACIÓN
class AppConfig:
    # Información de la aplicación
    APP_NAME = "Detector de Emociones"
    APP_VERSION = "2.0.0"
    APP_DESCRIPTION = "Aplicación GUI moderna para detección de emociones en tiempo real"
    
    # Configuración de ventana
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    WINDOW_MIN_WIDTH = 1200
    WINDOW_MIN_HEIGHT = 700
    
    # Configuración de cámara
    CAMERA_DEFAULT_INDEX = 0
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    
    # Configuración de detección
    DEFAULT_CAPTURE_INTERVAL = 5.0  # segundos
    MIN_CAPTURE_INTERVAL = 0.1
    MAX_CAPTURE_INTERVAL = 60.0
    DEFAULT_CONFIDENCE_THRESHOLD = 0.5
    
    # Configuración de modelo
    MODELS_DIR = "models"
    DEFAULT_MODEL = "emotion_model.h5"
    
    # Configuración de archivos
    RESULTS_DIR = "results"
    LOGS_DIR = "logs"
    
    @classmethod
    def get_models_dir(cls):
        return Path(__file__).parent / cls.MODELS_DIR
    
    @classmethod
    def get_results_dir(cls):
        return Path(__file__).parent / cls.RESULTS_DIR
    
    @classmethod
    def get_logs_dir(cls):
        return Path(__file__).parent / cls.LOGS_DIR

# 🎨 CONFIGURACIÓN DE DISEÑO
class Colors:
    # Colores principales
    PRIMARY = "#16a04d"  # Verde principal
    PRIMARY_DARK = "#0c783f"
    PRIMARY_LIGHT = "#27ae60"
    
    # Colores secundarios
    SECONDARY = "#ecf0f1"  # Gris claro
    ACCENT = "#3498db"  # Azul
    ACCENT_DARK = "#2980b9"
    
    # Estados
    SUCCESS = "#27ae60"  # Verde éxito
    WARNING = "#f39c12"  # Naranja
    DANGER = "#e74c3c"  # Rojo
    INFO = "#3498db"  # Azul información
    
    # Texto
    TEXT_DARK = "#2c3e50"
    TEXT_LIGHT = "#7f8c8d"
    TEXT_MUTED = "#95a5a6"
    
    # Fondos
    WHITE = "#ffffff"
    CARD_BG = "#f8f9fa"
    BACKGROUND = "#ecf0f1"
    SHADOW = "#bdc3c7"
    
    # Gradientes y efectos
    GRADIENT_START = PRIMARY
    GRADIENT_END = PRIMARY_DARK

class Fonts:
    # Fuentes principales
    FAMILY = "Segoe UI"
    TITLE = (FAMILY, 14, "bold")
    HEADER = (FAMILY, 12, "bold")
    BODY = (FAMILY, 10, "normal")
    CAPTION = (FAMILY, 9, "normal")
    BUTTON = (FAMILY, 10, "bold")
    
    # Tamaños especiales
    LARGE = 16
    MEDIUM = 12
    SMALL = 10
    TINY = 8

class Spacing:
    # Espaciado estándar
    TINY = 4
    SMALL = 8
    MEDIUM = 16
    LARGE = 24
    XLARGE = 32
    
    # Padding y márgenes
    PADDING = MEDIUM
    MARGIN = MEDIUM
    
    # Radios de bordes
    BORDER_RADIUS = 20
    CARD_RADIUS = 25
    BUTTON_RADIUS = 20

# 🚀 CONFIGURACIÓN DE PERFORMANCE
class PerformanceConfig:
    # Intervalos de actualización (en milisegundos)
    UI_UPDATE_INTERVAL = 33  # ~30 FPS
    TIMER_UPDATE_INTERVAL = 100  # 10 Hz
    STATS_UPDATE_INTERVAL = 500  # 2 Hz
    
    # Límites de memoria
    MAX_EMOTION_HISTORY = 1000
    MAX_SESSION_DURATION = 3600  # 1 hora en segundos
    
    # Configuración de threading
    MAX_WORKER_THREADS = 2

# 🔒 CONFIGURACIÓN DE SEGURIDAD
class SecurityConfig:
    # Validaciones
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_MODEL_EXTENSIONS = ['.h5', '.keras', '.pb']
    ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp']
    
    # Paths seguros
    SAFE_CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."

# 📊 CONFIGURACIÓN DE EMOCIONES
class EmotionConfig:
    # Etiquetas estándar FER2013
    EMOTION_LABELS_5 = ['Enojado', 'Asco', 'Feliz', 'Miedo', 'Triste']
    EMOTION_LABELS_6 = ['Enojado', 'Asco', 'Feliz', 'Miedo', 'Triste', 'Neutral']
    EMOTION_LABELS_7 = ['Enojado', 'Asco', 'Feliz', 'Miedo', 'Triste', 'Neutral', 'Sorpresa']
    EMOTION_LABELS_8 = ['Enojado', 'Asco', 'Feliz', 'Miedo', 'Triste', 'Neutral', 'Sorpresa', 'Otro']
    
    # Colores para las emociones
    EMOTION_COLORS = {
        'Enojado': '#e74c3c',
        'Asco': '#8e44ad',
        'Feliz': '#f1c40f',
        'Miedo': '#9b59b6',
        'Triste': '#3498db',
        'Neutral': '#95a5a6',
        'Sorpresa': '#e67e22',
        'Otro': '#34495e'
    }
    
    @classmethod
    def get_labels_for_classes(cls, num_classes: int):
        """Obtener etiquetas según el número de clases"""
        if num_classes == 5:
            return cls.EMOTION_LABELS_5
        elif num_classes == 6:
            return cls.EMOTION_LABELS_6
        elif num_classes == 7:
            return cls.EMOTION_LABELS_7
        elif num_classes == 8:
            return cls.EMOTION_LABELS_8
        else:
            return [f"Clase_{i}" for i in range(num_classes)]

# 🎯 CONFIGURACIÓN DE ESTILOS UI
class UIStyles:
    # Estilos de botones
    BUTTON_STYLES = {
        'primary': {
            'bg': Colors.PRIMARY,
            'hover': Colors.PRIMARY_DARK,
            'text': Colors.WHITE
        },
        'secondary': {
            'bg': Colors.SECONDARY,
            'hover': Colors.TEXT_LIGHT,
            'text': Colors.TEXT_DARK
        },
        'success': {
            'bg': Colors.SUCCESS,
            'hover': Colors.PRIMARY_DARK,
            'text': Colors.WHITE
        },
        'danger': {
            'bg': Colors.DANGER,
            'hover': '#c0392b',
            'text': Colors.WHITE
        },
        'warning': {
            'bg': Colors.WARNING,
            'hover': '#d68910',
            'text': Colors.WHITE
        }
    }
    
    # Estilos de tarjetas
    CARD_STYLES = {
        'default': {
            'bg': Colors.CARD_BG,
            'border': Colors.SHADOW,
            'shadow': True
        },
        'accent': {
            'bg': Colors.WHITE,
            'border': Colors.ACCENT,
            'shadow': True
        }
    }

# 🌐 CONFIGURACIÓN DE INTERNACIONALIZACIÓN
class i18n:
    # Textos de la interfaz
    TEXTS = {
        'app_title': 'Detector de Emociones',
        'start_camera': 'Iniciar Cámara',
        'stop_camera': 'Detener Cámara',
        'view_results': 'Ver Resultados',
        'model_status': 'Estado del Modelo',
        'session_metrics': 'Métricas de Sesión',
        'timer_panel': 'Temporizador de Captura',
        'settings': 'Configuración',
        'detection_count': 'Detecciones',
        'session_duration': 'Duración',
        'next_capture': 'Próxima Captura',
        'capture_interval': 'Intervalo (s)',
        'confidence_threshold': 'Umbral de Confianza',
        'select_model': 'Seleccionar Modelo',
        'no_camera': 'Cámara no detectada',
        'camera_active': 'Cámara activa',
        'model_loaded': 'Modelo cargado',
        'model_error': 'Error en modelo',
        'session_started': 'Sesión iniciada',
        'session_stopped': 'Sesión detenida',
        'timer_active': 'Temporizador activo',
        'timer_inactive': 'Temporizador inactivo'
    }