import pygame
import math
import random
import numpy as np
from scipy.integrate import dblquad

# --- 1. PROBABILITY ENGINE (The Physicist) ---
def calculate_pc(dist_3d, combined_radius=15, sigma=25):
    """Calculates Pc using Foster's 2D Gaussian Integration on the Encounter Plane"""
    def pdf(y, x):
        exponent = -0.5 * ((x - dist_3d)**2 / sigma**2 + y**2 / sigma**2)
        return (1.0 / (2 * np.pi * sigma**2)) * np.exp(exponent)

    # High-fidelity double integral over the collision cross-section
    pc, _ = dblquad(pdf, -combined_radius, combined_radius,
                    lambda x: -math.sqrt(max(0, combined_radius**2 - x**2)),
                    lambda x: math.sqrt(max(0, combined_radius**2 - x**2)))
    return pc

# --- 2. SETUP & CONSTANTS ---
WIDTH, HEIGHT = 900, 900
CENTER = (WIDTH // 2, HEIGHT // 2)
BLUE, WHITE, RED, GREEN, BLACK, GOLD = (0, 100, 255), (255, 255, 255), (255, 50, 50), (50, 255, 50), (10, 10, 10), (255, 215, 0)
FOV = 400 

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Orbital Guardian: CAS v1.0")
font_small = pygame.font.SysFont("Consolas", 12)
font_bold = pygame.font.SysFont("Consolas", 16, bold=True)
clock = pygame.time.Clock()

# Debris: [a, b, angle, speed, rotation, z, id]
debris_list = []
def add_debris(count):
    start_id = len(debris_list)
    for i in range(count):
        a = random.randint(160, 420)
        b = random.randint(120, a)
        angle = random.uniform(0, 6.28)
        speed = random.uniform(0.003, 0.007)
        rotation = random.uniform(0, 3.14)
        z = random.randint(-200, 200)
        debris_list.append([a, b, angle, speed, rotation, z, start_id + i])

add_debris(50)

# Rocket State
rocket = {
    'x': 0, 'y': 0, 'z': 250,
    'vx': random.uniform(-0.3, 0.3), 
    'vy': random.uniform(-0.3, 0.3), 
    'vz': -0.6,
    'history': []
}

# --- 3. UI/UX DRAWING FUNCTIONS (The Creative Director) ---
def draw_ui_overlay(screen, mission_time, active_threats):
    # Corner Borders
    pygame.draw.rect(screen, (40, 40, 40), (10, 10, WIDTH-20, HEIGHT-20), 1)
    
    # Top Left: Telemetry
    screen.blit(font_bold.render("L-V TELEMETRY", True, GREEN), (30, 30))
    screen.blit(font_small.render(f"TIME: {mission_time//1000}s", True, WHITE), (30, 50))
    screen.blit(font_small.render(f"VEL: {abs(rocket['vz']):.2f} km/s", True, WHITE), (30, 65))
    
    # Top Right: System Status
    status = "CRITICAL" if active_threats else "NOMINAL"
    color = RED if active_threats else GREEN
    screen.blit(font_bold.render(f"STATUS: {status}", True, color), (WIDTH-200, 30))
    
    # Bottom Left: Coordinate Frame
    pygame.draw.line(screen, RED, (50, HEIGHT-50), (80, HEIGHT-50), 2) # X
    pygame.draw.line(screen, GREEN, (50, HEIGHT-50), (50, HEIGHT-80), 2) # Y
    screen.blit(font_small.render("X-AXIS", True, RED), (85, HEIGHT-55))
    screen.blit(font_small.render("Y-AXIS", True, GREEN), (35, HEIGHT-100))

def draw_reticle(screen, rx, ry, status_color):
    size = 12
    pygame.draw.line(screen, status_color, (rx-size, ry-size), (rx-size+5, ry-size), 2)
    pygame.draw.line(screen, status_color, (rx-size, ry-size), (rx-size, ry-size+5), 2)
    pygame.draw.line(screen, status_color, (rx+size, ry+size), (rx+size-5, ry+size), 2)
    pygame.draw.line(screen, status_color, (rx+size, ry+size), (rx+size, ry+size-5), 2)

# --- 4. MAIN LOOP ---
running = True
while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_k: add_debris(100)

    # A. UPDATE DEBRIS & COLLISION MONITORING
    active_threats = []
    current_debris_coords = []
    
    for d in debris_list:
        d[2] += d[3] # Update orbital angle
        raw_x, raw_y = d[0] * math.cos(d[2]), d[1] * math.sin(d[2])
        # Original 3D Rotation
        rot_x = (raw_x * math.cos(d[4]) - raw_y * math.sin(d[4]))
        rot_y = (raw_x * math.sin(d[4]) + raw_y * math.cos(d[4]))
        current_debris_coords.append((rot_x, rot_y, d[5]))
        
        # 3D Distance Formula (Navigator)
        dist_3d = math.sqrt((rot_x - rocket['x'])**2 + (rot_y - rocket['y'])**2 + (d[5] - rocket['z'])**2)
        
        if dist_3d < 45: # Conjunction Search Radius
            pc = calculate_pc(dist_3d)
            if pc > 1e-4:
                active_threats.append({'pos': (rot_x, rot_y, d[5]), 'pc': pc, 'id': d[6]})

    # B. NAVIGATOR: CALCULATE ADVISORY PATH
    recommended_path = []
    if active_threats:
        # Sort by highest risk
        threat = max(active_threats, key=lambda x: x['pc'])['pos']
        tx, ty, tz = rocket['x'], rocket['y'], rocket['z']
        # Projected Evasion Vector
        dx, dy, dz = tx - threat[0], ty - threat[1], tz - threat[2]
        mag = math.sqrt(dx**2 + dy**2 + dz**2)
        v_evade = (rocket['vx'] + (dx/mag)*0.8, rocket['vy'] + (dy/mag)*0.8, rocket['vz'] + (dz/mag)*0.8)
        
        for t_step in range(40): # Look 40 steps ahead
            tx += v_evade[0]; ty += v_evade[1]; tz += v_evade[2]
            recommended_path.append((tx, ty, tz))

    # C. UPDATE ROCKET (Maintain original path)
    rocket['x'] += rocket['vx']
    rocket['y'] += rocket['vy']
    rocket['z'] += rocket['vz']
    rocket['history'].append((rocket['x'], rocket['y'], rocket['z']))
    if len(rocket['history']) > 300: rocket['history'].pop(0)

    # D. DRAWING ENVIRONMENT
    # 1. Earth
    pygame.draw.circle(screen, BLUE, CENTER, 40)
    pygame.draw.circle(screen, (0, 50, 150), CENTER, 45, 1) # Atmos. Glow

    # 2. Draw Recommended Advisory Path (Gold)
    if len(recommended_path) > 2:
        for i in range(1, len(recommended_path)):
            p1, p2 = recommended_path[i-1], recommended_path[i]
            f1, f2 = FOV/(FOV+p1[2]), FOV/(FOV+p2[2])
            pygame.draw.line(screen, GOLD, (CENTER[0]+p1[0]*f1, CENTER[1]+p1[1]*f1), 
                             (CENTER[0]+p2[0]*f2, CENTER[1]+p2[1]*f2), 2)

    # 3. Draw Actual Trajectory (Green)
    for i in range(1, len(rocket['history'])):
        h1, h2 = rocket['history'][i-1], rocket['history'][i]
        f1, f2 = FOV/(FOV+h1[2]), FOV/(FOV+h2[2])
        alpha = int(180 * (i/len(rocket['history'])))
        pygame.draw.line(screen, (0, alpha, 0), (CENTER[0]+h1[0]*f1, CENTER[1]+h1[1]*f1), 
                         (CENTER[0]+h2[0]*f2, CENTER[1]+h2[1]*f2), 1)

    # 4. Draw Debris
    for idx, d_pos in enumerate(current_debris_coords):
        factor = FOV / (FOV + d_pos[2])
        color = (100, 40, 40)
        for t in active_threats:
            if debris_list[idx][6] == t['id']: color = WHITE
        
        px, py = CENTER[0] + d_pos[0]*factor, CENTER[1] + d_pos[1]*factor
        pygame.draw.circle(screen, color, (int(px), int(py)), int(3 * factor))

    # 5. Draw Rocket & Reticle
    rf = FOV / (FOV + rocket['z'])
    rx, ry = CENTER[0] + rocket['x']*rf, CENTER[1] + rocket['y']*rf
    r_color = WHITE if active_threats else GREEN
    pygame.draw.circle(screen, r_color, (int(rx), int(ry)), int(6 * rf))
    draw_reticle(screen, rx, ry, r_color)

    # 4. NAVIGATOR: CALCULATE "RECOMMENDED" PATH (DO NOT APPLY)
    recommended_points = []
    if active_threats:
        # Calculate a 60-frame "What-if" projection
        temp_vx, temp_vy, temp_vz = rocket['vx'], rocket['vy'], rocket['vz']
        temp_x, temp_y, temp_z = rocket['x'], rocket['y'], rocket['z']
        
        # Apply evasion logic to the TEMP variables only
        threat = active_threats[0]['pos']
        dx, dy, dz = temp_x - threat[0], temp_y - threat[1], temp_z - threat[2]
        mag = math.sqrt(dx**2 + dy**2 + dz**2)
        
        # Suggested delta-v
        temp_vx += (dx/mag) * 0.8 
        temp_vy += (dy/mag) * 0.8
        temp_vz += (dz/mag) * 0.8
        
    # 6. HUD
    draw_ui_overlay(screen, pygame.time.get_ticks(), active_threats)
    if active_threats:
        screen.blit(font_bold.render("ADVISORY: EXECUTE GOLD MANEUVER", True, GOLD), (WIDTH//2 - 150, HEIGHT - 60))

    pygame.display.flip()
    clock.tick(30) # Cinematic Framerate

pygame.quit()
