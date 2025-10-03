#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 MÓDULO DE CÁMARA
Manejo de captura de video y procesamiento de frames
"""

import cv2
import threading
import time
from typing import Optional, Callable, Tuple
import numpy as np
from ..config import AppConfig

class CameraManager:
    """Gestor de cámara para captura de video y procesamiento de frames."""
    
    def __init__(self, camera_index: int = None):
        """
        Inicializar gestor de cámara.
        
        Args:
            camera_index: Índice de la cámara (por defecto usa AppConfig.CAMERA_DEFAULT_INDEX)
        """
        self.camera_index = camera_index or AppConfig.CAMERA_DEFAULT_INDEX
        self.cap = None
        self.is_running = False
        self.is_capturing = False
        
        # Threading
        self.capture_thread = None
        self.thread_lock = threading.Lock()
        
        # Callbacks
        self.frame_callback: Optional[Callable] = None
        self.error_callback: Optional[Callable] = None
        
        # Configuración de video
        self.width = AppConfig.CAMERA_WIDTH
        self.height = AppConfig.CAMERA_HEIGHT
        self.fps = AppConfig.CAMERA_FPS
        
        # Frame actual
        self.current_frame = None
        self.frame_count = 0
        
        # Estadísticas
        self.start_time = None
        self.last_frame_time = None
        self.actual_fps = 0.0
        
    def initialize_camera(self) -> bool:
        """
        Inicializar la cámara.
        
        Returns:
            True si la inicialización fue exitosa, False en caso contrario
        """
        try:
            # Intentar abrir la cámara
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                self._handle_error("No se pudo abrir la cámara")
                return False
            
            # Configurar propiedades de la cámara
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Verificar que la cámara funcione
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self._handle_error("No se pudo leer frame de la cámara")
                self.release_camera()
                return False
            
            print(f"[CAMERA] Cámara inicializada: {self.width}x{self.height} @ {self.fps}fps")
            return True
            
        except Exception as e:
            self._handle_error(f"Error al inicializar cámara: {str(e)}")
            return False
    
    def start_capture(self) -> bool:
        """
        Iniciar captura de video en hilo separado.
        
        Returns:
            True si se inició correctamente, False en caso contrario
        """
        if self.is_capturing:
            print("[CAMERA] La captura ya está en curso")
            return True
        
        if not self.cap or not self.cap.isOpened():
            if not self.initialize_camera():
                return False
        
        with self.thread_lock:
            self.is_capturing = True
            self.is_running = True
            self.start_time = time.time()
            self.frame_count = 0
            
            # Iniciar hilo de captura
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
        
        print("[CAMERA] Captura iniciada")
        return True
    
    def stop_capture(self):
        """Detener captura de video."""
        with self.thread_lock:
            self.is_capturing = False
            self.is_running = False
        
        # Esperar que termine el hilo
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)
        
        print("[CAMERA] Captura detenida")
    
    def release_camera(self):
        """Liberar recursos de la cámara."""
        self.stop_capture()
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.current_frame = None
        print("[CAMERA] Cámara liberada")
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """
        Obtener el frame actual.
        
        Returns:
            Frame actual como numpy array o None si no está disponible
        """
        with self.thread_lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def get_frame_size(self) -> Tuple[int, int]:
        """
        Obtener el tamaño del frame.
        
        Returns:
            Tupla con (ancho, alto) del frame
        """
        return (self.width, self.height)
    
    def get_fps_stats(self) -> dict:
        """
        Obtener estadísticas de FPS.
        
        Returns:
            Diccionario con estadísticas de FPS
        """
        return {
            'actual_fps': self.actual_fps,
            'target_fps': self.fps,
            'frame_count': self.frame_count,
            'uptime': time.time() - self.start_time if self.start_time else 0
        }
    
    def is_camera_available(self) -> bool:
        """
        Verificar si la cámara está disponible.
        
        Returns:
            True si la cámara está disponible y funcionando
        """
        return (self.cap is not None and 
                self.cap.isOpened() and 
                self.is_capturing)
    
    def set_frame_callback(self, callback: Callable):
        """
        Establecer callback para recibir frames.
        
        Args:
            callback: Función a llamar con cada frame capturado
        """
        self.frame_callback = callback
    
    def set_error_callback(self, callback: Callable):
        """
        Establecer callback para errores.
        
        Args:
            callback: Función a llamar cuando ocurra un error
        """
        self.error_callback = callback
    
    def _capture_loop(self):
        """Loop principal de captura de video."""
        frame_interval = 1.0 / self.fps
        
        while self.is_running:
            try:
                start_time = time.time()
                
                # Capturar frame
                ret, frame = self.cap.read()
                
                if not ret or frame is None:
                    self._handle_error("Error al leer frame de la cámara")
                    break
                
                # Procesar frame
                processed_frame = self._process_frame(frame)
                
                # Actualizar frame actual
                with self.thread_lock:
                    self.current_frame = processed_frame
                    self.frame_count += 1
                    self.last_frame_time = time.time()
                
                # Calcular FPS actual
                self._update_fps_stats()
                
                # Llamar callback si está configurado
                if self.frame_callback:
                    self.frame_callback(processed_frame)
                
                # Control de FPS
                elapsed = time.time() - start_time
                if elapsed < frame_interval:
                    time.sleep(frame_interval - elapsed)
                    
            except Exception as e:
                self._handle_error(f"Error en loop de captura: {str(e)}")
                break
        
        print("[CAMERA] Loop de captura terminado")
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Procesar frame capturado.
        
        Args:
            frame: Frame original de la cámara
            
        Returns:
            Frame procesado
        """
        # Voltear horizontalmente para efecto espejo
        frame = cv2.flip(frame, 1)
        
        # Asegurar que el frame tenga el tamaño correcto
        if frame.shape[:2] != (self.height, self.width):
            frame = cv2.resize(frame, (self.width, self.height))
        
        return frame
    
    def _update_fps_stats(self):
        """Actualizar estadísticas de FPS."""
        if self.start_time and self.frame_count > 0:
            elapsed = time.time() - self.start_time
            self.actual_fps = self.frame_count / elapsed
    
    def _handle_error(self, error_msg: str):
        """
        Manejar errores de cámara.
        
        Args:
            error_msg: Mensaje de error
        """
        print(f"[CAMERA ERROR] {error_msg}")
        
        if self.error_callback:
            self.error_callback(error_msg)
        
        # Detener captura en caso de error crítico
        self.is_running = False
        self.is_capturing = False
    
    def __del__(self):
        """Destructor para liberar recursos."""
        self.release_camera()


class FrameProcessor:
    """Procesador de frames para detección facial y preparación de datos."""
    
    def __init__(self):
        """Inicializar procesador de frames."""
        # Cargar clasificador de rostros
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Configuración de detección
        self.min_face_size = (48, 48)
        self.scale_factor = 1.1
        self.min_neighbors = 5
        
        # Estadísticas
        self.faces_detected = 0
        self.total_frames_processed = 0
    
    def detect_faces(self, frame: np.ndarray) -> list:
        """
        Detectar rostros en el frame.
        
        Args:
            frame: Frame de entrada
            
        Returns:
            Lista de rectángulos con rostros detectados [(x, y, w, h), ...]
        """
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detectar rostros
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors,
                minSize=self.min_face_size
            )
            
            self.total_frames_processed += 1
            if len(faces) > 0:
                self.faces_detected += len(faces)
            
            return faces.tolist()
            
        except Exception as e:
            print(f"[PROCESSOR ERROR] Error en detección de rostros: {str(e)}")
            return []
    
    def extract_face_region(self, frame: np.ndarray, face_rect: tuple, 
                           target_size: tuple = (48, 48)) -> Optional[np.ndarray]:
        """
        Extraer región facial del frame.
        
        Args:
            frame: Frame de entrada
            face_rect: Rectángulo del rostro (x, y, w, h)
            target_size: Tamaño objetivo para redimensionar
            
        Returns:
            Imagen del rostro redimensionada o None si hay error
        """
        try:
            x, y, w, h = face_rect
            
            # Extraer región facial
            face_region = frame[y:y+h, x:x+w]
            
            # Convertir a escala de grises si es necesario
            if len(face_region.shape) == 3:
                face_region = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            # Redimensionar al tamaño objetivo
            face_resized = cv2.resize(face_region, target_size)
            
            return face_resized
            
        except Exception as e:
            print(f"[PROCESSOR ERROR] Error extrayendo región facial: {str(e)}")
            return None
    
    def draw_face_rectangles(self, frame: np.ndarray, faces: list, 
                           color: tuple = (0, 255, 0), thickness: int = 2) -> np.ndarray:
        """
        Dibujar rectángulos alrededor de los rostros detectados.
        
        Args:
            frame: Frame de entrada
            faces: Lista de rostros detectados
            color: Color del rectángulo en formato BGR
            thickness: Grosor de las líneas
            
        Returns:
            Frame con rectángulos dibujados
        """
        frame_with_faces = frame.copy()
        
        for face in faces:
            x, y, w, h = face
            cv2.rectangle(frame_with_faces, (x, y), (x+w, y+h), color, thickness)
        
        return frame_with_faces
    
    def get_detection_stats(self) -> dict:
        """
        Obtener estadísticas de detección.
        
        Returns:
            Diccionario con estadísticas
        """
        detection_rate = (self.faces_detected / self.total_frames_processed 
                         if self.total_frames_processed > 0 else 0)
        
        return {
            'total_frames': self.total_frames_processed,
            'faces_detected': self.faces_detected,
            'detection_rate': detection_rate
        }