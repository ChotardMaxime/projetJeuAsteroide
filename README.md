# Asteroid Defender

A mouse-controlled top-down shooter built with Python and Pygame. You're a spaceship in the center of the screen — enemies come from all sides and you have to survive as long as possible.

---

## Gameplay

- Your ship sits **fixed at the center** of the screen and rotates to face your mouse cursor.
- **Click** to shoot a bullet toward the cursor.
- Enemies spawn from the edges and move straight toward the center. If one reaches you, you take damage.
- Kill enemies to earn points. Collect drops for bonuses.
- Game ends when your HP hits 0.

### Enemy types

| Type | Speed | HP | Color |
|------|-------|----|-------|
| Normal | 2 | 2 | Red |
| Fast | 4 | 1 | Orange |
| Slow | 1 | 3 | Purple |

### Bonus drops (10% drop chance on kill)

| Drop | Color | Effect |
|------|-------|--------|
| HP | Green | +1 HP |
| Fire Rate | Yellow | Shoot twice as fast for 10s |
| Multiplier | Cyan | ×2 score for 10s |

Drops also move toward the center — you collect them automatically if they reach you.

---

## Installation

### Requirements

- Python 3.8+
- Pygame

### Install Pygame

```bash
pip install pygame
```

Or if you're using Python 3 explicitly:

```bash
pip3 install pygame
```

To verify it works:

```bash
python -c "import pygame; print(pygame.__version__)"
```

### Run the game

```bash
python asteroide_defender.py
```

No assets needed — everything is drawn programmatically.

---

## Code overview

The whole game runs in a single file with a classic Pygame loop.

### Architecture

No classes — everything is stored in plain Python **dicts** inside lists (`bullets`, `enemies`, `drops`, `effects`). Each entity is just `{'x', 'y', 'vx', 'vy', ...}`. Simple and readable, though it would start getting messy if the game grew much bigger.

### Main loop structure

Each frame (60 FPS via `clock.tick(60)`):
1. Clear screen
2. Tick down timers (shoot cooldown, active bonuses)
3. Handle events (quit, mouse click to shoot)
4. Move and draw bullets, cull off-screen ones
5. Spawn enemies randomly (`2%` chance per frame ≈ ~1.2 enemies/sec)
6. Move enemies, check collision with center and with bullets
7. Move and collect drops
8. Update and draw particle effects
9. Apply screen flash if the player just took damage
10. Draw the rotated player sprite

### Rotation

The player is a triangle drawn on a `pygame.Surface`. Each frame, `pygame.transform.rotate()` is called with the angle from `math.atan2()` between the center and the mouse. Clean enough, though it recalculates every frame even when the mouse doesn't move.

### Particles

`spawn_particles()` fires off a burst of small squares (`effects` list) with randomized angles and speeds. Each square shrinks as its `lifetime` counts down to zero (`size * lifetime/max_lifetime`), giving a natural fade-out without alpha math.

### Collision detection

Bullet-enemy collision uses `pygame.Rect.collidepoint()` on a bounding box built from the enemy's radius. It's approximate (circle vs point) but fast and feels fine in practice. Enemy-player collision is a simple Euclidean distance check against a hardcoded radius of 30px.

---

## Possible improvements

- Game over screen instead of a console print
- Persistent high score
- More enemy behaviors (homing, shooting back, etc.)
- Wave/difficulty progression
- Sound effects
