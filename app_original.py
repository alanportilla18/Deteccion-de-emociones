#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 DETECTOR DE EMOCIONES - INTERFAZ MODERNA
Aplicación GUI con diseño basado en Figma para detección de emociones en tiempo real
"""

import os
import sys
import time
import threading
from datetime import datetime
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import tkinter.font as tkfont

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

from utils.model_utils import (
    list_models,
    load_emotion_model,
    prepare_frame_for_model,
    predict_emotion,
    get_label_set_for_classes,
)
from utils.pdf_report import save_session_report

# 🎨 CONFIGURACIÓN DE DISEÑO
class Colors:
    PRIMARY = "#16a04d"  # Verde principal
    PRIMARY_DARK = "#0c783f"
    SECONDARY = "#ecf0f1"  # Gris claro
    ACCENT = "#3498db"  # Azul
    SUCCESS = "#27ae60"  # Verde éxito
    WARNING = "#f39c12"  # Naranja
    DANGER = "#e74c3c"  # Rojo
    TEXT_DARK = "#2c3e50"
    TEXT_LIGHT = "#7f8c8d"
    WHITE = "#ffffff"
    CARD_BG = "#f8f9fa"
    SHADOW = "#bdc3c7"  # Para efectos de sombra sutiles

class Fonts:
    TITLE = ("Segoe UI", 14, "bold")
    SUBTITLE = ("Segoe UI", 12, "bold")
    BODY = ("Segoe UI", 10)
    SMALL = ("Segoe UI", 9)
    LARGE = ("Segoe UI", 16, "bold")

APP_TITLE = "Detector de Emociones"
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
GRAPHICS_DIR = os.path.join(os.path.dirname(__file__), "graficas")

class RoundedButton(tk.Canvas):
    """Botón personalizado con bordes redondeados y estilo moderno."""
    def __init__(self, parent, text='', command=None, style='primary', font=Fonts.BODY, padx=16, pady=10, radius=20, **kwargs):
        # Configurar colores según el estilo
        if style == 'primary':
            bg_color = Colors.PRIMARY
            fg_color = Colors.WHITE
            active_bg = Colors.PRIMARY_DARK
        elif style == 'secondary':
            bg_color = Colors.SECONDARY
            fg_color = Colors.TEXT_DARK
            active_bg = "#d5dbdb"
        elif style == 'success':
            bg_color = Colors.SUCCESS
            fg_color = Colors.WHITE
            active_bg = "#229954"
        elif style == 'danger':
            bg_color = Colors.DANGER
            fg_color = Colors.WHITE
            active_bg = "#cb4335"
        else:
            bg_color = Colors.PRIMARY
            fg_color = Colors.WHITE
            active_bg = Colors.PRIMARY_DARK

        # Medir tamaño del texto para auto-ajuste
        font_obj = tkfont.Font(font=font)
        text_width = font_obj.measure(text)
        text_height = font_obj.metrics("linespace")
        width = text_width + 2 * padx
        height = text_height + 2 * pady

        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent['bg'],
            highlightthickness=0,
            bd=0,
            relief='flat',
            cursor='hand2',
            **kwargs
        )

        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.active_bg = active_bg
        self.radius = radius
        self.font = font
        self.padx = padx
        self.pady = pady

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Configure>", self._on_resize)

        self._draw_button(self.bg_color)

    def _draw_button(self, fill):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        r = min(self.radius, width / 2, height / 2)

        # Dibujar rectángulo redondeado
        self.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=fill, outline=fill)
        self.create_arc(0, height-2*r, 2*r, height, start=180, extent=90, fill=fill, outline=fill)
        self.create_arc(width-2*r, height-2*r, width, height, start=270, extent=90, fill=fill, outline=fill)
        self.create_arc(width-2*r, 0, width, 2*r, start=0, extent=90, fill=fill, outline=fill)
        self.create_rectangle(r, 0, width-r, height, fill=fill, outline=fill)
        self.create_rectangle(0, r, width, height-r, fill=fill, outline=fill)

        # Texto centrado
        self.create_text(width/2, height/2, text=self.text, font=self.font, fill=self.fg_color)

    def _on_enter(self, event):
        self._draw_button(self.active_bg)

    def _on_leave(self, event):
        self._draw_button(self.bg_color)

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_resize(self, event):
        self._draw_button(self.bg_color)

class ModernCard(tk.Canvas):
    """Tarjeta personalizada con estilo moderno y bordes redondeados."""
    def __init__(self, parent, title=None, radius=25, **kwargs):
        # Configuración base
        bg_color = Colors.WHITE
        width = kwargs.pop('width', 300)  # Ajusta según necesites
        height = kwargs.pop('height', 400)  # Ajusta según necesites
        super().__init__(
            parent,
            bg=parent['bg'],
            highlightthickness=0,
            bd=0,
            relief='flat',
            width=width,
            height=height,
            **kwargs
        )
        
        self.radius = radius  # Esta es la variable que controla el redondeo (cámbiala aquí o al instanciar)
        self.bg_color = bg_color
        self.title = title
        
        self.bind("<Configure>", self._on_resize)
        self._draw_card()
        
        # Contenedor interno para widgets (para que puedas agregar labels, etc., dentro)
        self.inner_frame = tk.Frame(self, bg=bg_color)
        self.create_window(0, 0, anchor=tk.NW, window=self.inner_frame, tags="inner")
        
        if title:
            header = tk.Frame(self.inner_frame, bg=Colors.CARD_BG, height=40)
            header.pack(fill=tk.X)
            header.pack_propagate(False)
            title_label = tk.Label(
                header, 
                text=title, 
                font=Fonts.SUBTITLE,
                bg=Colors.CARD_BG,
                fg=Colors.TEXT_DARK
            )
            title_label.pack(side=tk.LEFT, padx=12, pady=8)

    def _draw_card(self):
        self.delete("card")
        width = self.winfo_width()
        height = self.winfo_height()
        r = min(self.radius, width / 2, height / 2)
        
        # Dibujar rectángulo redondeado
        self.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=self.bg_color, outline=self.bg_color, tags="card")
        self.create_arc(0, height-2*r, 2*r, height, start=180, extent=90, fill=self.bg_color, outline=self.bg_color, tags="card")
        self.create_arc(width-2*r, height-2*r, width, height, start=270, extent=90, fill=self.bg_color, outline=self.bg_color, tags="card")
        self.create_arc(width-2*r, 0, width, 2*r, start=0, extent=90, fill=self.bg_color, outline=self.bg_color, tags="card")
        self.create_rectangle(r, 0, width-r, height, fill=self.bg_color, outline=self.bg_color, tags="card")
        self.create_rectangle(0, r, width, height-r, fill=self.bg_color, outline=self.bg_color, tags="card")
        
        # Ajustar posición del inner_frame
        self.coords("inner", self.radius, self.radius)  # Para centrar contenido con padding

    def _on_resize(self, event):
        self._draw_card()

class StatusIndicator(tk.Frame):
    """Indicador de estado con colores."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.dot = tk.Label(
            self, 
            text="●", 
            font=("Segoe UI", 12),
            bg=self['bg']
        )
        self.dot.pack(side=tk.LEFT, padx=(0, 5))
        
        self.label = tk.Label(
            self,
            font=Fonts.SMALL,
            bg=self['bg']
        )
        self.label.pack(side=tk.LEFT)
    
    def set_status(self, text, status='neutral'):
        colors = {
            'success': Colors.SUCCESS,
            'warning': Colors.WARNING,
            'danger': Colors.DANGER,
            'info': Colors.ACCENT,
            'neutral': Colors.TEXT_LIGHT
        }
        
        self.dot.config(fg=colors.get(status, Colors.TEXT_LIGHT))
        self.label.config(text=text, fg=Colors.TEXT_DARK)

class EmotionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1400x900")
        self.configure(bg=Colors.SECONDARY)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Configurar estilo
        self.setup_styles()
        
        # Estado de la aplicación
        self.cap = None
        self.running = False
        self.preview_after_id = None
        self.last_preview_time = None
        self.fps = 0.0
        self.last_detect_time = 0.0
        
        # Variables de UI
        self.capture_interval_sec = tk.DoubleVar(value=2.0)
        self.selected_model_path = tk.StringVar(value="")
        self.selected_model_name = tk.StringVar(value="")
        self.last_emotion = tk.StringVar(value="-")
        self.last_emotion_time = tk.StringVar(value="-")
        self.status_text = tk.StringVar(value="Listo")
        
        # Variables del temporizador
        self.next_capture_timer = tk.StringVar(value="-")
        self.timer_after_id = None
        self.timer_enabled = False
        self.timer_start_time = 0.0  # Para el temporizador independiente
        
        # Estado del modelo
        self.model = None
        self.model_input_shape = None
        self.model_num_classes = None
        self.model_labels = None
        
        # Sesión
        self.session_records = []
        self.session_start_time = None
        
        # Construir interfaz
        self._build_ui()
        self._load_models_into_combobox()
    
    def setup_styles(self):
        """Configurar estilos de ttk."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar estilos personalizados
        style.configure(
            "Modern.TCombobox",
            fieldbackground=Colors.WHITE,
            background=Colors.WHITE,
            borderwidth=1,
            focuscolor='none',
            arrowsize=15
        )
        
        style.configure(
            "Modern.TSpinbox",
            fieldbackground=Colors.WHITE,
            background=Colors.WHITE,
            borderwidth=1,
            arrowsize=15
        )
    
    def _build_ui(self):
        """Construir toda la interfaz de usuario."""
        self._build_header()
        self._build_main_content()
        self._build_control_panel()
        self._build_status_bar()
    
    def _build_header(self):
        """Construir header superior con selección de modelo."""
        header = tk.Frame(self, bg=Colors.PRIMARY, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Contenedor interno
        header_content = tk.Frame(header, bg=Colors.PRIMARY)
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Título y logo
        title_frame = tk.Frame(header_content, bg=Colors.PRIMARY)
        title_frame.pack(side=tk.LEFT)
        
        # Icono/Logo
        logo_frame = tk.Frame(title_frame, bg=Colors.WHITE, width=30, height=30)
        logo_frame.pack(side=tk.LEFT, padx=(0, 10))
        logo_frame.pack_propagate(False)
        
        logo_label = tk.Label(
            logo_frame, 
            text="🧠", 
            font=("Segoe UI", 14),
            bg=Colors.WHITE
        )
        logo_label.pack(expand=True)
        
        # Título
        title_label = tk.Label(
            title_frame,
            text=APP_TITLE,
            font=Fonts.LARGE,
            bg=Colors.PRIMARY,
            fg=Colors.WHITE
        )
        title_label.pack(side=tk.LEFT, pady=5)
        
        # Selector de modelo
        model_frame = tk.Frame(header_content, bg=Colors.PRIMARY)
        model_frame.pack(side=tk.RIGHT)
        
        tk.Label(
            model_frame,
            text="Modelo:",
            font=Fonts.BODY,
            bg=Colors.PRIMARY,
            fg=Colors.WHITE
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.model_combo = ttk.Combobox(
            model_frame,
            state="readonly",
            width=35,
            style="Modern.TCombobox",
            font=Fonts.BODY
        )
        self.model_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_selected)
        
        RoundedButton(
            model_frame,
            text="🔄 Recargar",
            style='secondary',
            command=self._load_models_into_combobox
        ).pack(side=tk.LEFT)
    
    def _build_main_content(self):
        """Construir contenido principal con video e información."""
        main_frame = tk.Frame(self, bg=Colors.SECONDARY)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Panel de video (izquierda)
        video_card = ModernCard(main_frame, title="📹 Vista de Cámara")
        video_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Contenedor del video
        self.video_container = tk.Frame(video_card, bg=Colors.TEXT_DARK, width=640, height=480)
        self.video_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(8, 15))
        self.video_container.pack_propagate(False)
        
        # Label del video
        self.video_label = tk.Label(
            self.video_container,
            bg=Colors.TEXT_DARK,
            fg=Colors.WHITE,
            text="📷\n\nCámara desconectada\n\nPresiona 'Iniciar Cámara' para comenzar",
            font=Fonts.SUBTITLE,
            justify=tk.CENTER
        )
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Panel de información (derecha)
        info_card = ModernCard(main_frame, title="ℹ️ Información del Sistema")
        info_card.pack(side=tk.RIGHT, fill=tk.Y, ipadx=20)
        
        # Contenido de información
        info_content = tk.Frame(info_card, bg=Colors.WHITE)
        info_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=(8, 10))
        
        # Estado del modelo
        self._build_model_status(info_content)
        
        # Métricas en tiempo real
        self._build_metrics_panel(info_content)
        
        # Panel de temporizador
        self._build_timer_panel(info_content)
        
        # Configuración
        self._build_settings_panel(info_content)
    
    def _build_model_status(self, parent):
        """Panel de estado del modelo."""
        status_frame = tk.LabelFrame(
            parent,
            text="Estado del Modelo",
            font=Fonts.SUBTITLE,
            bg=Colors.WHITE,
            fg=Colors.TEXT_DARK,
            pady=5
        )
        status_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Indicador de estado
        self.model_status = StatusIndicator(status_frame, bg=Colors.WHITE)
        self.model_status.pack(fill=tk.X, padx=10, pady=5)
        self.model_status.set_status("Modelo no cargado", 'warning')
        
        # Nombre del modelo actual
        model_info = tk.Frame(status_frame, bg=Colors.WHITE)
        model_info.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            model_info,
            text="Modelo actual:",
            font=Fonts.SMALL,
            bg=Colors.WHITE,
            fg=Colors.TEXT_LIGHT
        ).pack(anchor=tk.W)
        
        self.current_model_label = tk.Label(
            model_info,
            textvariable=self.selected_model_name,
            font=Fonts.BODY,
            bg=Colors.WHITE,
            fg=Colors.TEXT_DARK,
            wraplength=200
        )
        self.current_model_label.pack(anchor=tk.W, pady=(2, 0))
    
    def _build_metrics_panel(self, parent):
        """Panel de métricas en tiempo real."""
        metrics_frame = tk.LabelFrame(
            parent,
            text="Métricas en Tiempo Real",
            font=Fonts.SUBTITLE,
            bg=Colors.WHITE,
            fg=Colors.TEXT_DARK,
            pady=5
        )
        metrics_frame.pack(fill=tk.X, pady=(0, 8))
        
        # FPS
        fps_frame = tk.Frame(metrics_frame, bg=Colors.WHITE)
        fps_frame.pack(fill=tk.X, padx=10, pady=2)
        
        tk.Label(
            fps_frame,
            text="FPS:",
            font=Fonts.SMALL,
            bg=Colors.WHITE,
            fg=Colors.TEXT_LIGHT
        ).pack(side=tk.LEFT)
        
        self.fps_label = tk.Label(
            fps_frame,
            text="0.0",
            font=Fonts.BODY,
            bg=Colors.WHITE,
            fg=Colors.TEXT_DARK
        )
        self.fps_label.pack(side=tk.RIGHT)
        
        # Última emoción
        emotion_frame = tk.Frame(metrics_frame, bg=Colors.WHITE)
        emotion_frame.pack(fill=tk.X, padx=10, pady=2)
        
        tk.Label(
            emotion_frame,
            text="Última emoción:",
            font=Fonts.SMALL,
            bg=Colors.WHITE,
            fg=Colors.TEXT_LIGHT
        ).pack(anchor=tk.W)
        
        self.emotion_label = tk.Label(
            emotion_frame,
            textvariable=self.last_emotion,
            font=Fonts.BODY,
            bg=Colors.WHITE,
            fg=Colors.ACCENT,
            wraplength=180
        )
        self.emotion_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Hora de detección
        time_frame = tk.Frame(metrics_frame, bg=Colors.WHITE)
        time_frame.pack(fill=tk.X, padx=10, pady=2)
        
        tk.Label(
            time_frame,
            text="Última detección:",
            font=Fonts.SMALL,
            bg=Colors.WHITE,
            fg=Colors.TEXT_LIGHT
        ).pack(anchor=tk.W)
        
        tk.Label(
            time_frame,
            textvariable=self.last_emotion_time,
            font=Fonts.SMALL,
            bg=Colors.WHITE,
            fg=Colors.TEXT_DARK,
            wraplength=180
        ).pack(anchor=tk.W, pady=(2, 0))
    
    def _build_timer_panel(self, parent):
        """Panel dedicado al temporizador de captura."""
        timer_frame = tk.LabelFrame(
            parent,
            text="⏰ Temporizador de Captura",
            font=Fonts.SUBTITLE,
            bg=Colors.WHITE,
            fg=Colors.TEXT_DARK,
            pady=8
        )
        timer_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Contenedor principal del temporizador
        timer_container = tk.Frame(timer_frame, bg=Colors.WHITE)
        timer_container.pack(fill=tk.X, padx=10, pady=5)
        
        # Layout horizontal para optimizar espacio
        timer_top = tk.Frame(timer_container, bg=Colors.WHITE)
        timer_top.pack(fill=tk.X, pady=(0, 3))
        
        # Título y display en la misma línea
        tk.Label(
            timer_top,
            text="Próxima captura:",
            font=Fonts.SMALL,
            bg=Colors.WHITE,
            fg=Colors.TEXT_LIGHT
        ).pack(side=tk.LEFT)
        
        # Display del temporizador más compacto
        self.timer_display_frame = tk.Frame(timer_top, bg=Colors.CARD_BG, relief="solid", bd=1)
        self.timer_display_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.timer_label = tk.Label(
            self.timer_display_frame,
            textvariable=self.next_capture_timer,
            font=("Segoe UI", 12, "bold"),
            bg=Colors.CARD_BG,
            fg=Colors.ACCENT,
            padx=8,
            pady=4
        )
        self.timer_label.pack()
        
        # Estado en línea separada pero compacta
        self.timer_status = tk.Label(
            timer_container,
            text="Esperando inicio...",
            font=Fonts.SMALL,
            bg=Colors.WHITE,
            fg=Colors.TEXT_DARK
        )
        self.timer_status.pack(anchor=tk.W, pady=(2, 0))
    
    def _build_settings_panel(self, parent):
        """Panel de configuración."""
        settings_frame = tk.LabelFrame(
            parent,
            text="Configuración",
            font=Fonts.SUBTITLE,
            bg=Colors.WHITE,
            fg=Colors.TEXT_DARK,
            pady=5
        )
        settings_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Intervalo de captura
        interval_frame = tk.Frame(settings_frame, bg=Colors.WHITE)
        interval_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            interval_frame,
            text="Intervalo de captura (s):",
            font=Fonts.SMALL,
            bg=Colors.WHITE,
            fg=Colors.TEXT_LIGHT
        ).pack(anchor=tk.W)
        
        self.interval_spinbox = ttk.Spinbox(
            interval_frame,
            from_=0.2,
            to=10.0,
            increment=0.2,
            textvariable=self.capture_interval_sec,
            width=15,
            style="Modern.TSpinbox",
            font=Fonts.BODY
        )
        self.interval_spinbox.pack(anchor=tk.W, pady=(5, 0))
    
    def _build_control_panel(self):
        """Panel de control con botones."""
        control_frame = tk.Frame(self, bg=Colors.SECONDARY, height=70)
        control_frame.pack(fill=tk.X, padx=15, pady=(0, 8))
        control_frame.pack_propagate(False)
        
        # Botones principales
        button_frame = tk.Frame(control_frame, bg=Colors.SECONDARY)
        button_frame.pack(expand=True, pady=10)
        
        self.start_btn = RoundedButton(
            button_frame,
            text="▶️ Iniciar Cámara",
            style='success',
            command=self.start_camera,
            font=Fonts.SUBTITLE
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.stop_btn = RoundedButton(
            button_frame,
            text="⏹️ Detener y Guardar",
            style='danger',
            command=self.stop_and_save,
            font=Fonts.SUBTITLE
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        RoundedButton(
            button_frame,
            text="📊 Ver Resultados",
            style='secondary',
            command=self.open_results_window,
            font=Fonts.SUBTITLE
        ).pack(side=tk.LEFT)
    
    def _build_status_bar(self):
        """Barra de estado inferior."""
        status_frame = tk.Frame(self, bg=Colors.TEXT_DARK, height=30)
        status_frame.pack(fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_indicator = StatusIndicator(status_frame, bg=Colors.TEXT_DARK)
        self.status_indicator.pack(side=tk.LEFT, padx=15, pady=5)
        
        # Información adicional
        info_frame = tk.Frame(status_frame, bg=Colors.TEXT_DARK)
        info_frame.pack(side=tk.RIGHT, padx=15, pady=5)
        
        self.session_info = tk.Label(
            info_frame,
            text="Sesión: No iniciada",
            font=Fonts.SMALL,
            bg=Colors.TEXT_DARK,
            fg=Colors.WHITE
        )
        self.session_info.pack(side=tk.RIGHT)
    
    def _load_models_into_combobox(self):
        """Cargar modelos disponibles en el combobox."""
        try:
            items = list_models(MODELS_DIR)
            display = [os.path.basename(p) for p in items]
            self.model_combo["values"] = display
            
            if items:
                if self.selected_model_path.get() in items:
                    idx = items.index(self.selected_model_path.get())
                    self.model_combo.current(idx)
                else:
                    self.model_combo.current(0)
                    self.on_model_selected()
            else:
                self.model_combo.set("")
                self.selected_model_path.set("")
                self.selected_model_name.set("No hay modelos disponibles")
                self.status_indicator.set_status("No se encontraron modelos", 'warning')
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar modelos: {e}")
    
    def on_model_selected(self, event=None):
        """Manejar selección de modelo."""
        values = self.model_combo["values"]
        if not values:
            return
        
        sel_name = self.model_combo.get()
        sel_path = os.path.join(MODELS_DIR, sel_name)
        self.selected_model_path.set(sel_path)
        self.selected_model_name.set(sel_name)
        
        self.status_indicator.set_status(f"Cargando modelo {sel_name}...", 'info')
        self.model_status.set_status("Cargando modelo...", 'warning')
        
        self.after(50, self._load_model_async, sel_path)
    
    def _load_model_async(self, path):
        """Cargar modelo de forma asíncrona."""
        def worker():
            try:
                model, input_shape, num_classes = load_emotion_model(path)
                labels = get_label_set_for_classes(num_classes)
                return (model, input_shape, num_classes, labels, None)
            except Exception as e:
                return (None, None, None, None, e)
        
        def on_done(result):
            model, input_shape, num_classes, labels, err = result
            if err is not None:
                messagebox.showerror("Error", f"No se pudo cargar el modelo.\n{err}")
                self.status_indicator.set_status("Error al cargar modelo", 'danger')
                self.model_status.set_status("Error en carga", 'danger')
                return
            
            self.model = model
            self.model_input_shape = input_shape
            self.model_num_classes = num_classes
            self.model_labels = labels
            
            self.status_indicator.set_status("Modelo cargado correctamente", 'success')
            self.model_status.set_status("Modelo listo", 'success')
        
        threading.Thread(target=lambda: self._thread_wrapper(worker, on_done), daemon=True).start()
    
    def _thread_wrapper(self, work_fn, callback):
        """Wrapper para ejecutar funciones en hilos."""
        result = work_fn()
        self.after(0, lambda: callback(result))
    
    def start_camera(self):
        """Iniciar cámara y detección."""
        if self.running:
            return
        
        if self.model is None:
            if not self.selected_model_path.get():
                messagebox.showwarning("Modelo requerido", "Selecciona un modelo antes de iniciar la cámara.")
                return
            
            try:
                self.model, self.model_input_shape, self.model_num_classes = load_emotion_model(self.selected_model_path.get())
                self.model_labels = get_label_set_for_classes(self.model_num_classes)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el modelo.\n{e}")
                return
        
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            messagebox.showerror("Cámara", "No se pudo abrir la cámara.")
            return
        
        self.running = True
        self.session_records = []
        self.session_start_time = time.time()
        self.last_preview_time = time.time()
        self.last_detect_time = 0.0
        
        # Iniciar temporizador de captura
        self.timer_start_time = time.time()
        self._start_capture_timer()
        
        # Actualizar UI
        self.status_indicator.set_status("Detección en curso", 'success')
        self.model_status.set_status("Detectando emociones...", 'success')
        self.session_info.config(text=f"Sesión iniciada: {datetime.now().strftime('%H:%M:%S')}")
        
        self._schedule_preview()
    
    def _schedule_preview(self):
        """Programar actualización de vista previa."""
        if not self.running:
            return
        self.preview_after_id = self.after(33, self._update_preview)  # ~30 FPS
    
    def _update_preview(self):
        """Actualizar vista previa de cámara."""
        if not self.running:
            return
        
        ret, frame = self.cap.read()
        if not ret:
            self.status_indicator.set_status("Error leyendo cámara", 'danger')
            self._schedule_preview()
            return
        
        # Calcular FPS
        now = time.time()
        dt = now - (self.last_preview_time or now)
        self.last_preview_time = now
        
        if dt > 0:
            inst_fps = 1.0 / dt
            self.fps = (0.9 * self.fps + 0.1 * inst_fps) if self.fps > 0 else inst_fps
            self.fps_label.config(text=f"{self.fps:.1f}")
        
        # Mostrar frame
        display = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(display)
        
        # Redimensionar manteniendo aspecto
        container_width = self.video_container.winfo_width()
        container_height = self.video_container.winfo_height()
        if container_width > 1 and container_height > 1:
            img = img.resize(self._fit_size(img.size, (container_width, container_height)), Image.LANCZOS)
        
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk, text="")
        
        # Ejecutar detección
        if self.model is not None and (now - self.last_detect_time) >= max(0.1, float(self.capture_interval_sec.get())):
            self.last_detect_time = now
            frame_copy = frame.copy()
            threading.Thread(target=self._run_detection, args=(frame_copy,), daemon=True).start()
        
        self._schedule_preview()
    
    def _run_detection(self, frame_bgr):
        """Ejecutar detección de emociones."""
        try:
            batch = prepare_frame_for_model(frame_bgr, self.model_input_shape)
            label_idx, confidence, prob_vec = predict_emotion(self.model, batch)
            
            if self.model_labels and len(self.model_labels) > label_idx:
                label = self.model_labels[label_idx]
            else:
                labels = get_label_set_for_classes(len(prob_vec))
                label = labels[label_idx] if label_idx < len(labels) else f"Clase {label_idx}"
            
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Guardar imagen en memoria
            _, img_encoded = cv2.imencode('.jpg', frame_bgr)
            img_data = img_encoded.tobytes()
            
            # Actualizar UI
            emotion_text = f"{label} ({confidence*100:.1f}%)"
            self.last_emotion.set(emotion_text)
            self.last_emotion_time.set(ts)
            
            # Registrar detección
            self.session_records.append({
                "timestamp": ts,
                "emotion": label,
                "confidence": float(confidence),
                "img_data": img_data,
                "model": self.selected_model_name.get(),
            })
            
            print(f"[DEBUG] Detección #{len(self.session_records)}: {label} ({confidence*100:.1f}%) a las {ts}")
            
        except Exception as e:
            self.status_indicator.set_status(f"Error en predicción: {e}", 'danger')
    
    def stop_and_save(self):
        """Detener cámara y guardar sesión."""
        if not self.running:
            messagebox.showinfo("Info", "La cámara no está activa.")
            return
        
        print(f"[DEBUG] Deteniendo sesión. Registros capturados: {len(self.session_records)}")
        
        # Detener cámara
        self.running = False
        
        # Detener temporizador
        self._stop_capture_timer()
        
        try:
            if self.preview_after_id is not None:
                self.after_cancel(self.preview_after_id)
                self.preview_after_id = None
        except Exception:
            pass
        
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None
        
        # Restaurar UI
        self.video_label.configure(
            image="",
            text="📷\n\nSesión finalizada\n\nPresiona 'Iniciar Cámara' para comenzar una nueva sesión"
        )
        self.fps_label.config(text="0.0")
        
        # Guardar reporte
        if self.session_records:
            print(f"[DEBUG] Guardando reporte con {len(self.session_records)} registros...")
            self._save_session_report()
        else:
            print("[DEBUG] No hay registros para guardar")
            messagebox.showinfo("Sesión Vacía", "No se detectaron emociones durante la sesión.\n\nNo se creará reporte PDF.")
        
        # Actualizar estado
        self.status_indicator.set_status("Sesión finalizada", 'info')
        self.model_status.set_status("Modelo listo", 'success')
        self.session_info.config(text="Sesión: Finalizada")
    
    def _save_session_report(self):
        """Guardar reporte de sesión."""
        print(f"[DEBUG] Iniciando guardado de reporte...")
        print(f"[DEBUG] Número de registros: {len(self.session_records)}")
        
        os.makedirs(RESULTS_DIR, exist_ok=True)
        session_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = os.path.join(RESULTS_DIR, f"sesion_{session_time}.pdf")
        
        print(f"[DEBUG] Ruta del PDF: {pdf_path}")
        
        try:
            total_duration = 0.0
            if self.session_start_time:
                total_duration = time.time() - self.session_start_time
            
            print(f"[DEBUG] Duración total: {total_duration:.1f}s")
            print(f"[DEBUG] Modelo: {self.selected_model_name.get()}")
            
            save_session_report(
                pdf_path=pdf_path,
                session_records=self.session_records,
                model_name=self.selected_model_name.get(),
                capture_interval=float(self.capture_interval_sec.get()),
                total_duration=total_duration,
            )
            
            print(f"[DEBUG] PDF creado exitosamente: {pdf_path}")
            
            messagebox.showinfo(
                "Guardado Exitoso",
                f"Sesión guardada correctamente:\n\n📁 Archivo: {os.path.basename(pdf_path)}\n📊 Detecciones: {len(self.session_records)}\n⏱️ Duración: {total_duration:.1f}s"
            )
        except Exception as e:
            print(f"[ERROR] Error guardando PDF: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error al Guardar", f"No se pudo guardar el reporte:\n\n{str(e)}\n\nVerifica la consola para más detalles.")
    
    def open_results_window(self):
        """Abrir ventana de resultados con diseño moderno."""
        self.results_window = ResultsWindow(self)
    
    def _fit_size(self, image_size, container_size):
        """Calcular tamaño ajustado manteniendo aspecto."""
        img_w, img_h = image_size
        cont_w, cont_h = container_size
        
        scale = min(cont_w / img_w, cont_h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        
        return (new_w, new_h)
    
    def _start_capture_timer(self):
        """Iniciar el temporizador de próxima captura."""
        self.timer_enabled = True
        self.timer_start_time = time.time()
        self.timer_status.config(text="Temporizador iniciado", fg=Colors.SUCCESS)
        print(f"[DEBUG] Temporizador iniciado en {self.timer_start_time}, Intervalo: {self.capture_interval_sec.get()}s")
        self._last_debug_time = -1  # Reset debug tracker
        self._update_capture_timer()
    
    def _stop_capture_timer(self):
        """Detener el temporizador de próxima captura."""
        self.timer_enabled = False
        if self.timer_after_id:
            self.after_cancel(self.timer_after_id)
            self.timer_after_id = None
        self.next_capture_timer.set("-")
        self.timer_status.config(text="Temporizador detenido", fg=Colors.TEXT_LIGHT)
        self.timer_display_frame.config(bg=Colors.CARD_BG)
        self.timer_label.config(fg=Colors.TEXT_LIGHT)
    
    def _update_capture_timer(self):
        """Actualizar el contador regresivo del temporizador."""
        if not self.timer_enabled or not self.running:
            self.next_capture_timer.set("-")
            self.timer_status.config(text="Temporizador desactivado", fg=Colors.TEXT_LIGHT)
            self.timer_display_frame.config(bg=Colors.CARD_BG)
            return
        
        try:
            # Calcular tiempo transcurrido desde el inicio del ciclo del temporizador
            current_time = time.time()
            capture_interval = max(0.1, float(self.capture_interval_sec.get()))
            
            # Calcular cuántos ciclos han pasado y el tiempo en el ciclo actual
            total_time = current_time - self.timer_start_time
            current_cycle = int(total_time // capture_interval)
            time_in_cycle = total_time % capture_interval
            time_remaining = capture_interval - time_in_cycle
            
            # Debug prints solo para valores enteros
            if int(time_remaining) != getattr(self, '_last_debug_time', -1):
                print(f"[TIMER DEBUG] Tiempo restante: {time_remaining:.1f}s de {capture_interval}s")
                self._last_debug_time = int(time_remaining)
            
            if time_remaining <= 0:
                # Ya es hora de la próxima captura
                self.next_capture_timer.set("¡CAPTURANDO!")
                self.timer_label.config(fg=Colors.WHITE)
                self.timer_display_frame.config(bg=Colors.SUCCESS)
                self.timer_status.config(text="Detectando emoción ahora...", fg=Colors.SUCCESS)
            elif time_remaining <= 1.0:
                # Menos de 1s - estado crítico
                self.next_capture_timer.set(f"{time_remaining:.1f}s")
                self.timer_label.config(fg=Colors.WHITE)
                self.timer_display_frame.config(bg=Colors.WARNING)
                self.timer_status.config(text="¡Preparándose para capturar!", fg=Colors.WARNING)
            elif time_remaining <= 2.0:
                # Menos de 2s - color naranja
                self.next_capture_timer.set(f"{time_remaining:.1f}s")
                self.timer_label.config(fg=Colors.TEXT_DARK)
                self.timer_display_frame.config(bg="#FFE4B5")  # Moccasin claro
                self.timer_status.config(text="Captura próxima...", fg="#FF8C00")
            else:
                # Tiempo normal - color accent
                self.next_capture_timer.set(f"{time_remaining:.1f}s")
                self.timer_label.config(fg=Colors.ACCENT)
                self.timer_display_frame.config(bg=Colors.CARD_BG)
                self.timer_status.config(text="Esperando intervalo de captura", fg=Colors.TEXT_DARK)
            
            # Programar próxima actualización cada 0.1 segundos
            self.timer_after_id = self.after(100, self._update_capture_timer)
            
        except (ValueError, TypeError):
            # Error en conversión - mostrar guión
            self.next_capture_timer.set("-")
            self.timer_label.config(fg=Colors.TEXT_LIGHT)
            self.timer_display_frame.config(bg=Colors.CARD_BG)
            self.timer_status.config(text="Error en configuración", fg=Colors.DANGER)
            # Reintentar en 0.5s
            self.timer_after_id = self.after(500, self._update_capture_timer)
    
    def on_close(self):
        """Manejar cierre de aplicación."""
        if self.running:
            self.stop_and_save()
        self.destroy()

class ResultsWindow(tk.Toplevel):
    """Ventana de resultados con diseño moderno."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Resultados de Sesiones")
        self.geometry("900x600")
        self.configure(bg=Colors.SECONDARY)
        self.transient(parent)
        self.grab_set()
        
        self.build_ui()
        self.load_results()
    
    def build_ui(self):
        """Construir interfaz de resultados."""
        # Header
        header = tk.Frame(self, bg=Colors.PRIMARY, height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📊 Resultados de Sesiones",
            font=Fonts.LARGE,
            bg=Colors.PRIMARY,
            fg=Colors.WHITE
        ).pack(side=tk.LEFT, padx=20, pady=10)
        
        # Controles
        controls = tk.Frame(header, bg=Colors.PRIMARY)
        controls.pack(side=tk.RIGHT, padx=20, pady=10)
        
        RoundedButton(
            controls,
            text="🔄 Actualizar",
            style='secondary',
            command=self.load_results
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        RoundedButton(
            controls,
            text="📁 Abrir Carpeta",
            style='secondary',
            command=self.open_results_folder
        ).pack(side=tk.LEFT)
        
        # Contenido principal
        main_frame = tk.Frame(self, bg=Colors.SECONDARY)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Lista de archivos
        files_card = ModernCard(main_frame, title="📄 Archivos de Sesión")
        files_card.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para archivos
        tree_frame = tk.Frame(files_card, bg=Colors.WHITE)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.files_tree = ttk.Treeview(
            tree_frame,
            columns=("fecha", "modelo", "detecciones"),
            show="tree headings",
            yscrollcommand=scrollbar.set
        )
        self.files_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.files_tree.yview)
        
        # Configurar columnas
        self.files_tree.heading("#0", text="Archivo")
        self.files_tree.heading("fecha", text="Fecha")
        self.files_tree.heading("modelo", text="Modelo")
        self.files_tree.heading("detecciones", text="Detecciones")
        
        self.files_tree.column("#0", width=200)
        self.files_tree.column("fecha", width=120)
        self.files_tree.column("modelo", width=180)
        self.files_tree.column("detecciones", width=100)
        
        # Bind eventos
        self.files_tree.bind("<Double-1>", self.on_file_double_click)
    
    def load_results(self):
        """Cargar lista de resultados."""
        # Limpiar tree
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        
        if not os.path.exists(RESULTS_DIR):
            return
        
        # Cargar archivos PDF
        pdf_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith('.pdf')]
        pdf_files.sort(reverse=True)  # Más recientes primero
        
        for pdf_file in pdf_files:
            # Extraer información del nombre del archivo
            try:
                # Formato: sesion_YYYYMMDD_HHMMSS.pdf
                name_part = pdf_file.replace('sesion_', '').replace('.pdf', '')
                date_part, time_part = name_part.split('_')
                
                # Formatear fecha
                year = date_part[:4]
                month = date_part[4:6]
                day = date_part[6:8]
                hour = time_part[:2]
                minute = time_part[2:4]
                second = time_part[4:6]
                
                fecha = f"{day}/{month}/{year} {hour}:{minute}:{second}"
            except:
                fecha = "N/A"
            
            modelo = "N/A"
            detecciones = "N/A"
            
            # Intentar extraer de PDF si posible
            if PdfReader:
                try:
                    filepath = os.path.join(RESULTS_DIR, pdf_file)
                    reader = PdfReader(filepath)
                    text = ""
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                    
                    # Buscar modelo (asumiendo formato en PDF como "Modelo: nombre")
                    if "Modelo:" in text:
                        modelo = text.split("Modelo:")[1].split("\n")[0].strip()
                    
                    # Buscar detecciones (asumiendo "Detecciones totales: X" o similar)
                    if "Detecciones totales:" in text:
                        detecciones = text.split("Detecciones totales:")[1].split("\n")[0].strip()
                    elif "Detecciones:" in text:
                        detecciones = text.split("Detecciones:")[1].split("\n")[0].strip()
                except:
                    pass
            
            self.files_tree.insert(
                "",
                tk.END,
                text=pdf_file,
                values=(fecha, modelo, detecciones)
            )
    
    def on_file_double_click(self, event):
        """Manejar doble clic en archivo."""
        selection = self.files_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        filename = self.files_tree.item(item, "text")
        filepath = os.path.join(RESULTS_DIR, filename)
        
        if os.path.exists(filepath):
            os.startfile(filepath)  # Abrir con aplicación predeterminada
    
    def open_results_folder(self):
        """Abrir carpeta de resultados."""
        if os.path.exists(RESULTS_DIR):
            os.startfile(RESULTS_DIR)
        else:
            messagebox.showinfo("Info", "La carpeta de resultados no existe aún.")

def main():
    """Función principal."""
    app = EmotionApp()
    app.mainloop()

if __name__ == "__main__":
    main()