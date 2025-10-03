#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 MÓDULO DE MANEJO DE SESIONES
Gestión de sesiones, estadísticas y almacenamiento de datos
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict, deque
from ..config import AppConfig, PerformanceConfig, EmotionConfig
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from utils.pdf_report import save_session_report

class EmotionDetection:
    """Clase para representar una detección de emoción individual."""
    
    def __init__(self, emotion: str, confidence: float, timestamp: float = None):
        """
        Inicializar detección de emoción.
        
        Args:
            emotion: Etiqueta de la emoción detectada
            confidence: Nivel de confianza (0.0 a 1.0)
            timestamp: Tiempo de la detección (por defecto tiempo actual)
        """
        self.emotion = emotion
        self.confidence = confidence
        self.timestamp = timestamp or time.time()
        self.datetime = datetime.fromtimestamp(self.timestamp)
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario para serialización."""
        return {
            'emotion': self.emotion,
            'confidence': self.confidence,
            'timestamp': self.timestamp,
            'datetime': self.datetime.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EmotionDetection':
        """Crear instancia desde diccionario."""
        return cls(
            emotion=data['emotion'],
            confidence=data['confidence'],
            timestamp=data['timestamp']
        )


class SessionStatistics:
    """Estadísticas de una sesión de detección."""
    
    def __init__(self):
        """Inicializar estadísticas."""
        # Contadores básicos
        self.total_detections = 0
        self.emotion_counts = defaultdict(int)
        self.confidence_sum = defaultdict(float)
        
        # Estadísticas temporales
        self.start_time = None
        self.end_time = None
        self.duration = 0.0
        
        # Historial de detecciones (limitado para performance)
        self.detections_history = deque(maxlen=PerformanceConfig.MAX_EMOTION_HISTORY)
        
        # Estadísticas por intervalos de tiempo
        self.detections_per_minute = defaultdict(int)
        self.peak_emotion_times = defaultdict(list)
    
    def add_detection(self, detection: EmotionDetection):
        """
        Agregar una nueva detección a las estadísticas.
        
        Args:
            detection: Detección de emoción a agregar
        """
        # Actualizar contadores
        self.total_detections += 1
        self.emotion_counts[detection.emotion] += 1
        self.confidence_sum[detection.emotion] += detection.confidence
        
        # Agregar al historial
        self.detections_history.append(detection)
        
        # Estadísticas temporales
        minute_key = int(detection.timestamp // 60)
        self.detections_per_minute[minute_key] += 1
        
        # Registrar picos de emociones (confianza alta)
        if detection.confidence > 0.8:
            self.peak_emotion_times[detection.emotion].append(detection.timestamp)
    
    def get_dominant_emotion(self) -> Optional[Tuple[str, int, float]]:
        """
        Obtener la emoción dominante en la sesión.
        
        Returns:
            Tupla con (emoción, conteo, confianza_promedio) o None si no hay datos
        """
        if not self.emotion_counts:
            return None
        
        # Encontrar emoción más frecuente
        dominant_emotion = max(self.emotion_counts.items(), key=lambda x: x[1])
        emotion, count = dominant_emotion
        
        # Calcular confianza promedio
        avg_confidence = self.confidence_sum[emotion] / count if count > 0 else 0
        
        return (emotion, count, avg_confidence)
    
    def get_emotion_distribution(self) -> Dict[str, float]:
        """
        Obtener distribución porcentual de emociones.
        
        Returns:
            Diccionario con porcentajes por emoción
        """
        if self.total_detections == 0:
            return {}
        
        return {
            emotion: (count / self.total_detections) * 100
            for emotion, count in self.emotion_counts.items()
        }
    
    def get_average_confidences(self) -> Dict[str, float]:
        """
        Obtener confianzas promedio por emoción.
        
        Returns:
            Diccionario con confianzas promedio por emoción
        """
        return {
            emotion: self.confidence_sum[emotion] / self.emotion_counts[emotion]
            for emotion in self.emotion_counts
            if self.emotion_counts[emotion] > 0
        }
    
    def get_detection_rate(self) -> float:
        """
        Obtener tasa de detección (detecciones por minuto).
        
        Returns:
            Detecciones por minuto
        """
        if not self.duration or self.duration == 0:
            return 0.0
        
        return self.total_detections / (self.duration / 60.0)
    
    def get_timeline_data(self, interval_minutes: int = 1) -> Dict:
        """
        Obtener datos de línea de tiempo por intervalos.
        
        Args:
            interval_minutes: Intervalo en minutos
            
        Returns:
            Diccionario con datos de línea de tiempo
        """
        if not self.start_time:
            return {}
        
        timeline = {}
        current_time = self.start_time
        end_time = self.end_time or time.time()
        
        while current_time < end_time:
            interval_start = current_time
            interval_end = current_time + (interval_minutes * 60)
            
            # Contar detecciones en este intervalo
            interval_detections = [
                d for d in self.detections_history
                if interval_start <= d.timestamp < interval_end
            ]
            
            interval_key = datetime.fromtimestamp(interval_start).strftime('%H:%M')
            timeline[interval_key] = {
                'total': len(interval_detections),
                'emotions': defaultdict(int)
            }
            
            for detection in interval_detections:
                timeline[interval_key]['emotions'][detection.emotion] += 1
            
            current_time = interval_end
        
        return timeline
    
    def to_dict(self) -> Dict:
        """Convertir estadísticas a diccionario para serialización."""
        return {
            'total_detections': self.total_detections,
            'emotion_counts': dict(self.emotion_counts),
            'confidence_sum': dict(self.confidence_sum),
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'detections_history': [d.to_dict() for d in self.detections_history],
            'dominant_emotion': self.get_dominant_emotion(),
            'emotion_distribution': self.get_emotion_distribution(),
            'average_confidences': self.get_average_confidences(),
            'detection_rate': self.get_detection_rate()
        }


class SessionManager:
    """Gestor principal de sesiones de detección de emociones."""
    
    def __init__(self):
        """Inicializar gestor de sesiones."""
        self.current_session = None
        self.session_active = False
        self.session_id = None
        
        # Configuración
        self.results_dir = Path(AppConfig.get_results_dir())
        self.results_dir.mkdir(exist_ok=True)
        
        # Timer para capturas automáticas
        self.capture_timer_enabled = False
        self.capture_timer_start = None
        self.capture_interval = AppConfig.DEFAULT_CAPTURE_INTERVAL
        self.next_capture_time = None
        
        # Callbacks
        self.detection_callback = None
        self.timer_callback = None
        
    def start_session(self) -> str:
        """
        Iniciar nueva sesión de detección.
        
        Returns:
            ID de la sesión creada
        """
        if self.session_active:
            self.end_session()
        
        # Crear nueva sesión
        self.session_id = datetime.now().strftime("sesion_%Y%m%d_%H%M%S")
        self.current_session = SessionStatistics()
        self.current_session.start_time = time.time()
        self.session_active = True
        
        # Inicializar timer de capturas
        self.capture_timer_start = time.time()
        self.next_capture_time = self.capture_timer_start + self.capture_interval
        
        print(f"[SESSION] Nueva sesión iniciada: {self.session_id}")
        return self.session_id
    
    def end_session(self, save_report: bool = True) -> Optional[Dict]:
        """
        Finalizar sesión actual.
        
        Args:
            save_report: Si generar reporte PDF automáticamente
            
        Returns:
            Diccionario con estadísticas de la sesión o None
        """
        if not self.session_active or not self.current_session:
            return None
        
        # Finalizar sesión
        self.current_session.end_time = time.time()
        self.current_session.duration = (
            self.current_session.end_time - self.current_session.start_time
        )
        self.session_active = False
        self.capture_timer_enabled = False
        
        # Obtener estadísticas finales
        stats = self.current_session.to_dict()
        
        print(f"[SESSION] Sesión finalizada: {self.session_id}")
        print(f"  - Duración: {stats['duration']:.1f}s")
        print(f"  - Detecciones: {stats['total_detections']}")
        print(f"  - Emoción dominante: {stats['dominant_emotion']}")
        
        # Generar reporte PDF si se solicita
        if save_report and stats['total_detections'] > 0:
            try:
                self._save_session_report(stats)
            except Exception as e:
                print(f"[SESSION ERROR] Error guardando reporte: {str(e)}")
        
        # Limpiar sesión actual
        session_stats = stats.copy()
        self.current_session = None
        self.session_id = None
        
        return session_stats
    
    def add_detection(self, emotion: str, confidence: float, timestamp: float = None):
        """
        Agregar detección a la sesión actual.
        
        Args:
            emotion: Emoción detectada
            confidence: Nivel de confianza
            timestamp: Tiempo de detección (por defecto tiempo actual)
        """
        if not self.session_active or not self.current_session:
            return
        
        # Crear y agregar detección
        detection = EmotionDetection(emotion, confidence, timestamp)
        self.current_session.add_detection(detection)
        
        # Llamar callback si está configurado
        if self.detection_callback:
            self.detection_callback(detection)
        
        print(f"[SESSION] Detección agregada: {emotion} ({confidence:.2f})")
    
    def get_current_stats(self) -> Optional[Dict]:
        """
        Obtener estadísticas de la sesión actual.
        
        Returns:
            Diccionario con estadísticas actuales o None
        """
        if not self.session_active or not self.current_session:
            return None
        
        # Actualizar duración actual
        current_time = time.time()
        self.current_session.duration = current_time - self.current_session.start_time
        
        return self.current_session.to_dict()
    
    def is_session_active(self) -> bool:
        """
        Verificar si hay una sesión activa.
        
        Returns:
            True si hay una sesión activa
        """
        return self.session_active
    
    def get_session_id(self) -> Optional[str]:
        """
        Obtener ID de la sesión actual.
        
        Returns:
            ID de la sesión o None si no hay sesión activa
        """
        return self.session_id
    
    # Timer de capturas
    def start_capture_timer(self, interval: float = None):
        """
        Iniciar timer de capturas automáticas.
        
        Args:
            interval: Intervalo entre capturas en segundos
        """
        if interval is not None:
            self.capture_interval = max(0.1, interval)
        
        self.capture_timer_enabled = True
        self.capture_timer_start = time.time()
        self.next_capture_time = self.capture_timer_start + self.capture_interval
        
        print(f"[TIMER] Timer iniciado: {self.capture_interval}s")
    
    def stop_capture_timer(self):
        """Detener timer de capturas."""
        self.capture_timer_enabled = False
        print("[TIMER] Timer detenido")
    
    def get_timer_status(self) -> Dict:
        """
        Obtener estado del timer de capturas.
        
        Returns:
            Diccionario con estado del timer
        """
        if not self.capture_timer_enabled:
            return {
                'enabled': False,
                'time_remaining': 0,
                'next_capture': None,
                'interval': self.capture_interval
            }
        
        current_time = time.time()
        elapsed = current_time - self.capture_timer_start
        time_in_cycle = elapsed % self.capture_interval
        time_remaining = self.capture_interval - time_in_cycle
        
        return {
            'enabled': True,
            'time_remaining': time_remaining,
            'next_capture': current_time + time_remaining,
            'interval': self.capture_interval,
            'cycle_count': int(elapsed // self.capture_interval)
        }
    
    def is_capture_time(self) -> bool:
        """
        Verificar si es momento de capturar.
        
        Returns:
            True si es momento de hacer una captura
        """
        if not self.capture_timer_enabled:
            return False
        
        timer_status = self.get_timer_status()
        return timer_status['time_remaining'] <= 0.1  # Margen de 100ms
    
    # Configuración y callbacks
    def set_capture_interval(self, interval: float):
        """
        Establecer intervalo de captura.
        
        Args:
            interval: Intervalo en segundos
        """
        self.capture_interval = max(AppConfig.MIN_CAPTURE_INTERVAL, 
                                  min(AppConfig.MAX_CAPTURE_INTERVAL, interval))
    
    def set_detection_callback(self, callback):
        """
        Establecer callback para nuevas detecciones.
        
        Args:
            callback: Función a llamar con cada detección
        """
        self.detection_callback = callback
    
    def set_timer_callback(self, callback):
        """
        Establecer callback para updates del timer.
        
        Args:
            callback: Función a llamar con updates del timer
        """
        self.timer_callback = callback
    
    def _save_session_report(self, stats: Dict):
        """
        Guardar reporte de sesión en PDF.
        
        Args:
            stats: Estadísticas de la sesión
        """
        # Preparar datos para el reporte
        session_data = {
            'session_id': self.session_id,
            'start_time': datetime.fromtimestamp(stats['start_time']),
            'end_time': datetime.fromtimestamp(stats['end_time']),
            'duration': stats['duration'],
            'total_detections': stats['total_detections'],
            'emotion_counts': stats['emotion_counts'],
            'emotion_distribution': stats['emotion_distribution'],
            'average_confidences': stats['average_confidences'],
            'detection_rate': stats['detection_rate'],
            'dominant_emotion': stats['dominant_emotion']
        }
        
        # Generar nombre de archivo
        filename = f"{self.session_id}.pdf"
        filepath = self.results_dir / filename
        
        # Guardar reporte
        save_session_report(
            session_data=session_data,
            output_path=str(filepath),
            include_charts=True
        )
        
        print(f"[SESSION] Reporte guardado: {filepath}")
    
    def load_session_history(self, limit: int = 10) -> List[Dict]:
        """
        Cargar historial de sesiones guardadas.
        
        Args:
            limit: Número máximo de sesiones a cargar
            
        Returns:
            Lista de metadatos de sesiones
        """
        try:
            pdf_files = list(self.results_dir.glob("sesion_*.pdf"))
            pdf_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            sessions = []
            for pdf_file in pdf_files[:limit]:
                try:
                    stat = pdf_file.stat()
                    sessions.append({
                        'filename': pdf_file.name,
                        'session_id': pdf_file.stem,
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'size': stat.st_size,
                        'path': str(pdf_file)
                    })
                except Exception as e:
                    print(f"[SESSION] Error procesando {pdf_file}: {e}")
            
            return sessions
            
        except Exception as e:
            print(f"[SESSION ERROR] Error cargando historial: {str(e)}")
            return []