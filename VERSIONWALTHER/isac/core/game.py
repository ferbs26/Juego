import pygame
from typing import Type

from isac.settings import WIDTH, HEIGHT, FPS, TITLE, GRAY
from .scene import Scene


class Game:
    def __init__(self, initial_scene: Type[Scene]) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.scene: Scene = initial_scene(self)
        self.scene.start()

    def change_scene(self, scene_type: Type[Scene]) -> None:
        self.scene.stop()
        self.scene = scene_type(self)
        self.scene.start()

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.scene.handle_event(event)

            self.scene.update(dt)

            # Clear
            self.screen.fill(GRAY)

            # Draw scene
            self.scene.draw(self.screen)

            # Flip
            pygame.display.flip()

