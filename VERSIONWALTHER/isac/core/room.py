import pygame
import random
from dataclasses import dataclass, field
from typing import Dict, Tuple, List

# Supongamos que isac.settings está disponible
from isac.settings import (
    WIDTH,
    HEIGHT,
    ROOM_PADDING,
    # ... otras configuraciones que no se muestran
)

# --- Configuración para la Generación Aleatoria ---
ROOM_SIZE = 18 # Asumimos 18x18 basado en los patrones originales
# Parámetros para el generador geométrico
MAX_SHAPES = 4      # Número máximo de formas a generar por sala
MIN_SHAPE_SIZE = 3  # Tamaño mínimo de un lado de la forma (cuadrado/línea)
MAX_SHAPE_SIZE = 7  # Tamaño máximo de un lado de la forma
WALL_SYMBOL = '#'
FLOOR_SYMBOL = '.'
# No necesitamos INITIAL_WALL_DENSITY, WALK_STEPS o WALK_LENGTH
# porque ya no se usa el algoritmo de caminata aleatoria.


# --- Patrón fijo para la Sala Inicial (0, 0) ---
PATTERN_EMPTY = [
    "##################",
    "#................#",
    "#................#",
    "#................#",
    "#................#",
    "#................#",
    "#................#",
    "#................#",
    "#................#",
    "#................#",
    "#................#",
    "#................#",
    "#................#",
    "#................#",
    "#................#",
    "#................#",
    "#................#",
    "##################"
]

# ----------------------------------------------------
# --- FUNCIÓN MODIFICADA: Generación de Patrones Base Aleatorios con Restricciones ---
# ----------------------------------------------------

def _generate_random_base_pattern(size: int = ROOM_SIZE) -> List[str]:
    """
    Genera un patrón base de sala (size x size) con formas geométricas 
    aleatorias que nunca tocan el borde exterior (restricción 2).
    """
    
    # 1. Inicializar el mapa completamente vacío (piso)
    initial_map = [[FLOOR_SYMBOL] * size for _ in range(size)]
        
    # 2. Asegurar bordes de muros (fila 0, fila size-1, col 0, col size-1)
    # Estos muros SÍ tocarán el borde de la matriz, pero los obstáculos internos no.
    for i in range(size):
        initial_map[0][i] = WALL_SYMBOL
        initial_map[size - 1][i] = WALL_SYMBOL
        initial_map[i][0] = WALL_SYMBOL
        initial_map[i][size - 1] = WALL_SYMBOL
        
    # 3. Generar Líneas o Formas Geométricas (restricción 1)
    
    # Área útil para generar obstáculos (sin tocar la pared de la sala, que está en [1] a [size-2])
    # Para la restricción 2 (no tocar la pared), generamos en el rango [2] a [size-3]
    MIN_COORD = 2
    MAX_COORD = size - 3
    
    num_shapes = random.randint(1, MAX_SHAPES)
    
    for _ in range(num_shapes):
        shape_type = random.choice(['line_h', 'line_v', 'square'])
        
        # Tamaño aleatorio
        s = random.randint(MIN_SHAPE_SIZE, MAX_SHAPE_SIZE)
        
        # Posición de inicio aleatoria (asegurando que la forma no se salga)
        start_x = random.randint(MIN_COORD, MAX_COORD - s)
        start_y = random.randint(MIN_COORD, MAX_COORD - s)

        if shape_type == 'line_h':
            # Línea Horizontal
            for x in range(start_x, start_x + s):
                initial_map[start_y][x] = WALL_SYMBOL
                
        elif shape_type == 'line_v':
            # Línea Vertical
            for y in range(start_y, start_y + s):
                initial_map[y][start_x] = WALL_SYMBOL
                
        elif shape_type == 'square':
            # Cuadrado o Rectángulo (usamos el mismo tamaño para que sea cuadrado)
            for y in range(start_y, start_y + s):
                for x in range(start_x, start_x + s):
                    # Opcional: solo dibujar el contorno
                    # if x == start_x or x == start_x + s - 1 or y == start_y or y == start_y + s - 1:
                    initial_map[y][x] = WALL_SYMBOL


    # 4. Convertir el mapa de lista de listas a lista de strings
    final_pattern = ["".join(row) for row in initial_map]
    
    return final_pattern

# ----------------------------------------------------
# --- FIN FUNCIÓN DE GENERACIÓN GEOMÉTRICA ---
# ----------------------------------------------------


# --- Función Auxiliar para insertar puertas (sin cambios) ---

def _insert_doors(pattern: List[str], pos: Tuple[int, int]) -> List[str]:
    """Modifica el patrón base para insertar las aperturas de puerta 'D'."""
    gx, gy = pos
    modified_pattern = list(pattern)
    map_size = len(modified_pattern) # Debería ser 18

    # Puerta ARRIBA (up): gy - 1, fila 0 (4 caracteres centrales)
    row_up = modified_pattern[0]
    modified_pattern[0] = row_up[:7] + "DDDD" + row_up[11:]
        
    # Puerta ABAJO (down): gy + 1, fila 17 (4 caracteres centrales)
    row_down = modified_pattern[map_size - 1]
    modified_pattern[map_size - 1] = row_down[:7] + "DDDD" + row_down[11:]

    # Puerta IZQUIERDA (left): gx - 1, filas 7 a 10 (primer caracter)
    for i in range(7, 11): 
        row_left = modified_pattern[i]
        modified_pattern[i] = "D" + row_left[1:]

    # Puerta DERECHA (right): gx + 1, filas 7 a 10 (último caracter)
    for i in range(7, 11): 
        row_right = modified_pattern[i]
        modified_pattern[i] = row_right[:-1] + "D"

    return modified_pattern

# --- Clase Door y Room (Sin Cambios en su estructura principal) ---

@dataclass
class Door:
    open: bool = False
    locked: bool = False


@dataclass
class Room:
    pos: Tuple[int, int]  # (gx, gy)
    doors: Dict[str, Door] = field(default_factory=lambda: {
        'up': Door(open=False, locked=False),
        'down': Door(open=False, locked=False),
        'left': Door(open=False, locked=False),
        'right': Door(open=False, locked=False),
    })
    cleared: bool = False
    spawned: bool = False
    enemies: list = field(default_factory=list)  # Persistir enemigos por sala
    chests: list = field(default_factory=list)  # Persistir cofres por sala
    _room_pattern: List[str] = field(init=False, default=None)

    def __post_init__(self):
        self._room_pattern = self._generate_random_room_pattern()


    def walls(self) -> List[pygame.Rect]:
        p = ROOM_PADDING
        return [
            pygame.Rect(p, p, WIDTH - 2 * p, 10),  # top
            pygame.Rect(p, HEIGHT - p - 10, WIDTH - 2 * p, 10),  # bottom
            pygame.Rect(p, p, 10, HEIGHT - 2 * p),  # left
            pygame.Rect(WIDTH - p - 10, p, 10, HEIGHT - 2 * p),  # right
        ]


    def _generate_random_room_pattern(self) -> List[str]:
        """Selecciona un patrón: fijo (0,0) o aleatorio (otros) y le inserta las puertas."""
        
        if self.pos == (0, 0):
            base_pattern = PATTERN_EMPTY
        else:
            # Ahora utiliza la generación geométrica restringida
            base_pattern = _generate_random_base_pattern(ROOM_SIZE)
            
        final_pattern = _insert_doors(base_pattern, self.pos)
        
        return final_pattern


    def get_room_map(self) -> List[str]:
        return self._room_pattern

    def obstacles(self) -> List[pygame.Rect]:
        """Genera obstáculos basados en el mapa de caracteres de la sala."""
        room_map = self.get_room_map()
        obstacles = []
        
        map_height = len(room_map)
        map_width = len(room_map[0]) if room_map else 0
        
        if map_width == 0 or map_height == 0:
            return obstacles
        
        p = ROOM_PADDING
        usable_width = WIDTH - 2 * p - 20
        usable_height = HEIGHT - 2 * p - 20
        
        cell_width = usable_width // map_width
        cell_height = usable_height // map_height
        
        offset_x = p + 10 + (usable_width - (cell_width * map_width)) // 2
        offset_y = p + 10 + (usable_height - (cell_height * map_height)) // 2
        
        for row_idx, row in enumerate(room_map):
            for col_idx, cell in enumerate(row):
                if cell == WALL_SYMBOL:
                    x = offset_x + col_idx * cell_width
                    y = offset_y + row_idx * cell_height
                    obstacle_rect = pygame.Rect(x, y, cell_width, cell_height)
                    obstacles.append(obstacle_rect)
        
        return obstacles

    def door_rect(self, direction: str) -> pygame.Rect:
        p = ROOM_PADDING
        w = 60
        h = 20
        if direction == 'up':
            return pygame.Rect(WIDTH // 2 - w // 2, p - 5, w, h)
        if direction == 'down':
            return pygame.Rect(WIDTH // 2 - w // 2, HEIGHT - p - h + 5, w, h)
        if direction == 'left':
            return pygame.Rect(p - 5, HEIGHT // 2 - w // 2, h, w)
        if direction == 'right':
            return pygame.Rect(WIDTH - p - h + 5, HEIGHT // 2 - w // 2, h, w)
        return pygame.Rect(0, 0, 0, 0)

    def neighbors(self) -> Dict[str, Tuple[int, int]]:
        gx, gy = self.pos
        return {
            'up': (gx, gy - 1),
            'down': (gx, gy + 1),
            'left': (gx - 1, gy),
            'right': (gx + 1, gy),
        }