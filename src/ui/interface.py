#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 INTERFAZ PRINCIPAL MODULAR
Interfaz de usuario principal para la aplicación de detección de emociones
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import threading
import time
from typing import Optional

from .components import (
    RoundedButton, ModernCard, StatusIndicator, 
    ProgressBar, ModernCombobox, ModernSpinbox
)
from ..config import Colors, Fonts, Spacing, UIStyles, AppConfig, i18n
from ..core.camera import CameraManager, FrameProcessor
from ..core.emotion_detector import ModelManager
from ..core.session_manager import SessionManager

class EmotionDetectionInterface(tk.Tk):
    """Interfaz principal de la aplicación de detección de emociones."""
    
    def __init__(self):
        """Inicializar interfaz principal."""
        super().__init__()
        
        # Configurar ventana principal
        self._setup_window()
        
        # Inicializar módulos centrales
        self._setup_core_modules()
        
        # Configurar interfaz
        self._setup_styles()
        self._build_interface()
        
        # Inicializar estado
        self._setup_initial_state()
        
    def _setup_window(self):
        """Configurar propiedades de la ventana principal."""
        self.title(f"{i18n.TEXTS['app_title']} v{AppConfig.APP_VERSION}")
        self.geometry(f"{AppConfig.WINDOW_WIDTH}x{AppConfig.WINDOW_HEIGHT}")
        self.minsize(AppConfig.WINDOW_MIN_WIDTH, AppConfig.WINDOW_MIN_HEIGHT)
        self.configure(bg=Colors.BACKGROUND)
        
        # Centrar ventana en pantalla
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Configurar cierre de ventana
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_core_modules(self):
        """Inicializar módulos centrales."""
        # Gestores principales
        self.camera_manager = CameraManager()
        self.frame_processor = FrameProcessor()
        self.model_manager = ModelManager()
        self.session_manager = SessionManager()
        
        # Estado de la aplicación
        self.is_running = False
        self.current_frame = None
        self.preview_after_id = None
        
        # Configurar callbacks
        self.camera_manager.set_frame_callback(self._on_new_frame)
        self.camera_manager.set_error_callback(self._on_camera_error)
        self.session_manager.set_detection_callback(self._on_emotion_detected)
    
    def _setup_styles(self):
        """Configurar estilos de la interfaz."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar estilos personalizados
        style.configure('Modern.TFrame', background=Colors.BACKGROUND)
        style.configure('Card.TFrame', background=Colors.CARD_BG)
        style.configure('Header.TLabel', 
                       font=Fonts.HEADER, 
                       background=Colors.BACKGROUND,
                       foreground=Colors.TEXT_DARK)
        style.configure('Body.TLabel', 
                       font=Fonts.BODY,
                       background=Colors.CARD_BG,
                       foreground=Colors.TEXT_DARK)
    
    def _build_interface(self):
        """Construir la interfaz de usuario."""
        # Crear contenedor principal
        self.main_container = tk.Frame(self, bg=Colors.BACKGROUND)
        self.main_container.pack(fill="both", expand=True, padx=Spacing.MEDIUM, pady=Spacing.MEDIUM)
        
        # Construir componentes
        self._build_header()
        self._build_main_content()
        self._build_status_bar()
    
    def _build_header(self):
        """Construir cabecera de la aplicación."""
        header_frame = tk.Frame(self.main_container, bg=Colors.BACKGROUND, height=80)
        header_frame.pack(fill="x", pady=(0, Spacing.MEDIUM))
        header_frame.pack_propagate(False)
        
        # Título principal
        title_label = tk.Label(header_frame, 
                              text="🎯 " + i18n.TEXTS['app_title'],
                              font=(Fonts.FAMILY, 18, "bold"),
                              bg=Colors.BACKGROUND,
                              fg=Colors.PRIMARY)
        title_label.pack(side="left", pady=Spacing.MEDIUM)
        
        # Botones de control principales
        controls_frame = tk.Frame(header_frame, bg=Colors.BACKGROUND)
        controls_frame.pack(side="right", pady=Spacing.MEDIUM)
        
        # Variables de interfaz
        self.camera_button_text = tk.StringVar(value=i18n.TEXTS['start_camera'])
        
        self.camera_button = RoundedButton(
            controls_frame,
            textvariable=self.camera_button_text,
            command=self._toggle_camera,
            style='primary'
        )
        self.camera_button.pack(side="left", padx=(0, Spacing.SMALL))
        
        self.results_button = RoundedButton(
            controls_frame,
            text=i18n.TEXTS['view_results'],
            command=self._show_results,
            style='secondary'
        )
        self.results_button.pack(side="left", padx=Spacing.SMALL)
    
    def _build_main_content(self):
        """Construir contenido principal."""
        content_frame = tk.Frame(self.main_container, bg=Colors.BACKGROUND)
        content_frame.pack(fill="both", expand=True)
        
        # Panel izquierdo - Video y controles
        left_panel = tk.Frame(content_frame, bg=Colors.BACKGROUND)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, Spacing.MEDIUM))
        
        # Panel derecho - Información y configuración
        right_panel = tk.Frame(content_frame, bg=Colors.BACKGROUND, width=350)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)
        
        # Construir paneles
        self._build_video_panel(left_panel)
        self._build_info_panels(right_panel)
    
    def _build_video_panel(self, parent):
        """Construir panel de video."""
        # Tarjeta de video
        self.video_card = ModernCard(parent, title="Vista de Cámara")
        self.video_card.pack(fill="both", expand=True)
        
        # Canvas para mostrar video
        self.video_canvas = tk.Canvas(self.video_card.content_frame,
                                     bg=Colors.TEXT_LIGHT,
                                     width=640, height=480)
        self.video_canvas.pack(expand=True, padx=Spacing.MEDIUM, pady=Spacing.MEDIUM)
        
        # Texto de estado cuando no hay video
        self.no_video_text = self.video_canvas.create_text(
            320, 240, text="Presiona 'Iniciar Cámara' para comenzar",
            font=Fonts.BODY, fill=Colors.WHITE, anchor="center"
        )
    
    def _build_info_panels(self, parent):
        """Construir paneles de información."""
        # Panel de estado del modelo
        self._build_model_panel(parent)
        
        # Panel de métricas de sesión
        self._build_metrics_panel(parent)
        
        # Panel de temporizador
        self._build_timer_panel(parent)
        
        # Panel de configuración
        self._build_settings_panel(parent)
    
    def _build_model_panel(self, parent):
        """Construir panel de estado del modelo."""
        model_card = ModernCard(parent, title=i18n.TEXTS['model_status'])
        model_card.pack(fill="x", pady=(0, Spacing.MEDIUM))
        
        # Estado del modelo
        self.model_status = StatusIndicator(model_card.content_frame)
        self.model_status.pack(fill="x", padx=Spacing.MEDIUM, pady=Spacing.SMALL)
        
        # Selector de modelo
        selector_frame = tk.Frame(model_card.content_frame, bg=Colors.CARD_BG)
        selector_frame.pack(fill="x", padx=Spacing.MEDIUM, pady=Spacing.SMALL)
        
        tk.Label(selector_frame, text=i18n.TEXTS['select_model'],
                font=Fonts.CAPTION, bg=Colors.CARD_BG, fg=Colors.TEXT_DARK).pack(anchor="w")
        
        self.model_combobox = ModernCombobox(selector_frame)
        self.model_combobox.pack(fill="x", pady=(Spacing.TINY, 0))
        self.model_combobox.bind("<<ComboboxSelected>>", self._on_model_selected)
        
        # Cargar modelos disponibles
        self._load_available_models()
    
    def _build_metrics_panel(self, parent):
        """Construir panel de métricas."""
        metrics_card = ModernCard(parent, title=i18n.TEXTS['session_metrics'])
        metrics_card.pack(fill="x", pady=(0, Spacing.MEDIUM))
        
        # Frame para métricas
        metrics_frame = tk.Frame(metrics_card.content_frame, bg=Colors.CARD_BG)
        metrics_frame.pack(fill="x", padx=Spacing.MEDIUM, pady=Spacing.SMALL)
        
        # Detecciones totales
        detections_frame = tk.Frame(metrics_frame, bg=Colors.CARD_BG)
        detections_frame.pack(fill="x", pady=Spacing.TINY)
        
        tk.Label(detections_frame, text=i18n.TEXTS['detection_count'] + ":",
                font=Fonts.CAPTION, bg=Colors.CARD_BG, fg=Colors.TEXT_DARK).pack(side="left")
        
        self.detections_label = tk.Label(detections_frame, text="0",
                                        font=Fonts.BODY, bg=Colors.CARD_BG, fg=Colors.PRIMARY)
        self.detections_label.pack(side="right")
        
        # Duración de sesión
        duration_frame = tk.Frame(metrics_frame, bg=Colors.CARD_BG)
        duration_frame.pack(fill="x", pady=Spacing.TINY)
        
        tk.Label(duration_frame, text=i18n.TEXTS['session_duration'] + ":",
                font=Fonts.CAPTION, bg=Colors.CARD_BG, fg=Colors.TEXT_DARK).pack(side="left")
        
        self.duration_label = tk.Label(duration_frame, text="00:00",
                                      font=Fonts.BODY, bg=Colors.CARD_BG, fg=Colors.PRIMARY)
        self.duration_label.pack(side="right")
        
        # Emoción dominante
        dominant_frame = tk.Frame(metrics_frame, bg=Colors.CARD_BG)
        dominant_frame.pack(fill="x", pady=Spacing.TINY)
        
        tk.Label(dominant_frame, text="Dominante:",
                font=Fonts.CAPTION, bg=Colors.CARD_BG, fg=Colors.TEXT_DARK).pack(side="left")
        
        self.dominant_emotion_label = tk.Label(dominant_frame, text="---",
                                             font=Fonts.BODY, bg=Colors.CARD_BG, fg=Colors.ACCENT)
        self.dominant_emotion_label.pack(side="right")
    
    def _build_timer_panel(self, parent):
        """Construir panel de temporizador."""
        timer_card = ModernCard(parent, title=i18n.TEXTS['timer_panel'])
        timer_card.pack(fill="x", pady=(0, Spacing.MEDIUM))
        
        # Display del timer
        timer_display_frame = tk.Frame(timer_card.content_frame, bg=Colors.PRIMARY, height=50)
        timer_display_frame.pack(fill="x", padx=Spacing.MEDIUM, pady=Spacing.SMALL)
        timer_display_frame.pack_propagate(False)
        
        self.timer_display_label = tk.Label(timer_display_frame, text="--:--",
                                           font=(Fonts.FAMILY, 16, "bold"),
                                           bg=Colors.PRIMARY, fg=Colors.WHITE)
        self.timer_display_label.pack(expand=True)
        
        # Estado del timer
        self.timer_status = StatusIndicator(timer_card.content_frame)
        self.timer_status.pack(fill="x", padx=Spacing.MEDIUM, pady=Spacing.SMALL)
    
    def _build_settings_panel(self, parent):
        """Construir panel de configuración."""
        settings_card = ModernCard(parent, title=i18n.TEXTS['settings'])
        settings_card.pack(fill="x")
        
        settings_frame = tk.Frame(settings_card.content_frame, bg=Colors.CARD_BG)
        settings_frame.pack(fill="x", padx=Spacing.MEDIUM, pady=Spacing.SMALL)
        
        # Intervalo de captura
        interval_frame = tk.Frame(settings_frame, bg=Colors.CARD_BG)
        interval_frame.pack(fill="x", pady=Spacing.TINY)
        
        tk.Label(interval_frame, text=i18n.TEXTS['capture_interval'],
                font=Fonts.CAPTION, bg=Colors.CARD_BG, fg=Colors.TEXT_DARK).pack(anchor="w")
        
        self.interval_spinbox = ModernSpinbox(interval_frame,
                                            from_=0.1, to=60.0, increment=0.5,
                                            format="%.1f", width=10)
        self.interval_spinbox.pack(fill="x", pady=(Spacing.TINY, 0))
        self.interval_spinbox.set(str(AppConfig.DEFAULT_CAPTURE_INTERVAL))
        self.interval_spinbox.bind("<KeyRelease>", self._on_interval_changed)
        
        # Umbral de confianza
        threshold_frame = tk.Frame(settings_frame, bg=Colors.CARD_BG)
        threshold_frame.pack(fill="x", pady=Spacing.TINY)
        
        tk.Label(threshold_frame, text=i18n.TEXTS['confidence_threshold'],
                font=Fonts.CAPTION, bg=Colors.CARD_BG, fg=Colors.TEXT_DARK).pack(anchor="w")
        
        self.threshold_spinbox = ModernSpinbox(threshold_frame,
                                             from_=0.0, to=1.0, increment=0.1,
                                             format="%.1f", width=10)
        self.threshold_spinbox.pack(fill="x", pady=(Spacing.TINY, 0))
        self.threshold_spinbox.set(str(AppConfig.DEFAULT_CONFIDENCE_THRESHOLD))
        self.threshold_spinbox.bind("<KeyRelease>", self._on_threshold_changed)
    
    def _build_status_bar(self):
        """Construir barra de estado."""
        self.status_bar = tk.Frame(self.main_container, bg=Colors.CARD_BG, height=30)
        self.status_bar.pack(fill="x", pady=(Spacing.MEDIUM, 0))
        self.status_bar.pack_propagate(False)
        
        # Indicador de estado principal
        self.main_status = StatusIndicator(self.status_bar)
        self.main_status.pack(side="left", padx=Spacing.SMALL, pady=Spacing.TINY)
        
        # Información adicional
        self.info_label = tk.Label(self.status_bar, text="Listo para iniciar",
                                  font=Fonts.CAPTION, bg=Colors.CARD_BG, fg=Colors.TEXT_LIGHT)
        self.info_label.pack(side="right", padx=Spacing.SMALL, pady=Spacing.TINY)
    
    def _setup_initial_state(self):
        """Configurar estado inicial de la aplicación."""
        # Establecer estados iniciales
        self.model_status.set_status("Modelo no cargado", 'warning')
        self.main_status.set_status("Listo", 'info')
        self.timer_status.set_status("Timer inactivo", 'neutral')
        
        # Inicializar timer de updates de UI
        self._schedule_ui_updates()
    
    # Métodos de control principal
    def _toggle_camera(self):
        """Alternar estado de la cámara."""
        if not self.is_running:
            self._start_detection()
        else:
            self._stop_detection()
    
    def _start_detection(self):
        """Iniciar detección de emociones."""
        # Verificar que haya un modelo cargado
        if not self.model_manager.is_model_loaded():
            messagebox.showwarning("Modelo requerido", 
                                 "Debe cargar un modelo antes de iniciar la detección.")
            return
        
        # Inicializar cámara
        if not self.camera_manager.initialize_camera():
            messagebox.showerror("Error de cámara", 
                               "No se pudo inicializar la cámara.")
            return
        
        # Iniciar captura
        if not self.camera_manager.start_capture():
            messagebox.showerror("Error de captura", 
                               "No se pudo iniciar la captura de video.")
            return
        
        # Iniciar sesión
        self.session_manager.start_session()
        
        # Configurar timer de capturas
        interval = float(self.interval_spinbox.get())
        self.session_manager.start_capture_timer(interval)
        
        # Actualizar estado
        self.is_running = True
        self.camera_button_text.set(i18n.TEXTS['stop_camera'])
        self.main_status.set_status("Detección en curso", 'success')
        
        print("[APP] Detección iniciada")
    
    def _stop_detection(self):
        """Detener detección de emociones."""
        # Detener captura
        self.camera_manager.stop_capture()
        
        # Finalizar sesión
        self.session_manager.end_session(save_report=True)
        
        # Actualizar estado
        self.is_running = False
        self.camera_button_text.set(i18n.TEXTS['start_camera'])
        self.main_status.set_status("Detenido", 'warning')
        
        # Limpiar display de video
        self.video_canvas.delete("all")
        self.video_canvas.create_text(
            320, 240, text="Detección detenida",
            font=Fonts.BODY, fill=Colors.WHITE, anchor="center"
        )
        
        print("[APP] Detección detenida")
    
    def _show_results(self):
        """Mostrar ventana de resultados."""
        # TODO: Implementar ventana de resultados
        sessions = self.session_manager.load_session_history()
        if sessions:
            messagebox.showinfo("Resultados", 
                              f"Se encontraron {len(sessions)} sesiones guardadas.")
        else:
            messagebox.showinfo("Resultados", 
                              "No hay sesiones guardadas.")
    
    # Callbacks de eventos
    def _on_new_frame(self, frame):
        """Callback para nuevos frames de la cámara."""
        self.current_frame = frame
        
        # Procesar frame para detección si es momento de capturar
        if self.session_manager.is_capture_time():
            self._process_frame_for_emotion(frame)
    
    def _on_camera_error(self, error_msg):
        """Callback para errores de cámara."""
        self.main_status.set_status(f"Error: {error_msg}", 'danger')
        messagebox.showerror("Error de Cámara", error_msg)
    
    def _on_emotion_detected(self, detection):
        """Callback para detecciones de emoción."""
        print(f"[EMOTION] {detection.emotion}: {detection.confidence:.2f}")
    
    def _on_model_selected(self, event):
        """Callback para selección de modelo."""
        selected_model = self.model_combobox.get()
        if selected_model and self.model_manager.load_model(selected_model):
            self.model_status.set_status(f"Modelo cargado: {selected_model}", 'success')
            # Actualizar umbral de confianza
            threshold = float(self.threshold_spinbox.get())
            self.model_manager.get_current_model().set_confidence_threshold(threshold)
        else:
            self.model_status.set_status("Error cargando modelo", 'danger')
    
    def _on_interval_changed(self, event):
        """Callback para cambio de intervalo de captura."""
        try:
            interval = float(self.interval_spinbox.get())
            self.session_manager.set_capture_interval(interval)
        except ValueError:
            pass
    
    def _on_threshold_changed(self, event):
        """Callback para cambio de umbral de confianza."""
        try:
            threshold = float(self.threshold_spinbox.get())
            if self.model_manager.is_model_loaded():
                self.model_manager.get_current_model().set_confidence_threshold(threshold)
        except ValueError:
            pass
    
    def _on_closing(self):
        """Manejar cierre de la aplicación."""
        if self.is_running:
            self._stop_detection()
        
        # Liberar recursos
        self.camera_manager.release_camera()
        self.destroy()
    
    # Métodos auxiliares
    def _load_available_models(self):
        """Cargar modelos disponibles en el combobox."""
        models = self.model_manager.get_available_models()
        self.model_combobox['values'] = models
        
        # Seleccionar modelo por defecto si está disponible
        if AppConfig.DEFAULT_MODEL in models:
            self.model_combobox.set(AppConfig.DEFAULT_MODEL)
            self._on_model_selected(None)
    
    def _process_frame_for_emotion(self, frame):
        """Procesar frame para detección de emociones."""
        if not self.model_manager.is_model_loaded():
            return
        
        # Detectar rostros
        faces = self.frame_processor.detect_faces(frame)
        
        if faces:
            # Procesar primer rostro detectado
            face = faces[0]
            face_region = self.frame_processor.extract_face_region(frame, face)
            
            if face_region is not None:
                # Predecir emoción
                emotion_model = self.model_manager.get_current_model()
                result = emotion_model.predict_emotion(face_region)
                
                if result:
                    # Agregar detección a la sesión
                    self.session_manager.add_detection(
                        result['emotion'], 
                        result['confidence']
                    )
    
    def _update_video_display(self):
        """Actualizar display de video."""
        if self.current_frame is not None and self.is_running:
            try:
                # Procesar frame para display
                display_frame = self.current_frame.copy()
                
                # Detectar y dibujar rostros
                faces = self.frame_processor.detect_faces(display_frame)
                if faces:
                    display_frame = self.frame_processor.draw_face_rectangles(
                        display_frame, faces, (0, 255, 0), 2
                    )
                
                # Redimensionar para display
                height, width = display_frame.shape[:2]
                canvas_width = self.video_canvas.winfo_width()
                canvas_height = self.video_canvas.winfo_height()
                
                if canvas_width > 1 and canvas_height > 1:
                    # Calcular escala manteniendo aspecto
                    scale = min(canvas_width / width, canvas_height / height)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    
                    display_frame = cv2.resize(display_frame, (new_width, new_height))
                    
                    # Convertir a formato PIL
                    frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    photo = ImageTk.PhotoImage(pil_image)
                    
                    # Actualizar canvas
                    self.video_canvas.delete("all")
                    x = (canvas_width - new_width) // 2
                    y = (canvas_height - new_height) // 2
                    self.video_canvas.create_image(x, y, anchor="nw", image=photo)
                    
                    # Mantener referencia
                    self.video_canvas.image = photo
                    
            except Exception as e:
                print(f"[UI ERROR] Error actualizando video: {e}")
    
    def _update_metrics_display(self):
        """Actualizar display de métricas."""
        if self.session_manager.is_session_active():
            stats = self.session_manager.get_current_stats()
            if stats:
                # Actualizar conteo de detecciones
                self.detections_label.config(text=str(stats['total_detections']))
                
                # Actualizar duración
                duration = int(stats['duration'])
                minutes = duration // 60
                seconds = duration % 60
                self.duration_label.config(text=f"{minutes:02d}:{seconds:02d}")
                
                # Actualizar emoción dominante
                dominant = stats['dominant_emotion']
                if dominant:
                    emotion, count, confidence = dominant
                    self.dominant_emotion_label.config(text=f"{emotion} ({count})")
                else:
                    self.dominant_emotion_label.config(text="---")
        else:
            # Resetear displays cuando no hay sesión
            self.detections_label.config(text="0")
            self.duration_label.config(text="00:00")
            self.dominant_emotion_label.config(text="---")
    
    def _update_timer_display(self):
        """Actualizar display del timer."""
        if self.session_manager.capture_timer_enabled:
            timer_status = self.session_manager.get_timer_status()
            time_remaining = timer_status['time_remaining']
            
            # Formatear tiempo restante
            if time_remaining <= 0:
                self.timer_display_label.config(text="¡AHORA!", bg=Colors.SUCCESS)
                self.timer_status.set_status("Capturando...", 'success')
            else:
                minutes = int(time_remaining // 60)
                seconds = int(time_remaining % 60)
                decimals = int((time_remaining % 1) * 10)
                
                if time_remaining <= 2:
                    bg_color = Colors.DANGER
                    status_text = "¡Preparándose!"
                    status_type = 'danger'
                elif time_remaining <= 5:
                    bg_color = Colors.WARNING
                    status_text = "Próxima captura"
                    status_type = 'warning'
                else:
                    bg_color = Colors.PRIMARY
                    status_text = "Esperando"
                    status_type = 'info'
                
                if minutes > 0:
                    time_text = f"{minutes}:{seconds:02d}.{decimals}"
                else:
                    time_text = f"{seconds}.{decimals}s"
                
                self.timer_display_label.config(text=time_text, bg=bg_color)
                self.timer_status.set_status(status_text, status_type)
        else:
            self.timer_display_label.config(text="--:--", bg=Colors.TEXT_LIGHT)
            self.timer_status.set_status("Timer inactivo", 'neutral')
    
    def _schedule_ui_updates(self):
        """Programar actualizaciones periódicas de la UI."""
        # Actualizar displays
        self._update_video_display()
        self._update_metrics_display()
        self._update_timer_display()
        
        # Programar próxima actualización
        self.after(33, self._schedule_ui_updates)  # ~30 FPS