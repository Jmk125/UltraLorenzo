import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

class Camera:
    def __init__(self, level_width, level_height):
        self.camera = pygame.Rect(0, 0, level_width, level_height)
        self.width = level_width
        self.height = level_height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_parallax(self, entity, parallax_factor):
        """Apply camera offset with parallax effect.

        Args:
            entity: The sprite to apply parallax to
            parallax_factor: How much the sprite moves with camera (0.0-1.0)
                           0.0 = doesn't move at all (far background)
                           1.0 = moves with camera (foreground)
        """
        parallax_x = int(self.camera.x * parallax_factor)
        parallax_y = int(self.camera.y * parallax_factor)
        return entity.rect.move(parallax_x, parallax_y)

    def update(self, target):
        x = -target.rect.centerx + WINDOW_WIDTH // 2
        y = -target.rect.centery + WINDOW_HEIGHT // 2

        # Limit scrolling to level size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - WINDOW_WIDTH), x)  # right
        y = max(-(self.height - WINDOW_HEIGHT), y)  # bottom

        self.camera = pygame.Rect(x, y, self.width, self.height)