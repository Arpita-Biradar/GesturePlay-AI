import math
import pygame
import random

from settings import *


class Level:
    def __init__(self):
        self.level_index = 1
        self.play_top = 72
        self.play_bottom = HEIGHT - 108
        self.floor_y = self.play_bottom - 32
        self.platforms = []
        self.floating_platforms = []
        self.collectibles = []
        self.hazards = []
        self.rng = random.Random()
        self.clouds = self._generate_clouds()
        self.mountains = self._generate_mountains()
        self._load_level(self.level_index)

    @staticmethod
    def score_to_level(score):
        if score < 0:
            return 1
        return min(MAX_LEVEL, score // LEVEL_SCORE_STEP + 1)

    def update_level_for_score(self, score):
        target_level = self.score_to_level(score)
        if target_level != self.level_index:
            self.level_index = target_level
            self._load_level(self.level_index)
            return True
        return False

    def _generate_clouds(self):
        return [
            (130, 90, 46),
            (340, 70, 34),
            (560, 100, 52),
            (780, 84, 42),
        ]

    def _generate_mountains(self):
        return [
            [(80, self.play_bottom - 45), (220, 150), (370, self.play_bottom - 45)],
            [(250, self.play_bottom - 45), (420, 130), (600, self.play_bottom - 45)],
            [(520, self.play_bottom - 45), (690, 155), (860, self.play_bottom - 45)],
        ]

    def _load_level(self, idx):
        difficulty = max(1, min(MAX_LEVEL, idx))

        self.platforms = [
            pygame.Rect(0, self.floor_y, WIDTH, 32),
        ]

        self.floating_platforms = [
            pygame.Rect(110 + difficulty * 7, self.floor_y - (90 + difficulty * 2), 220 - difficulty * 8, 22),
            pygame.Rect(400 - difficulty * 5, self.floor_y - (146 + difficulty * 2), 238 - difficulty * 6, 22),
            pygame.Rect(690 - difficulty * 8, self.floor_y - (98 + difficulty), 180 - difficulty * 4, 22),
        ]
        if difficulty >= 4:
            self.floating_platforms.append(pygame.Rect(510, self.floor_y - 208, 140, 20))

        self.platforms.extend(self.floating_platforms)

        self.hazards = []
        base_positions = [210, 390, 575, 760]
        hazard_count = min(len(base_positions), 1 + difficulty // 2)
        for i in range(hazard_count):
            width = 42 + difficulty * 3
            shift = difficulty * 9 if i % 2 == 0 else -difficulty * 6
            x = max(14, min(WIDTH - width - 14, base_positions[i] + shift))
            self.hazards.append(pygame.Rect(x, self.floor_y - 12, width, 12))

        if difficulty >= 3:
            mid = self.floating_platforms[1]
            self.hazards.append(pygame.Rect(mid.centerx - 24, mid.top - 12, 48, 12))
        if difficulty >= 6:
            top = self.floating_platforms[-1]
            self.hazards.append(pygame.Rect(top.centerx - 20, top.top - 10, 40, 10))

        self._spawn_collectibles(idx)

    def _spawn_collectibles(self, idx):
        rng = random.Random(100 + idx * 17)
        self.collectibles = []
        for plat in self.floating_platforms:
            x = rng.randint(plat.left + 22, plat.right - 22)
            y = plat.top - 14
            self.collectibles.append(
                {
                    "rect": pygame.Rect(x - 9, y - 9, 18, 18),
                    "taken": False,
                    "kind": "core",
                    "value": 24,
                }
            )

        ground = self.platforms[0]
        for _ in range(4):
            x = rng.randint(ground.left + 42, ground.right - 42)
            y = ground.top - 14
            self.collectibles.append(
                {
                    "rect": pygame.Rect(x - 8, y - 8, 16, 16),
                    "taken": False,
                    "kind": "coin",
                    "value": 12,
                }
            )

    def reset_collectibles(self):
        self._spawn_collectibles(self.level_index)

    def remaining_collectibles(self):
        return sum(0 if item["taken"] else 1 for item in self.collectibles)

    def collect(self, player_rect):
        gained = 0
        cores = 0
        coins = 0
        for item in self.collectibles:
            if item["taken"]:
                continue
            if player_rect.colliderect(item["rect"].inflate(10, 10)):
                item["taken"] = True
                gained += item["value"]
                if item["kind"] == "core":
                    cores += 1
                else:
                    coins += 1
        return gained, cores, coins

    def hit_hazard(self, player_rect):
        hurtbox = player_rect.inflate(-6, -4)
        for hazard in self.hazards:
            if hurtbox.colliderect(hazard):
                return True
        return False

    def get_platforms(self):
        return self.platforms

    def get_lab_door_rect(self):
        lab_main = pygame.Rect(52, self.play_bottom - 182, 206, 122)
        return pygame.Rect(lab_main.left + 82, lab_main.bottom - 56, 44, 52)

    def get_lab_door_spawn(self):
        door = self.get_lab_door_rect()
        return (door.centerx, self.floor_y)

    def _random_platform_width(self):
        w = 210 - self.level_index * 8 + self.rng.randint(-26, 26)
        return max(120, min(240, w))

    def _random_platform_y(self):
        top_min = self.play_top + 74
        top_max = self.floor_y - 74
        if top_min >= top_max:
            return self.floor_y - 110
        return self.rng.randint(top_min, top_max)

    def _recycle_floating_platforms(self):
        if not self.floating_platforms:
            return

        far_right = max([WIDTH] + [plat.right for plat in self.floating_platforms])
        for plat in self.floating_platforms:
            if plat.right >= -40:
                continue

            gap = self.rng.randint(120, 230)
            width = self._random_platform_width()
            x = far_right + gap
            y = self._random_platform_y()
            plat.update(x, y, width, plat.height)
            far_right = plat.right

    def _recycle_hazards(self):
        if not self.hazards:
            return

        far_right = max([WIDTH] + [hazard.right for hazard in self.hazards])
        for hazard in self.hazards:
            if hazard.right >= -24:
                continue

            width = 42 + self.level_index * 3 + self.rng.randint(-6, 8)
            width = max(32, min(72, width))
            if self.rng.random() < 0.35 and self.floating_platforms:
                target = self.rng.choice(self.floating_platforms)
                x = max(far_right + 70, target.centerx - width // 2)
                y = target.top - 12
            else:
                x = far_right + self.rng.randint(130, 260)
                y = self.floor_y - 12

            hazard.update(int(x), int(y), width, 12)
            far_right = hazard.right

    def _respawn_collectible(self, item):
        if item["kind"] == "core" and self.floating_platforms:
            platform = self.rng.choice(self.floating_platforms)
            pad = min(22, max(8, platform.width // 5))
            if platform.width <= pad * 2:
                x = platform.centerx
            else:
                x = self.rng.randint(platform.left + pad, platform.right - pad)
            y = platform.top - 14
            item["rect"].center = (x, y)
        else:
            right_edge = max([WIDTH] + [plat.right for plat in self.floating_platforms])
            x = right_edge + self.rng.randint(40, 220)
            item["rect"].center = (x, self.floor_y - 14)
        item["taken"] = False

    def _recycle_collectibles(self):
        for item in self.collectibles:
            if item["taken"] or item["rect"].right < -18:
                self._respawn_collectible(item)

    def scroll_world(self, dx):
        if dx == 0:
            return

        for plat in self.floating_platforms:
            plat.x += dx

        for hazard in self.hazards:
            hazard.x += dx

        for item in self.collectibles:
            item["rect"].x += dx

        self.clouds = [(x + dx * 0.16, y, size) for x, y, size in self.clouds]
        self.mountains = [
            [(px + dx * 0.08, py) for (px, py) in tri]
            for tri in self.mountains
        ]

        self._recycle_floating_platforms()
        self._recycle_hazards()
        self._recycle_collectibles()

    def draw_background(self, screen):
        for y in range(HEIGHT):
            t = y / max(HEIGHT - 1, 1)
            r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
            g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
            b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

        for tri in self.mountains:
            pygame.draw.polygon(screen, MOUNTAIN_COLOR, tri)
            shadow = [(tri[0][0] + 24, tri[0][1]), tri[1], (tri[2][0] - 24, tri[2][1])]
            pygame.draw.polygon(screen, MOUNTAIN_SHADOW, shadow)

        for x, y, size in self.clouds:
            pygame.draw.circle(screen, CLOUD_COLOR, (x, y), size // 2)
            pygame.draw.circle(screen, CLOUD_COLOR, (x + size // 3, y - 6), size // 3)
            pygame.draw.circle(screen, CLOUD_COLOR, (x - size // 3, y - 4), size // 3)
            pygame.draw.ellipse(screen, CLOUD_COLOR, (x - size // 2, y - size // 4, size, size // 2))

        lab_main = pygame.Rect(52, self.play_bottom - 182, 206, 122)
        lab_annex = pygame.Rect(lab_main.right - 56, lab_main.top + 30, 72, 84)
        roof = pygame.Rect(lab_main.left - 12, lab_main.top - 16, lab_main.width + 24, 20)

        shadow = [
            (lab_main.left + 18, lab_main.bottom + 2),
            (lab_annex.right + 36, lab_annex.bottom + 12),
            (lab_annex.right + 14, lab_annex.bottom + 20),
            (lab_main.left - 10, lab_main.bottom + 8),
        ]
        pygame.draw.polygon(screen, (70, 82, 106), shadow)

        pygame.draw.rect(screen, (119, 132, 159), lab_main, border_radius=8)
        pygame.draw.rect(screen, (84, 95, 120), lab_main, width=3, border_radius=8)
        pygame.draw.rect(screen, (101, 115, 142), lab_annex, border_radius=6)
        pygame.draw.rect(screen, (77, 88, 111), lab_annex, width=3, border_radius=6)

        pygame.draw.rect(screen, (68, 78, 103), roof, border_radius=8)
        pygame.draw.rect(screen, (47, 56, 78), roof, width=3, border_radius=8)
        skylight = pygame.Rect(roof.left + 24, roof.top + 5, roof.width - 48, 8)
        pygame.draw.rect(screen, (153, 221, 255), skylight, border_radius=4)
        pygame.draw.rect(screen, (95, 143, 173), skylight, width=2, border_radius=4)

        for row in range(2):
            for col in range(3):
                window = pygame.Rect(lab_main.left + 16 + col * 52, lab_main.top + 20 + row * 34, 34, 20)
                pygame.draw.rect(screen, (28, 45, 72), window, border_radius=3)
                pane = window.inflate(-4, -4)
                pygame.draw.rect(screen, (125, 213, 255), pane, border_radius=2)
                pygame.draw.line(screen, (210, 242, 255), (pane.left + 2, pane.top + 2), (pane.right - 2, pane.top + 2), 1)

        annex_window = pygame.Rect(lab_annex.left + 14, lab_annex.top + 18, 44, 22)
        pygame.draw.rect(screen, (28, 45, 72), annex_window, border_radius=3)
        pygame.draw.rect(screen, (132, 217, 255), annex_window.inflate(-4, -4), border_radius=2)

        door = self.get_lab_door_rect()
        pygame.draw.rect(screen, (47, 57, 81), door, border_radius=5)
        pygame.draw.rect(screen, (22, 29, 44), door, width=3, border_radius=5)
        pygame.draw.circle(screen, (230, 188, 86), (door.right - 9, door.centery), 3)
        step = pygame.Rect(door.left - 10, door.bottom - 2, door.width + 20, 8)
        pygame.draw.rect(screen, (90, 104, 132), step, border_radius=3)

        for y in range(lab_main.top + 14, lab_main.bottom - 10, 24):
            pygame.draw.line(screen, (142, 154, 179), (lab_main.left + 6, y), (lab_main.right - 6, y), 1)

        mast_x = roof.right - 22
        mast_top = roof.top - 28
        pygame.draw.line(screen, (196, 208, 232), (mast_x, roof.top + 2), (mast_x, mast_top), 2)
        pygame.draw.circle(screen, HUD_BLUE, (mast_x, mast_top), 4)
        pygame.draw.circle(screen, (166, 195, 232), (mast_x, mast_top), 9, width=1)
        pygame.draw.circle(screen, (151, 178, 213), (mast_x, mast_top), 15, width=1)

        vent = pygame.Rect(roof.left + 10, roof.top - 10, 18, 10)
        pygame.draw.rect(screen, (92, 103, 126), vent, border_radius=2)
        pygame.draw.rect(screen, (58, 66, 84), vent, width=2, border_radius=2)

        sign_left = pygame.Rect(lab_main.left + 20, lab_main.top - 36, 166, 24)
        pygame.draw.rect(screen, HUD_PANEL_DARK, sign_left, border_radius=6)
        pygame.draw.rect(screen, HUD_BLUE, sign_left, width=2, border_radius=6)
        font = pygame.font.SysFont("consolas", 15, bold=True)
        surf = font.render("RESEARCH LAB", True, HUD_WHITE)
        screen.blit(surf, (sign_left.centerx - surf.get_width() // 2, sign_left.top + 3))

        runway = pygame.Rect(0, self.play_bottom - 8, WIDTH, 18)
        pygame.draw.rect(screen, (84, 97, 122), runway)
        shift = int((pygame.time.get_ticks() / 45.0) % 44)
        for x in range(-shift, WIDTH + 44, 44):
            pygame.draw.rect(screen, (231, 236, 248), (x, runway.top + 6, 20, 4))

        pygame.draw.rect(screen, GROUND_COLOR, (0, self.play_bottom, WIDTH, HEIGHT - self.play_bottom))

    def _draw_stripes(self, screen, rect, offset=0):
        stripe_h = 8
        y = rect.top + offset
        x = rect.left
        while x < rect.right:
            pygame.draw.rect(screen, HAZARD_YELLOW, (x, y, 12, stripe_h))
            pygame.draw.rect(screen, HAZARD_BLACK, (x + 12, y, 12, stripe_h))
            x += 24

    def draw(self, screen):
        for plat in self.platforms:
            pygame.draw.rect(screen, PLATFORM_COLOR, plat, border_radius=2)
            pygame.draw.rect(screen, GROUND_EDGE, (plat.left, plat.top, plat.width, 4), border_radius=2)
            highlight = pygame.Rect(plat.left, plat.top + 4, plat.width, 3)
            pygame.draw.rect(screen, PLATFORM_HIGHLIGHT, highlight, border_radius=2)
            self._draw_stripes(screen, plat, offset=7)

        for hazard in self.hazards:
            spike_w = 14
            x = hazard.left
            while x + spike_w <= hazard.right:
                points = [(x, hazard.bottom), (x + spike_w // 2, hazard.top), (x + spike_w, hazard.bottom)]
                pygame.draw.polygon(screen, SPIKE_COLOR, points)
                pygame.draw.polygon(screen, (92, 108, 132), points, width=1)
                x += spike_w - 2

    def draw_collectibles(self, screen):
        time_s = pygame.time.get_ticks() / 1000.0
        for item in self.collectibles:
            if item["taken"]:
                continue

            rect = item["rect"]
            center = rect.center
            pulse = 1.0 + 0.16 * math.sin(time_s * 4 + center[0] * 0.04)
            glow_r = int(9 * pulse)

            if item["kind"] == "core":
                pygame.draw.circle(screen, COLLECTIBLE_GLOW, center, glow_r)
                pygame.draw.circle(screen, COLLECTIBLE_COLOR, center, 6)
                pygame.draw.circle(screen, HUD_WHITE, center, 2)
            else:
                pygame.draw.circle(screen, (255, 237, 180), center, glow_r)
                pygame.draw.circle(screen, COIN_COLOR, center, 6)
                pygame.draw.circle(screen, (248, 160, 45), center, 6, width=2)
