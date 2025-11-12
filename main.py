from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

sens = 50  # Mouse sensitivity
score = 0
score_text = Text(text=f'Score: {score}', position=(-0.85,0.45), scale=2)

class Target(Entity):
	def __init__(self):
		super().__init__(
			model='sphere',
			color=color.green,
			scale=0.3,
			position=(random.uniform(-5,5), random.uniform(1,4), random.uniform(5,15)),
			collider='sphere'
		)
	def input(self, key):
		global score
		if self.hovered and key == 'left mouse down':
			score += 1
			score_text.text = f'Score: {score}'
			destroy(self)
			spawn_target()

def spawn_target():
	Target()

player = FirstPersonController()
player.mouse_sensitivity = Vec2(sens, sens)
ground = Entity(model='plane', scale=50, texture='white_cube', texture_scale=(50,50), collider='box', color=color.gray)

window.exit_button.visible = False
window.title = 'Minimal FPS Aim Trainer'
window.vsync = False
window.fps = 0  # 0 means unlimited FPS in Ursina

spawn_target()

app.run()
