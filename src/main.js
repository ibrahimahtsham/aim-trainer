import { SceneManager } from "./game/SceneManager.js";
import { Target } from "./game/Target.js";
import { Score } from "./game/Score.js";
import { Input } from "./game/Input.js";

// Core singletons
const score = new Score();
const sceneManager = new SceneManager();
const input = new Input(sceneManager, score);

let remaining = 60; // seconds
let lastSpawn = 0;
let spawnInterval = 1200; // ms between spawns
let activeTarget = null;
let running = false;

const startBtn = document.getElementById("startBtn");
const timeEl = document.getElementById("time");

function spawnTarget() {
  if (activeTarget) {
    sceneManager.scene.remove(activeTarget.mesh);
  }
  activeTarget = new Target(sceneManager.bounds);
  sceneManager.scene.add(activeTarget.mesh);
  input.setCurrentTarget(activeTarget);
}

function update() {
  if (!running) return;
  const dt = sceneManager.getDelta(); // seconds
  lastSpawn += dt * 1000; // convert to ms
  remaining -= dt;

  if (remaining <= 0) {
    endGame();
    return;
  }
  timeEl.textContent = "Time: " + Math.ceil(remaining) + "s";

  if (lastSpawn >= spawnInterval) {
    lastSpawn = 0;
    spawnTarget();
  }

  if (activeTarget) activeTarget.pulse(dt);
  sceneManager.render();
  requestAnimationFrame(update);
}

function startGame() {
  startBtn.classList.add("hidden");
  running = true;
  remaining = 60;
  score.reset();
  spawnTarget();
  requestAnimationFrame(update);
}

function endGame() {
  running = false;
  if (activeTarget) sceneManager.scene.remove(activeTarget.mesh);
  activeTarget = null;
  alert(`Final Score: ${score.hits} | Accuracy: ${score.getAccuracyString()}`);
  startBtn.classList.remove("hidden");
}

startBtn.addEventListener("click", startGame);
window.addEventListener("resize", () => sceneManager.onResize());
