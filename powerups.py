import pygame
import random
from settings import *

POWERUP_REWARDS = [
    {"type": "xp", "amount": 40, "label": "Wisdom Fragment"},
    {"type": "life", "amount": 1, "label": "Spare Heart"},
    {"type": "score", "amount": 200, "label": "Treasure Cache"}
]

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type_):
        super().__init__()
        self.type = type_
        self.image = pygame.Surface((30, 30))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class PowerUpBox(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hit_time = 0
        self.has_powerup = True

    def hit(self):
        current_time = pygame.time.get_ticks()
        if self.has_powerup and current_time - self.hit_time > 1000:
            self.has_powerup = False
            self.hit_time = current_time
            self.image.fill((100, 100, 100))
            return random.choice(POWERUP_REWARDS)
        return None


class FinalBox(pygame.sprite.Sprite):
    """Special box at level end that triggers level completion when all collectibles are obtained."""

    def __init__(self, x, y, game):
        super().__init__()
        self.game = game
        self.size = POWERUP_SIZE
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.has_powerup = True
        self.hit_time = 0
        self.animation_offset = 0
        self.update_appearance()

    def is_ready(self):
        """Check if all enemies, coins, and powerup boxes are collected."""
        enemies_cleared = len(self.game.enemies) == 0
        coins_collected = len(self.game.coins) == 0
        boxes_collected = all(not box.has_powerup for box in self.game.powerup_boxes if box != self)
        return enemies_cleared and coins_collected and boxes_collected

    def update_appearance(self):
        """Update the box appearance based on ready state."""
        self.image.fill((0, 0, 0, 0))  # Clear with transparency

        if self.is_ready():
            # Solid golden box when ready
            pygame.draw.rect(self.image, (255, 215, 0), (0, 0, self.size, self.size))
            pygame.draw.rect(self.image, (255, 255, 100), (2, 2, self.size - 4, self.size - 4), 3)
            # Draw sparkle effect
            sparkle_color = (255, 255, 255)
            pygame.draw.circle(self.image, sparkle_color, (self.size // 4, self.size // 4), 2)
            pygame.draw.circle(self.image, sparkle_color, (3 * self.size // 4, 3 * self.size // 4), 2)
        else:
            # Dashed outline when not ready
            dash_color = (150, 150, 150)
            dash_length = 4
            gap_length = 3

            # Top edge
            for x in range(0, self.size, dash_length + gap_length):
                pygame.draw.line(self.image, dash_color, (x, 0), (min(x + dash_length, self.size), 0), 2)
            # Bottom edge
            for x in range(0, self.size, dash_length + gap_length):
                pygame.draw.line(self.image, dash_color, (x, self.size - 1), (min(x + dash_length, self.size), self.size - 1), 2)
            # Left edge
            for y in range(0, self.size, dash_length + gap_length):
                pygame.draw.line(self.image, dash_color, (0, y), (0, min(y + dash_length, self.size)), 2)
            # Right edge
            for y in range(0, self.size, dash_length + gap_length):
                pygame.draw.line(self.image, dash_color, (self.size - 1, y), (self.size - 1, min(y + dash_length, self.size)), 2)

    def update(self):
        """Update animation."""
        self.animation_offset += 1
        if self.animation_offset % 10 == 0:  # Update appearance periodically
            self.update_appearance()

    def hit(self):
        """Attempt to collect the box and complete the level."""
        if self.is_ready() and self.has_powerup:
            current_time = pygame.time.get_ticks()
            if current_time - self.hit_time > 1000:
                self.has_powerup = False
                self.hit_time = current_time
                # Trigger level completion
                self.game.on_level_complete()
                return {"type": "level_complete", "label": "Level Complete!"}
        return None