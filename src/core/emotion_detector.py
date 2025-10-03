#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 MÓDULO DE DETECCIÓN DE EMOCIONES
Manejo de modelos de IA y predicción de emociones
"""

import os
import numpy as np
from typing import Optional, Tuple, List, Dict
from pathlib import Path
import time
from ..config import AppConfig, EmotionConfig

# Importación tardía de TensorFlow para evitar problemas de inicialización
def _ensure_tf():
    """Asegurar que TensorFlow esté disponible."""
    try:
        import tensorflow as tf
        return tf
    except ImportError:
        raise ImportError("TensorFlow no está instalado. Instálalo con: pip install tensorflow")

class EmotionModel:
    """Gestor de modelo de detección de emociones."""
    
    def __init__(self):
        """Inicializar gestor de modelo."""
        self.model = None
        self.input_shape = None
        self.num_classes = None
        self.emotion_labels = None
        self.model_path = None
        self.is_loaded = False
        
        # Configuración de predicción
        self.confidence_threshold = AppConfig.DEFAULT_CONFIDENCE_THRESHOLD
        
        # Estadísticas
        self.total_predictions = 0
        self.successful_predictions = 0
        self.load_time = None
        
    def load_model(self, model_path: str) -> bool:
        """
        Cargar modelo de detección de emociones.
        
        Args:
            model_path: Ruta al archivo del modelo
            
        Returns:
            True si el modelo se cargó correctamente, False en caso contrario
        """
        try:
            start_time = time.time()
            
            # Verificar que el archivo existe
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Modelo no encontrado: {model_path}")
            
            # Importar TensorFlow
            tf = _ensure_tf()
            
            # Cargar el modelo
            print(f"[MODEL] Cargando modelo: {model_path}")
            self.model = tf.keras.models.load_model(model_path)
            
            # Obtener información del modelo
            self.input_shape = self.model.input_shape
            
            # Deducir número de clases de la última capa
            output_shape = self.model.output_shape
            if len(output_shape) >= 2:
                self.num_classes = output_shape[-1]
                if not isinstance(self.num_classes, int):
                    self.num_classes = int(self.num_classes)
            else:
                raise ValueError(f"Forma de salida del modelo no válida: {output_shape}")
            
            # Obtener etiquetas de emociones
            self.emotion_labels = EmotionConfig.get_labels_for_classes(self.num_classes)
            
            # Actualizar estado
            self.model_path = model_path
            self.is_loaded = True
            self.load_time = time.time() - start_time
            
            print(f"[MODEL] Modelo cargado exitosamente:")
            print(f"  - Archivo: {os.path.basename(model_path)}")
            print(f"  - Forma de entrada: {self.input_shape}")
            print(f"  - Número de clases: {self.num_classes}")
            print(f"  - Etiquetas: {self.emotion_labels}")
            print(f"  - Tiempo de carga: {self.load_time:.2f}s")
            
            return True
            
        except Exception as e:
            print(f"[MODEL ERROR] Error cargando modelo: {str(e)}")
            self.is_loaded = False
            self.model = None
            return False
    
    def predict_emotion(self, face_image: np.ndarray) -> Optional[Dict]:
        """
        Predecir emoción de una imagen facial.
        
        Args:
            face_image: Imagen facial como numpy array
            
        Returns:
            Diccionario con predicción o None si hay error
        """
        if not self.is_loaded or self.model is None:
            print("[MODEL ERROR] Modelo no cargado")
            return None
        
        try:
            self.total_predictions += 1
            
            # Preparar imagen para el modelo
            processed_image = self._prepare_image_for_model(face_image)
            if processed_image is None:
                return None
            
            # Hacer predicción
            predictions = self.model.predict(processed_image, verbose=0)
            
            # Procesar resultados
            result = self._process_predictions(predictions[0])
            
            if result:
                self.successful_predictions += 1
            
            return result
            
        except Exception as e:
            print(f"[MODEL ERROR] Error en predicción: {str(e)}")
            return None
    
    def predict_batch(self, face_images: List[np.ndarray]) -> List[Optional[Dict]]:
        """
        Predecir emociones para un lote de imágenes.
        
        Args:
            face_images: Lista de imágenes faciales
            
        Returns:
            Lista de predicciones
        """
        if not self.is_loaded or self.model is None:
            return [None] * len(face_images)
        
        try:
            # Preparar todas las imágenes
            batch_images = []
            valid_indices = []
            
            for i, face_image in enumerate(face_images):
                processed = self._prepare_image_for_model(face_image, expand_dims=False)
                if processed is not None:
                    batch_images.append(processed[0])  # Remover dimensión de batch
                    valid_indices.append(i)
            
            if not batch_images:
                return [None] * len(face_images)
            
            # Crear batch
            batch_array = np.array(batch_images)
            
            # Hacer predicciones
            predictions = self.model.predict(batch_array, verbose=0)
            
            # Procesar resultados
            results = [None] * len(face_images)
            for i, pred_idx in enumerate(valid_indices):
                result = self._process_predictions(predictions[i])
                results[pred_idx] = result
                
                self.total_predictions += 1
                if result:
                    self.successful_predictions += 1
            
            return results
            
        except Exception as e:
            print(f"[MODEL ERROR] Error en predicción por lotes: {str(e)}")
            return [None] * len(face_images)
    
    def get_model_info(self) -> Dict:
        """
        Obtener información del modelo cargado.
        
        Returns:
            Diccionario con información del modelo
        """
        return {
            'is_loaded': self.is_loaded,
            'model_path': self.model_path,
            'input_shape': self.input_shape,
            'num_classes': self.num_classes,
            'emotion_labels': self.emotion_labels,
            'load_time': self.load_time,
            'confidence_threshold': self.confidence_threshold
        }
    
    def get_prediction_stats(self) -> Dict:
        """
        Obtener estadísticas de predicción.
        
        Returns:
            Diccionario con estadísticas
        """
        success_rate = (self.successful_predictions / self.total_predictions 
                       if self.total_predictions > 0 else 0)
        
        return {
            'total_predictions': self.total_predictions,
            'successful_predictions': self.successful_predictions,
            'success_rate': success_rate,
            'confidence_threshold': self.confidence_threshold
        }
    
    def set_confidence_threshold(self, threshold: float):
        """
        Establecer umbral de confianza.
        
        Args:
            threshold: Umbral de confianza (0.0 a 1.0)
        """
        self.confidence_threshold = max(0.0, min(1.0, threshold))
    
    def _prepare_image_for_model(self, face_image: np.ndarray, 
                               expand_dims: bool = True) -> Optional[np.ndarray]:
        """
        Preparar imagen facial para el modelo.
        
        Args:
            face_image: Imagen facial
            expand_dims: Si agregar dimensión de batch
            
        Returns:
            Imagen procesada o None si hay error
        """
        try:
            if self.input_shape is None:
                return None
            
            # Obtener dimensiones objetivo del modelo
            target_height = self.input_shape[1]
            target_width = self.input_shape[2]
            target_channels = self.input_shape[3] if len(self.input_shape) > 3 else 1
            
            # Redimensionar imagen
            import cv2
            resized_image = cv2.resize(face_image, (target_width, target_height))
            
            # Manejar canales de color
            if target_channels == 1:
                # Modelo espera escala de grises
                if len(resized_image.shape) == 3:
                    resized_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
                resized_image = np.expand_dims(resized_image, axis=-1)
            elif target_channels == 3:
                # Modelo espera RGB
                if len(resized_image.shape) == 2:
                    resized_image = cv2.cvtColor(resized_image, cv2.COLOR_GRAY2RGB)
                elif len(resized_image.shape) == 3 and resized_image.shape[2] == 3:
                    resized_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
            
            # Normalizar valores de píxeles
            normalized_image = resized_image.astype(np.float32) / 255.0
            
            # Agregar dimensión de batch si es necesario
            if expand_dims:
                normalized_image = np.expand_dims(normalized_image, axis=0)
            
            return normalized_image
            
        except Exception as e:
            print(f"[MODEL ERROR] Error preparando imagen: {str(e)}")
            return None
    
    def _process_predictions(self, predictions: np.ndarray) -> Optional[Dict]:
        """
        Procesar predicciones del modelo.
        
        Args:
            predictions: Array de predicciones
            
        Returns:
            Diccionario con resultado procesado o None
        """
        try:
            # Encontrar clase con mayor probabilidad
            predicted_class = np.argmax(predictions)
            confidence = float(predictions[predicted_class])
            
            # Verificar umbral de confianza
            if confidence < self.confidence_threshold:
                return None
            
            # Obtener etiqueta de emoción
            if (self.emotion_labels and 
                0 <= predicted_class < len(self.emotion_labels)):
                emotion_label = self.emotion_labels[predicted_class]
            else:
                emotion_label = f"Clase_{predicted_class}"
            
            # Crear distribución de probabilidades
            probabilities = {
                self.emotion_labels[i]: float(predictions[i]) 
                for i in range(len(self.emotion_labels))
                if self.emotion_labels and i < len(self.emotion_labels)
            }
            
            return {
                'emotion': emotion_label,
                'confidence': confidence,
                'class_index': int(predicted_class),
                'probabilities': probabilities,
                'timestamp': time.time()
            }
            
        except Exception as e:
            print(f"[MODEL ERROR] Error procesando predicciones: {str(e)}")
            return None


class ModelManager:
    """Gestor de múltiples modelos de detección de emociones."""
    
    def __init__(self, models_directory: str = None):
        """
        Inicializar gestor de modelos.
        
        Args:
            models_directory: Directorio donde buscar modelos
        """
        self.models_dir = Path(models_directory or AppConfig.get_models_dir())
        self.available_models = []
        self.current_model = EmotionModel()
        
        # Escanear modelos disponibles
        self.scan_available_models()
    
    def scan_available_models(self) -> List[str]:
        """
        Escanear modelos disponibles en el directorio.
        
        Returns:
            Lista de archivos de modelos encontrados
        """
        self.available_models = []
        
        if not self.models_dir.exists():
            print(f"[MODELS] Directorio de modelos no existe: {self.models_dir}")
            return []
        
        # Extensiones válidas para modelos
        valid_extensions = ['.h5', '.keras', '.pb']
        
        for file_path in self.models_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in valid_extensions:
                self.available_models.append(file_path.name)
        
        print(f"[MODELS] Encontrados {len(self.available_models)} modelos: {self.available_models}")
        return self.available_models
    
    def load_model(self, model_name: str) -> bool:
        """
        Cargar un modelo específico.
        
        Args:
            model_name: Nombre del archivo del modelo
            
        Returns:
            True si se cargó correctamente
        """
        model_path = self.models_dir / model_name
        return self.current_model.load_model(str(model_path))
    
    def get_available_models(self) -> List[str]:
        """
        Obtener lista de modelos disponibles.
        
        Returns:
            Lista de nombres de archivos de modelos
        """
        return self.available_models.copy()
    
    def get_current_model(self) -> EmotionModel:
        """
        Obtener modelo actualmente cargado.
        
        Returns:
            Instancia del modelo actual
        """
        return self.current_model
    
    def is_model_loaded(self) -> bool:
        """
        Verificar si hay un modelo cargado.
        
        Returns:
            True si hay un modelo cargado y listo
        """
        return self.current_model.is_loaded