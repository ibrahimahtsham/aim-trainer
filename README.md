# 3D Aim Trainer

A minimal modular 3D aim trainer built with Three.js.

## Structure

```
assets/
  textures/            # (placeholder for future assets)
index.html             # Entry point with HUD & start button
src/
  main.js              # Game loop & lifecycle
  game/
    SceneManager.js    # Sets up scene, camera, renderer
    Target.js          # Target sphere logic + pulse animation
    Score.js           # Score & accuracy tracking
    Input.js           # Raycasting + pointer tracking
  utils/
    random.js          # Helper for random spawn positions
```

## Running

Just open `index.html` in a modern browser (Chrome, Firefox). No build step required.

Optionally serve via a static server to avoid any future module origin restrictions:

```
python3 -m http.server 5173
```

Then visit: http://localhost:5173

## Gameplay

- Click Start.
- Move the mouse to aim; crosshair is centered.
- Targets spawn every ~1.2s at a fixed depth with random x/y.
- Click to shoot. Green indicates a successful hit.
- Score increments on hits; accuracy is hits/shots.
- Timer runs for 60s; final alert shows stats.

## Next Ideas

- Add difficulty levels (spawn interval, target size).
- Add sound effects & hit particle bursts.
- Add moving targets (animate x/y).
- Store high scores in localStorage.
- Replace alert with in-page summary UI.

## License

MIT
