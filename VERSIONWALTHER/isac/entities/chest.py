import os
import pygame
import random
import math
from isac.settings import TILE

class Chest:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.opened = False
        self.item_dropped = None
        
        # Cargar sprites
        self.closed_sprite = pygame.image.load(os.path.join('assets', 'structure', 'cofre2.png'))
        self.open_sprite = pygame.image.load(os.path.join('assets', 'structure', 'cofre2b.png'))
        
        # Escalar los sprites al tamaño del tile
        self.closed_sprite = pygame.transform.scale(self.closed_sprite, (TILE, TILE))
        self.open_sprite = pygame.transform.scale(self.open_sprite, (TILE, TILE))
        
        # Animación de apertura
        self.opening_timer = 0.0
        self.opening_duration = 0.5
        
    def can_be_opened(self, inventory) -> bool:
        """Verifica si el jugador tiene una llave para abrir el cofre"""
        return inventory.keys > 0
        
    def open(self, inventory) -> str:
        """Intenta abrir el cofre y devuelve el tipo de item que contiene si se pudo abrir"""
        if self.opened:
            return None
            
        # Verificar si el jugador tiene una llave
        if not self.can_be_opened(inventory):
            return None
            
        # Usar una llave
        inventory.use_key()
        self.opened = True
        self.opening_timer = self.opening_duration
        
        # Seleccionar item aleatorio con probabilidades ajustadas
        # 25% de probabilidad para cada uno de los 4 objetos
        rand_num = random.random()
        if rand_num < 0.25:
            self.item_dropped = 'speed_boots'
        elif rand_num < 0.50:
            self.item_dropped = 'companion'
        elif rand_num < 0.75:
            self.item_dropped = 'health_doubler'
        else:
            self.item_dropped = 'infinite_shot'
        return self.item_dropped
    
    def update(self, dt: float):
        """Actualiza la animación de apertura"""
        if self.opening_timer > 0:
            self.opening_timer = max(0.0, self.opening_timer - dt)
    
    def draw(self, surface: pygame.Surface):
        """Dibuja el cofre con el sprite correspondiente"""
        if self.opening_timer > 0 or self.opened:
            # Mostrar sprite de cofre abierto si se está abriendo o ya está abierto
            surface.blit(self.open_sprite, self.rect)
        else:
            # Mostrar sprite de cofre cerrado
            surface.blit(self.closed_sprite, self.rect)
        
        # Efecto de brillo cuando se abre
        if self.opening_timer > 0:
            alpha = int(255 * (self.opening_timer / self.opening_duration))
            glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
            glow_color = (255, 255, 0, max(0, alpha // 2))
            pygame.draw.rect(glow_surface, glow_color, 
                           (10, 10, self.rect.width, self.rect.height), border_radius=5)
            surface.blit(glow_surface, (self.rect.x - 10, self.rect.y - 10))
