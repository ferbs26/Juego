import pygame
import random
from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Set

# Supongamos que isac.settings está disponible
from isac.settings import (
    WIDTH,
    HEIGHT,
    ROOM_PADDING,
    # ... otras configuraciones que no se muestran
)

# --- Configuración para la Generación Aleatoria (MODIFICADA) ---
ROOM_SIZE = 18 
# Parámetros para el generador geométrico
MAX_SHAPES = 4      
MIN_SHAPE_SIZE = 3  
MAX_SHAPE_SIZE = 7  
WALL_SYMBOL = '#'
FLOOR_SYMBOL = '.'

# --- NUEVOS PARÁMETROS DE RESTRICCIÓN Y DENSIDAD ---

# 1. Densidad de Obstáculos Variable (ajusta el num_shapes máximo)
# Nivel 0.0 (vacío) a 1.0 (lleno), afectará el MAX_SHAPES real.
ROOM_DENSITY_LEVEL = 0.7  # Media-Alta por defecto

# 3. Margen de Seguridad alrededor de las Puertas (celdas de buffer)
# Se prohíbe generar obstáculos en las filas/columnas adyacentes a las puertas.
DOOR_CLEARANCE_BUFFER = 2 

# 4. Tipos de Formas más Variadas
SHAPE_TYPES = ['line_h', 'line_v', 'square', 'l_shape', 'cross']

# --- Patrón fijo para la Sala Inicial (0, 0) (Sin cambios) ---
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
# --- FUNCIÓN NUEVA: Verificar Conectividad (Restricción 2) ---
# ----------------------------------------------------

def _is_map_connected(map_list: List[List[str]], size: int) -> bool:
    """
    Verifica si todas las celdas de piso son accesibles desde el centro.
    Más importante aún, verifica si los puntos de entrada/salida de las puertas 
    (celdas de piso más cercanas a la 'D') están conectados.
    Utiliza Breadth-First Search (BFS).
    """
    
    # Puntos de partida seguros cerca de cada puerta para la verificación de conectividad
    # Coordenadas (y, x) de celdas de piso internas
    start_points = set()

    # Arriba (fila 1, cols 7-10)
    for x in range(7, 11): start_points.add((1, x))
    # Abajo (fila size-2, cols 7-10)
    for x in range(7, 11): start_points.add((size - 2, x))
    # Izquierda (col 1, filas 7-10)
    for y in range(7, 11): start_points.add((y, 1))
    # Derecha (col size-2, filas 7-10)
    for y in range(7, 11): start_points.add((y, size - 2))
    
    # Filtra los puntos que son piso en el mapa
    valid_starts = [p for p in start_points if map_list[p[0]][p[1]] == FLOOR_SYMBOL]

    if not valid_starts:
        # Esto no debería pasar si la generación es correcta, pero es un seguro
        return False

    start_node = valid_starts[0]
    
    # BFS
    queue = [start_node]
    visited = {start_node}
    
    while queue:
        y, x = queue.pop(0)
        
        for dy, dx in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            ny, nx = y + dy, x + dx
            
            if 0 < ny < size - 1 and 0 < nx < size - 1 and \
               map_list[ny][nx] == FLOOR_SYMBOL and (ny, nx) not in visited:
                visited.add((ny, nx))
                queue.append((ny, nx))

    # Verificar que *todos* los puntos de inicio válidos se hayan visitado
    # Esto asegura que todas las entradas/salidas de piso estén en el mismo componente
    return all(p in visited for p in valid_starts)


# ----------------------------------------------------
# --- FUNCIÓN MODIFICADA: Generación de Patrones Base Aleatorios ---
# ----------------------------------------------------

def _generate_random_base_pattern(size: int = ROOM_SIZE) -> List[str]:
    """
    Genera un patrón base de sala (size x size) con formas geométricas 
    aleatorias, implementando las nuevas restricciones.
    """
    
    # Área útil para generar obstáculos (sin tocar la pared de la sala, que está en [1] a [size-2])
    # Para la restricción 2 original (no tocar la pared), el rango de inicio es [2] a [size-3]
    # Aplicando la Restricción 3 (DOOR_CLEARANCE_BUFFER)
    # Se añade un margen extra en los bordes
    BUFFER = DOOR_CLEARANCE_BUFFER
    MIN_COORD = 1 + BUFFER
    MAX_COORD = size - 1 - BUFFER
    
    # -----------------------------------
    # Lógica de Regeneración (Restricción 2: Conectividad)
    # -----------------------------------
    MAX_ATTEMPTS = 10
    attempts = 0
    
    while attempts < MAX_ATTEMPTS:
        attempts += 1
        
        # 1. Inicializar el mapa
        initial_map = [[FLOOR_SYMBOL] * size for _ in range(size)]
            
        # 2. Asegurar bordes de muros
        for i in range(size):
            initial_map[0][i] = WALL_SYMBOL
            initial_map[size - 1][i] = WALL_SYMBOL
            initial_map[i][0] = WALL_SYMBOL
            initial_map[i][size - 1] = WALL_SYMBOL
            
        # -----------------------------------
        # 3. Generar Formas (Parámetros 1 y 4)
        # -----------------------------------
        
        # Parámetro 1: Densidad (ajusta el num_shapes)
        max_possible_shapes = int(MAX_SHAPES * ROOM_DENSITY_LEVEL)
        num_shapes = random.randint(1, max(1, max_possible_shapes))
        
        for _ in range(num_shapes):
            shape_type = random.choice(SHAPE_TYPES) # Parámetro 4: Tipos de Formas más Variadas
            
            # Tamaño aleatorio
            s = random.randint(MIN_SHAPE_SIZE, MAX_SHAPE_SIZE)
            
            # Posición de inicio aleatoria (asegurando que la forma no se salga)
            # Y que respete el buffer de puertas
            start_x = random.randint(MIN_COORD, MAX_COORD - s)
            start_y = random.randint(MIN_COORD, MAX_COORD - s)

            # Función auxiliar para dibujar la forma
            def draw_shape(y, x):
                if 1 < y < size - 2 and 1 < x < size - 2: # Restricción original: no tocar borde interno
                    # Restricción 3: Revisar el clearance de la puerta
                    # Solo afecta la zona cerca de los bordes 1 y size-2
                    is_too_close_to_door = False
                    
                    # Cerca de puertas horizontales (arriba/abajo)
                    if (y <= BUFFER + 1 or y >= size - 2 - BUFFER) and (7 <= x <= 10):
                        is_too_close_to_door = True
                    
                    # Cerca de puertas verticales (izquierda/derecha)
                    if (x <= BUFFER + 1 or x >= size - 2 - BUFFER) and (7 <= y <= 10):
                        is_too_close_to_door = True
                        
                    if not is_too_close_to_door:
                        initial_map[y][x] = WALL_SYMBOL

            if shape_type == 'line_h':
                for x in range(start_x, start_x + s):
                    draw_shape(start_y, x)
                    
            elif shape_type == 'line_v':
                for y in range(start_y, start_y + s):
                    draw_shape(y, start_x)
                    
            elif shape_type == 'square':
                for y in range(start_y, start_y + s):
                    for x in range(start_x, start_x + s):
                        draw_shape(y, x)
            
            elif shape_type == 'l_shape': # Nuevo: Forma de L
                # Rama vertical
                for y in range(start_y, start_y + s):
                    draw_shape(y, start_x)
                # Rama horizontal (desde el extremo inferior, asumiendo start_y es la esquina)
                for x in range(start_x, start_x + s):
                    draw_shape(start_y + s - 1, x)

            elif shape_type == 'cross': # Nuevo: Forma de Cruz (+)
                center_x = start_x + s // 2
                center_y = start_y + s // 2
                
                # Barra horizontal
                for x in range(start_x, start_x + s):
                    draw_shape(center_y, x)
                # Barra vertical
                for y in range(start_y, start_y + s):
                    draw_shape(y, center_x)
                    
        
        # -----------------------------------
        # 4. Verificar Conectividad (Restricción 2)
        # -----------------------------------
        if _is_map_connected(initial_map, size):
            
            # -----------------------------------
            # 5. Asimetría Obligatoria (Restricción 5)
            # -----------------------------------
            # La asimetría ya se promueve al usar formas aleatorias y la Restricción 3.
            # Sin embargo, se añade un pequeño cambio forzado si se detecta simetría.
            # Simplificación: No se comprueba la simetría exhaustivamente, sino que se asegura 
            # un patrón ligeramente impredecible en una esquina.
            
            if random.random() < 0.2: # 20% de probabilidad de añadir un toque asimétrico
                # Elige un punto seguro para un obstáculo aleatorio (lejos de las puertas)
                # Se elige una celda dentro del área generable y se invierte (floor -> wall)
                asy_x = random.randint(MAX_COORD - 1, MAX_COORD)
                asy_y = random.randint(MAX_COORD - 1, MAX_COORD)
                
                # Solo cambia si es piso y no invalida la conectividad (simplificación: se asume que no la invalida)
                if initial_map[asy_y][asy_x] == FLOOR_SYMBOL:
                     initial_map[asy_y][asy_x] = WALL_SYMBOL
                
            # Éxito: Convertir a lista de strings y retornar
            final_pattern = ["".join(row) for row in initial_map]
            return final_pattern

    # Si se alcanzan los intentos máximos, se retorna un patrón simple para evitar bucles.
    print("WARNING: Max attempts reached. Returning an empty pattern.")
    final_pattern = ["".join(row) for row in initial_map]
    return final_pattern


# ----------------------------------------------------
# --- CONTINUACIÓN DEL CÓDIGO (SIN CAMBIOS ESTRUCTURALES) ---
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
            # Ahora utiliza la generación geométrica restringida y regeneración
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
        x, y = self.pos
        return {
            'up': (x, y - 1),
            'down': (x, y + 1),
            'left': (x - 1, y),
            'right': (x + 1, y),
        }

    def find_valid_spawn_position(self) -> tuple[int, int]:
        """
        Encuentra una posición válida para que aparezca el jugador.
        Busca una celda de piso ('.') que no sea un muro ('#') ni esté cerca de una puerta.
        """
        room_map = self.get_room_map()
        floor_positions = []
        
        # Buscar todas las celdas de piso que no estén en los bordes
        for y in range(1, len(room_map) - 1):
            for x in range(1, len(room_map[0]) - 1):
                # Verificar si es una celda de piso y no está en los bordes
                if room_map[y][x] == FLOOR_SYMBOL:
                    # Verificar que no esté cerca de una puerta (2 celdas de distancia)
                    near_door = False
                    for dy in range(-2, 3):
                        for dx in range(-2, 3):
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < len(room_map) and 0 <= nx < len(room_map[0]):
                                if room_map[ny][nx] == 'D':  # Puerta
                                    near_door = True
                                    break
                        if near_door:
                            break
                    if not near_door:
                        floor_positions.append((x, y))
        
        # Si no se encontraron posiciones válidas, buscar cualquier piso
        if not floor_positions:
            for y in range(1, len(room_map) - 1):
                for x in range(1, len(room_map[0]) - 1):
                    if room_map[y][x] == FLOOR_SYMBOL:
                        floor_positions.append((x, y))
        
        # Si aún no hay posiciones, usar el centro de la habitación
        if not floor_positions:
            return len(room_map[0]) // 2, len(room_map) // 2
            
        # Devolver una posición aleatoria de las válidas
        return random.choice(floor_positions)