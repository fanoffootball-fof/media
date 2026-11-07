// Rendu 3D stylisé du « but refait » pour @fanoffootball (three.js, piloté par tools/pitch3d.py).
// Mêmes coordonnées que la scène 2D : x 0→100 (touche gauche → droite, 68 m),
// y 0→100 (propre but → but adverse, 105 m). Monde : mètres, but adverse en z = -52,5.
import * as THREE from 'three';

const W = 1080, H = 1920, PL = 105, PW = 68;
const BALL_R = 0.3;           // ballon grossi (×2,7) pour rester lisible de loin
const SCALE = 1.7;            // joueurs grossis pour la lisibilité sur téléphone
const GOAL_Z = -PL / 2;

const params = new URLSearchParams(location.search);
const Q = parseFloat(params.get('q') || '1');          // échelle de rendu (1 = 1080x1920)
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: params.get('aa') !== '0', preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(Math.round(W * Q), Math.round(H * Q), false);
renderer.shadowMap.enabled = params.get('sh') !== '0';
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
const MAX_ANISO = Math.min(renderer.capabilities.getMaxAnisotropy(), parseInt(params.get('ani') || '2'));

const wx = (x) => x / 100 * PW - PW / 2;
const wz = (y) => PL / 2 - y / 100 * PL;
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

// ------------------------------------------------------------ trajectoires
function parseKeys(path) {
  return path.map((p) => {
    const flags = typeof p[3] === 'string' ? p[3].split(/\s+/) : [];
    let z = null;
    for (const f of flags) if (f.startsWith('z=')) z = parseFloat(f.slice(2));
    return { x: +p[0], y: +p[1], t: +p[2], air: flags.includes('air'), high: flags.includes('high'),
             low: flags.includes('low'), z };
  }).sort((a, b) => a.t - b.t);
}

function playerAt(k, t) {
  if (t <= k[0].t || k.length === 1) return [k[0].x, k[0].y];
  for (let i = 0; i < k.length - 1; i++) {
    const a = k[i], b = k[i + 1];
    if (t <= b.t) {
      const u = (t - a.t) / Math.max(1e-6, b.t - a.t);
      const first = i === 0, last = i === k.length - 2;
      let v = u;
      if (first && last) v = u * u * (3 - 2 * u);
      else if (first) v = u * u * (2 - u);
      else if (last) v = 1 - (1 - u) * (1 - u);
      return [a.x + (b.x - a.x) * v, a.y + (b.y - a.y) * v];
    }
  }
  const e = k[k.length - 1];
  return [e.x, e.y];
}

const keyH = (q) => (q.z != null ? q.z : (q.y > 100 ? (q.high ? 2.1 : q.low ? 0.25 : 1.0) : 0));

function ballAt(k, t) {
  if (t <= k[0].t || k.length === 1) return [k[0].x, k[0].y, keyH(k[0])];
  for (let i = 0; i < k.length - 1; i++) {
    const a = k[i], b = k[i + 1];
    if (t <= b.t) {
      const u = (t - a.t) / Math.max(1e-6, b.t - a.t);
      const v = b.air ? u : 1 - Math.pow(1 - u, 1.4);
      const dist = Math.hypot((b.x - a.x) / 100 * PW, (b.y - a.y) / 100 * PL);
      const peak = b.air ? clamp(0.13 * dist, 1.5, 9) : 0;
      const h = keyH(a) + (keyH(b) - keyH(a)) * v + peak * 4 * u * (1 - u);
      return [a.x + (b.x - a.x) * v, a.y + (b.y - a.y) * v, h];
    }
  }
  const e = k[k.length - 1];
  return [e.x, e.y, keyH(e)];
}

// ------------------------------------------------------------ textures
function canvasTex(w, h, paint, repeat) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  paint(c.getContext('2d'), w, h);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = MAX_ANISO;
  if (repeat) { tex.wrapS = tex.wrapT = THREE.RepeatWrapping; tex.repeat.set(repeat[0], repeat[1]); }
  return tex;
}

function seeded(seed) {
  let s = seed >>> 0;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
}

const PAD = 7;
function pitchTexture() {
  const S = 20;
  const cw = Math.round((PW + 2 * PAD) * S), ch = Math.round((PL + 2 * PAD) * S);
  return canvasTex(cw, ch, (g) => {
    const P = (mx, my) => [(mx + PAD) * S, (PL + PAD - my) * S];
    g.fillStyle = '#1f5f36';
    g.fillRect(0, 0, cw, ch);
    for (let i = -2; i < 24; i++) {          // bandes de tonte tous les 5,25 m
      const [, y0] = P(0, PL - i * 5.25);
      g.fillStyle = i % 2 === 0 ? '#2b7d45' : '#256f3d';
      g.fillRect(0, y0, cw, 5.25 * S);
    }
    const rnd = seeded(7);
    for (let i = 0; i < 26000; i++) {         // grain de la pelouse
      g.fillStyle = rnd() < 0.5 ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.035)';
      g.fillRect(rnd() * cw, rnd() * ch, 3, 3);
    }
    g.strokeStyle = 'rgba(255,255,255,0.93)';
    g.fillStyle = 'rgba(255,255,255,0.93)';
    g.lineWidth = 0.13 * S;
    const line = (a, b) => { g.beginPath(); g.moveTo(...P(...a)); g.lineTo(...P(...b)); g.stroke(); };
    const rect = (x0, y0, x1, y1) => { const [a, b] = P(x0, y1); const [c, d] = P(x1, y0); g.strokeRect(a, b, c - a, d - b); };
    const arc = (cx, cy, r, s, e) => { g.beginPath(); g.arc(...P(cx, cy), r * S, s * Math.PI / 180, e * Math.PI / 180); g.stroke(); };
    const spot = (cx, cy) => { g.beginPath(); g.arc(...P(cx, cy), 0.25 * S, 0, 2 * Math.PI); g.fill(); };
    rect(0, 0, PW, PL);
    line([0, PL / 2], [PW, PL / 2]);
    arc(PW / 2, PL / 2, 9.15, 0, 360);
    spot(PW / 2, PL / 2);
    for (const end of [PL, 0]) {
      const sg = end === PL ? 1 : -1;
      const bx = (PW - 40.32) / 2, gx = (PW - 18.32) / 2;
      rect(bx, Math.min(end, end - sg * 16.5), bx + 40.32, Math.max(end, end - sg * 16.5));
      rect(gx, Math.min(end, end - sg * 5.5), gx + 18.32, Math.max(end, end - sg * 5.5));
      spot(PW / 2, end - sg * 11);
      if (sg === 1) arc(PW / 2, end - 11, 9.15, 36.87, 143.13);
      else arc(PW / 2, end + 11, 9.15, 216.87, 323.13);
    }
    arc(0, PL, 1, 0, 90); arc(PW, PL, 1, 90, 180); arc(0, 0, 1, 270, 360); arc(PW, 0, 1, 180, 270);
  });
}

function crowdTexture(seed) {
  return canvasTex(512, 512, (g, w, h) => {
    g.fillStyle = '#121620';
    g.fillRect(0, 0, w, h);
    const rnd = seeded(seed);
    const pal = ['#2e3446', '#454d60', '#262c3a', '#5c2a33', '#2a3e62', '#626878', '#3d3026', '#8c7f62'];
    for (let row = 0; row < 32; row++) {
      g.fillStyle = 'rgba(0,0,0,0.35)';
      g.fillRect(0, row * 16 + 13, w, 3);
      for (let i = 0; i < 70; i++) {
        g.fillStyle = pal[Math.floor(rnd() * pal.length)];
        const x = rnd() * w, y = row * 16 + 2 + rnd() * 4;
        g.fillRect(x, y, 5, 8);
        g.fillRect(x + 1, y - 3, 3, 3);
      }
    }
  }, [6, 1]);
}

function boardTexture() {
  return canvasTex(1024, 64, (g, w, h) => {
    g.fillStyle = '#0b0d14';
    g.fillRect(0, 0, w, h);
    g.fillStyle = '#f2c14e';
    g.font = 'bold 40px sans-serif';
    g.textBaseline = 'middle';
    g.fillText('FAN OF FOOTBALL', 30, h / 2 + 2);
    g.fillText('FAN OF FOOTBALL', 545, h / 2 + 2);
  }, [8, 1]);
}

function ballTexture() {
  return canvasTex(256, 128, (g, w, h) => {
    g.fillStyle = '#f4f5f7';
    g.fillRect(0, 0, w, h);
    g.fillStyle = '#1a1c22';
    const pts = [[20, 30], [85, 64], [150, 30], [215, 64], [52, 100], [118, 100], [182, 100], [245, 100], [118, 12]];
    for (const [x, y] of pts) { g.beginPath(); g.arc(x, y, 13, 0, 2 * Math.PI); g.fill(); }
  });
}

// ------------------------------------------------------------ décor
function buildStadium(scene) {
  const sky = canvasTex(4, 512, (g, w, h) => {
    const gr = g.createLinearGradient(0, 0, 0, h);
    gr.addColorStop(0, '#04060b'); gr.addColorStop(0.55, '#0c1424'); gr.addColorStop(1, '#1a2a44');
    g.fillStyle = gr; g.fillRect(0, 0, w, h);
  });
  scene.background = sky;
  scene.fog = new THREE.Fog(0x0e1626, 95, 230);

  scene.add(new THREE.HemisphereLight(0xc8d6ff, 0x1c3322, 1.15));
  const sun = new THREE.DirectionalLight(0xfff4e0, 2.4);
  sun.position.set(28, 60, 6);
  sun.target.position.set(0, 0, -22);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -48, right: 48, top: 48, bottom: -48, near: 10, far: 160 });
  sun.shadow.bias = -0.0004;
  scene.add(sun, sun.target);
  const fill = new THREE.DirectionalLight(0xbfd0ff, 0.6);
  fill.position.set(-40, 30, 30);
  scene.add(fill);

  const pitch = new THREE.Mesh(new THREE.PlaneGeometry(PW + 2 * PAD, PL + 2 * PAD),
    new THREE.MeshLambertMaterial({ map: pitchTexture() }));
  pitch.rotation.x = -Math.PI / 2;
  pitch.receiveShadow = true;
  scene.add(pitch);
  const outer = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshLambertMaterial({ color: 0x163a24 }));
  outer.rotation.x = -Math.PI / 2;
  outer.position.y = -0.02;
  scene.add(outer);

  const boardMat = new THREE.MeshBasicMaterial({ map: boardTexture() });
  const board = (len, x, z, rotY) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(len, 0.9, 0.12), boardMat);
    m.position.set(x, 0.45, z); m.rotation.y = rotY; scene.add(m);
  };
  board(PL + 10, -PW / 2 - 4.5, 0, Math.PI / 2);
  board(PL + 10, PW / 2 + 4.5, 0, -Math.PI / 2);
  board(PW - 12, 0, GOAL_Z - 5.5, 0);
  board(PW - 12, 0, -GOAL_Z + 5.5, Math.PI);

  const standMat = (seed, rx) => {
    const t = crowdTexture(seed); t.repeat.set(rx, 1);
    return new THREE.MeshBasicMaterial({ map: t, color: 0x8c93a4 });
  };
  const stand = (len, depth, x, z, rotY, seed) => {
    const g = new THREE.PlaneGeometry(len, depth);
    const m = new THREE.Mesh(g, standMat(seed, len / 22));
    m.position.set(x, 0, z);
    m.rotation.order = 'YXZ';
    m.rotation.y = rotY;
    m.rotation.x = -0.62;              // gradins inclinés vers le terrain
    m.translateY(depth / 2 + 1);
    scene.add(m);
  };
  stand(PL + 30, 46, -PW / 2 - 9, 0, Math.PI / 2, 11);
  stand(PL + 30, 46, PW / 2 + 9, 0, -Math.PI / 2, 12);
  stand(PW + 30, 46, 0, GOAL_Z - 9, 0, 13);
  stand(PW + 30, 46, 0, -GOAL_Z + 9, Math.PI, 14);

  const glow = new THREE.SpriteMaterial({ map: canvasTex(64, 64, (g) => {
    const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, 'rgba(255,250,235,1)'); gr.addColorStop(0.25, 'rgba(255,245,220,0.5)'); gr.addColorStop(1, 'rgba(255,240,210,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
  }), transparent: true, depthWrite: false, fog: false });
  for (const [x, z] of [[-60, -78], [60, -78], [-60, 70], [60, 70]]) {   // projecteurs
    const s = new THREE.Sprite(glow); s.position.set(x, 52, z); s.scale.set(26, 26, 1); scene.add(s);
  }

  buildGoal(scene, GOAL_Z, -1);
  buildGoal(scene, -GOAL_Z, 1);
}

function buildGoal(scene, zLine, dir) {
  const white = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.4 });
  const postG = new THREE.CylinderGeometry(0.06, 0.06, 2.44, 12);
  for (const x of [-3.66, 3.66]) {
    const p = new THREE.Mesh(postG, white); p.position.set(x, 1.22, zLine); p.castShadow = true; scene.add(p);
  }
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 7.44, 12), white);
  bar.rotation.z = Math.PI / 2; bar.position.set(0, 2.44, zLine); bar.castShadow = true; scene.add(bar);
  const pts = [];
  const back = (y) => zLine + dir * (2.0 - 1.0 * y / 2.44);   // filet : 2 m de fond au sol, 1 m en haut
  for (let x = -3.66; x <= 3.661; x += 0.25) {             // fond + toit
    pts.push(x, 0, back(0), x, 2.44, back(2.44), x, 2.44, back(2.44), x, 2.44, zLine);
  }
  for (let y = 0; y <= 2.441; y += 0.25) {
    pts.push(-3.66, y, back(y), 3.66, y, back(y));
    for (const x of [-3.66, 3.66]) pts.push(x, y, zLine, x, y, back(y));
  }
  for (let d = 0; d <= 1.001; d += 0.125) {
    const z = zLine + dir * d * 2.0;
    const D = d * 2.0, top = D <= 1 ? 2.44 : 2.44 * (2 - D);
    for (const x of [-3.66, 3.66]) pts.push(x, 0, z, x, top, z);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
  scene.add(new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.45 })));
}

// ------------------------------------------------------------ joueurs
function makePlayer(jersey, star) {
  const root = new THREE.Group();
  const body = new THREE.Group();
  body.scale.setScalar(SCALE);
  root.add(body);
  const jc = new THREE.Color(jersey[0] / 255, jersey[1] / 255, jersey[2] / 255).convertSRGBToLinear();
  const mat = (c, r = 0.75) => new THREE.MeshStandardMaterial({ color: c, roughness: r });
  const jerseyM = mat(jc), shortsM = mat(0x1a2030), skinM = mat(0xc9ced8, 0.6), sockM = mat(jc.clone().multiplyScalar(0.8));
  const cap = (r, l, m) => { const x = new THREE.Mesh(new THREE.CapsuleGeometry(r, l, 4, 10), m); x.castShadow = true; return x; };
  const limb = (r, l, m, px, py, below) => {
    const piv = new THREE.Group(); piv.position.set(px, py, 0);
    const c = cap(r, l, m); c.position.y = -below; piv.add(c); body.add(piv); return piv;
  };
  const legL = limb(0.1, 0.62, sockM, -0.12, 0.92, 0.45);
  const legR = limb(0.1, 0.62, sockM, 0.12, 0.92, 0.45);
  const shorts = new THREE.Mesh(new THREE.CylinderGeometry(0.21, 0.23, 0.28, 14), shortsM);
  shorts.position.y = 0.98; shorts.castShadow = true; body.add(shorts);
  const torso = cap(0.22, 0.42, jerseyM); torso.position.y = 1.33; body.add(torso);
  const armL = limb(0.07, 0.48, jerseyM, -0.31, 1.52, 0.3);
  const armR = limb(0.07, 0.48, jerseyM, 0.31, 1.52, 0.3);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.13, 16, 12), skinM);
  head.position.y = 1.8; head.castShadow = true; body.add(head);
  if (star) {
    const ring = new THREE.Mesh(new THREE.RingGeometry(0.8, 1.02, 48),
      new THREE.MeshBasicMaterial({ color: 0xf2c14e, transparent: true, opacity: 0.95 }));
    ring.rotation.x = -Math.PI / 2; ring.position.y = 0.03; root.add(ring);
  }
  return { root, legL, legR, armL, armR };
}

// ------------------------------------------------------------ état
let scene, camera, S;

function init(spec) {
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(58, W / H, 0.5, 600);
  buildStadium(scene);
  const att = spec.att_color || [61, 123, 255];
  const colors = { att, def: spec.def_color || [205, 45, 60], gk: [255, 196, 40] };
  const players = (spec.players || []).map((p) => {
    const team = p.team || 'att';
    const m = makePlayer(p.color || colors[team], !!p.star);
    scene.add(m.root);
    return { k: parseKeys(p.path), m, label: p.label || null, star: !!p.star };
  });
  const ball = new THREE.Mesh(new THREE.SphereGeometry(BALL_R, 32, 16),
    new THREE.MeshStandardMaterial({ map: ballTexture(), roughness: 0.35 }));
  ball.castShadow = true;
  scene.add(ball);
  S = { spec, players, ballMesh: ball, bk: spec.ball ? parseKeys(spec.ball) : null, trail: null };
  return true;
}

function travelled(k, t) {
  let d = 0, prev = playerAt(k, k[0].t);
  for (let tt = k[0].t + 1 / 30; tt <= t; tt += 1 / 30) {
    const p = playerAt(k, tt);
    d += Math.hypot((p[0] - prev[0]) / 100 * PW, (p[1] - prev[1]) / 100 * PL);
    prev = p;
  }
  return d;
}

function updatePlayers(t) {
  const b = S.bk ? ballAt(S.bk, t) : null;
  for (const p of S.players) {
    const [x, y] = playerAt(p.k, t);
    const [x0, y0] = playerAt(p.k, t - 0.12);
    const [x1, y1] = playerAt(p.k, t + 0.04);
    const vx = (x1 - x0) / 100 * PW / 0.16, vz = -(y1 - y0) / 100 * PL / 0.16;
    const speed = Math.hypot(vx, vz);
    p.m.root.position.set(wx(x), 0, wz(y));
    if (speed > 0.4) p.m.root.rotation.y = Math.atan2(vx, vz);
    else if (b) p.m.root.rotation.y = Math.atan2(wx(b[0]) - wx(x), wz(b[1]) - wz(y));
    const phase = travelled(p.k, t) / 1.1 * Math.PI;
    const amp = clamp(speed / 7, 0.08, 0.75);
    const sw = Math.sin(phase) * amp;
    p.m.legL.rotation.x = sw; p.m.legR.rotation.x = -sw;
    p.m.armL.rotation.x = -sw * 0.8; p.m.armR.rotation.x = sw * 0.8;
  }
}

function updateBall(t) {
  if (!S.bk) return;
  const [x, y, h] = ballAt(S.bk, t);
  S.ballMesh.position.set(wx(x), h + BALL_R, wz(y));
  const [xa, ya] = ballAt(S.bk, t - 0.05);
  const dx = wx(x) - wx(xa), dz = wz(y) - wz(ya);
  const len = Math.hypot(dx, dz);
  if (len > 1e-4) {
    let d = 0, prev = ballAt(S.bk, S.bk[0].t);
    for (let tt = S.bk[0].t + 1 / 30; tt <= t; tt += 1 / 30) {
      const q = ballAt(S.bk, tt);
      d += Math.hypot((q[0] - prev[0]) / 100 * PW, (q[1] - prev[1]) / 100 * PL);
      prev = q;
    }
    S.ballMesh.quaternion.setFromAxisAngle(new THREE.Vector3(dz / len, 0, -dx / len), d / BALL_R);
  }
  if (S.trail) { scene.remove(S.trail); S.trail.geometry.dispose(); S.trail = null; }
  const pts = [];
  const nearGoalCam = (S.spec.camera || {}).mode === 'goal';
  for (let tt = S.bk[0].t; tt <= t; tt += 1 / 30) {
    const q = ballAt(S.bk, tt);
    if (nearGoalCam && wz(q[1]) < GOAL_Z + 4) break;   // pas de trace collée à la caméra filet
    pts.push(new THREE.Vector3(wx(q[0]), q[2] + BALL_R, wz(q[1])));
  }
  if (!nearGoalCam || wz(y) >= GOAL_Z + 4) pts.push(new THREE.Vector3(wx(x), h + BALL_R, wz(y)));
  if (pts.length > 2 && pts[0].distanceTo(pts[pts.length - 1]) > 0.5) {
    const curve = new THREE.CatmullRomCurve3(pts);
    S.trail = new THREE.Mesh(new THREE.TubeGeometry(curve, Math.min(400, pts.length * 2), 0.07, 6, false),
      new THREE.MeshBasicMaterial({ color: 0xf2c14e, transparent: true, opacity: 0.85, depthWrite: false }));
    scene.add(S.trail);
  }
}

function updateCamera(t) {
  const cam = S.spec.camera || {};
  const mode = cam.mode || 'follow';
  let sx = 0, sz = 0, n = 0;
  if (S.bk) {
    for (let i = 0; i <= 10; i++) {           // position du ballon lissée sur 0,5 s
      const b = ballAt(S.bk, t - 0.3 * i / 10);
      sx += wx(b[0]); sz += wz(b[1]); n++;
    }
    sx /= n; sz /= n;
  }
  const star = S.players.find((p) => p.star);
  if (star) {                                  // cadre le ballon ET le joueur clé
    let px = 0, pz = 0;
    for (let i = 0; i <= 10; i++) { const q = playerAt(star.k, t - 0.3 * i / 10); px += wx(q[0]); pz += wz(q[1]); }
    sx = 0.6 * sx + 0.4 * px / 11; sz = 0.6 * sz + 0.4 * pz / 11;
  }
  if (mode === 'goal') {                       // derrière le but adverse, à hauteur d'homme
    camera.fov = cam.fov || 46;                // caméra en hauteur derrière le but adverse
    camera.position.set(cam.side ?? -2, cam.height || 9, GOAL_Z - (cam.back || 16));
    camera.lookAt(sx * 0.9, 0.5, 0.68 * sz + 0.32 * GOAL_Z);  // cadre le tireur et le but ensemble
  } else {                                     // caméra aérienne derrière l'action
    camera.fov = cam.fov || 70;
    const fz = 0.72 * sz + 0.28 * GOAL_Z;      // l'action au centre, le but en haut
    camera.position.set(sx, cam.height || 34, sz + (cam.back || 27));
    camera.lookAt(sx, 0, fz);
  }
  camera.updateProjectionMatrix();
}

function renderAt(t) {
  updatePlayers(t);
  updateBall(t);
  updateCamera(t);
  const t0 = performance.now();
  renderer.render(scene, camera);
  const gl = renderer.getContext();
  gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array(4));   // attend la fin du rendu
  const t1 = performance.now();
  const labels = [];
  const v = new THREE.Vector3();
  for (const p of S.players) {
    if (!p.label) continue;
    v.copy(p.m.root.position); v.y = 2.55 * SCALE;
    v.project(camera);
    if (v.z < 1) labels.push({ x: (v.x + 1) / 2 * W, y: (1 - v.y) / 2 * H, text: p.label, star: p.star });
  }
  const img = canvas.toDataURL('image/jpeg', 0.92);
  return { img, labels, ms: [t1 - t0, performance.now() - t1] };
}

window.fof = { init, renderAt };
