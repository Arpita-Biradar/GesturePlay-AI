import cv2
import pygame

from gesture_controller import GestureController
from home_screen import HomeScreen
from level import Level
from player import Player
from sound_manager import SoundManager
from settings import *


def draw_text(screen, text, font, color, pos):
    surf = font.render(text, True, color)
    screen.blit(surf, pos)


def _hex_points(rect, cut=12):
    return [
        (rect.left + cut, rect.top),
        (rect.right - cut, rect.top),
        (rect.right, rect.centery),
        (rect.right - cut, rect.bottom),
        (rect.left + cut, rect.bottom),
        (rect.left, rect.centery),
    ]


def draw_hex_panel(screen, rect, fill, border, cut=12):
    pts = _hex_points(rect, cut=cut)
    pygame.draw.polygon(screen, fill, pts)
    pygame.draw.polygon(screen, border, pts, width=2)


def camera_to_surface(frame, size):
    resized = cv2.resize(frame, size)
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    return pygame.image.frombuffer(rgb.tobytes(), size, "RGB").copy()


def draw_top_hud(screen, tiny_font, label_font, value_font, energy_pct, core_bank, score):
    left = pygame.Rect(16, 16, 290, 52)
    center = pygame.Rect(318, 16, 334, 52)

    draw_hex_panel(screen, left, HUD_PANEL, BUTTON_BORDER, cut=14)
    draw_hex_panel(screen, center, HUD_PANEL, BUTTON_BORDER, cut=14)

    draw_text(screen, "ENERGY", label_font, HUD_WHITE, (left.left + 38, left.top + 11))
    pygame.draw.polygon(
        screen,
        HUD_BLUE,
        [
            (left.left + 14, left.top + 33),
            (left.left + 22, left.top + 11),
            (left.left + 30, left.top + 18),
            (left.left + 23, left.top + 37),
        ],
    )

    bar_bg = pygame.Rect(left.left + 86, left.top + 26, left.width - 112, 12)
    pygame.draw.rect(screen, HUD_PANEL_DARK, bar_bg, border_radius=6)
    segments = 7
    seg_w = (bar_bg.width - 8) // segments
    filled = int((max(0, min(100, energy_pct)) / 100.0) * segments + 0.01)
    for i in range(segments):
        color = (100, 245, 121) if i < filled else (39, 63, 90)
        pygame.draw.rect(
            screen,
            color,
            (bar_bg.left + 4 + i * seg_w, bar_bg.top + 2, seg_w - 2, bar_bg.height - 4),
            border_radius=2,
        )

    draw_text(screen, "ENERGY CORES", label_font, HUD_WHITE, (center.left + 48, center.top + 11))
    draw_text(screen, f"{core_bank:04d}", value_font, HUD_WHITE, (center.right - 100, center.top + 9))
    pygame.draw.circle(screen, HUD_BLUE, (center.left + 24, center.top + 25), 10)
    pygame.draw.circle(screen, COLLECTIBLE_GLOW, (center.left + 24, center.top + 25), 6)

    draw_text(screen, f"SCORE {score}", tiny_font, (0, 0, 0), (24, 74))


def draw_camera_panel(screen, tiny_font, cam_frame):
    panel = pygame.Rect(WIDTH - CAMERA_SIZE[0] - 22, 16, CAMERA_SIZE[0] + 12, CAMERA_SIZE[1] + 34)
    pygame.draw.rect(screen, HUD_PANEL_DARK, panel, border_radius=10)
    pygame.draw.rect(screen, BUTTON_BORDER, panel, width=2, border_radius=10)
    draw_text(screen, "CAMERA", tiny_font, HUD_WHITE, (panel.left + 12, panel.top + 6))

    frame_rect = pygame.Rect(panel.left + 6, panel.top + 26, CAMERA_SIZE[0], CAMERA_SIZE[1])
    if cam_frame is not None:
        cam_surface = camera_to_surface(cam_frame, CAMERA_SIZE)
        screen.blit(cam_surface, frame_rect.topleft)
    else:
        pygame.draw.rect(screen, (45, 59, 92), frame_rect, border_radius=6)
        draw_text(screen, "OFFLINE", tiny_font, HUD_WHITE, (frame_rect.left + 42, frame_rect.top + 38))


def draw_bottom_hud(screen, tiny_font, value_font, score, distance_m, level_idx, coin_bank):
    gesture_panel = pygame.Rect(18, HEIGHT - 126, 240, 116)
    draw_hex_panel(screen, gesture_panel, HUD_PANEL_DARK, BUTTON_BORDER, cut=16)
    draw_text(screen, "GESTURE CONTROLS", tiny_font, HUD_WHITE, (gesture_panel.left + 44, gesture_panel.top + 10))
    draw_text(screen, "MOVE  : Hand Left/Right", tiny_font, HUD_BLUE, (gesture_panel.left + 14, gesture_panel.top + 34))
    draw_text(screen, "JUMP  : Hand Up", tiny_font, HUD_WHITE, (gesture_panel.left + 14, gesture_panel.top + 54))
    draw_text(screen, "CROUCH: Hand Down", tiny_font, HUD_WHITE, (gesture_panel.left + 14, gesture_panel.top + 74))
    draw_text(screen, "ATTACK: Fist", tiny_font, HUD_WHITE, (gesture_panel.left + 14, gesture_panel.top + 94))

    panel = pygame.Rect(WIDTH // 2 - 220, HEIGHT - 96, 440, 90)
    draw_hex_panel(screen, panel, HUD_PANEL_DARK, HUD_BLUE, cut=18)

    draw_text(screen, f"DISTANCE: {int(distance_m)} m", value_font, HUD_WHITE, (panel.left + 102, panel.top + 7))
    draw_text(screen, "RUN PROGRESS", value_font, HUD_WHITE, (panel.left + 136, panel.top + 58))

    if level_idx >= MAX_LEVEL:
        progress_ratio = 1.0
    else:
        progress_ratio = (score % LEVEL_SCORE_STEP) / float(LEVEL_SCORE_STEP)

    progress_rect = pygame.Rect(panel.left + 70, panel.top + 34, 300, 14)
    pygame.draw.rect(screen, (39, 53, 79), progress_rect, border_radius=6)
    fill_w = int(progress_rect.width * max(0.0, min(1.0, progress_ratio)))
    pygame.draw.rect(screen, HUD_BLUE, (progress_rect.left, progress_rect.top, fill_w, progress_rect.height), border_radius=6)

    marker_x = progress_rect.left + fill_w
    pygame.draw.circle(screen, HAZARD_YELLOW, (marker_x, progress_rect.centery), 6)
    draw_text(screen, f"LEVEL {level_idx}", tiny_font, HUD_GREEN, (panel.right - 98, panel.top + 8))

    coin_panel = pygame.Rect(WIDTH - 178, HEIGHT - 96, 160, 86)
    draw_hex_panel(screen, coin_panel, HUD_PANEL_DARK, HAZARD_YELLOW, cut=16)
    draw_text(screen, "COINS", tiny_font, HUD_WHITE, (coin_panel.left + 52, coin_panel.top + 12))
    draw_text(screen, f"{coin_bank:03d}", value_font, HAZARD_YELLOW, (coin_panel.left + 56, coin_panel.top + 38))
    pygame.draw.circle(screen, COIN_COLOR, (coin_panel.left + 32, coin_panel.top + 44), 12)
    pygame.draw.circle(screen, (255, 233, 168), (coin_panel.left + 32, coin_panel.top + 44), 5)


def main():
    pygame.init()
    flags = pygame.FULLSCREEN | pygame.SCALED
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    except pygame.error:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Gesture Runner")
    clock = pygame.time.Clock()

    tiny_font = pygame.font.SysFont("bahnschrift", 18, bold=True)
    label_font = pygame.font.SysFont("bahnschrift", 22, bold=True)
    value_font = pygame.font.SysFont("consolas", 30, bold=True)
    panel_font = pygame.font.SysFont("consolas", 20, bold=True)
    over_font = pygame.font.SysFont("bahnschrift", 62, bold=True)

    max_lives = 4
    level = Level()
    player = Player()
    home_screen = HomeScreen(level)
    sound = SoundManager()
    controller = GestureController()

    score = 0
    core_bank = 0
    coin_bank = 0
    distance_m = 0.0
    lives = max_lives
    gesture_label = "IDLE"
    damage_cooldown = 0
    paused = False
    game_over = False
    cam_frame = None
    running = True
    run_anchor_x = int(WIDTH * 0.58)
    game_state = "menu"
    game_over_sound_played = False

    sound.set_enabled(home_screen.sound_on)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif game_state == "playing":
                    if event.key == pygame.K_p:
                        paused = not paused
                        sound.play("ui_click")
                    if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                        if player.jump():
                            sound.play("jump")
                    if event.key == pygame.K_f:
                        player.attack()
                        sound.play("attack")
                    if event.key == pygame.K_r and game_over:
                        level = Level()
                        player = Player()
                        score = 0
                        core_bank = 0
                        coin_bank = 0
                        distance_m = 0.0
                        lives = max_lives
                        gesture_label = "IDLE"
                        damage_cooldown = 0
                        player.set_spawn(level.get_lab_door_spawn(), respawn_now=True)
                        paused = False
                        game_over = False
                        game_over_sound_played = False
                        sound.play("ui_click")

            if game_state == "menu":
                menu_action = home_screen.handle_event(event)
                if menu_action == "toggle_sound":
                    sound.set_enabled(home_screen.sound_on)
                    sound.play("ui_click")
                elif menu_action == "run":
                    player.set_spawn(home_screen.start_game_from_menu(), respawn_now=True)
                    player.facing = 1
                    paused = False
                    game_over = False
                    game_over_sound_played = False
                    sound.play("ui_click")
                    game_state = "playing"

        if game_state == "playing":
            keys = pygame.key.get_pressed()
            move_dir = 0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                move_dir = -1
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                move_dir = 1

            manual_crouch = keys[pygame.K_s] or keys[pygame.K_DOWN]
            controls, cam_frame = controller.get_gesture()
            if controls["direction"] != 0:
                move_dir = controls["direction"]
            if controls["jump"]:
                if player.jump():
                    sound.play("jump")
            if controls["attack"]:
                player.attack()
                sound.play("attack")
            player.set_crouch((controls["crouch"] or manual_crouch) and not paused)
            gesture_label = controls["label"]

            if not game_over and not paused:
                prev_x = player.rect.x
                player.update(move_dir, level.get_platforms())
                scroll_dx = 0
                if player.rect.centerx > run_anchor_x:
                    scroll_dx = player.rect.centerx - run_anchor_x
                    player.rect.centerx = run_anchor_x
                    level.scroll_world(-scroll_dx)

                delta_x = abs(player.rect.x - prev_x) + abs(scroll_dx)
                if delta_x > 0:
                    distance_m += delta_x * 0.35

                gained, cores, coins = level.collect(player.rect)
                if gained > 0:
                    score += gained
                    core_bank += cores * 25
                    coin_bank += coins
                    distance_m += gained * 0.12
                    if cores > 0:
                        sound.play("core")
                    if coins > 0:
                        sound.play("coin")

                if level.remaining_collectibles() == 0:
                    score += 30 + level.level_index * 5
                    coin_bank += 1
                    level.reset_collectibles()

                if level.update_level_for_score(score):
                    player.respawn()
                    damage_cooldown = 28
                    sound.play("level_up")

                if damage_cooldown > 0:
                    damage_cooldown -= 1

                if damage_cooldown == 0 and level.hit_hazard(player.rect):
                    lives -= 1
                    damage_cooldown = 52
                    player.respawn()
                    sound.play("hit")

                if player.rect.top > HEIGHT:
                    lives -= 1
                    damage_cooldown = 52
                    player.respawn()
                    sound.play("hit")

                if lives <= 0:
                    game_over = True
                    if not game_over_sound_played:
                        sound.play("game_over")
                        game_over_sound_played = True

            level.draw_background(screen)
            level.draw(screen)
            level.draw_collectibles(screen)
            player.draw(screen)

            energy_pct = int(100 * max(0, lives) / max_lives)
            draw_top_hud(screen, tiny_font, label_font, value_font, energy_pct, core_bank, score)
            draw_camera_panel(screen, tiny_font, cam_frame)
            draw_bottom_hud(screen, tiny_font, panel_font, score, distance_m, level.level_index, coin_bank)

            if paused and not game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((8, 14, 28, 120))
                screen.blit(overlay, (0, 0))
                draw_text(screen, "PAUSED", over_font, HUD_WHITE, (WIDTH // 2 - 120, HEIGHT // 2 - 60))

            if game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((10, 18, 35, 170))
                screen.blit(overlay, (0, 0))
                draw_text(
                    screen,
                    "MISSION FAILED",
                    pygame.font.SysFont("bahnschrift", 54, bold=True),
                    HUD_WHITE,
                    (WIDTH // 2 - 220, HEIGHT // 2 - 60),
                )
                draw_text(screen, "Press R to restart", value_font, HUD_GREEN, (WIDTH // 2 - 130, HEIGHT // 2 + 8))
        else:
            home_screen.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    controller.release()
    pygame.quit()


if __name__ == "__main__":
    main()
