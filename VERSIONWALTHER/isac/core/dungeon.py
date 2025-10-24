from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Tuple, Set, List
import random

from .room import Room, Door


@dataclass
class Door:
    open: bool = False
    locked: bool = False
    exists: bool = True  # Indica si la puerta existe (si hay una habitación del otro lado)


@dataclass
class Dungeon:
    rooms: Dict[Tuple[int, int], Room] = field(default_factory=dict)
    current: Tuple[int, int] = (0, 0)

    def __post_init__(self) -> None:
        if not self.rooms:
            # Generate a random connected dungeon if no rooms are provided
            self.generate_dungeon(size=5, num_rooms=10)
            # Set the starting room to the first room in the dictionary
            if self.rooms:
                self.current = next(iter(self.rooms))
                # Open all unlocked doors in the starting room
                self.open_all_unlocked_in_current()

    def _sync_doors(self) -> None:
        # Primero, actualizar el estado de las puertas basado en las habitaciones vecinas
        for (gx, gy), room in self.rooms.items():
            for direction in list(room.doors.keys()):
                nx, ny = room.neighbors()[direction]
                # Si no hay habitación vecina, marcar la puerta como inexistente
                if (nx, ny) not in self.rooms:
                    room.doors[direction].exists = False
                else:
                    room.doors[direction].exists = True
        
        # Luego, sincronizar el estado de las puertas entre habitaciones conectadas
        for (gx, gy), room in self.rooms.items():
            for d, door in room.doors.items():
                if not door.exists:
                    continue
                    
                nx, ny = room.neighbors()[d]
                if (nx, ny) in self.rooms:
                    back = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}[d]
                    other = self.rooms[(nx, ny)].doors[back]
                    # Sincronizar solo si la puerta existe en ambos lados
                    if other.exists:
                        other.open = door.open
                        other.locked = door.locked

    def get_room(self) -> Room:
        return self.rooms[self.current]

    def move_through(self, direction: str) -> bool:
        room = self.get_room()
        nx, ny = room.neighbors()[direction]
        if (nx, ny) not in self.rooms:
            return False
        door = room.doors[direction]
        if not door.open:
            return False
        self.current = (nx, ny)
        return True

    def unlock(self, direction: str) -> bool:
        room = self.get_room()
        door = room.doors[direction]
        if not door.locked:
            return True
        # Desbloquear y abrir
        door.locked = False
        door.open = True
        # Sincronizar contraparte
        self._sync_doors()
        return True

    # Helpers para manejar puertas de la sala actual
    def set_current_doors_open(self, open_bool: bool, only_unlocked: bool = True) -> None:
        room = self.get_room()
        for d, door in room.doors.items():
            if only_unlocked and door.locked:
                continue
            door.open = open_bool
            # sincronizar contraparte
            nx, ny = room.neighbors()[d]
            if (nx, ny) in self.rooms:
                back = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}[d]
                other = self.rooms[(nx, ny)].doors[back]
                other.open = open_bool if not other.locked else other.open

    def open_all_unlocked_in_current(self) -> None:
        self.set_current_doors_open(True, only_unlocked=True)

    def generate_dungeon(self, size: int, num_rooms: int) -> None:
        """
        Genera un mapa de cuartos aleatorio y conectado.
        
        Args:
            size: Tamaño del mapa (el área será de size x size)
            num_rooms: Número de habitaciones a generar
        """
        if num_rooms <= 0:
            return

        # Limpiar habitaciones existentes
        self.rooms.clear()
        
        # Limitar el número de cuartos al máximo posible
        max_rooms = size * size
        num_rooms = min(num_rooms, max_rooms)
        
        # Conjuntos para el algoritmo
        created_rooms: Set[Tuple[int, int]] = set()
        potential_rooms: Set[Tuple[int, int]] = set()
        
        # 1. Inicializar con una habitación aleatoria
        start_x = random.randint(-size//2, size//2)
        start_y = random.randint(-size//2, size//2)
        start_pos = (start_x, start_y)
        
        self.rooms[start_pos] = Room(start_pos)
        created_rooms.add(start_pos)
        
        # Añadir vecinos iniciales
        for direction, coords in self.rooms[start_pos].neighbors().items():
            x, y = coords
            if -size//2 <= x <= size//2 and -size//2 <= y <= size//2:
                potential_rooms.add(coords)
                # Inicializar puertas cerradas
                self.rooms[start_pos].doors[direction] = Door(open=False, locked=False)

        # 2. Añadir habitaciones hasta alcanzar el número deseado
        while len(created_rooms) < num_rooms and potential_rooms:
            # Elegir una habitación potencial al azar
            new_room_pos = random.choice(list(potential_rooms))
            potential_rooms.remove(new_room_pos)
            
            # Obtener vecinos existentes
            temp_room = Room(new_room_pos)
            existing_neighbors = []
            
            for direction, coords in temp_room.neighbors().items():
                if coords in self.rooms:
                    existing_neighbors.append((coords, direction))
                elif -size//2 <= coords[0] <= size//2 and -size//2 <= coords[1] <= size//2:
                    potential_rooms.add(coords)
            
            # Conectar con al menos un vecino existente
            if existing_neighbors:
                # Añadir la habitación
                self.rooms[new_room_pos] = temp_room
                created_rooms.add(new_room_pos)
                
                # Conectar con un vecino aleatorio
                connected_pos, back_direction = random.choice(existing_neighbors)
                direction_to_neighbor = {
                    'up': 'down', 'down': 'up', 
                    'left': 'right', 'right': 'left'
                }[back_direction]
                
                # Establecer puertas abiertas
                self.rooms[new_room_pos].doors[direction_to_neighbor] = Door(open=True, locked=False)
                self.rooms[connected_pos].doors[back_direction] = Door(open=True, locked=False)
                
                # Añadir puertas cerradas a los demás vecinos
                for direction, coords in temp_room.neighbors().items():
                    if direction != direction_to_neighbor and coords in self.rooms:
                        if direction not in self.rooms[new_room_pos].doors:
                            self.rooms[new_room_pos].doors[direction] = Door(open=False, locked=False)
        
        # 3. Asegurar que todas las habitaciones estén conectadas
        self._ensure_fully_connected(size)
        
        # Sincronizar todas las puertas
        self._sync_all_doors()
    
    def _ensure_fully_connected(self, size: int) -> None:
        """
        Asegura que todas las habitaciones estén conectadas.
        """
        if not self.rooms:
            return
        
        # Usar BFS para encontrar componentes conectados
        visited: Set[Tuple[int, int]] = set()
        components: List[Set[Tuple[int, int]]] = []
        
        for room_pos in self.rooms:
            if room_pos not in visited:
                # BFS para encontrar el componente conectado
                queue = [room_pos]
                component = set()
                
                while queue:
                    current = queue.pop(0)
                    if current in visited:
                        continue
                        
                    visited.add(current)
                    component.add(current)
                    
                    # Añadir vecinos conectados
                    for direction, door in self.rooms[current].doors.items():
                        if door.open:  # Solo puertas abiertas
                            neighbor = self.rooms[current].neighbors()[direction]
                            if neighbor in self.rooms and neighbor not in visited:
                                queue.append(neighbor)
                
                components.append(component)
        
        # Si solo hay un componente, ya está todo conectado
        if len(components) <= 1:
            return
        
        # Conectar componentes desconectados
        for i in range(1, len(components)):
            # Encontrar el camino más corto entre componentes
            start = random.choice(list(components[i-1]))
            end = random.choice(list(components[i]))
            
            # Conectar directamente (puedes implementar un mejor algoritmo de conexión)
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            
            if abs(dx) > 0:
                direction = 'right' if dx > 0 else 'left'
                back_direction = 'left' if dx > 0 else 'right'
            else:
                direction = 'up' if dy > 0 else 'down'
                back_direction = 'down' if dy > 0 else 'up'
            
            # Establecer puertas abiertas
            if start in self.rooms and direction in self.rooms[start].doors:
                self.rooms[start].doors[direction] = Door(open=True, locked=False)
            if end in self.rooms and back_direction in self.rooms[end].doors:
                self.rooms[end].doors[back_direction] = Door(open=True, locked=False)
    
    def _sync_all_doors(self) -> None:
        """
        Sincroniza todas las puertas del calabozo.
        """
        # Primero, asegurarse de que todas las puertas tengan su contraparte
        for pos, room in list(self.rooms.items()):
            for direction, coords in room.neighbors().items():
                if coords in self.rooms and direction not in room.doors:
                    room.doors[direction] = Door(open=False, locked=False)
        
        # Luego, sincronizar todas las puertas
        self._sync_doors()
