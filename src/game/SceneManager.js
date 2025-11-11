export class SceneManager {
  constructor() {
    this.clock = new THREE.Clock();
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x111111);

    this.camera = new THREE.PerspectiveCamera(
      70,
      window.innerWidth / window.innerHeight,
      0.1,
      200
    );
    this.camera.position.set(0, 0, 10);

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setPixelRatio(window.devicePixelRatio || 1);
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(this.renderer.domElement);

    // Lighting
    const light = new THREE.PointLight(0xffffff, 1.2);
    light.position.set(5, 5, 10);
    this.scene.add(light);
    this.scene.add(new THREE.AmbientLight(0x555555));

    // Bounds for spawning on a plane at z = -2
    this.bounds = { x: 6, y: 3.5, z: -2 };
  }

  getDelta() {
    return this.clock.getDelta();
  }

  render() {
    this.renderer.render(this.scene, this.camera);
  }

  onResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }
}
