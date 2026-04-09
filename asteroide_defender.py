import pygame
import math
import random

#--------Configuration et initialisation--------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
CENTER = (WIDTH // 2, HEIGHT // 2)

#--------Couleurs--------
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
BLUE = (0,100,255)
ORANGE = (255, 140, 0)
PURPLE = (160, 0, 200)

#--------Bonus-----------
BONUSES = {
    'hp':         {'color': (0, 255, 100), 'radius': 10},
    'fire_rate':  {'color': (255, 255, 0),  'radius': 10},
    'multiplier': {'color': (0, 220, 255),  'radius': 10},
}

# Chargement du vaisseau (ou création d'un rectangle si pas d'image)
player_img = pygame.Surface((50, 40), pygame.SRCALPHA)
pygame.draw.polygon(player_img, BLUE, [(0, 0), (50, 20), (0, 40)])  # Un triangle vers la droite

#--------Variables de jeu--------
bullets = []       # Liste de dict : {"x", "y", "vx", "vy"}
enemies = []       # Liste de dict : {"x", "y", "vx", "vy", "hp", "radius", "color"}
drops = []
effects = []       # Liste de dict : {'x','y','vx','vy','size','color','lifetime','max_lifetime'}
score = 0
running = True
player_hp = 3
shoot_cooldown = 0
SHOOT_DELAY = 15          # frames entre chaque tir (base)
score_multiplier = 1
multiplier_timer = 0      # frames restantes du multiplicateur (600 = 10s)
fire_rate_timer = 0       # frames restantes du bonus fire_rate
screen_flash = 0          # frames restantes du flash écran


def spawn_enemy():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':      x, y = random.randint(0, WIDTH), -30
    elif side == 'bottom': x, y = random.randint(0, WIDTH), HEIGHT + 30
    elif side == 'left':   x, y = -30, random.randint(0, HEIGHT)
    else:                  x, y = WIDTH + 30, random.randint(0, HEIGHT)

    dx, dy = CENTER[0] - x, CENTER[1] - y
    dist = math.sqrt(dx**2 + dy**2)

    enemy_type = random.choices(['normal', 'fast', 'slow'], weights=[50, 30, 20])[0]

    if enemy_type == 'normal':
        speed, hp, radius, color = 2, 2, 15, RED
    elif enemy_type == 'fast':
        speed, hp, radius, color = 4, 1, 10, ORANGE
    else:  # slow
        speed, hp, radius, color = 1, 3, 20, PURPLE

    enemies.append({
        'x': x, 'y': y,
        'vx': (dx / dist) * speed,
        'vy': (dy / dist) * speed,
        'hp': hp,
        'radius': radius,
        'color': color
    })


def spawn_drop(x, y):
    if random.random() < 0.10:
        bonus_type = random.choice(list(BONUSES.keys()))
        dx, dy = CENTER[0] - x, CENTER[1] - y
        dist = math.sqrt(dx**2 + dy**2)
        drops.append({
            'x': x, 'y': y,
            'vx': (dx / dist) * 1.5,
            'vy': (dy / dist) * 1.5,
            'type': bonus_type,
            'color': BONUSES[bonus_type]['color'],
            'radius': BONUSES[bonus_type]['radius'],
        })


def spawn_particles(x, y, color, count=8, speed=3, size=6, lifetime=30):
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        vx = math.cos(angle) * speed * random.uniform(0.5, 1.5)
        vy = math.sin(angle) * speed * random.uniform(0.5, 1.5)
        effects.append({
            'x': x, 'y': y,
            'vx': vx, 'vy': vy,
            'size': size,
            'color': color,
            'lifetime': lifetime,
            'max_lifetime': lifetime,
        })


# --- BOUCLE PRINCIPALE ---

while running:
    screen.fill(BLACK)

    # Décompte des timers
    if shoot_cooldown > 0:
        shoot_cooldown -= 1
    if multiplier_timer > 0:
        multiplier_timer -= 1
    else:
        score_multiplier = 1
    if fire_rate_timer > 0:
        fire_rate_timer -= 1

    # Gestion des évènements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if shoot_cooldown <= 0:
                mx, my = pygame.mouse.get_pos()
                dx, dy = mx - CENTER[0], my - CENTER[1]
                dist = math.sqrt(dx**2 + dy**2)
                if dist > 0:
                    bullets.append({
                        'x': CENTER[0], 'y': CENTER[1],
                        'vx': (dx / dist) * 7, 'vy': (dy / dist) * 7
                    })
                    shoot_cooldown = SHOOT_DELAY // 2 if fire_rate_timer > 0 else SHOOT_DELAY

    # Logique du joueur (rotation)
    mx, my = pygame.mouse.get_pos()
    angle_rad = math.atan2(my - CENTER[1], mx - CENTER[0])
    angle_deg = math.degrees(angle_rad)

    # Rotation de l'image
    rotated_player = pygame.transform.rotate(player_img, -angle_deg)
    player_rect = rotated_player.get_rect(center=CENTER)

    # Gestion des balles
    for b in bullets[:]:
        b['x'] += b['vx']
        b['y'] += b['vy']
        if not screen.get_rect().collidepoint(b['x'], b['y']):
            bullets.remove(b)
        else:
            pygame.draw.circle(screen, WHITE, (int(b['x']), int(b['y'])), 5)

    # Spawn ennemis
    if random.random() < 0.02:
        spawn_enemy()

    # Gestion des ennemis
    for e in enemies[:]:
        e['x'] += e['vx']
        e['y'] += e['vy']

        dist_to_center = math.sqrt((e['x'] - CENTER[0])**2 + (e['y'] - CENTER[1])**2)
        if dist_to_center < 30:
            player_hp -= 1
            screen_flash = 8
            spawn_particles(CENTER[0], CENTER[1], WHITE, count=12, speed=5, size=5, lifetime=25)
            enemies.remove(e)
            if player_hp <= 0:
                print(f"Game Over! Score = {score}")
                running = False
            continue

        r = e['radius']
        enemy_rect = pygame.Rect(e['x'] - r, e['y'] - r, r * 2, r * 2)
        pygame.draw.circle(screen, e['color'], (int(e['x']), int(e['y'])), r)

        for b in bullets[:]:
            if enemy_rect.collidepoint(b['x'], b['y']):
                if b in bullets:
                    bullets.remove(b)
                e['hp'] -= 1
                if e['hp'] <= 0 and e in enemies:
                    enemies.remove(e)
                    score += 1 * score_multiplier
                    spawn_particles(e['x'], e['y'], e['color'], count=10, speed=4, size=7, lifetime=35)
                    spawn_drop(e['x'], e['y'])
                break  # Une balle ne touche qu'un seul ennemi

    # Gestion des drops
    for d in drops[:]:
        d['x'] += d['vx']
        d['y'] += d['vy']
        pygame.draw.circle(screen, d['color'], (int(d['x']), int(d['y'])), d['radius'])

        if not screen.get_rect().collidepoint(d['x'], d['y']):
            drops.remove(d)
            continue

        dist_to_center = math.sqrt((d['x'] - CENTER[0])**2 + (d['y'] - CENTER[1])**2)
        if dist_to_center < 25:
            if d['type'] == 'hp':
                player_hp += 1
            elif d['type'] == 'fire_rate':
                fire_rate_timer = 600       # 10 secondes
            elif d['type'] == 'multiplier':
                score_multiplier = 2
                multiplier_timer = 600
            spawn_particles(d['x'], d['y'], d['color'], count=6, speed=2, size=4, lifetime=20)
            drops.remove(d)

    # Gestion des effets
    for ef in effects[:]:
        ef['x'] += ef['vx']
        ef['y'] += ef['vy']
        ef['lifetime'] -= 1
        ratio = ef['lifetime'] / ef['max_lifetime']
        size = max(1, int(ef['size'] * ratio))
        pygame.draw.rect(screen, ef['color'], (int(ef['x']), int(ef['y']), size, size))
        if ef['lifetime'] <= 0:
            effects.remove(ef)

    # Flash écran
    if screen_flash > 0:
        flash_surf = pygame.Surface((WIDTH, HEIGHT))
        flash_surf.set_alpha(min(180, screen_flash * 20))
        flash_surf.fill(WHITE)
        screen.blit(flash_surf, (0, 0))
        screen_flash -= 1

    # Affichage final
    screen.blit(rotated_player, player_rect)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()