import pygame
import random
import math
from settings import *


class WalkerEnemy(pygame.sprite.Sprite):
    """Classic ground patroller."""

    def __init__(self, game, x, y, difficulty_scale=1.0):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill((70, 120, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.direction = random.choice([-1, 1])
        self.move_counter = 0
        self.vel_y = 0
        self.on_ground = False
        self.speed = ENEMY_SPEED * difficulty_scale

    def update(self):
        self.rect.x += self.speed * self.direction
        self.move_counter += 1

        if self.move_counter > 120:
            self.direction *= -1
            self.move_counter = 0

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        if hits:
            if self.vel_y > 0:
                self.rect.bottom = hits[0].rect.top
                self.vel_y = 0
                self.on_ground = True
            elif self.vel_y < 0:
                self.rect.top = hits[0].rect.bottom
                self.vel_y = 0

        ahead_check = self.rect.copy()
        ahead_check.x += self.speed * self.direction
        ahead_check.y += 5

        has_ground = False
        for platform in self.game.platforms:
            if platform.rect.colliderect(ahead_check):
                has_ground = True
                break

        if not has_ground:
            self.direction *= -1


class HopperEnemy(pygame.sprite.Sprite):
    """Enemy that makes unpredictable hops."""

    def __init__(self, game, x, y, difficulty_scale=1.0):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill((255, 180, 80))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vel_y = 0
        self.direction = random.choice([-1, 1])
        self.speed = (ENEMY_SPEED - 0.5) * max(0.6, difficulty_scale)
        self.hop_cooldown = random.randint(30, 90)
        self.difficulty_scale = difficulty_scale

    def update(self):
        self.hop_cooldown -= 1
        if self.hop_cooldown <= 0:
            self.vel_y = JUMP_POWER * 0.6
            self.direction = random.choice([-1, 1])
            self.hop_cooldown = random.randint(45, 90)

        self.rect.x += self.speed * self.direction
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        if hits:
            if self.vel_y > 0:
                self.rect.bottom = hits[0].rect.top
                self.vel_y = 0
            elif self.vel_y < 0:
                self.rect.top = hits[0].rect.bottom
                self.vel_y = 0

        if self.rect.left < 0 or self.rect.right > LEVEL_WIDTH:
            self.direction *= -1


class FlyerEnemy(pygame.sprite.Sprite):
    """Aerial foe that weaves through the sky."""

    def __init__(self, game, x, y, difficulty_scale=1.0):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (200, 60, 160),
                            [(0, ENEMY_HEIGHT), (ENEMY_WIDTH // 2, 0), (ENEMY_WIDTH, ENEMY_HEIGHT)])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.base_y = y
        self.amplitude = random.randint(30, 60)
        self.wave_offset = random.random() * math.tau
        self.direction = random.choice([-1, 1])
        self.speed = 2.0 * difficulty_scale
        self.min_x = max(50, x - 150)
        self.max_x = min(LEVEL_WIDTH - 50, x + 150)

    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.left <= self.min_x or self.rect.right >= self.max_x:
            self.direction *= -1

        t = pygame.time.get_ticks() * 0.005
        self.rect.y = self.base_y + math.sin(t + self.wave_offset) * self.amplitude
