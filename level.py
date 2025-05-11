# Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-05-10 15:03:47
# Current User's Login: Jmk125

import pygame
from settings import *
import random
import math
from enemies import Enemy
from powerups import PowerUpBox

class Hill(pygame.sprite.Sprite):
    def __init__(self, x, base_y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Use a solid green for hills
        hill_color = (45, 100, 45, 255)
        
        # Create points for a smooth hill curve
        points = []
        
        # Start at bottom left
        points.append((0, height))
        
        # Create the curved top of the hill
        num_points = 40  # More points for smoother curve
        for i in range(num_points + 1):
            x_pos = (width * i) / num_points
            # Use sine wave for smooth curve, adjusted to make a full round hill
            y_val = math.sin(math.pi * i / num_points)  # Values between 0 and 1
            y_pos = height - (y_val * height * 0.7)  # Scale height and invert
            points.append((x_pos, y_pos))
        
        # End at bottom right
        points.append((width, height))
        
        # Draw the hill
        pygame.draw.polygon(self.image, hill_color, points)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = base_y - height

class Mountain(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        mountain_color = (80, 90, 120, 180)
        
        points = [
            (0, height),
            (width * 0.5, 0),
            (width, height)
        ]
        pygame.draw.polygon(self.image, mountain_color, points)
        
        # Add snow cap
        snow_points = [
            (width * 0.4, height * 0.15),
            (width * 0.5, 0),
            (width * 0.6, height * 0.15)
        ]
        pygame.draw.polygon(self.image, (255, 255, 255, 200), snow_points)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.game_active:
                        self.player.jump()
                    elif event.key == pygame.K_r and not self.game_active:
                        self.game_active = True
                        self.level_number = 1
                        self.start_time = datetime.utcnow()
                        self.setup_new_game()
            
            if self.game_active:
                # Update
                self.all_sprites.update()
                self.camera.update(self.player)
                
                # Check for coin collisions
                coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
                for coin in coin_hits:
                    self.player.score += 10
                
                # Check for powerup box collisions
                powerup_hits = pygame.sprite.spritecollide(self.player, self.powerup_boxes, False)
                for box in powerup_hits:
                    if box.hit():
                        self.player.score += 50
                
                # Draw
                self.screen.fill(SKY_BLUE)
                
                # Draw all sprites with camera offset in their added order
                for sprite in self.all_sprites.sprites():  # Changed from self.all_sprites to self.all_sprites.sprites()
                    if not (sprite == self.player and 
                           self.player.invulnerable and 
                           self.player.blinking):
                        self.screen.blit(sprite.image, self.camera.apply(sprite))
                
                # Draw HUD
                self.draw_hud()
            else:
                # Draw game over screen
                self.screen.fill(BLACK)
                self.draw_game_over()
            
            # Update display
            pygame.display.flip()

class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        width = random.randint(60, 120)
        height = random.randint(30, 50)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        cloud_color = (255, 255, 255, 160)
        center_y = height // 2
        circle_radius = height // 2
        
        positions = [
            (circle_radius, center_y),
            (width // 3, center_y - 5),
            (width // 2, center_y),
            (2 * width // 3, center_y + 5),
            (width - circle_radius, center_y)
        ]
        
        for pos in positions:
            pygame.draw.circle(self.image, cloud_color, pos, circle_radius)
            
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
        points = []
        current_y = 0
        
        points.append((zigzag_width, 0))
        while current_y < height:
            points.append((0, current_y + zigzag_height//2))
            if current_y + zigzag_height >= height:
                break
            points.append((zigzag_width, current_y + zigzag_height))
            current_y += zigzag_height
        
        points.append((0, height))
        points.append((width, height))
        points.append((width, 0))
        
        pygame.draw.polygon(self.image, BLACK, points)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        pygame.draw.rect(self.image, (34, 139, 34), (0, 0, w, 5))
        for i in range(0, w, TILE_SIZE):
            pygame.draw.line(self.image, (34, 139, 34), (i, 0), (i, h), 1)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((COIN_SIZE, COIN_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (COIN_SIZE//2, COIN_SIZE//2), COIN_SIZE//2)
        pygame.draw.circle(self.image, (255, 215, 0), 
                         (COIN_SIZE//3, COIN_SIZE//3), COIN_SIZE//6)
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
        
    def is_gap_jumpable(self, gap_width, platform_height_diff):
        return (gap_width <= PLAYER_SPEED * 6 and
                abs(platform_height_diff) <= MAX_JUMP_HEIGHT)

    def generate_level(self):
        # Create separate groups for background layers
        background = pygame.sprite.Group()  # Furthest back (mountains)
        midground = pygame.sprite.Group()   # Middle (hills)
        platforms = pygame.sprite.Group()
        coins = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        foreground = pygame.sprite.Group()  # End marker goes here
        
        # Add mountains (in the far back)
        for i in range(3):
            x = i * (LEVEL_WIDTH // 3)  # More evenly spaced
            width = random.randint(600, 800)  # Wider mountains
            height = random.randint(300, 400)  # Taller mountains
            mountain = Mountain(x, LEVEL_HEIGHT - height, width, height)
            background.add(mountain)
        
        # Add hills (complete mounds)
        hill_width = 600  # Wider hills for complete mounds
        hill_overlap = 200  # Amount of overlap between hills
        for i in range((LEVEL_WIDTH + hill_overlap) // (hill_width - hill_overlap)):
            x = i * (hill_width - hill_overlap) - hill_overlap//2
            height = random.randint(200, 300)  # Taller hills
            hill = Hill(x, LEVEL_HEIGHT, hill_width, height)
            midground.add(hill)
        
        # Add clouds
        for i in range(10):
            x = random.randint(0, LEVEL_WIDTH)
            y = random.randint(50, LEVEL_HEIGHT // 3)
            cloud = Cloud(x, y)
            midground.add(cloud)
        
        # Generate ground platforms
        current_x = 0
        while current_x < LEVEL_WIDTH - 400:
            if current_x > WINDOW_WIDTH and random.random() < 0.3:
                gap_width = random.randint(MIN_GAP_WIDTH, MAX_GAP_WIDTH)
                current_x += gap_width
            else:
                width = random.randint(MIN_PLATFORM_WIDTH * 2, MAX_PLATFORM_WIDTH * 2)
                platform = Platform(current_x, LEVEL_HEIGHT - PLATFORM_HEIGHT, width, PLATFORM_HEIGHT)
                platforms.add(platform)
                current_x += width
        
        # Generate floating platforms
        current_x = 100
        last_platform_y = LEVEL_HEIGHT - PLATFORM_HEIGHT
        
        while current_x < LEVEL_WIDTH - 400:
            width = random.randint(MIN_PLATFORM_WIDTH, MAX_PLATFORM_WIDTH)
            
            # Calculate valid y-position range
            min_y = max(last_platform_y - MAX_JUMP_HEIGHT, LEVEL_HEIGHT - 300)
            max_y = min(last_platform_y + MAX_JUMP_HEIGHT, LEVEL_HEIGHT - 100)
            
            # Ensure min_y is less than max_y
            if min_y >= max_y:
                min_y = max_y - MAX_JUMP_HEIGHT
            
            # Generate platform position
            y = random.randint(int(min_y), int(max_y))
            platform = Platform(current_x, y, width, PLATFORM_HEIGHT)
            platforms.add(platform)
            
            # Add coins
            for i in range(random.randint(1, 3)):
                coin = Coin(current_x + (i + 1) * (width // 4), y - 50)
                coins.add(coin)
            
            # Add enemy
            if random.random() < 0.3:
                enemy = Enemy(self.game, current_x + width//2, y - ENEMY_HEIGHT)
                enemies.add(enemy)
            
            # Generate jumpable gap
            max_attempts = 5
            attempts = 0
            gap = random.randint(MIN_GAP_WIDTH, MAX_GAP_WIDTH)
            
            while not self.is_gap_jumpable(gap, y - last_platform_y) and attempts < max_attempts:
                gap = random.randint(MIN_GAP_WIDTH, MAX_GAP_WIDTH)
                y = random.randint(int(min_y), int(max_y))
                attempts += 1
            
            # If we couldn't find a valid gap, use minimum gap
            if attempts >= max_attempts:
                gap = MIN_GAP_WIDTH
            
            current_x += width + gap
            last_platform_y = y
        
        # Create end sequence
        end_x = LEVEL_WIDTH - 400
        
        # Add final platforms
        final_platform = Platform(end_x + 50, LEVEL_HEIGHT - 150, 150, PLATFORM_HEIGHT)
        platforms.add(final_platform)
        
        powerup_platform = Platform(end_x + 250, LEVEL_HEIGHT - 200, 100, PLATFORM_HEIGHT)
        platforms.add(powerup_platform)
        
        # Add powerup box
        powerup_box = PowerUpBox(end_x + 275, LEVEL_HEIGHT - 250)
        self.game.powerup_boxes.add(powerup_box)
        
        # Add coins to end sequence
        for i in range(5):
            coin = Coin(end_x + 200 + i * 30, LEVEL_HEIGHT - 300)
            coins.add(coin)
        
        # Add end marker last
        end_marker = EndLevelMarker(end_x, 0, LEVEL_HEIGHT)
        foreground.add(end_marker)
        
        return background, midground, platforms, coins, enemies, foreground