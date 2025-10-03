#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 COMPONENTES UI MODERNOS
Widgets personalizados para la interfaz de usuario
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from ..config import Colors, Fonts, Spacing, UIStyles

class RoundedButton(tk.Canvas):
    """Botón redondeado moderno con efectos hover."""
    
    def __init__(self, parent, text='', command=None, style='primary', 
                 font=Fonts.BODY, padx=16, pady=10, radius=20, **kwargs):
        """
        Inicializar botón redondeado.
        
        Args:
            parent: Widget padre
            text: Texto del botón
            command: Función a ejecutar al hacer clic
            style: Estilo del botón ('primary', 'secondary', 'success', 'danger', 'warning')
            font: Fuente del texto
            padx, pady: Padding interno
            radius: Radio de las esquinas redondeadas
        """
        # Calcular dimensiones
        temp_font = tkfont.Font(family=font[0], size=font[1], weight=font[2])
        text_width = temp_font.measure(text)
        text_height = temp_font.metrics("linespace")
        
        width = text_width + (2 * padx)
        height = text_height + (2 * pady)
        
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, **kwargs)
        
        self.text = text
        self.command = command
        self.font = font
        self.padx = padx
        self.pady = pady
        self.radius = radius
        self.style = style
        
        # Obtener colores del estilo
        style_config = UIStyles.BUTTON_STYLES.get(style, UIStyles.BUTTON_STYLES['primary'])
        self.bg_color = style_config['bg']
        self.hover_color = style_config['hover']
        self.text_color = style_config['text']
        
        # Estado del botón
        self.is_hovered = False
        self.is_pressed = False
        
        # Configurar eventos
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Configure>", self._on_resize)
        
        # Dibujar botón inicial
        self._draw_button(self.bg_color)
    
    def _draw_button(self, fill):
        """Dibujar el botón con el color especificado."""
        self.delete("all")
        
        width = self.winfo_width() or self.winfo_reqwidth()
        height = self.winfo_height() or self.winfo_reqheight()
        
        if width <= 0 or height <= 0:
            return
        
        # Dibujar rectángulo redondeado
        self._draw_rounded_rectangle(0, 0, width, height, self.radius, fill)
        
        # Dibujar texto
        self.create_text(width//2, height//2, text=self.text, 
                        fill=self.text_color, font=self.font, anchor="center")
    
    def _draw_rounded_rectangle(self, x1, y1, x2, y2, radius, fill):
        """Dibujar rectángulo con esquinas redondeadas."""
        points = []
        
        # Esquina superior izquierda
        points.extend([x1 + radius, y1])
        
        # Lado superior
        points.extend([x2 - radius, y1])
        
        # Esquina superior derecha
        for i in range(90, -1, -1):
            angle = i * 3.14159 / 180
            px = x2 - radius + radius * np.cos(angle)
            py = y1 + radius - radius * np.sin(angle)
            points.extend([px, py])
        
        # Lado derecho
        points.extend([x2, y2 - radius])
        
        # Esquina inferior derecha
        for i in range(0, 91):
            angle = i * 3.14159 / 180
            px = x2 - radius + radius * np.cos(angle)
            py = y2 - radius + radius * np.sin(angle)
            points.extend([px, py])
        
        # Lado inferior
        points.extend([x1 + radius, y2])
        
        # Esquina inferior izquierda
        for i in range(90, 181):
            angle = i * 3.14159 / 180
            px = x1 + radius + radius * np.cos(angle)
            py = y2 - radius + radius * np.sin(angle)
            points.extend([px, py])
        
        # Lado izquierdo
        points.extend([x1, y1 + radius])
        
        # Esquina superior izquierda
        for i in range(180, 271):
            angle = i * 3.14159 / 180
            px = x1 + radius + radius * np.cos(angle)
            py = y1 + radius + radius * np.sin(angle)
            points.extend([px, py])
        
        if len(points) >= 6:
            self.create_polygon(points, fill=fill, outline="")
    
    def _on_enter(self, event):
        """Manejar evento de entrada del mouse."""
        self.is_hovered = True
        self._draw_button(self.hover_color)
    
    def _on_leave(self, event):
        """Manejar evento de salida del mouse."""
        self.is_hovered = False
        self._draw_button(self.bg_color)
    
    def _on_click(self, event):
        """Manejar clic del botón."""
        if self.command:
            self.command()
    
    def _on_resize(self, event):
        """Manejar redimensionamiento."""
        color = self.hover_color if self.is_hovered else self.bg_color
        self._draw_button(color)


class ModernCard(tk.Canvas):
    """Tarjeta moderna con sombra y bordes redondeados."""
    
    def __init__(self, parent, title=None, radius=25, **kwargs):
        """
        Inicializar tarjeta moderna.
        
        Args:
            parent: Widget padre
            title: Título opcional de la tarjeta
            radius: Radio de las esquinas redondeadas
        """
        super().__init__(parent, highlightthickness=0, **kwargs)
        
        self.title = title
        self.radius = radius
        self.content_frame = None
        
        # Configurar eventos
        self.bind("<Configure>", self._on_resize)
        
        # Crear contenido
        self._setup_content()
    
    def _setup_content(self):
        """Configurar el contenido de la tarjeta."""
        # Crear frame interno para contenido
        self.content_frame = tk.Frame(self, bg=Colors.CARD_BG)
        
        if self.title:
            # Agregar título
            title_label = tk.Label(self.content_frame, text=self.title,
                                 font=Fonts.HEADER, bg=Colors.CARD_BG,
                                 fg=Colors.TEXT_DARK)
            title_label.pack(anchor="nw", padx=Spacing.MEDIUM, 
                           pady=(Spacing.MEDIUM, Spacing.SMALL))
        
        self._draw_card()
    
    def _draw_card(self):
        """Dibujar la tarjeta con sombra."""
        self.delete("all")
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:
            self.after(10, self._draw_card)
            return
        
        # Dibujar sombra
        shadow_offset = 3
        self._draw_rounded_rectangle(
            shadow_offset, shadow_offset, 
            width + shadow_offset, height + shadow_offset,
            self.radius, Colors.SHADOW
        )
        
        # Dibujar tarjeta principal
        self._draw_rounded_rectangle(
            0, 0, width, height, 
            self.radius, Colors.CARD_BG
        )
        
        # Posicionar frame de contenido
        content_y = Spacing.MEDIUM if self.title else 0
        self.create_window(Spacing.MEDIUM, content_y, 
                          window=self.content_frame, anchor="nw")
    
    def _draw_rounded_rectangle(self, x1, y1, x2, y2, radius, fill):
        """Dibujar rectángulo con esquinas redondeadas."""
        # Implementación simplificada para el canvas
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, 
                            fill=fill, outline="")
        self.create_rectangle(x1, y1 + radius, x2, y2 - radius, 
                            fill=fill, outline="")
        
        # Esquinas redondeadas
        self.create_arc(x1, y1, x1 + 2*radius, y1 + 2*radius,
                       start=90, extent=90, fill=fill, outline="")
        self.create_arc(x2 - 2*radius, y1, x2, y1 + 2*radius,
                       start=0, extent=90, fill=fill, outline="")
        self.create_arc(x1, y2 - 2*radius, x1 + 2*radius, y2,
                       start=180, extent=90, fill=fill, outline="")
        self.create_arc(x2 - 2*radius, y2 - 2*radius, x2, y2,
                       start=270, extent=90, fill=fill, outline="")
    
    def _on_resize(self, event):
        """Manejar redimensionamiento de la tarjeta."""
        self._draw_card()


class StatusIndicator(tk.Frame):
    """Indicador de estado con color y texto."""
    
    def __init__(self, parent, **kwargs):
        """
        Inicializar indicador de estado.
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent, bg=Colors.CARD_BG, **kwargs)
        
        # Crear componentes
        self.indicator = tk.Canvas(self, width=12, height=12, 
                                 highlightthickness=0, bg=Colors.CARD_BG)
        self.indicator.pack(side="left", padx=(0, Spacing.SMALL))
        
        self.label = tk.Label(self, font=Fonts.CAPTION, bg=Colors.CARD_BG)
        self.label.pack(side="left", fill="x", expand=True)
        
        # Estado inicial
        self.set_status("Sin estado", 'neutral')
    
    def set_status(self, text, status='neutral'):
        """
        Establecer el estado del indicador.
        
        Args:
            text: Texto a mostrar
            status: Estado ('success', 'warning', 'danger', 'neutral')
        """
        # Mapear estados a colores
        status_colors = {
            'success': Colors.SUCCESS,
            'warning': Colors.WARNING,
            'danger': Colors.DANGER,
            'neutral': Colors.TEXT_LIGHT,
            'info': Colors.INFO
        }
        
        color = status_colors.get(status, Colors.TEXT_LIGHT)
        
        # Actualizar indicador visual
        self.indicator.delete("all")
        self.indicator.create_oval(2, 2, 10, 10, fill=color, outline="")
        
        # Actualizar texto
        self.label.config(text=text, fg=Colors.TEXT_DARK)


class ProgressBar(tk.Frame):
    """Barra de progreso personalizada."""
    
    def __init__(self, parent, width=200, height=8, **kwargs):
        """
        Inicializar barra de progreso.
        
        Args:
            parent: Widget padre
            width: Ancho de la barra
            height: Alto de la barra
        """
        super().__init__(parent, **kwargs)
        
        self.canvas = tk.Canvas(self, width=width, height=height,
                              highlightthickness=0, bg=Colors.CARD_BG)
        self.canvas.pack()
        
        self.width = width
        self.height = height
        self.progress = 0.0  # Valor entre 0.0 y 1.0
        
        self._draw_progress()
    
    def set_progress(self, value):
        """
        Establecer el progreso de la barra.
        
        Args:
            value: Valor entre 0.0 y 1.0
        """
        self.progress = max(0.0, min(1.0, value))
        self._draw_progress()
    
    def _draw_progress(self):
        """Dibujar la barra de progreso."""
        self.canvas.delete("all")
        
        # Fondo de la barra
        self.canvas.create_rectangle(0, 0, self.width, self.height,
                                   fill=Colors.SECONDARY, outline="")
        
        # Progreso actual
        if self.progress > 0:
            progress_width = self.width * self.progress
            self.canvas.create_rectangle(0, 0, progress_width, self.height,
                                       fill=Colors.PRIMARY, outline="")


class ModernCombobox(ttk.Combobox):
    """Combobox con estilo moderno."""
    
    def __init__(self, parent, **kwargs):
        """Inicializar combobox moderno."""
        super().__init__(parent, font=Fonts.BODY, **kwargs)
        
        # Configurar estilo
        self.configure(state="readonly")


class ModernSpinbox(tk.Spinbox):
    """Spinbox con estilo moderno."""
    
    def __init__(self, parent, **kwargs):
        """Inicializar spinbox moderno."""
        defaults = {
            'font': Fonts.BODY,
            'bg': Colors.WHITE,
            'fg': Colors.TEXT_DARK,
            'buttonbackground': Colors.PRIMARY,
            'relief': 'flat',
            'bd': 1
        }
        defaults.update(kwargs)
        
        super().__init__(parent, **defaults)


# Importar numpy para los cálculos matemáticos
import numpy as np