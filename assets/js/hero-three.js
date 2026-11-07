/**
 * PCW CONTRACTING SERVICES - HERO ARCHITECTURAL GRID (THREE.JS)
 * Restrained, progressive, low-power architectural wireframe grid.
 * Gracefully disables on mobile and prefers-reduced-motion.
 */

(function initHeroThreeGrid() {
  const container = document.getElementById('hero-three-canvas');
  if (!container) return;

  // Fail gracefully if Three.js is unavailable
  if (typeof THREE === 'undefined') {
    return;
  }

  // Disable on reduced motion or mobile devices
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isSmallScreen = window.innerWidth < 768;

  if (prefersReducedMotion || isSmallScreen) {
    return;
  }

  try {
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x090d16, 0.015);

    const width = container.clientWidth || window.innerWidth;
    const height = container.clientHeight || window.innerHeight;

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 12, 32);
    camera.rotation.x = -0.32;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'low-power' });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);

    // Subtle ground perspective grid
    const gridHelper = new THREE.GridHelper(80, 20, 0x2563eb, 0x1e293b);
    gridHelper.position.y = -5;
    if (gridHelper.material) {
      gridHelper.material.opacity = 0.28;
      gridHelper.material.transparent = true;
    }
    scene.add(gridHelper);

    // Architectural structural frame lines
    const group = new THREE.Group();
    const cols = 10;
    const rows = 8;
    const spacingX = 7.0;
    const spacingZ = 7.0;
    const startX = -((cols - 1) * spacingX) / 2;
    const startZ = -((rows - 1) * spacingZ) / 2;

    const linePositions = [];
    for (let i = 0; i < cols; i++) {
      for (let j = 0; j < rows; j++) {
        const x = startX + i * spacingX;
        const z = startZ + j * spacingZ;
        const y = Math.sin(i * 0.4) * Math.cos(j * 0.4) * 1.6 - 3.2;

        if (i < cols - 1) {
          const nextX = startX + (i + 1) * spacingX;
          const nextY = Math.sin((i + 1) * 0.4) * Math.cos(j * 0.4) * 1.6 - 3.2;
          linePositions.push(x, y, z, nextX, nextY, z);
        }
        if (j < rows - 1) {
          const nextZ = startZ + (j + 1) * spacingZ;
          const nextY = Math.sin(i * 0.4) * Math.cos((j + 1) * 0.4) * 1.6 - 3.2;
          linePositions.push(x, y, z, x, nextY, nextZ);
        }
      }
    }

    const lineGeo = new THREE.BufferGeometry();
    lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
    const lineMat = new THREE.LineBasicMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.22,
      depthWrite: false
    });
    const lineSegments = new THREE.LineSegments(lineGeo, lineMat);
    group.add(lineSegments);

    // Subtle Amber structural intersection nodes
    const nodePositions = [];
    for (let i = 0; i < cols; i += 2) {
      for (let j = 0; j < rows; j += 2) {
        const x = startX + i * spacingX;
        const z = startZ + j * spacingZ;
        const y = Math.sin(i * 0.4) * Math.cos(j * 0.4) * 1.6 - 3.2;
        nodePositions.push(x, y, z);
      }
    }
    const nodeGeo = new THREE.BufferGeometry();
    nodeGeo.setAttribute('position', new THREE.Float32BufferAttribute(nodePositions, 3));
    const nodeMat = new THREE.PointsMaterial({
      color: 0xfbbf24,
      size: 2.2,
      transparent: true,
      opacity: 0.38,
      depthWrite: false
    });
    const nodePoints = new THREE.Points(nodeGeo, nodeMat);
    group.add(nodePoints);

    scene.add(group);

    // Subtle ambient animation
    let animationId = null;
    let clock = new THREE.Clock();

    function animate() {
      animationId = requestAnimationFrame(animate);
      const time = clock.getElapsedTime();
      group.position.y = Math.sin(time * 0.2) * 0.4;
      group.rotation.y = time * 0.015;
      renderer.render(scene, camera);
    }

    animate();

    // Resize handler
    function onResize() {
      if (!container || !renderer || !camera) return;
      const w = container.clientWidth || window.innerWidth;
      const h = container.clientHeight || window.innerHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    }
    window.addEventListener('resize', onResize, { passive: true });

    // Pause when hero is scrolled out of viewport
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting && animationId) {
          cancelAnimationFrame(animationId);
          animationId = null;
        } else if (entry.isIntersecting && !animationId) {
          animate();
        }
      });
    }, { threshold: 0.05 });
    observer.observe(container);

  } catch (err) {
    console.warn('Three.js hero ambient grid skipped gracefully:', err);
  }
})();
