import os
from typing import List, Tuple

import cv2
import numpy as np

# Lazy import tensorflow/keras to allow opening the GUI without models
_tf = None
_keras = None


def _ensure_tf():
    global _tf, _keras
    if _tf is None or _keras is None:
        import tensorflow as tf  # type: ignore
        from tensorflow import keras  # type: ignore
        _tf = tf
        _keras = keras
    return _tf, _keras


def list_models(models_dir: str) -> List[str]:
    if not os.path.isdir(models_dir):
        return []
    paths = []
    for name in os.listdir(models_dir):
        if name.lower().endswith('.h5'):
            paths.append(os.path.join(models_dir, name))
    paths.sort()
    return paths


def load_emotion_model(path: str):
    tf, keras = _ensure_tf()
    model = keras.models.load_model(path)
    # Deduce input shape (batch, h, w, c)
    input_shape = None
    try:
        ish = model.input_shape
        if isinstance(ish, list):
            ish = ish[0]
        # Normalize shape like (None, H, W, C)
        if len(ish) == 4:
            input_shape = ish
        else:
            raise ValueError(f"Forma de entrada inesperada: {ish}")
    except Exception as e:
        raise RuntimeError(f"No se pudo obtener input_shape del modelo: {e}")

    # Deduce number of classes from last layer output
    try:
        out_shape = model.output_shape
        if isinstance(out_shape, list):
            out_shape = out_shape[0]
        num_classes = out_shape[-1]
        if not isinstance(num_classes, int):
            num_classes = int(num_classes)
    except Exception as e:
        raise RuntimeError(f"No se pudo obtener el número de clases: {e}")

    return model, input_shape, num_classes


def prepare_frame_for_model(frame_bgr: np.ndarray, input_shape: Tuple[int, int, int, int]) -> np.ndarray:
    # Expect input_shape like (None, H, W, C) or (batch, H, W, C)
    if len(input_shape) != 4:
        raise ValueError(f"input_shape inesperado: {input_shape}")
    _, H, W, C = input_shape
    if C not in (1, 3):
        raise ValueError(f"Canales no soportados: {C}")

    img = frame_bgr
    if C == 1:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
        img = img.astype('float32') / 255.0
        img = np.expand_dims(img, axis=-1)
    else:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
        img = img.astype('float32') / 255.0

    batch = np.expand_dims(img, axis=0)
    return batch


def predict_emotion(model, batch: np.ndarray):
    # Returns (label_idx, confidence, prob_vec)
    preds = model.predict(batch, verbose=0)
    if preds.ndim == 2:
        prob = preds[0]
    else:
        prob = preds.ravel()
    idx = int(np.argmax(prob))
    conf = float(prob[idx])
    return idx, conf, prob


def get_label_set_for_classes(num_classes: int) -> List[str]:
    """
    Get emotion labels based on the number of classes.
    
    Base emotions from FER2013 dataset (5 classes):
    - angry (enfado)
    - disgust (asco) 
    - fear (miedo)
    - happy (feliz)
    - sad (triste)
    
    Additional emotions for extended models:
    - neutral
    - surprise (sorpresa)
    - other (otro)
    """
    # FER2013 dataset emotions (5 classes):
    fer5 = ["enfado", "asco", "miedo", "feliz", "triste"]
    
    if num_classes == 5:
        return fer5
    elif num_classes == 6:
        # If 6 classes, add neutral
        return fer5 + ["neutral"]
    elif num_classes == 7:
        # If 7 classes, add neutral and surprise
        return fer5 + ["neutral", "sorpresa"]
    elif num_classes == 8:
        # If 8 classes, add neutral, surprise and other
        return fer5 + ["neutral", "sorpresa", "otro"]
    else:
        # Fallback for any other number of classes
        return [f"clase_{i}" for i in range(num_classes)]
