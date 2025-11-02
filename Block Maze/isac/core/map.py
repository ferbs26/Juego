import pygame
from typing import Dict, Tuple

class MapViewer:
    def __init__(self, dungeon, cell_size=20, margin=5):
        self.dungeon = dungeon
        self.cell_size = cell_size
        self.margin = margin
        self.visible = False
        self.surface = None
        self.rect = None
        
    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self._update_surface()
    
    def _update_surface(self):
        rooms = self.dungeon.rooms
        current = self.dungeon.current
        
        if not rooms:
            return
            
        # Calcular límites del mapa
        min_x = min(x for x, y in rooms)
        max_x = max(x for x, y in rooms)
        min_y = min(y for x, y in rooms)
        max_y = max(y for x, y in rooms)
        
        # Tamaño del mapa
        width = (max_x - min_x + 1) * (self.cell_size + self.margin) + self.margin
        height = (max_y - min_y + 1) * (self.cell_size + self.margin) + self.margin
        
        # Crear superficie con transparencia
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.surface.fill((40, 40, 40, 200))  # Fondo gris oscuro semitransparente
        
        # Dibujar habitaciones
        for (gx, gy), room in rooms.items():
            # Calcular posición en pantalla
            x = (gx - min_x) * (self.cell_size + self.margin) + self.margin
            y = (gy - min_y) * (self.cell_size + self.margin) + self.margin
            
            # Color según si es la habitación actual o adyacente
            if (gx, gy) == current:
                color = (255, 255, 255)  # Blanco para habitación actual
            else:
                # Verificar si es adyacente a la habitación actual
                is_adjacent = any(
                    (gx + dx, gy + dy) == current
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                )
                color = (150, 150, 150) if is_adjacent else (80, 80, 80)
            
            # Dibujar habitación
            pygame.draw.rect(
                self.surface, 
                color, 
                (x, y, self.cell_size, self.cell_size)
            )
        
        # Posicionar en la esquina superior derecha
        screen = pygame.display.get_surface()
        if screen:
            self.rect = self.surface.get_rect(
                top=20,
                right=screen.get_width() - 20
            )
    
    def draw(self, surface):
        if self.visible and self.surface and self.rect:
            surface.blit(self.surface, self.rect)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            self.toggle()
            return True
        return False
