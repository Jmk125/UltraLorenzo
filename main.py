import pygame
import sys
import random
from datetime import datetime
from settings import *
from player import Player
from level import LevelGenerator
from camera import Camera


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("UltraLorenzo")
        self.clock = pygame.time.Clock()

        self.running = True
        self.state = "title"
        self.level_number = 1
        self.start_time = datetime.utcnow()
        self.username = "Jmk125"

        self.camera = None
        self.player = None
        self.level_generator = LevelGenerator(self)
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerup_boxes = pygame.sprite.Group()
        self.notifications = []
        self.current_theme = {"name": "Sky Realm", "sky": SKY_BLUE}
        self.title_particles = self.create_title_particles()
        self.selected_upgrade_index = 0  # For navigating level-up menu

    def create_title_particles(self):
        particles = []
        for _ in range(80):
            particles.append({
                "x": random.uniform(0, WINDOW_WIDTH),
                "y": random.uniform(0, WINDOW_HEIGHT),
                "speed": random.uniform(0.3, 1.2),
                "size": random.randint(1, 3)
            })
        return particles

    def start_run(self):
        self.level_number = 1
        self.start_time = datetime.utcnow()
        self.notifications.clear()
        self.setup_new_game()
        self.state = "playing"

    def setup_new_game(self):
        self.camera = Camera(LEVEL_WIDTH, LEVEL_HEIGHT)
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerup_boxes = pygame.sprite.Group()

        self.player = Player(self)
        self.all_sprites.add(self.player)
        self.generate_new_level()

    def get_difficulty_profile(self):
        level_index = max(1, self.level_number)
        gap_scale = min(1.0 + 0.05 * (level_index - 1), 1.7)
        enemy_density = min(0.25 + 0.05 * (level_index - 1), 0.8)
        moving_platform_chance = min(0.08 + 0.02 * (level_index - 1), 0.45)
        enemy_speed_scale = min(1.0 + 0.05 * (level_index - 1), 1.8)
        coin_cluster_size = min(4 + level_index, 8)
        mid_powerup_chance = max(0.4 - 0.03 * (level_index - 1), 0.15)
        return {
            "gap_scale": gap_scale,
            "enemy_density": enemy_density,
            "moving_platform_chance": moving_platform_chance,
            "enemy_speed_scale": enemy_speed_scale,
            "coin_cluster_size": coin_cluster_size,
            "mid_powerup_chance": mid_powerup_chance
        }

    def generate_new_level(self):
        if not self.player:
            return
        difficulty = self.get_difficulty_profile()
        background, midground, platforms, coins, enemies, powerups, foreground, theme = self.level_generator.generate_level(difficulty)

        self.platforms = platforms
        self.coins = coins
        self.enemies = enemies
        self.powerup_boxes = powerups
        self.current_theme = theme

        self.all_sprites.empty()
        for sprite in background:
            self.all_sprites.add(sprite)
        for sprite in midground:
            self.all_sprites.add(sprite)
        for sprite in foreground:
            self.all_sprites.add(sprite)
        for sprite in self.platforms:
            self.all_sprites.add(sprite)
        for sprite in self.powerup_boxes:
            self.all_sprites.add(sprite)
        for sprite in self.coins:
            self.all_sprites.add(sprite)
        for sprite in self.enemies:
            self.all_sprites.add(sprite)
        self.all_sprites.add(self.player)

        self.player.spawn()

    def push_notification(self, text, duration=2500):
        self.notifications.append({
            "text": text,
            "time": pygame.time.get_ticks(),
            "duration": duration
        })

    def on_level_complete(self):
        if not self.player:
            return
        self.player.reward_level_clear(self.level_number)
        self.level_number += 1

        # Check if player has pending level-ups
        if self.player.pending_level_ups > 0:
            self.state = "level_up"
            self.upgrade_choices = self.get_upgrade_choices()
            self.selected_upgrade_index = 0  # Reset selection
        else:
            self.generate_new_level()
            self.push_notification(f"World {self.level_number} intensifies")

    def get_upgrade_choices(self):
        """Generate 3 random upgrade choices for the level-up screen."""
        all_upgrades = [
            {"name": "Fleet Boots", "desc": f"Speed +{UPGRADE_SPEED_BOOST}"},
            {"name": "Sky Shoes", "desc": f"Jump +{UPGRADE_JUMP_BOOST}"},
            {"name": "Spirit Heart", "desc": "+1 Life"},
            {"name": "Treasure Sense", "desc": f"Score x{1 + UPGRADE_SCORE_MULTIPLIER:.2f}"},
        ]

        # Add fireball if player doesn't have it yet
        if not self.player.has_fireball and FIREBALL_ENABLED:
            all_upgrades.append({"name": "Fireball", "desc": "Press X to shoot!"})

        # Return 3 random unique choices
        import random
        return random.sample(all_upgrades, min(3, len(all_upgrades)))

    def game_over(self):
        self.state = "game_over"

    def update_gameplay(self):
        self.all_sprites.update()
        self.camera.update(self.player)

        coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
        for _ in coin_hits:
            self.player.collect_coin()

        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerup_boxes, False)
        for box in powerup_hits:
            reward = box.hit()
            if reward:
                self.player.apply_powerup_reward(reward)

    def draw_gameplay(self):
        self.screen.fill(self.current_theme.get("sky", SKY_BLUE))
        for sprite in self.all_sprites.sprites():
            if not (sprite == self.player and self.player.invulnerable and self.player.blinking):
                self.screen.blit(sprite.image, self.camera.apply(sprite))
        self.draw_hud()

    def draw_hud(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.player.score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))

        lives_text = font.render(f'Lives: {self.player.lives}', True, WHITE)
        self.screen.blit(lives_text, (10, 50))

        level_text = font.render(f'World: {self.level_number}', True, WHITE)
        self.screen.blit(level_text, (10, 90))

        player_text = font.render(f'Player: {self.username}', True, WHITE)
        self.screen.blit(player_text, (10, 130))

        elapsed_time = (datetime.utcnow() - self.start_time).seconds
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_text = font.render(f'Time: {minutes:02d}:{seconds:02d}', True, WHITE)
        self.screen.blit(time_text, (10, 170))

        xp_ratio = self.player.xp / self.player.xp_to_next if self.player.xp_to_next else 0
        bar_width = 260
        bar_rect = pygame.Rect(10, 210, bar_width, 20)
        pygame.draw.rect(self.screen, (255, 255, 255), bar_rect, 2)
        fill_rect = pygame.Rect(12, 212, int((bar_width - 4) * xp_ratio), 16)
        pygame.draw.rect(self.screen, (255, 215, 0), fill_rect)
        xp_text = font.render(f'Level {self.player.level}  XP {self.player.xp}/{self.player.xp_to_next}', True, WHITE)
        self.screen.blit(xp_text, (10, 240))

        theme_text = font.render(f'Biome: {self.current_theme.get("name", "")}', True, WHITE)
        self.screen.blit(theme_text, (10, 280))

        now = pygame.time.get_ticks()
        self.notifications = [n for n in self.notifications if now - n["time"] < n["duration"]]
        note_font = pygame.font.Font(None, 28)
        for index, note in enumerate(self.notifications):
            text_surface = note_font.render(note["text"], True, YELLOW)
            self.screen.blit(text_surface, (WINDOW_WIDTH - text_surface.get_width() - 20, 20 + index * 28))

    def draw_title_screen(self):
        self.screen.fill((8, 12, 35))
        for star in self.title_particles:
            star["y"] += star["speed"]
            if star["y"] > WINDOW_HEIGHT:
                star["y"] = 0
                star["x"] = random.uniform(0, WINDOW_WIDTH)
            pygame.draw.circle(self.screen, (200, 220, 255), (int(star["x"]), int(star["y"])), star["size"])

        title_font = pygame.font.Font(None, 96)
        title = title_font.render("UltraLorenzo", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        self.screen.blit(title, title_rect)

        subtitle_font = pygame.font.Font(None, 48)
        subtitle = subtitle_font.render("Rogue Run", True, (255, 215, 0))
        sub_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3 + 60))
        self.screen.blit(subtitle, sub_rect)

        info_font = pygame.font.Font(None, 28)
        lines = [
            "Procedural worlds with escalating danger",
            "Defeat enemies & collect coins to gain XP",
            "Level up to choose powerful upgrades",
            "Clear all collectibles to unlock exit",
            "Arrow keys to move, SPACE to jump",
            "Hold SHIFT to run & jump farther",
            "Press X to shoot (when unlocked)",
            "Press SPACE or ENTER to begin"
        ]
        for idx, line in enumerate(lines):
            text = info_font.render(line, True, WHITE)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + idx * 30))
            self.screen.blit(text, rect)

    def draw_game_over(self):
        self.screen.fill((15, 5, 20))
        font_large = pygame.font.Font(None, 72)
        text = font_large.render('Run Over', True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3))
        self.screen.blit(text, text_rect)

        font = pygame.font.Font(None, 40)
        score_text = font.render(f'Score: {self.player.score}', True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 20))
        self.screen.blit(score_text, score_rect)

        level_text = font.render(f'World Reached: {self.level_number}', True, WHITE)
        level_rect = level_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 20))
        self.screen.blit(level_text, level_rect)

        xp_text = font.render(f'Hero Level: {self.player.level}', True, WHITE)
        xp_rect = xp_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 60))
        self.screen.blit(xp_text, xp_rect)

        restart_text = font.render('Press R to return to the title', True, (255, 215, 0))
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 120))
        self.screen.blit(restart_text, restart_rect)

    def draw_level_up(self):
        """Draw the full-screen level-up menu with navigable list."""
        # Full-screen gradient background
        for y in range(WINDOW_HEIGHT):
            color_value = int(20 + (y / WINDOW_HEIGHT) * 40)
            pygame.draw.line(self.screen, (color_value // 3, color_value // 4, color_value),
                           (0, y), (WINDOW_WIDTH, y))

        # Animated particles/stars
        current_time = pygame.time.get_ticks()
        for i in range(30):
            x = (i * 97 + current_time // 20) % WINDOW_WIDTH
            y = (i * 73) % WINDOW_HEIGHT
            size = 1 + (i % 3)
            pygame.draw.circle(self.screen, (255, 255, 200, 100), (x, y), size)

        # Title with glow effect
        title_font = pygame.font.Font(None, 96)
        title = title_font.render("LEVEL UP!", True, (255, 215, 0))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        # Glow effect
        glow = title_font.render("LEVEL UP!", True, (255, 150, 0))
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_rect = glow.get_rect(center=(WINDOW_WIDTH // 2 + offset[0], 100 + offset[1]))
            self.screen.blit(glow, glow_rect)
        self.screen.blit(title, title_rect)

        # Level info with stats
        info_font = pygame.font.Font(None, 40)
        level_text = info_font.render(f"Hero Level {self.player.level}", True, WHITE)
        level_rect = level_text.get_rect(center=(WINDOW_WIDTH // 2, 170))
        self.screen.blit(level_text, level_rect)

        stats_font = pygame.font.Font(None, 28)
        stats = f"Score: {self.player.score}  |  Lives: {self.player.lives}  |  World: {self.level_number}"
        stats_text = stats_font.render(stats, True, (200, 200, 200))
        stats_rect = stats_text.get_rect(center=(WINDOW_WIDTH // 2, 210))
        self.screen.blit(stats_text, stats_rect)

        # Instructions
        instruction_font = pygame.font.Font(None, 32)
        instruction = instruction_font.render("Use UP/DOWN arrows to navigate, ENTER or SPACE to select", True, (180, 180, 180))
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, 260))
        self.screen.blit(instruction, instruction_rect)

        # Draw upgrade options as a vertical list
        option_font = pygame.font.Font(None, 48)
        desc_font = pygame.font.Font(None, 32)

        box_width = 600
        box_height = 90
        spacing = 20
        start_y = 320
        start_x = (WINDOW_WIDTH - box_width) // 2

        for i, upgrade in enumerate(self.upgrade_choices):
            y = start_y + i * (box_height + spacing)
            is_selected = (i == self.selected_upgrade_index)

            # Draw box background with selection highlight
            box_rect = pygame.Rect(start_x, y, box_width, box_height)
            if is_selected:
                # Selected item - bright and pulsing
                pulse = abs((current_time // 10) % 100 - 50) / 50.0
                glow_color = (80 + int(40 * pulse), 60 + int(30 * pulse), 100 + int(50 * pulse))
                # Draw glow
                glow_rect = pygame.Rect(start_x - 5, y - 5, box_width + 10, box_height + 10)
                pygame.draw.rect(self.screen, glow_color, glow_rect, border_radius=10)
                pygame.draw.rect(self.screen, (100, 80, 140), box_rect, border_radius=8)
                pygame.draw.rect(self.screen, (255, 215, 0), box_rect, 4, border_radius=8)
                # Selection arrow
                arrow_font = pygame.font.Font(None, 60)
                arrow = arrow_font.render("▶", True, (255, 215, 0))
                arrow_rect = arrow.get_rect(center=(start_x - 40, y + box_height // 2))
                self.screen.blit(arrow, arrow_rect)
            else:
                # Unselected item - darker
                pygame.draw.rect(self.screen, (40, 30, 60), box_rect, border_radius=8)
                pygame.draw.rect(self.screen, (120, 100, 140), box_rect, 2, border_radius=8)

            # Draw upgrade name (larger if selected)
            name_font = option_font if is_selected else pygame.font.Font(None, 42)
            name_text = name_font.render(upgrade["name"], True, WHITE if is_selected else (200, 200, 200))
            name_rect = name_text.get_rect(midleft=(start_x + 30, y + 30))
            self.screen.blit(name_text, name_rect)

            # Draw upgrade description
            desc_text = desc_font.render(upgrade["desc"], True, (220, 220, 220) if is_selected else (150, 150, 150))
            desc_rect = desc_text.get_rect(midleft=(start_x + 30, y + 60))
            self.screen.blit(desc_text, desc_rect)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif self.state == "playing":
                        if event.key == pygame.K_SPACE:
                            self.player.jump()
                        elif event.key == pygame.K_x:
                            self.player.shoot_fireball()
                    elif self.state == "title" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.start_run()
                    elif self.state == "game_over" and event.key == pygame.K_r:
                        self.state = "title"
                    elif self.state == "level_up":
                        if event.key == pygame.K_UP:
                            self.selected_upgrade_index = (self.selected_upgrade_index - 1) % len(self.upgrade_choices)
                        elif event.key == pygame.K_DOWN:
                            self.selected_upgrade_index = (self.selected_upgrade_index + 1) % len(self.upgrade_choices)
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self.apply_upgrade_choice(self.selected_upgrade_index)

            if self.state == "playing":
                self.update_gameplay()
                self.draw_gameplay()
            elif self.state == "title":
                self.draw_title_screen()
            elif self.state == "level_up":
                self.draw_level_up()
            else:
                self.draw_game_over()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def apply_upgrade_choice(self, choice_index):
        """Apply the selected upgrade and proceed."""
        upgrade = self.upgrade_choices[choice_index]
        self.player.apply_upgrade(upgrade["name"])
        self.player.pending_level_ups -= 1

        # If more level-ups pending, show another screen
        if self.player.pending_level_ups > 0:
            self.upgrade_choices = self.get_upgrade_choices()
            self.selected_upgrade_index = 0  # Reset selection for next screen
        else:
            # No more level-ups, continue to next level
            self.state = "playing"
            self.generate_new_level()
            self.push_notification(f"World {self.level_number} intensifies")


if __name__ == "__main__":
    game = Game()
    game.run()
