from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Tuple

from .room import Room, Door


@dataclass
class Dungeon:
    rooms: Dict[Tuple[int, int], Room] = field(default_factory=dict)
    current: Tuple[int, int] = (0, 0)

    def __post_init__(self) -> None:
        if not self.rooms:
            # Crear una pequeña grilla 3x3 con algunas puertas bloqueadas
            for gx in range(-1, 2):
                for gy in range(-1, 2):
                    self.rooms[(gx, gy)] = Room((gx, gy))
            # Bloquear una puerta como ejemplo
            self.rooms[(0, 0)].doors['right'] = Door(open=False, locked=True)
            # Ajustar simetría de puertas entre salas vecinas
            self._sync_doors()
            # Abrir puertas de la sala inicial (excepto las bloqueadas)
            start = self.rooms[self.current]
            for d, door in start.doors.items():
                if not door.locked:
                    door.open = True
            self._sync_doors()

    def _sync_doors(self) -> None:
        # Asegura que si una puerta está bloqueada u abierta, su contraparte coincida
        for (gx, gy), room in self.rooms.items():
            for d, door in room.doors.items():
                nx, ny = room.neighbors()[d]
                if (nx, ny) in self.rooms:
                    back = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}[d]
                    other = self.rooms[(nx, ny)].doors[back]
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
