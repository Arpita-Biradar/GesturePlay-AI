import pygame
from settings import *

class Player:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.rect.midbottom = (WIDTH // 2, HEIGHT - 142)
        self.spawn_point = self.rect.midbottom
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.crouching = False
        self.attack_timer = 0
        self.facing = 1

    def respawn(self):
        self.rect.width = PLAYER_WIDTH
        self.rect.height = PLAYER_HEIGHT
        self.rect.midbottom = self.spawn_point
        self.vel_y = 0
        self.on_ground = False
        self.crouching = False
        self.attack_timer = 0

    def set_crouch(self, should_crouch):
        target_height = PLAYER_CROUCH_HEIGHT if should_crouch and self.on_ground else PLAYER_HEIGHT
        if self.rect.height != target_height:
            bottom = self.rect.bottom
            self.rect.height = target_height
            self.rect.bottom = bottom
        self.crouching = should_crouch and self.on_ground

    def attack(self):
        self.attack_timer = ATTACK_FRAMES

    def update(self, move_dir, platforms):
        self.vel_x = move_dir * PLAYER_SPEED
        if move_dir != 0:
            self.facing = 1 if move_dir > 0 else -1

        # Horizontal motion and collision
        self.rect.x += int(round(self.vel_x))
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vel_x > 0:
                    self.rect.right = plat.left
                elif self.vel_x < 0:
                    self.rect.left = plat.right

        # Vertical motion and collision
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)
        self.rect.y += int(round(self.vel_y))
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vel_y > 0:
                    self.rect.bottom = plat.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = plat.bottom
                    self.vel_y = 0

        if self.attack_timer > 0:
            self.attack_timer -= 1

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

    def draw(self, screen):
        shadow_w = int(self.rect.width * 1.5)
        shadow_h = 6 if self.crouching else 8
        shadow = pygame.Rect(0, 0, shadow_w, shadow_h)
        shadow.center = (self.rect.centerx + self.facing, self.rect.bottom - 2)
        pygame.draw.ellipse(screen, (55, 73, 116), shadow)
        pygame.draw.ellipse(screen, (78, 96, 136), shadow.inflate(-10, -2), width=1)

        torso = pygame.Rect(self.rect.left + 4, self.rect.top + 9, self.rect.width - 8, self.rect.height - 10)
        if self.crouching:
            torso.y += 2
            torso.height -= 2

        arm_w = max(5, self.rect.width // 4)
        left_arm = pygame.Rect(torso.left - arm_w + 2, torso.top + 8, arm_w, torso.height - 10)
        right_arm = pygame.Rect(torso.right - 2, torso.top + 8, arm_w, torso.height - 10)
        pygame.draw.ellipse(screen, (87, 206, 238), left_arm)
        pygame.draw.ellipse(screen, (87, 206, 238), right_arm)
        pygame.draw.ellipse(screen, (66, 165, 204), left_arm, width=1)
        pygame.draw.ellipse(screen, (66, 165, 204), right_arm, width=1)

        pygame.draw.ellipse(screen, (95, 220, 247), torso)
        belly_highlight = torso.inflate(-8, -10)
        belly_highlight.move_ip(2, -1)
        pygame.draw.ellipse(screen, (188, 247, 255), belly_highlight)
        pygame.draw.ellipse(screen, (62, 163, 206), torso, width=2)

        left_foot = pygame.Rect(torso.centerx - 10, torso.bottom - 4, 9, 6)
        right_foot = pygame.Rect(torso.centerx + 1, torso.bottom - 4, 9, 6)
        pygame.draw.ellipse(screen, (93, 214, 242), left_foot)
        pygame.draw.ellipse(screen, (93, 214, 242), right_foot)
        pygame.draw.ellipse(screen, (61, 155, 193), left_foot, width=1)
        pygame.draw.ellipse(screen, (61, 155, 193), right_foot, width=1)

        head_radius = max(14, self.rect.width // 2 + 5)
        if self.crouching:
            head_radius -= 2
        head_center = (self.rect.centerx, torso.top - 6)

        tip_points = []
        for side in (-1, 1):
            base = (
                head_center[0] + side * int(head_radius * 0.56),
                head_center[1] - int(head_radius * 0.64),
            )
            tip = (base[0] + side * 6, base[1] - 14)
            tip_points.append((tip, side))
            pygame.draw.line(screen, (126, 236, 255), base, tip, 2)

        pygame.draw.circle(screen, (103, 229, 255), head_center, head_radius)
        face_glow_center = (head_center[0] - int(head_radius * 0.22), head_center[1] - int(head_radius * 0.3))
        pygame.draw.circle(screen, (198, 250, 255), face_glow_center, int(head_radius * 0.58))
        jaw_shadow = pygame.Rect(head_center[0] - head_radius + 2, head_center[1] + 4, head_radius * 2 - 4, head_radius - 2)
        pygame.draw.ellipse(screen, (63, 182, 225), jaw_shadow)
        pygame.draw.circle(screen, (61, 168, 209), head_center, head_radius, width=2)

        for tip, side in tip_points:
            pygame.draw.circle(screen, (112, 234, 255), tip, 4)
            pygame.draw.circle(screen, (211, 251, 255), (tip[0] - side, tip[1] - 1), 2)

        eye_w = int(head_radius * 0.74)
        eye_h = int(head_radius * 0.82)
        eye_y = head_center[1] + int(head_radius * 0.12)
        eye_dx = int(head_radius * 0.5)
        look_shift = self.facing
        left_eye = pygame.Rect(0, 0, eye_w, eye_h)
        right_eye = pygame.Rect(0, 0, eye_w, eye_h)
        left_eye.center = (head_center[0] - eye_dx + look_shift, eye_y)
        right_eye.center = (head_center[0] + eye_dx + look_shift, eye_y)
        for eye in (left_eye, right_eye):
            pygame.draw.ellipse(screen, (18, 27, 47), eye)
            eye_inner = eye.inflate(-4, -6)
            eye_inner.move_ip(1, -1)
            pygame.draw.ellipse(screen, (36, 49, 82), eye_inner)
            glint_pos = (eye.left + eye.width - 7, eye.top + 6)
            pygame.draw.circle(screen, HUD_WHITE, glint_pos, 3)

        pygame.draw.circle(screen, (26, 70, 104), (head_center[0] - 3, head_center[1] + int(head_radius * 0.34)), 1)
        pygame.draw.circle(screen, (26, 70, 104), (head_center[0] + 3, head_center[1] + int(head_radius * 0.34)), 1)
        mouth_rect = pygame.Rect(head_center[0] - 6, head_center[1] + int(head_radius * 0.38), 12, 8)
        pygame.draw.arc(screen, (26, 78, 112), mouth_rect, 0.25, 2.9, 2)

        if self.attack_timer > 0:
            pulse = self.attack_timer / float(ATTACK_FRAMES)
            hand = (torso.centerx + self.facing * (torso.width // 2 + 2), torso.centery + 2)
            bolt = (hand[0] + self.facing * (10 + int(8 * pulse)), hand[1] - 2)
            pygame.draw.line(screen, ATTACK_COLOR, hand, bolt, 4)
            orb_r = 4 + int(3 * pulse)
            pygame.draw.circle(screen, (120, 238, 255), bolt, orb_r)
            pygame.draw.circle(screen, HUD_WHITE, bolt, max(2, orb_r - 3))
