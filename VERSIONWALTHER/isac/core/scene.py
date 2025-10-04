import pygame
from typing import Optional


class Scene:
    """Clase base para escenas del juego.

    Debe implementar handle_event, update y draw.
    """

    def __init__(self, game: "Game") -> None:
        self.game = game
        self.next_scene: Optional[Scene] = None

    def start(self) -> None:
        """Se llama cuando la escena empieza a ser activa."""
        pass

    def stop(self) -> None:
        """Se llama cuando la escena deja de ser activa."""
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass
