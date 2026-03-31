import pygame
import math
import random

# 1. Setup constants
WIDTH, HEIGHT = 900, 900
CENTER = (WIDTH // 2, HEIGHT // 2)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
BLACK = (10, 10, 10)
FOV = 400  # Perspective constant (Field of View)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Orbital Collision Avoidance")
clock = pygame.time.Clock()

# Debris: [a, b, angle, speed, rotation, z]
debris_list = []

def add_debris(count):
    for _ in range(count):
        a = random.randint(150, 400)
        b = random.randint(100, a)
        angle = random.uniform(0, 6.28)
        speed = random.uniform(0.005, 0.02)
        rotation = random.uniform(0, 3.14)
        z = random.randint(-200, 200) # Depth coordinate
        debris_list.append([a, b, angle, speed, rotation, z])

# Start with a decent cloud
add_debris(50)

running = True
while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k: # Kessler Syndrome trigger
                add_debris(500)

    # 2. Draw Earth (Static at Z=0, so factor is 1)
    pygame.draw.circle(screen, BLUE, CENTER, 40)

    # 3. Draw & Update 3D Debris
    for d in debris_list:
        a, b, angle, speed, rotation, z = d[0], d[1], d[2], d[3], d[4], d[5]
        d[2] += speed # Update orbital position
        
        # Calculate raw 2D ellipse points
        raw_x = a * math.cos(d[2])
        raw_y = b * math.sin(d[2])
        
        # Apply Perspective Factor based on Z-depth
        # factor > 1 means it's close (Z is negative)
        # factor < 1 means it's far (Z is positive)
        factor = FOV / (FOV + z)
        
        # Rotate and Project to 2D Screen
        # We multiply the entire X/Y result by the perspective factor
        proj_x = CENTER[0] + (raw_x * math.cos(rotation) - raw_y * math.sin(rotation)) * factor
        proj_y = CENTER[1] + (raw_x * math.sin(rotation) + raw_y * math.cos(rotation)) * factor
        
        # 4. Visual Depth Cues
        size = max(1, int(5 * factor)) # Bigger = Closer
        shade = max(50, min(255, int(200 * factor))) # Brighter = Closer
        
        # Color based on depth: R (closer), G (middle), B (far)
        pygame.draw.circle(screen, (shade, 50, 50), (int(proj_x), int(proj_y)), size)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()