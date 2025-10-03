#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 DETECTOR DE EMOCIONES - Paquete Principal
Aplicación modular para detección de emociones en tiempo real
"""

__version__ = "2.0.0"
__author__ = "Emotion Detection Team"
__description__ = "Aplicación GUI moderna para detección de emociones"

from .config import (
    AppConfig,
    Colors,
    Fonts,
    Spacing,
    EmotionConfig,
    UIStyles
)

__all__ = [
    'AppConfig',
    'Colors', 
    'Fonts',
    'Spacing',
    'EmotionConfig',
    'UIStyles'
]