#!/usr/bin/env python3
"""
Simple FPS Aim Trainer using raw Panda3D (no Ursina).
Mouse is locked/hidden during play. ESC opens a menu with a sensitivity slider (1-100).
Click to shoot the target you're aiming at (center of screen).
Stats: hits / shots / accuracy / elapsed time / sensitivity.
"""

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectSlider, DirectButton, DirectFrame, DirectLabel
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import (
    WindowProperties, Vec3, Vec4, ClockObject, CollisionTraverser,
    CollisionHandlerQueue, CollisionNode, CollisionRay, BitMask32,
    CollisionSphere, loadPrcFileData
)
import random
import time

# Basic window config
loadPrcFileData('', 'window-title Aim Trainer (Panda3D)')
loadPrcFileData('', 'show-frame-rate-meter 1')
loadPrcFileData('', 'sync-video 0')  # disables vsync
loadPrcFileData('', 'clock-mode limited')  # disables frame limit
loadPrcFileData('', 'clock-frame-rate 0')  # unlimited FPS


class AimTrainer(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()  # we control the camera

        # Mouse/camera state
        self.yaw = 0.0
        self.pitch = 0.0
        self.pitch_limit = 85.0

        # Sensitivity model (degrees per pixel) range 1-100
        self.max_sens = 100
        self.sensitivity = 7  # default
        self.min_deg_per_px = 0.02
        self.max_deg_per_px = 0.9
        self.curve_exp = 1.15  # a bit more curve for finer low end control
        self.smoothing = 0.18
        self._prev_yaw_delta = 0.0
        self._prev_pitch_delta = 0.0

        # Stats
        self.hits = 0
        self.shots = 0
        self.start_time = time.time()

        # Scene setup
        self._setup_camera()
        self._setup_picker()
        self._setup_ui()
        self._setup_targets()

        self.menu_open = False
        self._lock_mouse()

        # Input
        self.accept('mouse1', self.on_shoot)
        self.accept('escape', self.toggle_menu)

        # Update task
        self.taskMgr.add(self.update_task, 'update')

    # ---------- Setup ----------
    def _setup_camera(self):
        self.cam.setPos(0, 0, 0)
        self.cam.setHpr(0, 0, 0)

        # Reticle: Onscreen small plus sign
        self.reticle = OnscreenText(text='+', fg=(1,1,1,1), pos=(0, 0), scale=0.08, mayChange=False)

    def _setup_picker(self):
        # Collision system for picking with a ray from camera center
        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()

        self.picker_node = CollisionNode('pickerRay')
        self.picker_node.setFromCollideMask(BitMask32.bit(1))  # collide with into mask 1
        self.picker_ray = CollisionRay()
        self.picker_node.addSolid(self.picker_ray)
        self.picker_np = self.camera.attachNewNode(self.picker_node)
        self.picker.addCollider(self.picker_np, self.pq)

    def _setup_ui(self):
        # Stats text (top-left)
        self.stats = OnscreenText(text='', fg=(1,1,1,1), pos=(-1.27, 0.9), align=0, scale=0.05, mayChange=True)

        # Menu overlay
        self.menu_frame = DirectFrame(frameColor=(0,0,0,0.7), frameSize=(-0.8,0.8,-0.5,0.5))
        self.menu_frame.hide()

        DirectLabel(text='Settings', scale=0.08, pos=(0, 0, 0.38), parent=self.menu_frame)
        self.sens_label = DirectLabel(text=f'Sensitivity: {self.sensitivity}', scale=0.05, pos=(-0.55, 0, 0.18), parent=self.menu_frame)

        self.sens_slider = DirectSlider(parent=self.menu_frame, range=(1, self.max_sens), value=self.sensitivity,
                                        pageSize=5, pos=(0, 0, 0.05), scale=0.7, command=self.on_sens_change)
        self.resume_btn = DirectButton(parent=self.menu_frame, text='Resume', scale=0.08, pos=(0, 0, -0.32), command=self.toggle_menu)

    def _setup_targets(self):
        self.targets = []
        for _ in range(10):
            self.spawn_target()

    # ---------- Mouse locking ----------
    def _lock_mouse(self):
        # Hide cursor and confine/relative behavior by constantly re-centering
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)
        self._center_mouse()

    def _unlock_mouse(self):
        props = WindowProperties()
        props.setCursorHidden(False)
        self.win.requestProperties(props)

    def _center_mouse(self):
        if not self.mouseWatcherNode.hasMouse():
            return
        cw = self.win.getXSize()
        ch = self.win.getYSize()
        self.win.movePointer(0, cw // 2, ch // 2)

    # ---------- Helpers ----------
    def _deg_per_pixel(self):
        t = (self.sensitivity / float(self.max_sens)) ** self.curve_exp
        return self.min_deg_per_px + (self.max_deg_per_px - self.min_deg_per_px) * t

    def update_stats(self):
        elapsed = time.time() - self.start_time
        acc = (self.hits / self.shots * 100.0) if self.shots else 0.0
        self.stats.setText(f"Hits: {self.hits}  Shots: {self.shots}  Acc: {acc:.1f}%  Time: {elapsed:.1f}s  Sens: {self.sensitivity}")

    # ---------- Menu / Sensitivity ----------
    def toggle_menu(self):
        self.menu_open = not self.menu_open
        if self.menu_open:
            self.menu_frame.show()
            self._unlock_mouse()
        else:
            self.menu_frame.hide()
            self._lock_mouse()
            # recenter so next frame delta is sane
            self._center_mouse()

    def on_sens_change(self):
        self.sensitivity = int(self.sens_slider['value'])
        self.sens_label['text'] = f'Sensitivity: {self.sensitivity}'

    # ---------- Targets ----------
    def spawn_target(self):
        # Use built-in smiley model for simplicity
        model = self.loader.loadModel('models/smiley')
        size = random.uniform(0.7, 1.4)
        model.setScale(size)
        # Position targets in a forward hemisphere
        yaw = random.uniform(-160, 160)
        pitch = random.uniform(-25, 25)
        dist = random.uniform(8, 25)
        # Convert to position
        from math import radians, sin, cos
        ry = radians(yaw)
        rp = radians(pitch)
        x = -sin(ry) * dist
        y = cos(ry) * dist
        z = sin(rp) * dist * 0.4
        model.setPos(x, y, z)
        model.setColor(random.random(), random.random(), random.random(), 1.0)
        model.reparentTo(self.render)

        # Collision sphere
        cs = CollisionSphere(0, 0, 0, 0.5 * size)
        cnode = CollisionNode('target')
        cnode.addSolid(cs)
        cnode.setIntoCollideMask(BitMask32.bit(1))
        cnp = model.attachNewNode(cnode)
        self.targets.append(model)

    # ---------- Shooting ----------
    def on_shoot(self):
        if self.menu_open:
            return
        self.shots += 1
        # Ray through center of lens
        self.picker_ray.setFromLens(self.camNode, 0, 0)
        self.picker.traverse(self.render)
        if self.pq.getNumEntries() > 0:
            self.pq.sortEntries()
            entry = self.pq.getEntry(0)
            # The collision node is named 'target'; get its parent model
            hit_np = entry.getIntoNodePath().getParent()
            if hit_np in self.targets:
                self.hits += 1
                hit_np.removeNode()
                self.targets.remove(hit_np)
                self.spawn_target()
        self.update_stats()

    # ---------- Per-frame update ----------
    def update_task(self, task):

        if not self.menu_open and self.mouseWatcherNode.hasMouse():
            # Pointer delta from window center, then recenter
            pointer = self.win.getPointer(0)
            cx = self.win.getXSize() // 2
            cy = self.win.getYSize() // 2
            dx = pointer.getX() - cx
            dy = pointer.getY() - cy
            self._center_mouse()

            if dx != 0 or dy != 0:
                deg_per_px = self._deg_per_pixel()
                # Invert yaw so moving mouse right rotates camera to the right (positive heading)
                delta_yaw = -dx * deg_per_px
                delta_pitch = -dy * deg_per_px
                # smoothing (EMA)
                if self.smoothing > 0:
                    delta_yaw = self._prev_yaw_delta * (1 - self.smoothing) + delta_yaw * self.smoothing
                    delta_pitch = self._prev_pitch_delta * (1 - self.smoothing) + delta_pitch * self.smoothing
                    self._prev_yaw_delta = delta_yaw
                    self._prev_pitch_delta = delta_pitch
                # No clamp: allow full delta for zero input delay

                self.yaw += delta_yaw
                self.pitch += delta_pitch
                if self.pitch > self.pitch_limit: self.pitch = self.pitch_limit
                if self.pitch < -self.pitch_limit: self.pitch = -self.pitch_limit
                self.cam.setHpr(self.yaw, self.pitch, 0)

        # Update stats text
        self.update_stats()
        return task.cont


if __name__ == '__main__':
    app = AimTrainer()
    app.run()
