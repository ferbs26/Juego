import pygame
from typing import Optional

class InfiniteShotPickup:
    """
    A power-up that grants the player infinite arrows for a limited time.
    """
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.rect.center = (x, y)
        self.collected = False
        self.duration = 10.0  # seconds
        self.timer = 0.0
        self.active = False
        
        # Load sprite if available
        self.image = None
        try:
            self.image = pygame.image.load('assets/player/infinite_shot.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (24, 24))
        except:
            # Fallback to a colored rectangle if image not found
            self.image = None
    
    def apply_effect(self, player):
        """Apply the infinite shot effect to the player."""
        if not self.active:
            self.active = True
            self.timer = self.duration
            player.set_infinite_shots(True)
            
    def update(self, dt: float, player) -> bool:
        """
        Update the power-up timer.
        Returns True if the effect is still active, False otherwise.
        """
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                player.set_infinite_shots(False)
                return False
            return True
        return False
    
    def draw(self, surface: pygame.Surface):
        """Draw the power-up if it hasn't been collected yet."""
        if not self.collected and not self.active:
            if self.image:
                surface.blit(self.image, self.rect)
            else:
                # Fallback drawing
                pygame.draw.rect(surface, (0, 255, 255), self.rect)  # Cyan color
