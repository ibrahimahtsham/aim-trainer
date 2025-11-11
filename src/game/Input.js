export class Input {
  constructor(sceneManager, score) {
    this.sceneManager = sceneManager;
    this.score = score;
    this.raycaster = new THREE.Raycaster();
    this.pointer = new THREE.Vector2();
    this.currentTarget = null;

    window.addEventListener("click", (e) => this.onClick(e));
    window.addEventListener("mousemove", (e) => this.onMove(e));
  }

  setCurrentTarget(target) {
    this.currentTarget = target;
  }

  onMove(e) {
    this.pointer.x = (e.clientX / window.innerWidth) * 2 - 1;
    this.pointer.y = -(e.clientY / window.innerHeight) * 2 + 1;
  }

  onClick() {
    let hitDetected = false;
    if (this.currentTarget && this.currentTarget.alive) {
      this.raycaster.setFromCamera(this.pointer, this.sceneManager.camera);
      const hits = this.raycaster.intersectObject(this.currentTarget.mesh);
      if (hits.length) {
        this.currentTarget.hit();
        hitDetected = true;
      }
    }
    this.score.registerShot(hitDetected);
  }
}
