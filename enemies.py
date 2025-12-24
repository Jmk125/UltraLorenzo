import pygame
import random
import math
from settings import *


class WalkerEnemy(pygame.sprite.Sprite):
    """Classic ground patroller."""

    def __init__(self, game, x, y, difficulty_scale=1.0):
        super().__init__()
        self.game = game
        self.create_sprite_frames()
        self.direction = random.choice([-1, 1])
        self.image = self.frames[0] if self.direction > 0 else pygame.transform.flip(self.frames[0], True, False)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.move_counter = 0
        self.vel_y = 0
        self.on_ground = False
        self.speed = ENEMY_SPEED * difficulty_scale
        self.animation_counter = 0
        self.current_frame = 0

    def create_sprite_frames(self):
        """Create pixel art Goomba-like enemy"""
        self.frames = []
        for i in range(2):
            sprite = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT), pygame.SRCALPHA)

            # Brown mushroom body
            brown = (120, 80, 40)
            dark_brown = (80, 50, 20)

            # Mushroom cap
            pygame.draw.rect(sprite, brown, (4, 4, 24, 12))
            pygame.draw.rect(sprite, dark_brown, (6, 4, 4, 4))
            pygame.draw.rect(sprite, dark_brown, (14, 4, 4, 4))
            pygame.draw.rect(sprite, dark_brown, (22, 4, 4, 4))

            # Body/stem
            pygame.draw.rect(sprite, (160, 110, 70), (8, 16, 16, 10))

            # Eyes (angry expression)
            eye_offset = 1 if i == 1 else 0
            pygame.draw.rect(sprite, BLACK, (10, 8 + eye_offset, 4, 4))
            pygame.draw.rect(sprite, BLACK, (18, 8 + eye_offset, 4, 4))
            pygame.draw.rect(sprite, (255, 255, 255), (11, 9 + eye_offset, 2, 2))
            pygame.draw.rect(sprite, (255, 255, 255), (19, 9 + eye_offset, 2, 2))

            # Feet (alternate for walking animation)
            if i == 0:
                pygame.draw.rect(sprite, dark_brown, (6, 26, 6, 6))
                pygame.draw.rect(sprite, dark_brown, (20, 26, 6, 6))
            else:
                pygame.draw.rect(sprite, dark_brown, (4, 26, 6, 6))
                pygame.draw.rect(sprite, dark_brown, (22, 26, 6, 6))

            self.frames.append(sprite)

    def update(self):
        self.rect.x += self.speed * self.direction
        self.move_counter += 1

        # Animate sprite
        self.animation_counter += 1
        if self.animation_counter >= 15:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % 2
            self.image = self.frames[self.current_frame] if self.direction > 0 else pygame.transform.flip(self.frames[self.current_frame], True, False)

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
        self.create_sprite_frames()
        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vel_y = 0
        self.direction = random.choice([-1, 1])
        self.speed = (ENEMY_SPEED - 0.5) * max(0.6, difficulty_scale)
        self.hop_cooldown = random.randint(30, 90)
        self.difficulty_scale = difficulty_scale
        self.animation_counter = 0

    def create_sprite_frames(self):
        """Create pixel art bouncing slime-like enemy"""
        self.frames = []
        for i in range(2):
            sprite = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT), pygame.SRCALPHA)

            # Orange/yellow slime creature
            orange = (255, 180, 80)
            dark_orange = (220, 140, 50)

            # Body shape changes for bounce animation
            if i == 0:  # Squished
                pygame.draw.ellipse(sprite, orange, (4, 14, 24, 18))
                pygame.draw.ellipse(sprite, dark_orange, (6, 16, 20, 14))
            else:  # Stretched
                pygame.draw.ellipse(sprite, orange, (6, 8, 20, 24))
                pygame.draw.ellipse(sprite, dark_orange, (8, 10, 16, 20))

            # Eyes
            pygame.draw.circle(sprite, BLACK, (12, 18), 3)
            pygame.draw.circle(sprite, BLACK, (20, 18), 3)
            pygame.draw.circle(sprite, (255, 255, 255), (13, 17), 1)
            pygame.draw.circle(sprite, (255, 255, 255), (21, 17), 1)

            self.frames.append(sprite)

    def update(self):
        self.hop_cooldown -= 1
        if self.hop_cooldown <= 0:
            self.vel_y = JUMP_POWER * 0.6
            self.direction = random.choice([-1, 1])
            self.hop_cooldown = random.randint(45, 90)

        # Animate based on velocity
        self.animation_counter += 1
        if self.animation_counter >= 10:
            self.animation_counter = 0
            if self.vel_y < -2:  # Jumping/stretching
                self.current_frame = 1
            else:  # Landed/squished
                self.current_frame = 0
            self.image = self.frames[self.current_frame]

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
        self.create_sprite_frames()
        self.current_frame = 0
        self.image = self.frames[0]
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
        self.animation_counter = 0

    def create_sprite_frames(self):
        """Create pixel art bat-like flying enemy"""
        self.frames = []
        for i in range(2):
            sprite = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT), pygame.SRCALPHA)

            # Purple bat creature
            purple = (200, 60, 160)
            dark_purple = (140, 40, 110)

            # Body
            pygame.draw.ellipse(sprite, purple, (10, 12, 12, 16))

            # Head
            pygame.draw.circle(sprite, purple, (16, 10), 6)

            # Ears
            pygame.draw.polygon(sprite, dark_purple, [(13, 6), (11, 2), (15, 8)])
            pygame.draw.polygon(sprite, dark_purple, [(19, 6), (21, 2), (17, 8)])

            # Eyes
            pygame.draw.circle(sprite, BLACK, (14, 10), 2)
            pygame.draw.circle(sprite, BLACK, (18, 10), 2)
            pygame.draw.circle(sprite, (255, 255, 255), (15, 9), 1)
            pygame.draw.circle(sprite, (255, 255, 255), (19, 9), 1)

            # Wings (flap animation)
            if i == 0:  # Wings up
                # Left wing
                pygame.draw.polygon(sprite, dark_purple, [(10, 16), (2, 10), (8, 20)])
                # Right wing
                pygame.draw.polygon(sprite, dark_purple, [(22, 16), (30, 10), (24, 20)])
            else:  # Wings down
                # Left wing
                pygame.draw.polygon(sprite, dark_purple, [(10, 18), (2, 22), (8, 24)])
                # Right wing
                pygame.draw.polygon(sprite, dark_purple, [(22, 18), (30, 22), (24, 24)])

            self.frames.append(sprite)

    def update(self):
        # Animate wing flapping
        self.animation_counter += 1
        if self.animation_counter >= 8:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % 2
            self.image = self.frames[self.current_frame] if self.direction > 0 else pygame.transform.flip(self.frames[self.current_frame], True, False)

        self.rect.x += self.direction * self.speed
        if self.rect.left <= self.min_x or self.rect.right >= self.max_x:
            self.direction *= -1

        t = pygame.time.get_ticks() * 0.005
        self.rect.y = self.base_y + math.sin(t + self.wave_offset) * self.amplitude
