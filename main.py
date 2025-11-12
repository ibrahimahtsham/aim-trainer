#!/usr/bin/env python3
"""
Simple FPS Aim Trainer using Ursina.
Falls back gracefully if Ursina isn't installed.
"""

import sys
import random

try:
    from ursina import (
        Ursina, Entity, camera, color, mouse, Text, Slider, Button,
        Vec3, raycast, held_keys, time, destroy, window
    )
except ImportError:
    print("Ursina not installed. Install dependencies first: pip install -r requirements.txt")
    sys.exit(0)

# Configurable parameters
INITIAL_SENSITIVITY = 50  # range 1-100
TARGET_COUNT = 8
SPAWN_RADIUS = 25
TARGET_MIN_SIZE = 0.6
TARGET_MAX_SIZE = 1.4

app = Ursina(borderless=False)
window.title = 'Aim Trainer'
window.exit_button.visible = False
window.fps_counter.enabled = True

# Hide system mouse & lock for FPS feel (pointer lock keeps cursor inside window)
mouse.visible = False
window.cursor = False
mouse.locked = True  # lock captures the cursor so it stays centered / inside

# Game state
sensitivity_value = INITIAL_SENSITIVITY
hits = 0
shots = 0
start_time = time.time()

# Collections
targets = []

# UI Entities
menu_background = Entity(parent=camera.ui, model='quad', scale=(1.4,0.9), color=color.rgba(0,0,0,180), enabled=False, z=-1)
menu_title = Text(parent=menu_background, text='Settings', scale=2, position=(-0.27,0.35), enabled=False)

sensitivity_text = Text(parent=menu_background, text=f'Sensitivity: {sensitivity_value}', position=(-0.55,0.15), enabled=False)
sensitivity_slider = Slider(parent=menu_background, min=1, max=100, default=INITIAL_SENSITIVITY, step=1, scale=(0.8,0.7), position=(0,-0.05), enabled=False)
resume_button = Button(parent=menu_background, text='Resume', scale=(0.3,0.1), position=(0,-0.35), color=color.azure, enabled=False)

stats_text = Text(parent=camera.ui, text='', origin=(0,-0.5), position=(-0.88,0.45))

# Reticle
reticle = Entity(parent=camera.ui, model='quad', color=color.white, scale=(0.01,0.01), position=(0,0))

# Sensitivity application factor
SENSITIVITY_SCALE = 0.015  # base multiplier for rotation

# Camera rotation state
yaw = 0
pitch = 0
PITCH_LIMIT = 85


def spawn_target():
    size = random.uniform(TARGET_MIN_SIZE, TARGET_MAX_SIZE)
    # Random spherical distribution around origin, place targets in front hemisphere for convenience
    angle_yaw = random.uniform(-160, 160)
    angle_pitch = random.uniform(-30, 30)
    distance = random.uniform(8, SPAWN_RADIUS)
    # Convert to Cartesian
    rad_y = angle_yaw * 3.14159 / 180
    rad_p = angle_pitch * 3.14159 / 180
    x = distance * random.uniform(0.7,1.0) * -1 * __import__('math').sin(rad_y)
    z = distance * __import__('math').cos(rad_y)
    y = distance * __import__('math').sin(rad_p) * 0.4
    target = Entity(model='sphere', color=color.random_color(), scale=size, position=Vec3(x,y,z), collider='box')
    targets.append(target)


def populate_targets():
    for _ in range(TARGET_COUNT):
        spawn_target()


populate_targets()


def update_stats():
    elapsed = time.time() - start_time
    acc = (hits / shots * 100) if shots else 0
    stats_text.text = f"Hits: {hits}  Shots: {shots}  Acc: {acc:.1f}%  Time: {elapsed:.1f}s  Sens: {sensitivity_value}"


def toggle_menu():
    enabled = not menu_background.enabled
    for e in (menu_background, menu_title, sensitivity_text, sensitivity_slider, resume_button):
        e.enabled = enabled
    mouse.visible = enabled
    window.cursor = enabled
    mouse.locked = not enabled  # unlock when menu open so user can interact, lock during play
    if not enabled:
        # reclaim focus when resuming to ensure lock works
        try:
            window.request_focus()
        except Exception:
            pass


# Slider callback
sensitivity_slider.on_value_changed = lambda val: set_sensitivity(int(val))


def set_sensitivity(val: int):
    global sensitivity_value
    sensitivity_value = max(1, min(100, val))
    sensitivity_text.text = f'Sensitivity: {sensitivity_value}'


def resume():
    toggle_menu()

resume_button.on_click = resume


# Shooting logic
def shoot():
    global shots, hits
    shots += 1
    origin = camera.world_position
    direction = camera.forward
    hit_info = raycast(origin, direction, distance=SPAWN_RADIUS+5, ignore=[reticle])
    if hit_info.hit and hit_info.entity in targets:
        hits += 1
        destroy(hit_info.entity)
        targets.remove(hit_info.entity)
        spawn_target()
    update_stats()


# Ursina automatically calls update() each frame
def update():
    # Menu open: skip camera movement
    if menu_background.enabled:
        return

    global yaw, pitch
    # Ensure mouse stays locked during gameplay (e.g., after alt-tab)
    if not mouse.locked:
        mouse.locked = True
        mouse.visible = False
    # Mouse velocity gives delta movement
    mv = mouse.velocity
    if mv.length() > 0:
        yaw += mv.x * sensitivity_value * SENSITIVITY_SCALE * 60 * time.dt
        pitch -= mv.y * sensitivity_value * SENSITIVITY_SCALE * 60 * time.dt
        pitch = max(-PITCH_LIMIT, min(PITCH_LIMIT, pitch))
        camera.rotation_x = pitch
        camera.rotation_y = yaw

    if mouse.left:
        shoot()

    if held_keys.get('escape'):
        # Prevent rapid toggle: delay using a simple cooldown
        if not hasattr(toggle_menu, 'last_time') or time.time() - toggle_menu.last_time > 0.3:
            toggle_menu.last_time = time.time()
            toggle_menu()

    update_stats()


# Start with stats update
update_stats()

app.run()
