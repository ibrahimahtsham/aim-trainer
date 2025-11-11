export class Score {
  constructor() {
    this.hits = 0;
    this.shots = 0;
    this.scoreEl = document.getElementById("score");
    this.accEl = document.getElementById("accuracy");
    this.update();
  }

  registerShot(hit) {
    this.shots++;
    if (hit) this.hits++;
    this.update();
  }

  getAccuracy() {
    return this.shots === 0 ? 0 : (this.hits / this.shots) * 100;
  }

  getAccuracyString() {
    return this.getAccuracy().toFixed(1) + "%";
  }

  update() {
    this.scoreEl.textContent = "Score: " + this.hits;
    this.accEl.textContent = "Accuracy: " + this.getAccuracyString();
  }

  reset() {
    this.hits = 0;
    this.shots = 0;
    this.update();
  }
}
