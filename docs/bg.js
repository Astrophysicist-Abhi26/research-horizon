/* Research Horizon background: a new scientific "poster" on every visit.

   Line-art motifs and equations are drawn from many fields. The research
   profile the reader has chosen makes its own fields more likely (weight()
   returns the profile's 0-100 interest in a taxonomy node). Everything is
   drawn into one SVG, sized to the window and used as the page background at
   low contrast, behind the content.

   API: RHBackground.url({theme, w, h, weight, reseed}) -> "data:image/svg+xml,…"
        same seed -> same composition (a theme change or resize keeps the poster;
        reseed: true draws a new one). */
(function () {
"use strict";

const PAL = {
  // op: overall strength. Kept low: the poster sits behind text and must never compete with it.
  dark:  {a: "#F2B544", c: "#74D7E4", v: "#C792EA", t: "#EDEAF7", m: "#8E89A6", bg: "#0C0A16", k: "#000000", op: .62},
  light: {a: "#C9861B", c: "#0E7C8C", v: "#8B5CB8", t: "#2A2342", m: "#6B6585", bg: "#F7F5FB", k: "#1B1730", op: .55},
};
const MONO = "Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace";
const SERIF = "'Cambria Math','STIX Two Math','STIX Two Text','Latin Modern Math','Times New Roman',serif";

// ---------------------------------------------------------------------------
// Equations: [taxonomy node(s), equation, caption]
// ---------------------------------------------------------------------------
const EQUATIONS = [
  ["cosmo.general", "H²(a) = (8πG/3)ρ − kc²/a² + Λc²/3", "Friedmann 1922"],
  ["cosmo.general", "ds² = −c²dt² + a²(t)[dr²/(1−kr²) + r²dΩ²]", "FLRW metric"],
  ["cosmo.de", "w(a) = w₀ + wₐ(1 − a)", "CPL dark energy"],
  ["cosmo.de", "ä/a = −(4πG/3)(ρ + 3p/c²) + Λc²/3", "cosmic acceleration"],
  ["cosmo.lss", "ξ(r) = ∫ P(k) (sin kr / kr) k² dk / 2π²", "two-point correlation"],
  ["cosmo.lss", "δ̈ + 2Hδ̇ = 4πGρ̄ δ", "linear growth of structure"],
  ["cosmo.early", "Δ²(k) = Aₛ (k/k*)^(nₛ−1)", "primordial power spectrum"],
  ["cosmo.early", "T(z) = T₀ (1 + z)", "CMB temperature"],
  ["cosmo.dm", "ρ(r) = ρₛ / [(r/rₛ)(1 + r/rₛ)²]", "NFW halo profile"],
  ["astro.he", "rₛ = 2GM/c²", "Schwarzschild radius"],
  ["astro.he", "T = ħc³ / (8πGMk_B)", "Hawking 1974"],
  ["astro.he", "L_Edd = 4πGMm_p c / σ_T", "Eddington luminosity"],
  ["astro.stellar", "L = 4πR²σT⁴", "Stefan–Boltzmann"],
  ["astro.stellar", "M_Ch ≈ 1.44 M☉", "Chandrasekhar limit"],
  ["astro.stellar", "dP/dr = −G m(r) ρ(r) / r²", "hydrostatic equilibrium"],
  ["astro.galactic", "v²(r) = G M(<r) / r", "rotation curve"],
  ["astro.general", "m − M = 5 log₁₀(d / 10 pc)", "distance modulus"],
  [["phys.gr", "cosmo.general"], "Gμν + Λgμν = (8πG/c⁴) Tμν", "Einstein 1915"],
  ["phys.gr", "□hμν = −(16πG/c⁴) Tμν", "gravitational waves"],
  ["phys.gr", "S = k_B c³ A / (4Għ)", "Bekenstein–Hawking entropy"],
  ["phys.hepth", "(iγ^μ ∂_μ − m) ψ = 0", "Dirac 1928"],
  ["phys.hepth", "ℒ = −¼ Fᵃ_μν Fᵃ^μν", "Yang–Mills"],
  ["phys.hepth", "Z = ∫ 𝒟φ e^(iS[φ]/ħ)", "path integral"],
  ["phys.hepth", "∂_μ j^μ = 0", "Noether 1918"],
  ["phys.hepth", "(□ + m²) φ = 0", "Klein–Gordon"],
  ["phys.quantum", "iħ ∂ψ/∂t = Ĥψ", "Schrödinger 1926"],
  ["phys.quantum", "Δx Δp ≥ ħ/2", "Heisenberg 1927"],
  ["phys.quantum", "|ψ⟩ = α|0⟩ + β|1⟩", "a qubit"],
  ["phys.quantum", "S(ρ) = −Tr ρ log ρ", "von Neumann entropy"],
  ["phys.quantum", "|⟨AB⟩ + ⟨AB′⟩ + ⟨A′B⟩ − ⟨A′B′⟩| ≤ 2", "CHSH inequality"],
  ["phys.quantum", "dρ/dt = −i[H, ρ] + Σ (LρL† − ½{L†L, ρ})", "Lindblad equation"],
  ["phys.condmat", "H = −J Σ σᵢσⱼ − h Σ σᵢ", "Ising model"],
  ["phys.condmat", "H = −t Σ c†ᵢσ cⱼσ + U Σ nᵢ↑ nᵢ↓", "Hubbard model"],
  ["phys.condmat", "σ_xy = ν e²/h", "quantum Hall effect"],
  ["phys.condmat", "C = (1/2π) ∫_BZ Ω(k) d²k", "Chern number"],
  ["phys.condmat", "γ = i ∮ ⟨u(k)|∇ₖ u(k)⟩ · dk", "Berry phase"],
  ["phys.condmat", "ψₖ(r) = e^(ik·r) uₖ(r)", "Bloch 1929"],
  ["phys.condmat", "Δ = 2ħω_D e^(−1/N(0)V)", "BCS gap"],
  ["phys.condmat", "Z = Σ e^(−βEᵢ)", "partition function"],
  ["phys.condmat", "S = k_B ln W", "Boltzmann"],
  ["phys.condmat", "f(E) = 1 / (e^((E−μ)/k_BT) + 1)", "Fermi–Dirac"],
  ["phys.fluids", "∂u/∂t + (u·∇)u = −∇p/ρ + ν∇²u", "Navier–Stokes"],
  ["phys.fluids", "E(k) ∝ ε^(2/3) k^(−5/3)", "Kolmogorov 1941"],
  [["phys.fluids", "math.other"], "ẋ = σ(y − x),  ż = xy − βz", "Lorenz 1963"],
  ["phys.general", "∇ × B = μ₀J + μ₀ε₀ ∂E/∂t", "Ampère–Maxwell"],
  ["phys.general", "E² = (pc)² + (mc²)²", "energy–momentum relation"],
  ["phys.general", "n₁ sin θ₁ = n₂ sin θ₂", "Snell's law"],
  ["math.nt", "p(n) ~ e^(π√(2n/3)) / 4n√3", "Hardy · Ramanujan 1918"],
  ["math.nt", "ζ(s) = Σ n⁻ˢ = Π (1 − p⁻ˢ)⁻¹", "Euler product"],
  ["math.nt", "π(x) ~ x / ln x", "prime number theorem"],
  ["math.nt", "aⁿ + bⁿ ≠ cⁿ,  n > 2", "Fermat–Wiles"],
  ["math.geometry", "∫_M K dA + ∫_∂M k_g ds = 2πχ(M)", "Gauss–Bonnet"],
  ["math.geometry", "Ric − ½Rg = 0", "Einstein manifolds"],
  ["math.topology", "V − E + F = 2", "Euler 1758"],
  ["math.topology", "∫_M dω = ∫_∂M ω", "Stokes' theorem"],
  ["math.topology", "π₁(S¹) ≅ ℤ", "fundamental group"],
  [["math.topology", "math.mathphys"], "ind D = ∫_M Â(M) ch(E)", "Atiyah–Singer"],
  [["math.mathphys", "phys.hepth"], "Z(M) = ∫ 𝒟A e^(ik CS(A))", "Chern–Simons TQFT"],
  ["math.mathphys", "[x, p] = iħ", "canonical commutation"],
  ["math.algebra", "|G| = |H| · [G : H]", "Lagrange's theorem"],
  ["math.algebra", "[Xᵢ, Xⱼ] = fᵢⱼᵏ Xₖ", "Lie algebra"],
  ["math.analysis", "e^(iπ) + 1 = 0", "Euler"],
  ["math.analysis", "∮ f(z)/(z − a) dz = 2πi f(a)", "Cauchy 1831"],
  ["math.analysis", "F(ξ) = ∫ f(x) e^(−2πixξ) dx", "Fourier transform"],
  ["math.analysis", "Σ 1/n² = π²/6", "Basel problem"],
  ["math.probability", "dXₜ = μ dt + σ dWₜ", "Itô SDE"],
  ["math.probability", "p(θ|D) = p(D|θ) p(θ) / p(D)", "Bayes"],
  ["math.probability", "√n (X̄ₙ − μ) → 𝒩(0, σ²)", "central limit theorem"],
  ["ai.general", "softmax(QKᵀ/√d) V", "attention, 2017"],
  ["ai.general", "θ ← θ − η ∇L(θ)", "gradient descent"],
  ["ai.general", "V(s) = maxₐ [r + γ Σ P(s′|s,a) V(s′)]", "Bellman equation"],
  ["ai.theory", "log p(x) ≥ E_q[log p(x|z)] − KL(q‖p)", "evidence lower bound"],
  ["ai.theory", "H(X) = −Σ p(x) log₂ p(x)", "Shannon 1948"],
  ["ai.theory", "R(h) ≤ R_emp(h) + O(√(d/n))", "generalisation bound"],
  ["ai.science", "p(θ | x_obs) ∝ p(x_obs | θ) p(θ)", "simulation-based inference"],
  ["ai.science", "dx = [f − g² ∇ₓ log pₜ(x)] dt + g dW", "score-based diffusion"],
];

// ---------------------------------------------------------------------------
// Motifs: line art in local coordinates around (0,0), size R
// ---------------------------------------------------------------------------
const f = n => Math.round(n * 10) / 10;
const pathOf = pts => "M" + pts.map(p => f(p[0]) + "," + f(p[1])).join("L");

const MOTIFS = [
  {id: "blackhole", tags: ["astro.he", "phys.gr"], op: .95, draw(R, P, r, id) {
    return `<defs><radialGradient id="${id}"><stop offset="55%" stop-color="${P.k}"/>
      <stop offset="72%" stop-color="${P.a}" stop-opacity=".55"/><stop offset="82%" stop-color="${P.a}" stop-opacity=".15"/>
      <stop offset="100%" stop-color="${P.a}" stop-opacity="0"/></radialGradient></defs>
      <circle r="${f(R)}" fill="url(#${id})"/><circle r="${f(R * .54)}" fill="${P.k}"/>
      <ellipse rx="${f(R * 1.27)}" ry="${f(R * .29)}" fill="none" stroke="${P.a}" stroke-width="2" opacity=".4"/>
      <path d="M${f(-R * 1.27)},0 A${f(R * 1.27)},${f(R * .5)} 0 0 1 ${f(R * 1.27)},0" fill="none" stroke="${P.a}" stroke-width="1.4" opacity=".55"/>
      <path d="M${f(-R * .8)},${f(-R * .73)} A${f(R * 1.08)},${f(R * 1.08)} 0 0 1 ${f(R * .8)},${f(-R * .73)}" fill="none" stroke="${P.c}" opacity=".35"/>`;
  }},
  {id: "galaxy", tags: ["astro.galactic"], op: .38, draw(R, P, r) {
    const s = R / 130, arm = (sign, col) => {
      const pts = [];
      for (let t = 0; t < 3.2; t += .08) {
        const rad = 12 * Math.exp(.55 * t) * s;
        pts.push([sign * rad * Math.cos(t), sign * rad * Math.sin(t)]);
      }
      return `<path d="${pathOf(pts)}" stroke="${col}" stroke-width="1.6" fill="none"/>`;
    };
    let dots = "";
    for (let i = 0; i < 26; i++) {
      const t = r() * 3.2, rad = 12 * Math.exp(.55 * t) * s * (0.85 + .3 * r()), sg = r() < .5 ? 1 : -1;
      dots += `<circle cx="${f(sg * rad * Math.cos(t))}" cy="${f(sg * rad * Math.sin(t))}" r="${f(.8 + r())}" fill="${P.t}"/>`;
    }
    return `<circle r="${f(7 * s + 2)}" fill="${P.a}"/>${arm(1, P.v)}${arm(-1, P.v)}<g transform="rotate(35)">${arm(1, P.c)}${arm(-1, P.c)}</g>${dots}`;
  }},
  {id: "supernova", tags: ["astro.stellar", "astro.general"], op: .8, draw(R, P, r, id) {
    let rays = "";
    for (let k = 0; k < 8; k++) {
      const a = k * Math.PI / 4, l1 = R * .3, l2 = R * (k % 2 ? .6 : .85);
      rays += `M${f(l1 * Math.cos(a))},${f(l1 * Math.sin(a))}L${f(l2 * Math.cos(a))},${f(l2 * Math.sin(a))}`;
    }
    return `<defs><radialGradient id="${id}"><stop offset="0%" stop-color="${P.t}" stop-opacity=".8"/>
      <stop offset="30%" stop-color="${P.c}" stop-opacity=".4"/><stop offset="100%" stop-color="${P.c}" stop-opacity="0"/></radialGradient></defs>
      <circle r="${f(R * .6)}" fill="url(#${id})"/><path d="${rays}" stroke="${P.t}" stroke-width="1.3" opacity=".5"/>`;
  }},
  {id: "cmb", tags: ["cosmo.early", "cosmo.general"], op: .42, draw(R, P, r) {
    const rx = R * 1.25, ry = R * .62;
    let blobs = "";
    for (let i = 0; i < 70; i++) {
      const u = r() * 2 - 1, v = r() * 2 - 1;
      if (u * u + v * v > .92) continue;
      blobs += `<circle cx="${f(u * rx)}" cy="${f(v * ry)}" r="${f(R * (.025 + .07 * r()))}" fill="${r() < .5 ? P.a : P.c}" opacity="${f(.25 + .45 * r())}"/>`;
    }
    return `${blobs}<ellipse rx="${f(rx)}" ry="${f(ry)}" fill="none" stroke="${P.t}" stroke-width="1.2"/>
      <path d="M${f(-rx)},0H${f(rx)}M0,${f(-ry)}V${f(ry)}" stroke="${P.m}" stroke-width=".7" opacity=".6"/>`;
  }},
  {id: "cosmicweb", tags: ["cosmo.lss", "cosmo.dm"], op: .45, draw(R, P, r) {
    const pts = [];
    for (let i = 0; i < 46; i++) {
      const a = r() * 6.283, d = R * Math.sqrt(r());
      pts.push([d * Math.cos(a), d * Math.sin(a)]);
    }
    let lines = "", nodes = "";
    pts.forEach((p, i) => {
      const near = pts.map((q, j) => [Math.hypot(p[0] - q[0], p[1] - q[1]), j]).filter(x => x[1] !== i)
        .sort((a, b) => a[0] - b[0]).slice(0, 2);
      near.forEach(([d, j]) => { if (j > i && d < R * .5) lines += `M${f(p[0])},${f(p[1])}L${f(pts[j][0])},${f(pts[j][1])}`; });
      nodes += `<circle cx="${f(p[0])}" cy="${f(p[1])}" r="${f(1 + 2.2 * r() * r())}" fill="${P.a}"/>`;
    });
    return `<path d="${lines}" stroke="${P.c}" stroke-width=".9" fill="none"/>${nodes}`;
  }},
  {id: "honeycomb", tags: ["phys.condmat"], op: .38, draw(R, P) {
    const b = R / 3.3, verts = new Map();
    let edges = "";
    for (let q = -2; q <= 2; q++) for (let s = -2; s <= 2; s++) {
      if (Math.abs(q + s) > 2) continue;
      const cx = Math.sqrt(3) * b * (q + s / 2), cy = 1.5 * b * s, pts = [];
      for (let k = 0; k < 6; k++) {
        const a = Math.PI / 6 + k * Math.PI / 3, p = [cx + b * Math.cos(a), cy + b * Math.sin(a)];
        pts.push(p);
        verts.set(Math.round(p[0]) + "," + Math.round(p[1]), [p, k % 2]);
      }
      edges += pathOf(pts.concat([pts[0]]));
    }
    let dots = "";
    verts.forEach(([p, sub]) => { dots += `<circle cx="${f(p[0])}" cy="${f(p[1])}" r="2.6" fill="${sub ? P.a : P.v}"/>`; });
    return `<path d="${edges}" stroke="${P.c}" stroke-width="1.1" fill="none"/>${dots}`;
  }},
  {id: "bands", tags: ["phys.condmat"], op: .42, draw(R, P) {
    const band = (y0, amp, ph) => {
      const pts = [];
      for (let x = -R; x <= R + .1; x += R / 30) pts.push([x, y0 + amp * Math.cos(Math.PI * x / R + ph)]);
      return pathOf(pts);
    };
    const lab = (x, t) => `<text x="${f(x)}" y="${f(R * .98)}" font-size="${f(R * .13)}" fill="${P.m}" text-anchor="middle" font-family="${SERIF}">${t}</text>`;
    return `<path d="M${f(-R)},${f(-R * .9)}V${f(R * .8)}H${f(R)}" stroke="${P.m}" fill="none" stroke-width="1"/>
      <path d="${band(-R * .62, R * .1, 0)}${band(R * .58, R * .08, Math.PI)}" stroke="${P.c}" stroke-width="1.5" fill="none"/>
      <path d="M${f(-R * .7)},${f(-R * .42)}L${f(R * .7)},${f(R * .42)}M${f(-R * .7)},${f(R * .42)}L${f(R * .7)},${f(-R * .42)}" stroke="${P.a}" stroke-width="1.6" fill="none"/>
      <path d="M${f(-R)},0H${f(R)}" stroke="${P.v}" stroke-dasharray="5 5" stroke-width="1"/>
      ${lab(-R, "Γ")}${lab(0, "K")}${lab(R, "M")}`;
  }},
  {id: "spins", tags: ["phys.condmat", "phys.quantum"], op: .45, draw(R, P, r) {
    const n = 7, dk = .35 + .6 * r(), L = R * .42;
    let out = `<path d="M${f(-R * 1.1)},0H${f(R * 1.1)}" stroke="${P.m}" stroke-width=".8"/>`;
    for (let i = 0; i < n; i++) {
      const x = -R + 2 * R * i / (n - 1), a = -Math.PI / 2 + i * dk, ex = x + L * Math.cos(a), ey = L * Math.sin(a);
      const h1 = a + 2.6, h2 = a - 2.6, hl = L * .28, col = i % 2 ? P.a : P.c;
      out += `<circle cx="${f(x)}" cy="0" r="3" fill="${P.t}"/><path d="M${f(x - .35 * L * Math.cos(a))},${f(-.35 * L * Math.sin(a))}L${f(ex)},${f(ey)}
        M${f(ex + hl * Math.cos(h1))},${f(ey + hl * Math.sin(h1))}L${f(ex)},${f(ey)}L${f(ex + hl * Math.cos(h2))},${f(ey + hl * Math.sin(h2))}"
        stroke="${col}" stroke-width="1.8" fill="none"/>`;
    }
    return out;
  }},
  {id: "bloch", tags: ["phys.quantum"], op: .42, draw(R, P, r) {
    const s = R * .82, th = .5 + .9 * r(), ph = 6.283 * r();
    const x = s * Math.sin(th) * Math.cos(ph), y = -s * Math.cos(th) + s * .28 * Math.sin(th) * Math.sin(ph);
    return `<circle r="${f(s)}" fill="none" stroke="${P.t}" stroke-width="1.2"/>
      <path d="M${f(-s)},0A${f(s)},${f(s * .28)} 0 0 0 ${f(s)},0" fill="none" stroke="${P.t}" stroke-width="1"/>
      <path d="M${f(-s)},0A${f(s)},${f(s * .28)} 0 0 1 ${f(s)},0" fill="none" stroke="${P.m}" stroke-dasharray="4 4"/>
      <path d="M0,${f(-s * 1.1)}V${f(s * 1.1)}" stroke="${P.m}" stroke-width=".8"/>
      <path d="M0,0L${f(x)},${f(y)}" stroke="${P.a}" stroke-width="2"/><circle cx="${f(x)}" cy="${f(y)}" r="3.5" fill="${P.a}"/>
      <text x="6" y="${f(-s * 1.13)}" font-size="${f(R * .14)}" fill="${P.m}" font-family="${SERIF}">|0⟩</text>
      <text x="6" y="${f(s * 1.25)}" font-size="${f(R * .14)}" fill="${P.m}" font-family="${SERIF}">|1⟩</text>`;
  }},
  {id: "feynman", tags: ["phys.hepth"], op: .45, draw(R, P) {
    const v1 = [-R * .38, 0], v2 = [R * .38, 0];
    const arrowLine = (a, b) => {
      const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, an = Math.atan2(b[1] - a[1], b[0] - a[0]), h = R * .09;
      return `M${f(a[0])},${f(a[1])}L${f(b[0])},${f(b[1])}M${f(mx - h * Math.cos(an - .5))},${f(my - h * Math.sin(an - .5))}L${f(mx)},${f(my)}L${f(mx - h * Math.cos(an + .5))},${f(my - h * Math.sin(an + .5))}`;
    };
    const wave = [];
    for (let x = v1[0]; x <= v2[0] + .1; x += R / 60) wave.push([x, R * .08 * Math.sin((x - v1[0]) / (R * .76) * 6 * Math.PI)]);
    return `<path d="${arrowLine([-R, -R * .62], v1)}${arrowLine(v1, [-R, R * .62])}${arrowLine(v2, [R, -R * .62])}${arrowLine([R, R * .62], v2)}"
      stroke="${P.t}" stroke-width="1.5" fill="none"/><path d="${pathOf(wave)}" stroke="${P.a}" stroke-width="1.6" fill="none"/>
      <circle cx="${f(v1[0])}" cy="0" r="3.2" fill="${P.c}"/><circle cx="${f(v2[0])}" cy="0" r="3.2" fill="${P.c}"/>`;
  }},
  {id: "atom", tags: ["phys.general", "phys.quantum"], op: .4, draw(R, P, r) {
    let out = `<circle r="${f(R * .09)}" fill="${P.a}"/>`;
    [0, 60, 120].forEach(rot => {
      const t = 6.283 * r();
      out += `<g transform="rotate(${rot})"><ellipse rx="${f(R)}" ry="${f(R * .32)}" fill="none" stroke="${P.c}" stroke-width="1.2"/>
        <circle cx="${f(R * Math.cos(t))}" cy="${f(R * .32 * Math.sin(t))}" r="3.4" fill="${P.v}"/></g>`;
    });
    return out;
  }},
  {id: "lorenz", tags: ["phys.fluids", "math.other"], op: .42, draw(R, P, r) {
    let x = .1 + .1 * r(), y = 0, z = 0;
    const pts = [], dt = .01;
    for (let i = 0; i < 2600; i++) {
      const dx = 10 * (y - x), dy = x * (28 - z) - y, dz = x * y - 8 / 3 * z;
      x += dx * dt; y += dy * dt; z += dz * dt;
      if (i > 80 && i % 2 === 0) pts.push([x / 20 * R, (25 - z) / 25 * R]);
    }
    return `<path d="${pathOf(pts)}" stroke="${P.c}" stroke-width=".8" fill="none"/>`;
  }},
  {id: "neuralnet", tags: ["ai.general", "ai.theory", "ai.science"], op: .42, draw(R, P, r) {
    const layers = [[3, 5, 4, 2], [4, 6, 6, 3], [3, 4, 4, 4, 2]][Math.floor(r() * 3)];
    const pos = layers.map((n, li) => Array.from({length: n}, (_, i) =>
      [-R + 2 * R * li / (layers.length - 1), (i - (n - 1) / 2) * R * .34]));
    let edges = "", nodes = "";
    for (let li = 0; li < pos.length - 1; li++)
      pos[li].forEach(a => pos[li + 1].forEach(b => { edges += `M${f(a[0])},${f(a[1])}L${f(b[0])},${f(b[1])}`; }));
    pos.flat().forEach(p => { nodes += `<circle cx="${f(p[0])}" cy="${f(p[1])}" r="${f(R * .055)}" fill="${P.bg}" stroke="${P.c}" stroke-width="1.4"/>`; });
    return `<path d="${edges}" stroke="${P.m}" stroke-width=".7" opacity=".7" fill="none"/>${nodes}`;
  }},
  {id: "gaussian", tags: ["math.probability", "ai.theory"], op: .42, draw(R, P, r) {
    let bars = "";
    const n = 13, w = 2 * R / n;
    for (let i = 0; i < n; i++) {
      const xc = -R + w * (i + .5), g = Math.exp(-(((xc / R) * 2.6) ** 2) / 2), hgt = R * 1.3 * g * (0.82 + .36 * r());
      bars += `<rect x="${f(xc - w / 2 + 1)}" y="${f(R * .6 - hgt)}" width="${f(w - 2)}" height="${f(hgt)}" fill="none" stroke="${P.m}" stroke-width="1"/>`;
    }
    const pts = [];
    for (let x = -R; x <= R + .1; x += R / 40) pts.push([x, R * .6 - R * 1.3 * Math.exp(-(((x / R) * 2.6) ** 2) / 2)]);
    return `${bars}<path d="${pathOf(pts)}" stroke="${P.a}" stroke-width="1.8" fill="none"/>
      <path d="M${f(-R * 1.05)},${f(R * .6)}H${f(R * 1.05)}" stroke="${P.t}" stroke-width="1"/>`;
  }},
  {id: "trefoil", tags: ["math.topology"], op: .45, draw(R, P) {
    const pts = [], s = R / 3.1;
    for (let t = 0; t <= 6.3; t += .03) pts.push([s * (Math.sin(t) + 2 * Math.sin(2 * t)), s * (Math.cos(t) - 2 * Math.cos(2 * t))]);
    return `<path d="${pathOf(pts)}" stroke="${P.v}" stroke-width="5" fill="none" opacity=".35"/>
      <path d="${pathOf(pts)}" stroke="${P.v}" stroke-width="1.6" fill="none"/>`;
  }},
  {id: "torus", tags: ["math.geometry", "math.topology"], op: .42, draw(R, P) {
    let lat = "";
    [.72, .86].forEach(k => { lat += `<ellipse rx="${f(R * k)}" ry="${f(R * .45 * k)}" fill="none" stroke="${P.m}" stroke-width=".8" stroke-dasharray="3 4"/>`; });
    let mer = "";
    for (let i = 0; i < 10; i++) {
      const a = i * Math.PI / 5, cx = R * .64 * Math.cos(a), cy = R * .29 * Math.sin(a), rx = R * .36 * Math.abs(Math.sin(a)) + 3;
      mer += `<ellipse cx="${f(cx)}" cy="${f(cy)}" rx="${f(rx)}" ry="${f(R * .3)}" fill="none" stroke="${P.c}" stroke-width=".8" opacity=".6"/>`;
    }
    return `${mer}${lat}<ellipse rx="${f(R)}" ry="${f(R * .45)}" fill="none" stroke="${P.c}" stroke-width="1.5"/>
      <path d="M${f(-R * .5)},${f(-R * .02)}Q0,${f(R * .2)} ${f(R * .5)},${f(-R * .02)}M${f(-R * .38)},${f(R * .06)}Q0,${f(-R * .1)} ${f(R * .38)},${f(R * .06)}"
      stroke="${P.c}" stroke-width="1.5" fill="none"/>`;
  }},
  {id: "contours", tags: ["math.geometry", "math.analysis"], op: .4, draw(R, P, r) {
    const p1 = 6.283 * r(), p2 = 6.283 * r();
    let out = "";
    for (let k = 1; k <= 6; k++) {
      const pts = [];
      for (let t = 0; t <= 6.29; t += .07) {
        const rad = R * k / 6 * (1 + .14 * Math.sin(3 * t + p1) + .07 * Math.cos(2 * t + p2));
        pts.push([rad * Math.cos(t), rad * Math.sin(t) * .8]);
      }
      out += `<path d="${pathOf(pts)}Z" stroke="${k % 2 ? P.v : P.c}" stroke-width="1" fill="none"/>`;
    }
    return out;
  }},
  {id: "primes", tags: ["math.nt"], op: .55, draw(R, P) {
    const N = 900, isP = n => { if (n < 2) return false; for (let d = 2; d * d <= n; d++) if (n % d === 0) return false; return true; };
    let dots = "";
    for (let n = 2; n <= N; n++) if (isP(n)) {
      const rad = R * Math.sqrt(n / N), a = 2 * Math.PI * Math.sqrt(n);
      dots += `<circle cx="${f(rad * Math.cos(a))}" cy="${f(rad * Math.sin(a))}" r="1.5" fill="${n % 4 === 1 ? P.a : P.t}"/>`;
    }
    return dots;
  }},
];

// Faint full-canvas patterns
const PATTERNS = [
  {id: "warp", tags: ["phys.gr", "cosmo.general", "astro.he"], draw(w, h, P, r) {
    const cx = w * (r() < .5 ? .15 + .15 * r() : .7 + .15 * r()), cy = h * (.75 + .15 * r()), A = h * .13, s = w * .12;
    let d = "";
    for (let y = h * .55; y < h; y += h * .085) {
      const pts = [];
      for (let x = 0; x <= w; x += w / 60) pts.push([x, y + A * Math.exp(-((x - cx) ** 2) / (2 * s * s)) * (1 - (y - h * .55) / h)]);
      d += pathOf(pts);
    }
    for (let x = w * .05; x < w; x += w * .09) {
      const pts = [];
      for (let y = h * .5; y <= h; y += h / 40) pts.push([x + (cx - x) * .18 * Math.exp(-((y - cy) ** 2) / (2 * (h * .15) ** 2)), y]);
      d += pathOf(pts);
    }
    return `<path d="${d}" stroke="${P.c}" stroke-width="1" fill="none" opacity=".13"/>`;
  }},
  {id: "lattice", tags: ["phys.condmat", "phys.quantum", "math.algebra"], draw(w, h, P) {
    let dots = "";
    const g = Math.max(46, w / 30);
    for (let y = g / 2; y < h; y += g) for (let x = (Math.round(y / g) % 2) * g / 2; x < w; x += g)
      dots += `<circle cx="${f(x)}" cy="${f(y)}" r="1.1"/>`;
    return `<g fill="${P.m}" opacity=".22">${dots}</g>`;
  }},
  {id: "none", tags: [], base: 1.4, draw() { return ""; }},
];

// ---------------------------------------------------------------------------
function rng(seed) {                                      // mulberry32
  return function () {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
const tagsOf = x => Array.isArray(x) ? x : [x];

function weightOf(tags, weight, base) {
  if (!tags.length) return base || 1;
  const w = Math.max(...tags.map(t => Math.max(0, +weight(t) || 0)));
  return .5 + w / 25;                                   // 0 -> 0.5, 100 -> 4.5
}
function pick(items, n, weightFn, r) {                  // weighted, without replacement
  const pool = items.slice(), out = [];
  while (out.length < n && pool.length) {
    const ws = pool.map(weightFn), tot = ws.reduce((a, b) => a + b, 0);
    let x = r() * tot, i = 0;
    while (i < pool.length - 1 && (x -= ws[i]) > 0) i++;
    out.push(pool.splice(i, 1)[0]);
  }
  return out;
}

function compose({theme = "dark", w = 1600, h = 900, weight = () => 50, seed = 1, avoid = []}) {
  const P = PAL[theme] || PAL.dark, r = rng(seed);
  w = Math.max(320, Math.round(w)); h = Math.max(480, Math.round(h));
  const area = w * h, parts = [];
  // keep-out rectangles [x0, y0, x1, y1]: page text the poster must not sit behind
  const hitsText = (cx, cy, rad) => avoid.some(b => {
    const nx = Math.max(b[0], Math.min(cx, b[2])), ny = Math.max(b[1], Math.min(cy, b[3]));
    return Math.hypot(nx - cx, ny - cy) < rad;
  });
  const boxHitsText = bx => avoid.some(b => !(bx[2] < b[0] || bx[0] > b[2] || bx[3] < b[1] || bx[1] > b[3]));

  const pat = pick(PATTERNS, 1, p => weightOf(p.tags, weight, p.base), r)[0];
  parts.push(pat.draw(w, h, P, r));

  // stars
  let stars = "";
  for (let i = 0; i < Math.round(area / 24000); i++)
    stars += `<circle cx="${f(r() * w)}" cy="${f(r() * h)}" r="${f(.6 + r() * 1.1)}"/>`;
  parts.push(`<g fill="${P.t}" opacity=".45">${stars}</g>`);

  // motifs
  const nMot = Math.max(2, Math.min(5, Math.round(area / 330000)));
  const baseR = Math.max(55, Math.min(150, Math.min(w, h) * .13));
  const placed = [];
  pick(MOTIFS, nMot, m => weightOf(m.tags, weight), r).forEach((m, i) => {
    const R = baseR * (.8 + .5 * r()), ext = m.id === "cmb" ? R * 1.3 : R * 1.15;
    for (let tries = 0; tries < 200; tries++) {
      const x = ext + r() * (w - 2 * ext), y = ext + r() * (h - 2 * ext);
      if (!hitsText(x, y, ext) && placed.every(p => Math.hypot(p.x - x, p.y - y) > (p.e + ext) * 1.1)) {
        placed.push({x, y, e: ext});
        const rot = ["blackhole", "bands", "gaussian", "neuralnet", "feynman", "spins", "bloch"].includes(m.id) ? 0 : Math.round(r() * 360);
        parts.push(`<g transform="translate(${f(x)},${f(y)}) rotate(${rot})" opacity="${f(m.op * P.op)}">${m.draw(R, P, r, "g" + i)}</g>`);
        break;
      }
    }
  });

  // equations
  const nEq = Math.max(4, Math.min(12, Math.round(area / 150000)));
  const fs0 = Math.max(15, Math.min(24, w / 68)), boxes = [];
  // fields with many equations in the library must not crowd out the others
  const perTag = {};
  EQUATIONS.forEach(e => { const t = tagsOf(e[0])[0]; perTag[t] = (perTag[t] || 0) + 1; });
  const eqs = pick(EQUATIONS, nEq * 2, e => weightOf(tagsOf(e[0]), weight) / Math.sqrt(perTag[tagsOf(e[0])[0]]), r);
  let text = "";
  for (const [, eq, cap] of eqs) {
    if (boxes.length >= nEq) break;
    // index notation (^, _) reads naturally in monospace; the rest mostly in italic serif
    const fs = fs0 * (.85 + .35 * r()), serif = !/[\^_]/.test(eq) && r() < .75;
    const bw = eq.length * fs * (serif ? .5 : .6), bh = fs * 2.1;
    if (bw > w - 40) continue;
    for (let tries = 0; tries < 150; tries++) {
      const x = 20 + r() * (w - 40 - bw), y = 30 + fs + r() * (h - 60 - bh);
      const box = [x - 12, y - fs - 8, x + bw + 12, y + fs * 1.1 + 10];
      const clashBox = boxes.some(b => !(box[2] < b[0] || box[0] > b[2] || box[3] < b[1] || box[1] > b[3]));
      const clashMot = placed.some(p => {
        const nx = Math.max(box[0], Math.min(p.x, box[2])), ny = Math.max(box[1], Math.min(p.y, box[3]));
        return Math.hypot(nx - p.x, ny - p.y) < p.e * .95;
      });
      if (clashBox || clashMot || boxHitsText(box)) continue;
      boxes.push(box);
      const col = r() < .72 ? P.t : [P.a, P.c, P.v][Math.floor(r() * 3)];
      text += `<text x="${f(x)}" y="${f(y)}" font-size="${f(fs)}" fill="${col}" font-family="${serif ? SERIF : MONO}"${serif ? ' font-style="italic"' : ""}>${esc(eq)}</text>
        <text x="${f(x)}" y="${f(y + fs * 1.05)}" font-size="${f(Math.max(10, fs * .52))}" fill="${P.m}" font-family="${MONO}">${esc(cap)}</text>`;
      break;
    }
  }
  parts.push(`<g opacity="${f(.5 * P.op)}">${text}</g>`);

  // readability fade toward the bottom
  parts.push(`<defs><linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="${P.bg}" stop-opacity="0"/>
    <stop offset="100%" stop-color="${P.bg}" stop-opacity=".55"/></linearGradient></defs><rect width="${w}" height="${h}" fill="url(#fade)"/>`);

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" preserveAspectRatio="xMidYMid slice">${parts.join("")}</svg>`;
}

let SEED = (Math.random() * 2 ** 31) | 0;
window.RHBackground = {
  svg: compose,
  url(opts = {}) {
    if (opts.reseed) SEED = (Math.random() * 2 ** 31) | 0;
    return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(compose({...opts, seed: SEED}));
  },
  EQUATIONS, MOTIFS, PATTERNS,
};
})();
