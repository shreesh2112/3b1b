import pygame
import math
import random

# 1. Setup constants
WIDTH, HEIGHT = 900, 900
CENTER = (WIDTH // 2, HEIGHT // 2)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
BLACK = (10, 10, 10) # Dark space

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Orbital Collision Avoidance System")
clock = pygame.time.Clock()

# 2. The Debris List: [a, b, angle, speed, orientation]
# a = semi-major axis, b = semi-minor axis
debris_list = []

def add_debris(count):
    for _ in range(count):
        a = random.randint(100, 400)
        b = random.randint(80, a) # Ellipse width
        angle = random.uniform(0, 6.28)
        speed = random.uniform(0.005, 0.02)
        rotation = random.uniform(0, 3.14) # Tilts the orbit
        debris_list.append([a, b, angle, speed, rotation])

# Start with a manageable 20 objects
add_debris(20)

running = True
while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k: # Press 'K' for Kessler Syndrome!
                add_debris(1000)

    # 3. Draw Earth
    pygame.draw.circle(screen, BLUE, CENTER, 40)

    # 4. Draw & Update Elliptical Debris
    for d in debris_list:
        a, b, angle, speed, rotation = d[0], d[1], d[2], d[3], d[4]
        d[2] += speed # Increment angle
        
        # Ellipse Math (X, Y)
        # Note: We add 'rotation' so not all ellipses are horizontal
        raw_x = a * math.cos(d[2])
        raw_y = b * math.sin(d[2])
        
        # Rotate the point to make orbits look realistic
        final_x = CENTER[0] + (raw_x * math.cos(rotation) - raw_y * math.sin(rotation))
        final_y = CENTER[1] + (raw_x * math.sin(rotation) + raw_y * math.cos(rotation))
        
        # Draw the debris dot
        pygame.draw.circle(screen, RED, (int(final_x), int(final_y)), 3)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()