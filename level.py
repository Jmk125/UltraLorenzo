import pygame
import random
import math
from settings import *
from enemies import WalkerEnemy, HopperEnemy, FlyerEnemy
from powerups import PowerUpBox, FinalBox

THEMES = [
    {
        "name": "Emerald Meadows",
        "sky": (135, 206, 235),
        "ground": (95, 180, 110),
        "platform_top": (86, 190, 120),
        "platform_side": (70, 140, 95),
        "mountain": (90, 110, 150),
        "snow_cap": (245, 245, 245),
        "hill": (60, 160, 90),
        "cloud": (255, 255, 255)
    },
    {
        "name": "Amber Dunes",
        "sky": (245, 205, 160),
        "ground": (205, 150, 80),
        "platform_top": (215, 180, 120),
        "platform_side": (175, 120, 70),
        "mountain": (160, 120, 90),
        "snow_cap": (230, 200, 160),
        "hill": (210, 160, 100),
        "cloud": (255, 240, 220)
    },
    {
        "name": "Violet Peaks",
        "sky": (90, 120, 200),
        "ground": (120, 110, 190),
        "platform_top": (140, 120, 210),
        "platform_side": (90, 70, 150),
        "mountain": (70, 60, 130),
        "snow_cap": (200, 210, 255),
        "hill": (130, 100, 200),
        "cloud": (220, 210, 255)
    }
]


class Hill(pygame.sprite.Sprite):
    def __init__(self, x, base_y, width, height, color):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        hill_color = (*color, 200)
        points = [(0, height)]
        num_points = 40
        for i in range(num_points + 1):
            x_pos = (width * i) / num_points
            y_val = math.sin(math.pi * i / num_points)
            y_pos = height - (y_val * height * 0.7)
            points.append((x_pos, y_pos))
        points.append((width, height))
        pygame.draw.polygon(self.image, hill_color, points)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = base_y - height


class Mountain(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, body_color, cap_color):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (*body_color, 210),
                            [(0, height), (width * 0.5, 0), (width, height)])
        pygame.draw.polygon(self.image, cap_color,
                            [(width * 0.4, height * 0.15),
                             (width * 0.5, 0),
                             (width * 0.6, height * 0.15)])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        width = random.randint(70, 130)
        height = random.randint(30, 60)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        center_y = height // 2
        circle_radius = height // 2
        positions = [
            (circle_radius, center_y),
            (width // 3, center_y - 5),
            (width // 2, center_y + 2),
            (2 * width // 3, center_y),
            (width - circle_radius, center_y - 3)
        ]
        for pos in positions:
            pygame.draw.circle(self.image, (*color, 180), pos, circle_radius)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = random.uniform(0.2, 0.5)
        self.float_x = float(x)

    def update(self):
        self.float_x += self.speed
        self.rect.x = int(self.float_x)
        if self.rect.left > LEVEL_WIDTH:
            self.rect.right = 0
            self.float_x = float(self.rect.x)


class EndLevelMarker(pygame.sprite.Sprite):
    def __init__(self, x, y, height):
        super().__init__()
        width = LEVEL_WIDTH - x
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        zigzag_width = 20
        zigzag_height = 20
        points = [(zigzag_width, 0)]
        current_y = 0
        while current_y < height:
            points.append((0, current_y + zigzag_height // 2))
            if current_y + zigzag_height >= height:
                break
            points.append((zigzag_width, current_y + zigzag_height))
            current_y += zigzag_height
        points.extend([(0, height), (width, height), (width, 0)])
        pygame.draw.polygon(self.image, BLACK, points)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, top_color, side_color):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(side_color)
        pygame.draw.rect(self.image, top_color, (0, 0, w, 6))
        for i in range(0, w, TILE_SIZE):
            pygame.draw.line(self.image, top_color, (i, 0), (i, h), 1)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        pass


class MovingPlatform(Platform):
    def __init__(self, x, y, w, h, travel_distance, speed, top_color, side_color):
        super().__init__(x, y, w, h, top_color, side_color)
        self.start_x = x
        self.travel_distance = travel_distance
        self.speed = speed
        self.direction = random.choice([-1, 1])

    def update(self):
        self.rect.x += self.speed * self.direction
        if abs(self.rect.x - self.start_x) >= self.travel_distance:
            self.direction *= -1


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((COIN_SIZE, COIN_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (COIN_SIZE // 2, COIN_SIZE // 2), COIN_SIZE // 2)
        pygame.draw.circle(self.image, (255, 215, 0), (COIN_SIZE // 3, COIN_SIZE // 3), COIN_SIZE // 6)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.original_y = y
        self.float_offset = 0
        self.float_speed = 0.1

    def update(self):
        self.float_offset = (self.float_offset + self.float_speed) % (2 * math.pi)
        self.rect.y = self.original_y + math.sin(self.float_offset) * 5


class LevelGenerator:
    def __init__(self, game):
        self.game = game

    def get_theme(self):
        return random.choice(THEMES)

    def is_gap_jumpable(self, gap_width, platform_height_diff):
        # Use run speed for gap calculations since player can run and jump
        return (gap_width <= PLAYER_RUN_SPEED * 6 and
                abs(platform_height_diff) <= MAX_JUMP_HEIGHT)

    def generate_level(self, difficulty_profile):
        theme = self.get_theme()
        background = pygame.sprite.Group()
        midground = pygame.sprite.Group()
        platforms = pygame.sprite.Group()
        coins = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        foreground = pygame.sprite.Group()
        powerup_boxes = pygame.sprite.Group()

        for i in range(3):
            x = i * (LEVEL_WIDTH // 3)
            width = random.randint(500, 800)
            height = random.randint(280, 420)
            mountain = Mountain(x, LEVEL_HEIGHT - height, width, height,
                                theme["mountain"], theme["snow_cap"])
            background.add(mountain)

        hill_width = 600
        hill_overlap = 180
        for i in range((LEVEL_WIDTH + hill_overlap) // (hill_width - hill_overlap)):
            x = i * (hill_width - hill_overlap) - hill_overlap // 2
            height = random.randint(180, 320)
            hill = Hill(x, LEVEL_HEIGHT, hill_width, height, theme["hill"])
            midground.add(hill)

        for i in range(12):
            x = random.randint(0, LEVEL_WIDTH)
            y = random.randint(50, LEVEL_HEIGHT // 2)
            cloud = Cloud(x, y, theme["cloud"])
            midground.add(cloud)

        current_x = 0
        while current_x < LEVEL_WIDTH - 400:
            if current_x > WINDOW_WIDTH and random.random() < 0.3:
                gap_width = random.randint(MIN_GAP_WIDTH,
                                           int(MAX_GAP_WIDTH * difficulty_profile["gap_scale"]))
                current_x += gap_width
            else:
                width = random.randint(MIN_PLATFORM_WIDTH * 2, MAX_PLATFORM_WIDTH * 2)
                platform = Platform(current_x, LEVEL_HEIGHT - PLATFORM_HEIGHT, width,
                                    PLATFORM_HEIGHT, theme["platform_top"], theme["platform_side"])
                platforms.add(platform)
                current_x += width

        current_x = 120
        last_platform_y = LEVEL_HEIGHT - PLATFORM_HEIGHT
        enemy_classes = [WalkerEnemy]
        if difficulty_profile["enemy_density"] > 0.35:
            enemy_classes.append(HopperEnemy)
        if difficulty_profile["enemy_density"] > 0.45:
            enemy_classes.append(FlyerEnemy)

        while current_x < LEVEL_WIDTH - 400:
            width = random.randint(MIN_PLATFORM_WIDTH, MAX_PLATFORM_WIDTH)
            min_y = max(last_platform_y - MAX_JUMP_HEIGHT, LEVEL_HEIGHT - 320)
            max_y = min(last_platform_y + MAX_JUMP_HEIGHT, LEVEL_HEIGHT - 120)
            if min_y >= max_y:
                min_y = max_y - MAX_JUMP_HEIGHT
            y = random.randint(int(min_y), int(max_y))

            moving = random.random() < difficulty_profile["moving_platform_chance"]
            if moving:
                travel = random.randint(40, 120)
                speed = random.uniform(1.0, 1.8) * difficulty_profile["enemy_speed_scale"]
                platform = MovingPlatform(current_x, y, width, PLATFORM_HEIGHT, travel, speed,
                                          theme["platform_top"], theme["platform_side"])
            else:
                platform = Platform(current_x, y, width, PLATFORM_HEIGHT,
                                    theme["platform_top"], theme["platform_side"])
            platforms.add(platform)

            # Use fixed spacing for coins instead of platform-dependent spacing
            COIN_SPACING = 45  # Fixed spacing between coins
            max_coins = max(1, (width - 20) // COIN_SPACING)  # Calculate how many coins fit
            coin_count = min(random.randint(1, difficulty_profile["coin_cluster_size"]), max_coins)

            # Center the coins on the platform
            total_coin_width = (coin_count - 1) * COIN_SPACING if coin_count > 1 else 0
            start_offset = (width - total_coin_width) // 2

            for i in range(coin_count):
                offset = start_offset + (i * COIN_SPACING)
                coin = Coin(current_x + offset - COIN_SIZE // 2, y - 50)
                coins.add(coin)

            if random.random() < difficulty_profile["mid_powerup_chance"]:
                powerup_box = PowerUpBox(current_x + width // 2 - POWERUP_SIZE // 2, y - POWERUP_SIZE - 10)
                powerup_boxes.add(powerup_box)

            if random.random() < difficulty_profile["enemy_density"]:
                enemy_class = random.choice(enemy_classes)
                spawn_y = y - ENEMY_HEIGHT
                if enemy_class == FlyerEnemy:
                    spawn_y = y - ENEMY_HEIGHT - random.randint(60, 140)
                enemy = enemy_class(self.game, current_x + width // 2, spawn_y,
                                    difficulty_profile["enemy_speed_scale"])
                enemies.add(enemy)

            gap = random.randint(MIN_GAP_WIDTH,
                                 int(MAX_GAP_WIDTH * difficulty_profile["gap_scale"]))
            attempts = 0
            while not self.is_gap_jumpable(gap, y - last_platform_y) and attempts < 5:
                gap = random.randint(MIN_GAP_WIDTH, MAX_GAP_WIDTH)
                y = random.randint(int(min_y), int(max_y))
                attempts += 1
            if attempts >= 5:
                gap = MIN_GAP_WIDTH

            current_x += width + gap
            last_platform_y = y

        end_x = LEVEL_WIDTH - 400
        final_platform = Platform(end_x + 50, LEVEL_HEIGHT - 150, 150, PLATFORM_HEIGHT,
                                  theme["platform_top"], theme["platform_side"])
        platforms.add(final_platform)
        powerup_platform = Platform(end_x + 250, LEVEL_HEIGHT - 220, 120, PLATFORM_HEIGHT,
                                    theme["platform_top"], theme["platform_side"])
        platforms.add(powerup_platform)
        # Create special final box that triggers level completion
        final_box = FinalBox(end_x + 280, LEVEL_HEIGHT - 270, self.game)
        powerup_boxes.add(final_box)

        for i in range(6):
            coin = Coin(end_x + 150 + i * 35, LEVEL_HEIGHT - 260)
            coins.add(coin)

        end_marker = EndLevelMarker(end_x, 0, LEVEL_HEIGHT)
        foreground.add(end_marker)

        return background, midground, platforms, coins, enemies, powerup_boxes, foreground, theme
