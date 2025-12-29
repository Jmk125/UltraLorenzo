import pygame
import math
from settings import *


class Fireball(pygame.sprite.Sprite):
    """Bouncing fireball projectile."""

    def __init__(self, x, y, direction, game):
        super().__init__()
        self.game = game
        self.direction = direction  # 1 for right, -1 for left
        self.create_sprite()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.vel_x = FIREBALL_SPEED * self.direction
        self.vel_y = 0
        self.start_x = x
        self.animation_frame = 0

    def create_sprite(self):
        """Create animated fireball sprite."""
        self.image = pygame.Surface((FIREBALL_SIZE, FIREBALL_SIZE), pygame.SRCALPHA)
        # Orange/red fireball with yellow center
        pygame.draw.circle(self.image, (255, 100, 0), (FIREBALL_SIZE // 2, FIREBALL_SIZE // 2), FIREBALL_SIZE // 2)
        pygame.draw.circle(self.image, (255, 200, 50), (FIREBALL_SIZE // 2, FIREBALL_SIZE // 2), FIREBALL_SIZE // 3)
        pygame.draw.circle(self.image, (255, 255, 150), (FIREBALL_SIZE // 2, FIREBALL_SIZE // 2), FIREBALL_SIZE // 6)
        # Store original image for rotation
        self.original_image = self.image.copy()

    def update(self):
        """Update fireball position and check collisions."""
        # Apply gravity
        self.vel_y += FIREBALL_GRAVITY

        # Update position
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Check if traveled too far
        distance_traveled = abs(self.rect.centerx - self.start_x)
        if distance_traveled > FIREBALL_MAX_DISTANCE:
            self.kill()
            return

        # Check platform collision for bouncing
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        if hits and self.vel_y > 0:
            self.rect.bottom = hits[0].rect.top
            self.vel_y = FIREBALL_BOUNCE_POWER

        # Check enemy collision
        enemy_hits = pygame.sprite.spritecollide(self, self.game.enemies, True)
        if enemy_hits:
            for enemy in enemy_hits:
                self.game.player.reward_enemy_defeat()
            self.kill()
            return

        # Remove if off screen or fallen too far
        if self.rect.top > LEVEL_HEIGHT or self.rect.right < 0 or self.rect.left > LEVEL_WIDTH:
            self.kill()

        # Animate rotation (rotate from original to prevent growth)
        self.animation_frame += 15 * self.direction
        rotated = pygame.transform.rotate(self.original_image, self.animation_frame)
        old_center = self.rect.center
        self.image = rotated
        self.rect = self.image.get_rect()
        self.rect.center = old_center
