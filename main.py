import pygame
import cv2
from settings import *
from player import Player
from gesture_controller import GestureController

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Initialize our modules
player = Player()
controller = GestureController()

running = True
while running:
    # 1. Get Gesture Input
    command, should_jump, cam_frame = controller.get_gesture()
    
    # 2. Pygame Events (to close window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 3. Apply Gestures to Player
    if should_jump:
        player.jump()
    player.update(command)

    # 4. Drawing
    screen.fill(BLUE) # Sky
    pygame.draw.rect(screen, GROUND_COLOR, (0, HEIGHT-50, WIDTH, 50)) # Floor
    player.draw(screen)
    
    # Show webcam in a small window
    if cam_frame is not None:
        cv2.imshow("Controller Feed", cam_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    pygame.display.flip()
    clock.tick(FPS)

controller.release()
pygame.quit()
cv2.destroyAllWindows()