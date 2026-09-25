/* Research Horizon background: a new scientific "poster" on every visit.

   Two layers, both behind the page content:
   - an SVG of line-art motifs (lattices, Feynman diagrams, knots, galaxies …),
     sized to the window and used as the page's background image;
   - the equations, typeset in LaTeX with KaTeX (docs/vendor/katex) in their
     own layer, so they carry real fractions, integrals, sums and indices.
   The research profile the reader has chosen makes its own fields more likely
   (weight(node) returns the profile's 0-100 interest in a taxonomy node).

   How strong the poster looks is set by the page: the "Background strength"
   slider under Appearance, default DEFAULT_BG_STRENGTH in docs/index.html.

   API: RHBackground.render({layer, math, theme, w, h, weight, avoid, reseed})
        same seed -> same poster (a theme change or resize keeps it; reseed:
        true draws a new one). */
(function () {
"use strict";

const PAL = {
  // op balances the two themes; overall strength is the page's slider (layer opacity)
  dark:  {a: "#F2B544", c: "#74D7E4", v: "#C792EA", t: "#EDEAF7", m: "#8E89A6", bg: "#0C0A16", k: "#000000", op: 1},
  light: {a: "#C9861B", c: "#0E7C8C", v: "#8B5CB8", t: "#2A2342", m: "#6B6585", bg: "#F7F5FB", k: "#1B1730", op: .9},
};
const MONO = "Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace";
const SERIF = "'Cambria Math','STIX Two Math','STIX Two Text','Latin Modern Math','Times New Roman',serif";
const EQ_OPACITY = .78;                                  // equations relative to the motifs

// ---------------------------------------------------------------------------
// Equations: [taxonomy node(s), LaTeX (KaTeX), caption]
// ---------------------------------------------------------------------------
const EQUATIONS = [
  ["cosmo.general", String.raw`H^2(a) = \frac{8\pi G}{3}\,\rho - \frac{kc^2}{a^2} + \frac{\Lambda c^2}{3}`, "Friedmann 1922"],
  ["cosmo.general", String.raw`ds^2 = -c^2\,dt^2 + a^2(t)\left[\frac{dr^2}{1-kr^2} + r^2\,d\Omega^2\right]`, "FLRW metric"],
  ["cosmo.de", String.raw`w(a) = w_0 + w_a\,(1-a)`, "CPL dark energy"],
  ["cosmo.de", String.raw`\frac{\ddot a}{a} = -\frac{4\pi G}{3}\left(\rho + \frac{3p}{c^2}\right) + \frac{\Lambda c^2}{3}`, "cosmic acceleration"],
  ["cosmo.lss", String.raw`\xi(r) = \int \frac{k^2\,dk}{2\pi^2}\,P(k)\,\frac{\sin kr}{kr}`, "two-point correlation"],
  ["cosmo.lss", String.raw`\ddot\delta + 2H\dot\delta = 4\pi G\,\bar\rho\,\delta`, "linear growth of structure"],
  ["cosmo.early", String.raw`\Delta^2_{\mathcal R}(k) = A_s\left(\frac{k}{k_*}\right)^{n_s-1}`, "primordial power spectrum"],
  ["cosmo.early", String.raw`T(z) = T_0\,(1+z)`, "CMB temperature"],
  ["cosmo.dm", String.raw`\rho(r) = \frac{\rho_s}{\dfrac{r}{r_s}\left(1+\dfrac{r}{r_s}\right)^{2}}`, "NFW halo profile"],
  ["astro.he", String.raw`r_s = \frac{2GM}{c^2}`, "Schwarzschild radius"],
  ["astro.he", String.raw`T_H = \frac{\hbar c^3}{8\pi G M k_B}`, "Hawking 1974"],
  ["astro.he", String.raw`L_{\mathrm{Edd}} = \frac{4\pi G M m_p c}{\sigma_T}`, "Eddington luminosity"],
  ["astro.stellar", String.raw`L = 4\pi R^2\,\sigma T^4`, "Stefan–Boltzmann"],
  ["astro.stellar", String.raw`M_{\mathrm{Ch}} \simeq 1.44\,M_\odot`, "Chandrasekhar limit"],
  ["astro.stellar", String.raw`\frac{dP}{dr} = -\frac{G\,m(r)\,\rho(r)}{r^2}`, "hydrostatic equilibrium"],
  ["astro.galactic", String.raw`v^2(r) = \frac{G\,M({<}\,r)}{r}`, "rotation curve"],
  ["astro.general", String.raw`m - M = 5\log_{10}\frac{d}{10\,\mathrm{pc}}`, "distance modulus"],
  [["phys.gr", "cosmo.general"], String.raw`G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4}\,T_{\mu\nu}`, "Einstein 1915"],
  ["phys.gr", String.raw`\Box\,\bar h_{\mu\nu} = -\frac{16\pi G}{c^4}\,T_{\mu\nu}`, "gravitational waves"],
  ["phys.gr", String.raw`S_{\mathrm{BH}} = \frac{k_B c^3 A}{4G\hbar}`, "Bekenstein–Hawking entropy"],
  ["phys.hepth", String.raw`(i\gamma^\mu \partial_\mu - m)\,\psi = 0`, "Dirac 1928"],
  ["phys.hepth", String.raw`\mathcal L = -\tfrac14\,F^a_{\mu\nu}F^{a\,\mu\nu} + \bar\psi\,(i\gamma^\mu D_\mu - m)\,\psi`, "Yang–Mills with fermions"],
  ["phys.hepth", String.raw`Z = \int \mathcal D\phi\; e^{\,iS[\phi]/\hbar}`, "path integral"],
  ["phys.hepth", String.raw`\partial_\mu j^\mu = 0`, "Noether 1918"],
  ["phys.hepth", String.raw`(\Box + m^2)\,\phi = 0`, "Klein–Gordon"],
  ["phys.quantum", String.raw`i\hbar\,\frac{\partial\psi}{\partial t} = \hat H\psi`, "Schrödinger 1926"],
  ["phys.quantum", String.raw`\Delta x\,\Delta p \ge \frac{\hbar}{2}`, "Heisenberg 1927"],
  ["phys.quantum", String.raw`|\psi\rangle = \alpha\,|0\rangle + \beta\,|1\rangle`, "a qubit"],
  ["phys.quantum", String.raw`S(\rho) = -\operatorname{Tr}\,\rho\ln\rho`, "von Neumann entropy"],
  ["phys.quantum", String.raw`\bigl|\langle AB\rangle + \langle AB'\rangle + \langle A'B\rangle - \langle A'B'\rangle\bigr| \le 2`, "CHSH inequality"],
  ["phys.quantum", String.raw`\dot\rho = -\tfrac{i}{\hbar}[H,\rho] + \sum_k\Bigl(L_k\rho L_k^\dagger - \tfrac12\{L_k^\dagger L_k,\rho\}\Bigr)`, "Lindblad equation"],
  ["phys.condmat", String.raw`H = -J\sum_{\langle ij\rangle}\sigma_i\sigma_j - h\sum_i\sigma_i`, "Ising model"],
  ["phys.condmat", String.raw`H = -t\sum_{\langle ij\rangle,\sigma} c^\dagger_{i\sigma}c_{j\sigma} + U\sum_i n_{i\uparrow}n_{i\downarrow}`, "Hubbard model"],
  ["phys.condmat", String.raw`\sigma_{xy} = \nu\,\frac{e^2}{h}`, "quantum Hall effect"],
  ["phys.condmat", String.raw`C = \frac{1}{2\pi}\int_{\mathrm{BZ}}\Omega(\mathbf k)\,d^2k`, "Chern number"],
  ["phys.condmat", String.raw`\gamma = i\oint \langle u_{\mathbf k}|\nabla_{\mathbf k}u_{\mathbf k}\rangle\cdot d\mathbf k`, "Berry phase"],
  ["phys.condmat", String.raw`\psi_{\mathbf k}(\mathbf r) = e^{i\mathbf k\cdot\mathbf r}\,u_{\mathbf k}(\mathbf r)`, "Bloch 1929"],
  ["phys.condmat", String.raw`\Delta = 2\hbar\omega_D\,e^{-1/N(0)V}`, "BCS gap"],
  ["phys.condmat", String.raw`Z = \sum_i e^{-\beta E_i}`, "partition function"],
  ["phys.condmat", String.raw`S = k_B\ln W`, "Boltzmann"],
  ["phys.condmat", String.raw`f(E) = \frac{1}{e^{(E-\mu)/k_BT} + 1}`, "Fermi–Dirac"],
  ["phys.fluids", String.raw`\frac{\partial\mathbf u}{\partial t} + (\mathbf u\cdot\nabla)\mathbf u = -\frac{\nabla p}{\rho} + \nu\nabla^2\mathbf u`, "Navier–Stokes"],
  ["phys.fluids", String.raw`E(k) \propto \varepsilon^{2/3}\,k^{-5/3}`, "Kolmogorov 1941"],
  [["phys.fluids", "math.other"], String.raw`\dot x = \sigma(y-x),\quad \dot y = x(\rho-z)-y,\quad \dot z = xy-\beta z`, "Lorenz 1963"],
  ["phys.general", String.raw`\nabla\times\mathbf B = \mu_0\mathbf J + \mu_0\varepsilon_0\,\frac{\partial\mathbf E}{\partial t}`, "Ampère–Maxwell"],
  ["phys.general", String.raw`E^2 = (pc)^2 + (mc^2)^2`, "energy–momentum relation"],
  ["phys.general", String.raw`n_1\sin\theta_1 = n_2\sin\theta_2`, "Snell's law"],
  ["math.nt", String.raw`p(n) \sim \frac{1}{4n\sqrt3}\,e^{\pi\sqrt{2n/3}}`, "Hardy–Ramanujan 1918"],
  ["math.nt", String.raw`\zeta(s) = \sum_{n=1}^{\infty}\frac{1}{n^s} = \prod_{p}\frac{1}{1-p^{-s}}`, "Euler product"],
  ["math.nt", String.raw`\pi(x) \sim \frac{x}{\ln x}`, "prime number theorem"],
  ["math.nt", String.raw`a^n + b^n \neq c^n \quad (n > 2)`, "Fermat–Wiles"],
  ["math.geometry", String.raw`\int_M K\,dA + \int_{\partial M} k_g\,ds = 2\pi\,\chi(M)`, "Gauss–Bonnet"],
  ["math.geometry", String.raw`\mathrm{Ric}(g) = \lambda\,g`, "Einstein metrics"],
  ["math.topology", String.raw`V - E + F = 2`, "Euler 1758"],
  ["math.topology", String.raw`\int_M d\omega = \int_{\partial M}\omega`, "Stokes' theorem"],
  ["math.topology", String.raw`\pi_1(S^1) \cong \mathbb Z`, "fundamental group"],
  [["math.topology", "math.mathphys"], String.raw`\operatorname{ind} D = \int_M \hat A(M)\,\mathrm{ch}(E)`, "Atiyah–Singer"],
  [["math.mathphys", "phys.hepth"], String.raw`S_{\mathrm{CS}} = \frac{k}{4\pi}\int_M \mathrm{tr}\Bigl(A\wedge dA + \tfrac23 A\wedge A\wedge A\Bigr)`, "Chern–Simons theory"],
  ["math.mathphys", String.raw`[\hat x,\hat p] = i\hbar`, "canonical commutation"],
  ["math.algebra", String.raw`|G| = |H|\,[G:H]`, "Lagrange's theorem"],
  ["math.algebra", String.raw`[X_i, X_j] = f_{ij}{}^{k}\,X_k`, "Lie algebra"],
  ["math.analysis", String.raw`e^{i\pi} + 1 = 0`, "Euler"],
  ["math.analysis", String.raw`\oint_\gamma \frac{f(z)}{z-a}\,dz = 2\pi i\,f(a)`, "Cauchy 1831"],
  ["math.analysis", String.raw`\hat f(\xi) = \int_{-\infty}^{\infty} f(x)\,e^{-2\pi i x\xi}\,dx`, "Fourier transform"],
  ["math.analysis", String.raw`\sum_{n=1}^{\infty}\frac{1}{n^2} = \frac{\pi^2}{6}`, "Basel problem"],
  ["math.probability", String.raw`dX_t = \mu\,dt + \sigma\,dW_t`, "Itô SDE"],
  ["math.probability", String.raw`p(\theta\mid D) = \frac{p(D\mid\theta)\,p(\theta)}{p(D)}`, "Bayes"],
  ["math.probability", String.raw`\sqrt{n}\,\bigl(\bar X_n - \mu\bigr) \xrightarrow{\;d\;} \mathcal N(0,\sigma^2)`, "central limit theorem"],
  ["ai.general", String.raw`\mathrm{Attention}(Q,K,V) = \mathrm{softmax}\!\left(\frac{QK^{\top}}{\sqrt{d_k}}\right)V`, "attention, 2017"],
  ["ai.general", String.raw`\theta_{t+1} = \theta_t - \eta\,\nabla_\theta \mathcal L(\theta_t)`, "gradient descent"],
  ["ai.general", String.raw`V(s) = \max_a\Bigl[r(s,a) + \gamma\sum_{s'}P(s'\mid s,a)\,V(s')\Bigr]`, "Bellman equation"],
  ["ai.theory", String.raw`\log p(x) \ge \mathbb E_{q(z)}\bigl[\log p(x\mid z)\bigr] - D_{\mathrm{KL}}\bigl(q\,\|\,p\bigr)`, "evidence lower bound"],
  ["ai.theory", String.raw`H(X) = -\sum_x p(x)\log_2 p(x)`, "Shannon 1948"],
  ["ai.theory", String.raw`R(h) \le \hat R_n(h) + O\Bigl(\sqrt{d/n}\Bigr)`, "generalisation bound"],
  ["ai.science", String.raw`p(\theta\mid x_{\mathrm{obs}}) \propto p(x_{\mathrm{obs}}\mid\theta)\,p(\theta)`, "simulation-based inference"],
  ["ai.science", String.raw`d\mathbf x = \bigl[\mathbf f(\mathbf x,t) - g(t)^2\,\nabla_{\mathbf x}\log p_t(\mathbf x)\bigr]dt + g(t)\,d\bar{\mathbf w}`, "score-based diffusion"],
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

  // readability fade toward the bottom
  parts.push(`<defs><linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="${P.bg}" stop-opacity="0"/>
    <stop offset="100%" stop-color="${P.bg}" stop-opacity=".55"/></linearGradient></defs><rect width="${w}" height="${h}" fill="url(#fade)"/>`);

  return {svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" preserveAspectRatio="xMidYMid slice">${parts.join("")}</svg>`,
          placed, w, h};
}

// ---------------------------------------------------------------------------
// Equations: typeset with KaTeX, measured, then placed where they fit
// ---------------------------------------------------------------------------
let mathJob = 0;
function placeMath(math, {theme = "dark", w, h, weight = () => 50, seed = 1, avoid = [], placed = []}) {
  const job = ++mathJob;
  math.innerHTML = "";
  if (!window.katex) {                                   // KaTeX still loading: try again once it is there
    window.addEventListener("load", () => { if (job === mathJob && window.katex) placeMath(math, arguments[1]); }, {once: true});
    return;
  }
  const P = PAL[theme] || PAL.dark, r = rng(seed ^ 0x5bd1e995);
  const area = w * h, nEq = Math.max(3, Math.min(11, Math.round(area / 150000)));
  const fs0 = Math.max(14, Math.min(21, w / 76));
  const perTag = {};                                     // big fields must not crowd out the others
  EQUATIONS.forEach(e => { const t = tagsOf(e[0])[0]; perTag[t] = (perTag[t] || 0) + 1; });
  const cands = pick(EQUATIONS, nEq * 2, e => weightOf(tagsOf(e[0]), weight) / Math.sqrt(perTag[tagsOf(e[0])[0]]), r);
  const els = cands.map(([, tex, cap]) => {
    const el = document.createElement("div");
    el.className = "eq";
    el.style.cssText = `font-size:${f(fs0 * (.85 + .35 * r()))}px;color:${r() < .7 ? P.t : [P.a, P.c, P.v][Math.floor(r() * 3)]};` +
                       `opacity:${f(EQ_OPACITY * P.op)};visibility:hidden;left:0;top:0`;
    try {
      el.innerHTML = window.katex.renderToString(tex, {throwOnError: false, output: "html"}) +
                     `<div class="cap" style="color:${P.m}">${esc(cap)}</div>`;
    } catch (e) { return null; }
    math.appendChild(el);
    return el;
  }).filter(Boolean);
  const fontsReady = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
  fontsReady.then(() => {
    if (job !== mathJob) return;
    const boxes = [], hits = (bx, list) => list.some(b => !(bx[2] < b[0] || bx[0] > b[2] || bx[3] < b[1] || bx[1] > b[3]));
    for (const el of els) {
      if (boxes.length >= nEq) { el.remove(); continue; }
      const bw = el.offsetWidth, bh = el.offsetHeight;
      let ok = false;
      if (bw && bw < w - 40) for (let tries = 0; tries < 150 && !ok; tries++) {
        const x = 20 + r() * (w - 40 - bw), y = 24 + r() * (h - 48 - bh);
        const box = [x - 14, y - 10, x + bw + 14, y + bh + 10];
        const nearMotif = placed.some(p => {
          const nx = Math.max(box[0], Math.min(p.x, box[2])), ny = Math.max(box[1], Math.min(p.y, box[3]));
          return Math.hypot(nx - p.x, ny - p.y) < p.e * .95;
        });
        if (hits(box, boxes) || hits(box, avoid) || nearMotif) continue;
        boxes.push(box);
        el.style.left = f(x) + "px"; el.style.top = f(y) + "px"; el.style.visibility = "visible";
        ok = true;
      }
      if (!ok) el.remove();
    }
  });
}

let SEED = (Math.random() * 2 ** 31) | 0;
window.RHBackground = {
  /* Draw the poster: motifs into `layer` (background image), equations into `math`. */
  render({layer, math, theme = "dark", w = 1600, h = 900, weight = () => 50, avoid = [], reseed = false} = {}) {
    if (reseed) SEED = (Math.random() * 2 ** 31) | 0;
    const out = compose({theme, w, h, weight, avoid, seed: SEED});
    if (layer) layer.style.backgroundImage = `url("data:image/svg+xml;charset=utf-8,${encodeURIComponent(out.svg)}")`;
    if (math) placeMath(math, {theme, w: out.w, h: out.h, weight, avoid, placed: out.placed, seed: SEED});
    return out;
  },
  clear(math) { mathJob++; if (math) math.innerHTML = ""; },
  svg: opts => compose(opts).svg,
  EQUATIONS, MOTIFS, PATTERNS,
};
})();
