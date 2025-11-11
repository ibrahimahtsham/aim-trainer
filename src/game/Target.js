import { randomInRange } from "../utils/random.js";

const geom = new THREE.SphereGeometry(0.6, 32, 32);

export class Target {
  constructor(bounds) {
    this.material = new THREE.MeshStandardMaterial({
      color: 0xe74c3c,
      emissive: 0x220000,
      roughness: 0.3,
      metalness: 0.1,
    });

    this.mesh = new THREE.Mesh(geom, this.material);
    this.mesh.position.set(
      randomInRange(-bounds.x, bounds.x),
      randomInRange(-bounds.y, bounds.y),
      bounds.z
    );

    this.scalePulse = 0;
    this.alive = true;
  }

  hit() {
    this.alive = false;
    this.material.color.set(0x2ecc71);
  }

  pulse(dt) {
    this.scalePulse += dt * 3;
    const s = 1 + Math.sin(this.scalePulse) * 0.07;
    this.mesh.scale.set(s, s, s);
  }
}
