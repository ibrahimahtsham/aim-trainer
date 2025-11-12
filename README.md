# Simple FPS Aim Trainer (Python + Panda3D)

## Features

- Mouse-look camera (no WASD movement).
- Click targets to score hits.
- Press `ESC` to open a menu overlay.
- Sensitivity slider (1–100) updates mouse look speed live (curved scaling for fine low-end control).
- Basic stats: total shots, hits, accuracy %.

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Controls

- Move mouse: look around.
- Left click: shoot (raycast from camera center).
- ESC: toggle settings menu.
- In menu: adjust sensitivity slider, click Resume to return.

## Next Ideas

- Add moving targets / spawn waves.
- Track reaction time per target.
- Add difficulty levels with smaller targets.
- Add session timer & end summary.

Enjoy training your aim!
