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

    def change_scene(self, scene_type: Type[Scene], **kwargs) -> None:
        self.scene.stop()
        self.scene = scene_type(self, **kwargs)
        self.scene.start()

    def run(self) -> None:
        try:
            while self.running:
                try:
                    # Limit the frame rate and calculate delta time
                    dt = self.clock.tick(FPS) / 1000.0

                    # Handle events
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                        else:
                            self.scene.handle_event(event)

                    # Update game state
                    self.scene.update(dt)

                    # Clear the screen
                    self.screen.fill(GRAY)

                    # Draw the current scene
                    self.scene.draw(self.screen)

                    # Update the display
                    pygame.display.flip()

                except KeyboardInterrupt:
                    print("\nGame interrupted by user. Exiting...")
                    self.running = False
                    break
                except Exception as e:
                    print(f"\nAn error occurred: {e}")
                    import traceback
                    traceback.print_exc()
                    self.running = False
                    break

        finally:
            # Ensure proper cleanup
            pygame.quit()
            print("Game closed successfully.")

