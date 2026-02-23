import math
import pygame

from settings import *


def _hex_points(rect, cut=12):
    return [
        (rect.left + cut, rect.top),
        (rect.right - cut, rect.top),
        (rect.right, rect.centery),
        (rect.right - cut, rect.bottom),
        (rect.left + cut, rect.bottom),
        (rect.left, rect.centery),
    ]


def _draw_hex_panel(screen, rect, fill, border, cut=12):
    pts = _hex_points(rect, cut=cut)
    pygame.draw.polygon(screen, fill, pts)
    pygame.draw.polygon(screen, border, pts, width=2)


def _draw_rounded_button(screen, rect, text, font, hovered=False):
    base = (45, 142, 230) if not hovered else (58, 164, 255)
    glow = (111, 212, 255) if hovered else (87, 187, 252)
    pygame.draw.rect(screen, glow, rect.inflate(8, 8), border_radius=16)
    pygame.draw.rect(screen, BUTTON_BORDER, rect.inflate(4, 4), width=2, border_radius=14)
    pygame.draw.rect(screen, base, rect, border_radius=12)
    pygame.draw.rect(screen, (32, 101, 176), rect, width=2, border_radius=12)

    hi = pygame.Rect(rect.left + 8, rect.top + 6, rect.width - 16, max(8, rect.height // 3))
    pygame.draw.rect(screen, (139, 220, 255), hi, border_radius=8)

    text_surf = font.render(text, True, HUD_WHITE)
    screen.blit(text_surf, (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2 + 1))


class HomeScreen:
    def __init__(self, level):
        self.level = level
        self.state = "home"
        self.sound_on = True

        self.title_font = pygame.font.SysFont("bahnschrift", 30, bold=True)
        self.body_font = pygame.font.SysFont("bahnschrift", 26, bold=False)
        self.small_font = pygame.font.SysFont("bahnschrift", 20, bold=False)
        self.button_font = pygame.font.SysFont("bahnschrift", 42, bold=True)
        self.alert_title_font = pygame.font.SysFont("bahnschrift", 36, bold=True)
        self.alert_body_font = pygame.font.SysFont("bahnschrift", 24, bold=False)
        self.alert_button_font = pygame.font.SysFont("bahnschrift", 30, bold=True)
        self.toggle_font = pygame.font.SysFont("bahnschrift", 24, bold=True)

        self.start_button = pygame.Rect(0, 0, 0, 0)
        self.run_button = pygame.Rect(0, 0, 0, 0)
        self.sound_button = pygame.Rect(WIDTH - 206, 18, 188, 44)

        self._reset_alien()

    def _reset_alien(self):
        door = self.level.get_lab_door_rect()
        self.alien_x = float(door.centerx - 12)
        self.alien_target_x = float(door.centerx + 126)
        self.alien_y = float(self.level.floor_y - 20)

    def reset(self):
        self.state = "home"
        self._reset_alien()

    def start_game_from_menu(self):
        return self.level.get_lab_door_spawn()

    def _draw_alien(self, screen):
        if self.state == "home" and self.alien_x < self.alien_target_x:
            self.alien_x += 2.1

        t = pygame.time.get_ticks() / 170.0
        bob = 2.8 * math.sin(t)
        leg_phase = math.sin(t * 1.65)
        x = int(self.alien_x)
        y = int(self.alien_y + bob)

        shadow = pygame.Rect(x - 18, y + 13, 36, 10)
        pygame.draw.ellipse(screen, (67, 87, 126), shadow)
        pygame.draw.ellipse(screen, (92, 112, 149), shadow.inflate(-8, -2), width=1)

        body = pygame.Rect(x - 13, y - 12, 26, 22)
        pygame.draw.ellipse(screen, (96, 223, 252), body)
        pygame.draw.ellipse(screen, (66, 170, 211), body, width=2)
        glow = body.inflate(-9, -10)
        glow.move_ip(2, -1)
        pygame.draw.ellipse(screen, (201, 249, 255), glow)

        head_center = (x, y - 16)
        pygame.draw.circle(screen, (104, 231, 255), head_center, 13)
        pygame.draw.circle(screen, (64, 176, 218), head_center, 13, width=2)
        pygame.draw.ellipse(screen, (16, 28, 45), (x - 10, y - 18, 7, 9))
        pygame.draw.ellipse(screen, (16, 28, 45), (x + 3, y - 18, 7, 9))
        pygame.draw.circle(screen, HUD_WHITE, (x - 4, y - 16), 1)
        pygame.draw.circle(screen, HUD_WHITE, (x + 9, y - 16), 1)

        lift = int(2 * leg_phase)
        left_foot = pygame.Rect(x - 10, y + 8 + max(0, lift), 8, 5)
        right_foot = pygame.Rect(x + 2, y + 8 + max(0, -lift), 8, 5)
        pygame.draw.ellipse(screen, (80, 200, 235), left_foot)
        pygame.draw.ellipse(screen, (80, 200, 235), right_foot)

        if self.state == "home":
            door = self.level.get_lab_door_rect()
            if x <= door.centerx + 44:
                steam = pygame.Rect(door.centerx - 8, door.top - 8, 24, 12)
                pygame.draw.ellipse(screen, (211, 242, 255), steam)
                pygame.draw.ellipse(screen, (230, 249, 255), steam.move(10, -5))

    def _draw_sound_toggle(self, screen, mouse_pos):
        hovered = self.sound_button.collidepoint(mouse_pos)
        bg = (37, 78, 136) if hovered else HUD_PANEL
        pygame.draw.rect(screen, bg, self.sound_button, border_radius=11)
        pygame.draw.rect(screen, BUTTON_BORDER, self.sound_button, width=2, border_radius=11)

        icon_center = (self.sound_button.left + 20, self.sound_button.centery)
        pygame.draw.polygon(
            screen,
            HAZARD_YELLOW if self.sound_on else (139, 154, 174),
            [
                (icon_center[0] - 7, icon_center[1] - 5),
                (icon_center[0] - 2, icon_center[1] - 5),
                (icon_center[0] + 4, icon_center[1] - 10),
                (icon_center[0] + 4, icon_center[1] + 10),
                (icon_center[0] - 2, icon_center[1] + 5),
                (icon_center[0] - 7, icon_center[1] + 5),
            ],
        )
        if self.sound_on:
            pygame.draw.arc(screen, HAZARD_YELLOW, (icon_center[0] + 2, icon_center[1] - 8, 9, 16), -0.8, 0.8, 2)
            pygame.draw.arc(screen, HAZARD_YELLOW, (icon_center[0] + 4, icon_center[1] - 11, 14, 22), -0.8, 0.8, 2)
        else:
            pygame.draw.line(screen, WARNING_RED, (icon_center[0] + 8, icon_center[1] - 8), (icon_center[0] + 18, icon_center[1] + 8), 2)
            pygame.draw.line(screen, WARNING_RED, (icon_center[0] + 8, icon_center[1] + 8), (icon_center[0] + 18, icon_center[1] - 8), 2)

        label = f"SOUND {'ON' if self.sound_on else 'OFF'}"
        surf = self.toggle_font.render(label, True, HUD_WHITE)
        screen.blit(surf, (self.sound_button.left + 40, self.sound_button.centery - surf.get_height() // 2))

    def _draw_home(self, screen, mouse_pos):
        top = pygame.Rect(16, 16, WIDTH - 32, 62)
        _draw_hex_panel(screen, top, HUD_PANEL, BUTTON_BORDER, cut=18)
        pygame.draw.circle(screen, HUD_BLUE, (top.left + 30, top.centery), 16)
        pygame.draw.circle(screen, (181, 247, 255), (top.left + 24, top.centery - 3), 4)
        pygame.draw.circle(screen, (181, 247, 255), (top.left + 36, top.centery - 3), 4)
        pygame.draw.arc(screen, (181, 247, 255), (top.left + 20, top.centery, 20, 10), 0.2, 2.9, 2)
        greeting = self.title_font.render("Hello User!", True, HUD_WHITE)
        screen.blit(greeting, (top.left + 58, top.top + 14))
        self._draw_sound_toggle(screen, mouse_pos)

        panel = pygame.Rect(WIDTH // 2 - 260, HEIGHT // 2 - 110, 520, 250)
        pygame.draw.rect(screen, (231, 243, 255), panel, border_radius=26)
        pygame.draw.rect(screen, (163, 204, 243), panel, width=4, border_radius=26)
        pygame.draw.line(screen, (179, 210, 238), (panel.left + 24, panel.top + 84), (panel.right - 24, panel.top + 84), 3)

        title = self.title_font.render("RESEARCH LAB ESCAPE", True, (44, 105, 168))
        msg1 = self.body_font.render("The alien is escaping the research lab.", True, (46, 62, 86))
        msg2 = self.body_font.render("Tap start and begin the run.", True, (46, 62, 86))
        screen.blit(title, (panel.centerx - title.get_width() // 2, panel.top + 28))
        screen.blit(msg1, (panel.centerx - msg1.get_width() // 2, panel.top + 106))
        screen.blit(msg2, (panel.centerx - msg2.get_width() // 2, panel.top + 138))

        self.start_button = pygame.Rect(panel.centerx - 140, panel.bottom - 74, 280, 54)
        hovered = self.start_button.collidepoint(mouse_pos)
        _draw_rounded_button(screen, self.start_button, "Start", self.button_font, hovered=hovered)

        footer = "Start here  ->  Alien exits lab  ->  Press Run  ->  Survive"
        footer_surf = self.small_font.render(footer, True, (49, 84, 129))
        footer_panel = pygame.Rect(0, HEIGHT - 64, WIDTH, 56)
        pygame.draw.rect(screen, (216, 236, 255), footer_panel)
        pygame.draw.rect(screen, (165, 199, 232), footer_panel, width=2)
        screen.blit(footer_surf, (WIDTH // 2 - footer_surf.get_width() // 2, HEIGHT - 44))

    def _draw_alert(self, screen, mouse_pos):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 17, 34, 175))
        screen.blit(overlay, (0, 0))

        box = pygame.Rect(WIDTH // 2 - 260, HEIGHT // 2 - 150, 520, 300)
        pygame.draw.rect(screen, (247, 251, 255), box, border_radius=20)
        pygame.draw.rect(screen, (76, 172, 255), box, width=4, border_radius=20)

        icon_center = (box.centerx, box.top + 56)
        pygame.draw.circle(screen, (87, 196, 255), icon_center, 22)
        pygame.draw.circle(screen, (228, 248, 255), (icon_center[0] - 7, icon_center[1] - 4), 4)
        pygame.draw.circle(screen, (228, 248, 255), (icon_center[0] + 7, icon_center[1] - 4), 4)
        pygame.draw.arc(screen, (228, 248, 255), (icon_center[0] - 8, icon_center[1] + 1, 16, 10), 0.2, 2.9, 2)

        title = self.alert_title_font.render("Alien Escape Alert", True, (29, 73, 128))
        line1 = self.alert_body_font.render("An alien was captured in the research lab.", True, (44, 59, 82))
        line2 = self.alert_body_font.render("It escaped. Press Run to begin the journey.", True, (44, 59, 82))
        screen.blit(title, (box.centerx - title.get_width() // 2, box.top + 94))
        screen.blit(line1, (box.centerx - line1.get_width() // 2, box.top + 140))
        screen.blit(line2, (box.centerx - line2.get_width() // 2, box.top + 170))

        self.run_button = pygame.Rect(box.centerx - 100, box.bottom - 72, 200, 48)
        hovered = self.run_button.collidepoint(mouse_pos)
        _draw_rounded_button(screen, self.run_button, "Run", self.alert_button_font, hovered=hovered)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        self.level.draw_background(screen)
        self._draw_alien(screen)
        self._draw_home(screen, mouse_pos)
        if self.state == "alert":
            self._draw_alert(screen, mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "home" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.state = "alert"
            elif self.state == "alert" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return "run"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.sound_button.collidepoint(event.pos):
                self.sound_on = not self.sound_on
                return "toggle_sound"
            if self.state == "home" and self.start_button.collidepoint(event.pos):
                self.state = "alert"
            elif self.state == "alert" and self.run_button.collidepoint(event.pos):
                return "run"
        return None
