// Offline check of phg_report.html: no network, no kernel. Usage: node check_html.cjs <html> <shot_dir>
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const file = path.resolve(process.argv[2] || 'phg_report.html');
  const shots = process.argv[3] || null;
  const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const results = {};
  for (const [label, vp] of [['desktop', { width: 1280, height: 900 }], ['phone', { width: 390, height: 844 }]]) {
    const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 1, offline: true });
    const page = await ctx.newPage();
    const errors = [], blocked = [];
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('pageerror', e => errors.push(String(e)));
    await page.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); blocked.push(u); return r.abort(); });
    await page.goto('file://' + file, { waitUntil: 'load' });
    await page.waitForTimeout(1500);
    const info = await page.evaluate(() => {
      const plots = [...document.querySelectorAll('.js-plotly-plot')];
      return {
        plotly: typeof window.Plotly, plots: plots.length,
        rendered: plots.filter(p => p._fullLayout && p.querySelector('svg.main-svg')).length,
        evidence: document.querySelectorAll('.phg-evidence').length,
        verify: document.querySelectorAll('.phg-verify').length,
        codeOpen: [...document.querySelectorAll('details.code')].filter(d => d.open).length,
        scrollW: document.documentElement.scrollWidth, innerW: window.innerWidth,
        widest: plots.map(p => p.getBoundingClientRect().width).reduce((a, b) => Math.max(a, b), 0),
      };
    });
    // Exercise every updatemenu button and slider step through Plotly's own API.
    const interact = await page.evaluate(async () => {
      let n = 0, bad = [];
      for (const gd of document.querySelectorAll('.js-plotly-plot')) {
        const menus = (gd.layout.updatemenus || []), sliders = (gd.layout.sliders || []);
        const steps = [...menus.flatMap(m => m.buttons), ...sliders.flatMap(s => s.steps)];
        for (const b of steps) {
          try { await Plotly[b.method](gd, ...b.args); n++; } catch (e) { bad.push(gd.id + ':' + b.label + ':' + e); }
        }
        const first = menus.length ? menus[0].buttons[menus[0].active || 0] : (sliders.length ? sliders[0].steps[sliders[0].active] : null);
        if (first) await Plotly[first.method](gd, ...first.args);
      }
      return { n, bad };
    });
    // A real click on a dropdown (4.3 prediction format) to confirm DOM interaction works.
    let clicked = false;
    try {
      const hdr = page.locator('[id="fig-4.2"] .updatemenu-header').first();
      await hdr.scrollIntoViewIfNeeded(); await hdr.click();
      const item = page.locator('[id="fig-4.2"] .updatemenu-dropdown-button').nth(2);
      await item.click(); await page.waitForTimeout(300);
      clicked = await page.evaluate(() => { const d = document.getElementById('fig-4.2').data;
        return d[2].visible === true && d[0].visible === false &&
          document.getElementById('label-4.2').textContent === 'Figure 4.2. Trait correlations (r)'; });
      await page.locator('[id="fig-4.2"] .updatemenu-header').first().click();
      await page.locator('[id="fig-4.2"] .updatemenu-dropdown-button').nth(0).click();
    } catch (e) { clicked = 'error: ' + e; }
    // Iteration 8: Figure 4.3 must draw all three series on load, after switching formats both ways (real clicks), and
    // after a tap on a legend entry (legend taps used to hide a series and grey it out).
    const series43 = async (id = '4.3') => page.evaluate((id) => {
      const g = document.getElementById('fig-' + id);
      const vis = g._fullData.filter(t => t.visible === true);
      const drawn = [...g.querySelectorAll('.scatterlayer .trace')].map(e => e.querySelectorAll('.point').length).filter(n => n > 0).length;
      const legend = [...g.querySelectorAll('.legend .traces')].map(e => [e.textContent, e.style.opacity || '1']);
      const label = document.getElementById('label-' + id).textContent;
      return { names: vis.map(t => t.name).sort().join('|'), drawn, legend, label, menus: (g.layout.updatemenus || []).length };
    }, id);
    const pred43 = {};
    try {
      await page.locator('[id="fig-4.3"]').scrollIntoViewIfNeeded(); await page.waitForTimeout(200);
      pred43.load = await series43();
      await page.locator('[id="fig-4.3"] .legend .traces').nth(1).click(); await page.waitForTimeout(300);
      pred43.afterLegendTap = await series43();
      pred43.xTitle = await page.evaluate(() => { const g = document.getElementById('fig-4.3'); const svg = g.querySelector('svg.main-svg').getBoundingClientRect();
        return [...g.querySelectorAll('.xtitle')].map(e => { const r = e.getBoundingClientRect(); return { left: r.left - svg.left, right: svg.right - r.right }; }); });
    } catch (e) { pred43.error = String(e); }
    const series43ok = s => s && s.names === 'Human benchmark|Qwen|Qwen, calibrated' && s.drawn === 3 && s.menus === 0 &&
      s.legend.length === 3 && s.legend.every(([, o]) => o === '1') && /^Figure E\.6\. How well Qwen/.test(s.label)  /* Figure 4.6 since iteration 33 */;
    const pred43ok = ['load', 'afterLegendTap'].every(k => series43ok(pred43[k])) &&
      pred43.xTitle && pred43.xTitle.length === 1 && pred43.xTitle[0].left >= 0 && pred43.xTitle[0].right >= 0;
    const extra = await page.evaluate(async () => {
      let out_m;
      const det = document.getElementById('detail-4.2');
      const initial = det ? det.dataset.pair : null;
      const gd = document.getElementById('fig-4.2');
      // Simulate a tap on a cell through Plotly's own event (Gregariousness row, Friendliness column).
      const names = gd.data[0].x;
      gd.emit('plotly_click', { points: [{ x: 'Friendliness', y: 'Gregariousness' }] });
      const after = det ? det.dataset.pair : null;
      out_m = { upperFilled: Number.isFinite(gd._fullData[0].z[0][5]), lowerFilled: Number.isFinite(gd._fullData[0].z[5][0]), diagBlank: !Number.isFinite(gd._fullData[0].z[3][3]),
        guided: (gd.layout.annotations || []).filter(a => /–/.test(a.text || '')).length + gd._fullData.filter(t => t.type === 'scatter').length,
        revBoxes: gd._fullLayout.shapes.filter(s => s.name === 'reversal').length, domainEdge: (gd.layout.annotations || []).filter(a => (a.name || '').startsWith('domband|facet')).length, bandShapes: gd._fullLayout.shapes.filter(s => s.fillcolor === '#e9edf3' || s.fillcolor === '#dbe2ec').length };
      const lab42 = () => document.getElementById('label-4.2').innerText;
      out_m.label0 = lab42();
      const dbtn = gd.layout.updatemenus[0].buttons.findIndex(b => b.label === 'Domains: People');
      await Plotly.update(gd, ...gd.layout.updatemenus[0].buttons[dbtn].args);
      out_m.domainX2 = gd.layout.xaxis2.visible === true && gd.layout.xaxis.visible === false;
      out_m.revBoxesDomain = gd._fullLayout.shapes.filter(s => s.name === 'reversal').length;
      await new Promise(r => setTimeout(r, 150)); out_m.labelDomain = lab42();
      out_m.cbarDomain = (gd._fullData.filter(t => t.visible === true)[0].colorbar.title || {}).text;
      out_m.domainCells = gd._fullData.filter(t => t.visible === true)[0].z.map(r => Array.from(r)).flat().filter(v => Number.isFinite(v)).length;
      await Plotly.update(gd, ...gd.layout.updatemenus[0].buttons[0].args);
      const phone = [...document.querySelectorAll('.phone-only')].map(e => getComputedStyle(e).display);
      const tech = [...document.querySelectorAll('details.technical')][0];
      tech.open = true; await new Promise(r => setTimeout(r, 400));
      const g44 = document.getElementById('fig-E.1');
      const w44 = g44 ? g44.getBoundingClientRect().width : 0;
      tech.open = false;
      const txt = document.body.innerText;
      // Iteration 5: structure, draft outlines, links, ordinary-roles toggle, facet-fit figure.
      const outlines = [...document.querySelectorAll('.phg-outline')];
      const s5 = { outlines: outlines.length, outlineLabels: outlines.filter(o => o.innerText.toUpperCase().includes('DRAFT OUTLINE')).length,
        contents: !!document.querySelector('nav.toc .toc-title') && document.querySelector('nav.toc .toc-title').innerText === 'Contents',
        tocEntries: document.querySelectorAll('nav.toc a').length,
        brokenLinks: [...document.querySelectorAll('a[href^="#"]')].map(a => a.getAttribute('href').slice(1)).filter(id => id && !document.getElementById(id)),
        sourceTags: document.querySelectorAll('.phg-source').length };
      // Iteration 6: six matrix views, format-averaged Qwen, no ordinary-role views; headline without a menu.
      s5.matrixLabels = gd.layout.updatemenus[0].buttons.map(b => b.label);
      const H = document.getElementById('fig-H');
      s5.headlineMenus = (H.layout.updatemenus || []).length; s5.headlineTraces = H.data.length;
      s5.headlineNote = (H.layout.annotations || []).map(a => a.text).join(' | ');
      // Iteration 11: the trait-pair density figure (Figure G.1 since iteration 16; was 2.1).
      const m21 = document.getElementById('fig-G.1');
      const m21s = () => ({ x: m21.layout.xaxis.title.text, y: m21.layout.yaxis.title.text,
        vis: m21._fullData.filter(t => t.visible === true).map(t => t.type + ':' + t.name).join('|'),
        note: (m21.layout.annotations || []).map(a => a.text).join(' '), label: document.getElementById('label-G.1').textContent,
        maxPts: Math.max(...m21._fullData.filter(t => t.type === 'scatter').map(t => (t.x || []).length)) });
      s5.m21 = [m21s()];
      for (const i of [1, 2, 0]) { await Plotly.update(m21, ...m21.layout.updatemenus[0].buttons[i].args); s5.m21.push(m21s()); }
      // Iteration 13: Qwen–Gemma on load; menu order Qwen–Gemma | Llama–Gemma | Qwen–Llama; buttons 1, 2, 0 visited.
      s5.m21menu = m21.layout.updatemenus[0].buttons.map(b => b.label).join('|');
      s5.m21active = m21._fullLayout.updatemenus[0].active;
      s5.m21header = (m21.querySelector('.updatemenu-header-group text') || {}).textContent;
      const exp = [['Qwen', 'Gemma', '.87', '0.98'], ['Qwen', 'Llama', '.73', '0.94'], ['Llama', 'Gemma', '.84', '1.04'], ['Qwen', 'Gemma', '.87', '0.98']];
      s5.m21ok = s5.m21.every((v, k) => v.x === 'Correlation between the two traits in ' + exp[k][0] + ' (r)' &&
        v.y === 'Correlation between the two traits in ' + exp[k][1] + ' (r)' &&
        v.note === 'agreement r = ' + exp[k][2] + ' · ' + exp[k][1] + ' links ' + exp[k][3] + 'x as strong as ' + exp[k][0] &&
        v.vis.split('|').length === 4 && ['heatmap:Trait pairs', 'scatter:Trend', 'scatter:Perfect agreement'].every(x => v.vis.split('|').includes(x)) &&
        v.label === 'Figure 2.1. Trait correlations compared between models (r)' && v.maxPts <= 3) &&
        s5.m21menu === 'Qwen–Gemma|Qwen–Llama|Llama–Gemma' && s5.m21active === 0 && s5.m21header === 'Qwen–Gemma';
      // Iteration 16: Figure 2.1 is the activation-axes heatmap (was G.3); menu Qwen–Gemma | Qwen–Llama updates the x title.
      const h21 = document.getElementById('fig-2.1');
      const h21s = () => ({ x: h21.layout.xaxis.title.text, y: h21.layout.yaxis.title.text,
        vis: h21._fullData.filter(t => t.visible === true).map(t => t.type).join('|'), label: document.getElementById('label-2.1').textContent });
      s5.h21 = [h21s()];
      for (const i of [1, 0]) { await Plotly.update(h21, ...h21.layout.updatemenus[0].buttons[i].args); s5.h21.push(h21s()); }
      s5.h21menu = h21.layout.updatemenus[0].buttons.map(b => b.label).join('|');
      s5.h21header = (h21.querySelector('.updatemenu-header-group text') || {}).textContent;
      const hx = ['Gemma', 'Llama', 'Gemma'];
      s5.h21ok = s5.h21.every((v, k) => v.x === hx[k] + "'s activation axes" && v.y === "Qwen's activation axes" && v.vis === 'heatmap' &&
        v.label === "Figure 2.2. Correlation between the models' main activation axes (r)") &&
        s5.h21menu === 'Qwen–Gemma|Qwen–Llama' && s5.h21header === 'Qwen–Gemma' &&
        !document.getElementById('wrap-G.3') && !document.getElementById('fig-G.3') &&
        !![...document.querySelectorAll('#g3-main-activation-axes ~ p a[href="#wrap-2.1"]')].length &&
        !document.getElementById('wrap-G.2') && !!document.querySelector('a[href="#wrap-G.1"]') &&
        document.getElementById('label-2.2').textContent.startsWith('Figure G.2. Agreement of character scores between models') &&
        // Iteration 53: Section 2 order is trait pairs (2.1), axes (2.2), shared directions (2.3); per-trait agreement in Appendix G.
        !!(document.getElementById('wrap-G.1').compareDocumentPosition(document.getElementById('wrap-2.1')) & Node.DOCUMENT_POSITION_FOLLOWING) &&
        !!(document.getElementById('g2-persona-scores').compareDocumentPosition(document.getElementById('wrap-2.2')) & Node.DOCUMENT_POSITION_FOLLOWING);
      // Iteration 18: Figure 2.2 (consensus C1-C5 vs activation PCs), model menu Qwen | Gemma | Llama, x title follows.
      const c23 = document.getElementById('fig-2.3');
      const c23s = () => ({ x: c23.layout.xaxis.title.text, vis: c23._fullData.filter(t => t.visible === true).length,
        label: document.getElementById('label-2.3').textContent });
      s5.c23 = [c23s()];
      // Iteration 43: HTML menus (Show; Model). Cycle the models, then the contributing-traits view (Qwen).
      for (const m of ['gemma', 'llama', 'qwen']) { if (window.CS) { window.CS.state.v = 'axes'; window.CS.state.m = m; window.CS.apply(); }
        await new Promise(r => setTimeout(r, 120)); s5.c23.push(c23s()); }
      if (window.CS) { window.CS.state.v = 'traits'; window.CS.state.m = 'qwen'; window.CS.apply(); await new Promise(r => setTimeout(r, 150)); }
      s5.c23traits = { vis: c23._fullData.filter(t => t.visible === true).map(t => t.name).join(),
        rows: (c23._fullData.find(t => t.visible === true) || {z: []}).z.length, opts: [...document.querySelectorAll('#cs-2 option')].length,
        bands: (c23.layout.annotations || []).filter(a => (a.name || '').startsWith('cband|')).length };
      if (window.CS) { window.CS.state.v = 'axes'; window.CS.state.m = 'qwen'; window.CS.apply(); await new Promise(r => setTimeout(r, 120)); }
      const cx = ['Qwen', 'Gemma', 'Llama', 'Qwen'];
      s5.c23ok = s5.c23.every((v, k) => v.x === cx[k] + "'s activation axes" && v.vis === 1 &&
        v.label === "Figure 2.3. Shared directions and their strongest traits on each model's main activation axes (r)") &&
        !(c23.layout.updatemenus || []).length && !!document.getElementById('cs-ctl') &&
        s5.c23traits.vis === 'Traits: Qwen' && s5.c23traits.rows === 30 && s5.c23traits.opts === 3 && s5.c23traits.bands === 5 &&
        // Iteration 19: key table above the figure, five rows; axis labels carry the short meanings.
        (() => { const t = document.getElementById('table-ckey'); const w = document.getElementById('wrap-2.3');
                 return !!t && t.querySelectorAll('tbody tr').length === 5 && !!(t.compareDocumentPosition(w) & Node.DOCUMENT_POSITION_FOLLOWING) &&
                   (c23.data[0].y[0] === (window.innerWidth < 600 ? 'D1' : 'D1 · charged vs moderate')); })();
      // Iteration 21: Figure 1.2 is the trait-coloured PC1-PC2 map with the axis guide; the factor figure is E.4.
      const f12 = document.getElementById('fig-1.1'), f31 = document.getElementById('fig-3.2'), fe4 = document.getElementById('fig-E.4');
      // Iteration 25: HTML menus (model, axis, trait); the trait list is rebuilt per model and axis.
      s5.f12 = {};
      if (f12 && window.PM) {
        const sel = id => document.getElementById(id);
        const opts = () => [...sel('pm-tr').options].map(o => o.textContent);
        s5.f12.q2 = opts();
        sel('pm-ax').value = 'PC3'; sel('pm-ax').dispatchEvent(new Event('change')); await new Promise(r => setTimeout(r, 150));
        s5.f12.q3 = opts(); s5.f12.yq3 = f12.layout.yaxis.title.text;
        sel('pm-m').value = 'llama'; sel('pm-m').dispatchEvent(new Event('change')); await new Promise(r => setTimeout(r, 150));
        s5.f12.l3 = opts(); s5.f12.xl = f12.layout.xaxis.title.text; s5.f12.yl = f12.layout.yaxis.title.text;
        s5.f12.note = (f12.layout.annotations || [])[0].text;
        sel('pm-m').value = 'qwen'; sel('pm-m').dispatchEvent(new Event('change'));
        sel('pm-ax').value = 'PC2'; sel('pm-ax').dispatchEvent(new Event('change')); await new Promise(r => setTimeout(r, 150));
      }
      s5.f12ok = !!f12 && !!document.getElementById('pm-ctl') && !(f12.layout.updatemenus || []).length &&
        JSON.stringify(s5.f12.q2) === JSON.stringify(['Factual (PC1 high)', 'Dramatic (PC1 low)', 'Experiential (PC2 high)',
          'Introverted (PC2 low)', 'Conscientious (PC1–PC2 diagonal)']) &&
        s5.f12.q3.length === 5 && s5.f12.q3[2] === 'Callous (PC3 high)' && s5.f12.q3[4].endsWith('(PC1–PC3 diagonal)') &&
        s5.f12.yq3 === "Position on Qwen's PC3" && s5.f12.l3.length === 5 && s5.f12.l3[0] === 'Grounded (PC1 high)' &&
        s5.f12.xl === "Position on Llama's PC1" && s5.f12.yl === "Position on Llama's PC3" && /^r with PC1 [+−]\.\d\d · PC2/.test(s5.f12.note) &&
        document.getElementById('label-1.1').textContent === "Figure 1.1. Characters on each model's activation axes, coloured by one trait" &&
        !!document.getElementById('table-axes') && document.querySelectorAll('#table-axes tbody tr').length === 9 &&
        !!fe4 && fe4.layout.updatemenus[0].buttons.map(b => b.label).join('|') === 'Qwen|Gemma|Llama' &&
        !!document.getElementById('table-fkey') && document.querySelectorAll('#table-fkey tbody tr').length === 5 &&
        document.getElementById('fig-2.1').data[0].x.length === 5 && document.getElementById('fig-2.3').data[0].x.length === 5;
      if (f31) { for (const i of [1, 0]) { await Plotly.update(f31, ...f31.layout.updatemenus[0].buttons[i].args); } }
      s5.f31ok = !!f31 && f31.layout.updatemenus[0].buttons.length === 2 && f31._fullData.filter(t => t.visible === true).length === 1 &&
        f31.data[0].visible !== false && f31.data[0].y.length === 26 &&
        document.getElementById('label-3.2').textContent === "Figure E.5. Qwen's facets and its main directions (r)" &&
        ![...document.querySelectorAll('#table-ckey th')].some(th => th.textContent === 'Closest Qwen factor');
      // Iteration 46: Figure 3.1 (key 1.3) is one Big Five matrix: Rows / Columns / Show HTML menus re-draw one heatmap.
      const f13 = document.getElementById('fig-1.3');
      s5.f13 = null;
      if (f13 && window.BM) {
        const S = window.BM.state, tick = () => new Promise(r => setTimeout(r, 150));
        const pick = async (r, c, s) => { S.r = r; S.c = c; S.s = s; window.BM.apply(); await tick();
          const t = f13.data[0]; return { st: [S.r, S.c, S.s].join('|'), ny: t.z.length, nx: t.z[0].length, z: t.z, y: f13.layout.yaxis.ticktext }; };
        const start = { st: [S.r, S.c, S.s].join('|'), z: f13.data[0].z, cap: document.getElementById('bm-cap').textContent };
        const tr = await pick('qwen', 'people', 'tr');
        const dtr = await pick('people', 'llama', 'dtr');
        const ddom = await pick('people', 'llama', 'ddom');
        const bf = await pick('gemma', 'bf', 'tr');
        const pc = await pick('llama', 'pc', 'dom');
        const fall = await pick('people', 'pc', 'dom');  // no data: falls back to Big Five columns
        const peoplePcDisabled = [...document.getElementById('bm-c').options].find(o => o.value === 'pc').disabled;
        await pick('qwen', 'people', 'dom');
        const sym = M => M.every((row, i) => row.every((v, j) => v === null || M[j][i] === null || Math.abs(v - M[j][i]) < 1e-9));
        s5.f13 = { start, menus: [...document.querySelectorAll('#bm-ctl select')].map(e => e.id).join('|'),
          shows: [...document.getElementById('bm-s').options].map(o => o.textContent).join('|'),
          label: document.getElementById('label-1.3').textContent,
          tr: { st: tr.st, ny: tr.ny, rev: tr.y.filter(y => / \(−\)$/.test(y)).length },
          dtr: { st: dtr.st, ny: dtr.ny, sym: sym(dtr.z), full: dtr.z[0][41] !== null && dtr.z[41][0] !== null },
          ddom: { st: ddom.st, ny: ddom.ny, sym: sym(ddom.z), full: ddom.z[0][4] !== null && ddom.z[4][0] !== null },
          bf: [bf.ny, bf.nx], pc: [pc.ny, pc.nx], fall: fall.st, peoplePcDisabled };
      }
      const F = s5.f13;
      s5.f13ok = !!F && F.menus === 'bm-r|bm-c|bm-s' && F.shows === 'Domain scores|Traits|Difference: domain scores|Difference: traits' &&
        F.label === 'Figure 3.1. Big Five traits and domains in people and the three models (r)' &&
        F.start.st === 'qwen|people|dom' && Math.abs(F.start.z[1][0] - 0.53) < 0.006 && Math.abs(F.start.z[0][1] + 0.21) < 0.006 &&
        /Below the diagonal: Qwen/.test(F.start.cap) &&
        F.tr.st === 'qwen|people|tr' && F.tr.ny === 42 && F.tr.rev === 15 &&
        F.dtr.st === 'people|llama|dtr' && F.dtr.ny === 42 && F.dtr.sym && F.dtr.full &&
        F.ddom.st === 'people|llama|ddom' && F.ddom.ny === 5 && F.ddom.sym && F.ddom.full &&
        F.bf.join() === '42,5' && F.pc.join() === '5,5' && F.fall === 'people|bf|dom' && F.peoplePcDisabled;
      // Iteration 32: Figure 6.1 (Discussion), three views; the generic-persona view shows six sources.
      const f61 = document.getElementById('fig-6.1');
      s5.f61ok = !!f61 && f61.layout.updatemenus[0].buttons.map(b => b.label).join('|') === 'Answers: generic personas|Answers: demographic personas|Activations: three models' &&
        f61._fullData.filter(t => t.visible === true).length === 6 && f61._fullData[0].x.length === 10 &&
        document.getElementById('label-6.1').textContent.startsWith('Figure 5.1. Correlation between Big Five domain scores');
      s5.labels = [...document.querySelectorAll('.fig-id')].map(e => e.textContent);
      // Iteration 14: Appendix G figures, source lines, G.3b default view.
      const g3b = document.getElementById('fig-G.3b'), g4 = document.getElementById('fig-G.4');
      s5.g = { ids: ['G.1', '2.2', 'G.3b', 'G.4'].map(id => !!document.getElementById('wrap-' + id)),
        sources: document.querySelectorAll('.phg-gsource').length,
        g3bMenu: g3b ? g3b.layout.updatemenus[0].buttons.map(b => b.label).join('|') : '',
        g3bHeader: g3b ? (g3b.querySelector('.updatemenu-header-group text') || {}).textContent : '',
        g3bY: g3b ? g3b.layout.yaxis.title.text : '', g4Shapes: g4 ? (g4.layout.shapes || []).length : 0,
        legendTaps: [...document.querySelectorAll('.js-plotly-plot[id^="fig-G."]')].every(g => g.layout.legend &&
          g.layout.legend.itemclick === false) };
      s5.gok = s5.g.ids.every(Boolean) && s5.g.sources === 9 && s5.g.g3bMenu === 'Qwen–Gemma|Qwen–Llama' &&
        s5.g.g3bHeader === 'Qwen–Gemma' && s5.g.g3bY === "Position on Gemma's PC1" && s5.g.g4Shapes === 5 && s5.g.legendTaps;
      // Iteration 9: no "scenario" / "survey" on main-text figures (svg text, menus, legends, axes) or table headers.
      const MAIN = ['H', '4.2', '4.3', '5a', '5b', '5c', '5d.2', '5d.3', '5e.1', '5e.3'];
      const appA = [...document.querySelectorAll('h2')].find(h => /^Appendix A/.test(h.textContent));
      const sec3 = [...document.querySelectorAll('h2')].find(h => /^3 /.test(h.textContent));
      const sec4 = [...document.querySelectorAll('h2')].find(h => /^4 /.test(h.textContent));
      const before = (a, b) => !!(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING);
      const inMain = el => appA && before(el, appA);  // iteration 10: Section 3 has no table or figure any more
      s5.no32 = /^Figure E.5. Qwen's facets/.test((document.getElementById('label-3.2') || {}).textContent || '') &&  // iteration 29: 3.2 is the facet-geometry figure; the old 3.2 (format agreement) is F.1
        !!document.getElementById('wrap-F.1') &&
        document.getElementById('label-F.1').textContent === 'Figure F.1. Agreement between the two elicitation methods' &&
        // Iteration 15: Figures F.2-F.4 removed; F.2 is a table whose "Shown in" links resolve to body figures.
        ['F.2', 'F.3', 'F.4', 'F.5'].every(id => !document.getElementById('wrap-' + id) && !document.getElementById('fig-' + id)) &&
        (() => { const t = document.getElementById('table-F.2'); if (!t) return false;
                 const links = [...t.querySelectorAll('a')].map(a => a.getAttribute('href'));
                 return links.length >= 8 && links.every(h => /^#wrap-(H|4\.2|4\.3)$/.test(h) && !!document.getElementById(h.slice(1))); })();
      s5.stamp = (document.getElementById('build-stamp') || {}).textContent || '';
      const h32 = document.getElementById('two-ways-of-eliciting-each-facet');
      s5.sec32 = !!h32 && before(sec4, h32) && before(h32, document.getElementById('wrap-H')) && !document.getElementById('where-the-facets-sit') && h32.textContent === 'How each facet was extracted' && !!document.getElementById('method-extraction');
      // Iteration 33: restructure. Section order, new figures and their reader-facing numbers.
      const h2 = [...document.querySelectorAll('h2')].map(h => h.textContent);
      const lab = id => (document.getElementById('label-' + id) || {}).textContent || '';
      const sapa1 = document.getElementById('fig-sapa1'), qc = document.getElementById('fig-qcloud');
      s5.newh2 = h2.filter(t => /^[1-8] |^Appendix H/.test(t));
      s5.newok = JSON.stringify(s5.newh2) === JSON.stringify(['1 The persona landscape', '2 The three models arrange traits in largely the same way',
          '3 Do people arrange the traits the same way?', '4 Measuring the Big Five facets directly inside Qwen', '5 Discussion', '6 Limitations',
          '7 Related work', '8 Open questions and next steps', 'Appendix H: Case study: Friendliness and Anger']) &&
        !document.getElementById('wrap-sapa1') && !document.getElementById('wrap-sapa2') && !document.getElementById('wrap-conv') && !document.getElementById('wrap-qcloud') && lab('4.2').startsWith('Figure 4.2.') &&
        lab('H').startsWith('Figure 4.1.') && lab('3.2').startsWith('Figure E.5.') && lab('4.3').startsWith('Figure E.6.') && before(document.getElementById('wrap-H'), document.getElementById('wrap-4.2')) && lab('1.3').startsWith('Figure 3.1.') && lab('1.2').startsWith('Figure 1.3.') && lab('tmap').startsWith('Figure 1.2.') && before(document.getElementById('wrap-1.1'), document.getElementById('wrap-tmap')) && before(document.getElementById('wrap-tmap'), document.getElementById('ple')) && !!window.TM && [...document.querySelectorAll('#tm-ctl select')].map(e => e.id).join('|') === 'tm-m|tm-y' && document.getElementById('fig-tmap').data[0].x.length === 240 && /at least half of 180 of the 240/.test(document.getElementById('tm-cap').textContent) && !!document.getElementById('table-axes').closest('details') && lab('elbow').startsWith('Figure G.3a.') && (document.getElementById('fig-elbow') || {layout: {updatemenus: [{buttons: []}]}}).layout.updatemenus[0].buttons.map(b => b.label).join('|') === 'Each component|Cumulative' && before(document.getElementById('wrap-2.3'), document.getElementById('wrap-elbow')) && before(document.getElementById('wrap-elbow'), document.getElementById('wrap-G.3b')) && !document.getElementById('wrap-bfpc') && before(document.getElementById('wrap-1.1'), document.getElementById('ple')) && before(document.getElementById('ple'), sec3) && before(sec3, document.getElementById('wrap-1.3')) && lab('5a').startsWith('Figure H.1.') &&
        !qc &&
        before(document.getElementById('wrap-1.3'), sec4) && before([...document.querySelectorAll('h2')].find(h => /^5 /.test(h.textContent)), document.getElementById('wrap-6.1')) && before(document.getElementById('wrap-6.1'), [...document.querySelectorAll('h2')].find(h => /^6 /.test(h.textContent)));
      s5.formatWords = MAIN.map(id => [id, (document.getElementById('wrap-' + id) || {}).querySelector ?
          [...document.getElementById('wrap-' + id).querySelectorAll('svg text, .fig-id')].map(e => e.textContent).join(' ') : 'MISSING'])
        .filter(([, t]) => /scenario|survey/i.test(t) || t === 'MISSING').map(([id]) => id);
      s5.formatHeaders = [...document.querySelectorAll('th')].filter(inMain).map(e => e.textContent).filter(t => /scenario|survey/i.test(t));
      s5.mainHeaders = [...document.querySelectorAll('th')].filter(inMain).length;
      s5.labelPx = [...document.querySelectorAll('.fig-id')].map(e => parseFloat(getComputedStyle(e).fontSize));
      s5.labelBold = [...document.querySelectorAll('.fig-id b')].map(e => getComputedStyle(e).fontWeight);
      s5.bodyPx = parseFloat(getComputedStyle(document.querySelector('.phg-caption')).fontSize);
      s5.plotTitles = [...document.querySelectorAll('.js-plotly-plot .gtitle')].map(e => e.textContent).filter(Boolean);
      s5.detailRows = det ? det.querySelectorAll('tr').length : 0;
      const ordBtn = gd.layout.updatemenus[0].buttons.findIndex(b => b.label === 'Domains: Qwen');
      s5.labelAfterOrd = null;
      await Plotly.update(gd, ...gd.layout.updatemenus[0].buttons[ordBtn].args);
      const ordT = gd._fullData.filter(t => t.visible === true)[0];
      s5.avgNN = Math.round(ordT.z[0][0] * 1000) / 1000; s5.avgAN = Math.round(ordT.z[3][0] * 1000) / 1000;
      await Plotly.update(gd, ...gd.layout.updatemenus[0].buttons[0].args);
      const pred = document.getElementById('fig-4.3');
      const predBands = () => (pred.layout.annotations || []).filter(a => (a.name || '').startsWith('domband|pred')).length;
      s5.predBands = predBands();
      s5.predBandShapes = pred._fullLayout.shapes.filter(sh => sh.fillcolor === '#e9edf3' || sh.fillcolor === '#dbe2ec').length;
      const fit = document.getElementById('fig-E.2');
      s5.fitTraces = fit ? fit._fullData.length : 0; s5.fitPoints = fit ? fit._fullData.map(t => t.x.length) : [];
      s5.fitBands = fit ? (fit.layout.annotations || []).filter(a => (a.name || '').startsWith('domband|fit')).length : 0;
      return { s5, matrix: out_m, detailInitial: initial, detailAfterClick: after, detailNote: det && det.innerText.includes('not effects of changing one trait'),
               phoneOnlyDisplay: phone, techFigWidth: Math.round(w44),
               placeholders: ['PROSE TBD', 'TODO'].filter(w => txt.includes(w)), detailsOpenByDefault: [...document.querySelectorAll('details')].filter(d => d.open).length };
    });
    const ple = await page.evaluate(async () => {
      const wait = ms => new Promise(r => setTimeout(r, ms));
      const root = document.getElementById('ple-root'), S = window.PLE && window.PLE.state;
      if (!root || !S) return { ok: false, why: 'explorer missing' };
      const out = { defaultA: root.dataset.a, defaultB: root.dataset.b, model0: root.dataset.model, dim0: root.dataset.dim,
                    bars0: root.dataset.top.split('|').length };
      const map = document.getElementById('ple-map'), bars = document.getElementById('ple-bars');
      out.mapRendered = !!(map._fullLayout && map.querySelector('svg.main-svg'));
      out.barsRendered = !!(bars._fullLayout && bars.querySelector('svg.main-svg'));
      // Tap a character on the map (Plotly event path): tap target starts at A.
      map.emit('plotly_click', { points: [{ text: 'judge' }] }); await wait(100);
      out.afterTapA = root.dataset.a;
      map.emit('plotly_click', { points: [{ text: 'librarian' }] }); await wait(100);
      out.afterTapB = root.dataset.b;
      // Switch model: selections persist, notice appears.
      const sel = document.getElementById('ple-model'); sel.value = 'llama'; sel.dispatchEvent(new Event('change')); await wait(150);
      out.modelAfter = root.dataset.model; out.keptA = root.dataset.a; out.keptB = root.dataset.b;
      const n = document.getElementById('ple-notice'); out.notice = n.style.display === 'block' ? n.innerText : '';
      sel.value = 'gemma'; sel.dispatchEvent(new Event('change')); await wait(150); out.noticeLG = n.innerText;
      sel.value = 'qwen'; sel.dispatchEvent(new Event('change')); await wait(150);
      // 3D toggle.
      document.querySelector('#ple [data-dim="3"]').click(); await wait(800);
      out.dim3 = root.dataset.dim; out.gl = map.querySelectorAll('canvas').length;
      document.querySelector('#ple [data-dim="2"]').click(); await wait(200);
      // Modes, scale, list, search.
      // Modes A, B, Difference; standardized scores only.
      out.scaleButtons = document.querySelectorAll('#ple [data-scale]').length;
      out.modeButtons = [...document.querySelectorAll('#ple [data-mode]')].map(b => b.textContent);
      document.querySelector('#ple [data-mode="a"]').click(); await wait(100);
      out.modeA = { n: root.dataset.top.split('|').length, note: document.getElementById('ple-barnote').innerText, title: bars.layout.xaxis.title.text.replace(/<br>/g, ' '),
                    sorted: bars.data[0].x.every((x, i, a) => i === 0 || a[i - 1] >= x), divider: (bars.layout.shapes || []).length };
      document.querySelector('#ple [data-mode="b"]').click(); await wait(100);
      out.modeB = { n: root.dataset.top.split('|').length, title: bars.layout.xaxis.title.text.replace(/<br>/g, ' ') };
      document.querySelector('#ple [data-mode="diff"]').click(); await wait(100);
      out.zTitle = bars.layout.xaxis.title.text.replace(/<br>/g, ' ');
      // Native select menus with a filter box.
      out.selects = ['ple-a', 'ple-b'].map(id => { const e = document.getElementById(id); return e.tagName + ':' + e.options.length; });
      const ps = document.getElementById('ple-psearch'); ps.value = 'jud'; ps.dispatchEvent(new Event('input')); await wait(50);
      out.filtered = [...document.getElementById('ple-a').options].map(o => o.value);
      ps.value = ''; ps.dispatchEvent(new Event('input'));
      document.getElementById('ple-all').click(); await wait(200);
      const sc = document.getElementById('ple-scroll');
      out.allView = root.dataset.view; out.allBars = root.dataset.top.split('|').length;
      out.allHeight = Math.round(bars.getBoundingClientRect().height); out.scrollBox = Math.round(sc.clientHeight);
      out.scrollable = sc.scrollHeight > sc.clientHeight;
      document.querySelector('#ple [data-sort="name"]').click(); await wait(100);
      out.firstByName = root.dataset.top.split('|')[0];
      document.querySelector('#ple [data-sort="diff"]').click(); await wait(100);
      const q = document.getElementById('ple-q'); q.value = 'calm'; q.dispatchEvent(new Event('input')); await wait(100);
      out.searchBars = root.dataset.top.split('|').filter(Boolean).length;
      q.value = ''; q.dispatchEvent(new Event('input'));
      document.getElementById('ple-all').click(); await wait(100); out.backView = root.dataset.view;
      out.barNote = document.getElementById('ple-barnote').innerText;
      // Restore defaults for screenshots.
      window.PLE.setPersona('a', out.defaultA); window.PLE.setPersona('b', out.defaultB); S.tap = 'A';
      document.getElementById('ple-notice').style.display = 'none'; window.PLE.draw(); await wait(200);
      const L = document.querySelector('.ple-left').getBoundingClientRect(), R = document.querySelector('.ple-right').getBoundingClientRect();
      out.stacked = R.top >= L.bottom - 1; out.sideBySide = Math.abs(R.top - L.top) < 2 && R.left > L.left;
      return out;
    });
    // 3D persistence: after every change, all 275 background points must still be drawn.
    const grey3d = async () => {
      const buf = await page.locator('#ple-map').screenshot();
      return await page.evaluate(async (b64) => {
        const img = new Image(); img.src = 'data:image/png;base64,' + b64; await img.decode();
        const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
        const g = c.getContext('2d'); g.drawImage(img, 0, 0); const d = g.getImageData(0, 0, c.width, c.height).data;
        let n = 0; for (let i = 0; i < d.length; i += 4) { if (Math.abs(d[i]-195) < 18 && Math.abs(d[i+1]-201) < 18 && Math.abs(d[i+2]-210) < 18) n++; }
        return n; }, buf.toString('base64'));
    };
    const glState = () => page.evaluate(() => { const gd = document.getElementById('ple-map'), sc = gd._fullLayout.scene && gd._fullLayout.scene._scene;
      const bg = gd._fullData[0]; return { n: bg.x.length, opacity: bg.marker.opacity, glPoints: sc ? sc.glplot.objects[0].pointCount : null }; });
    const steps3d = [];
    await page.locator('#ple-map').scrollIntoViewIfNeeded();
    await page.evaluate(() => document.querySelector('#ple [data-dim="3"]').click()); await page.waitForTimeout(1200);
    const base = await grey3d(); steps3d.push({ step: '3D on', grey: base, ...(await glState()) });
    const act = {
      'tap A': () => page.evaluate(() => { window.PLE.state.tap = 'A'; document.getElementById('ple-map').emit('plotly_click', { points: [{ text: 'judge' }] }); }),
      'tap B': () => page.evaluate(() => document.getElementById('ple-map').emit('plotly_click', { points: [{ text: 'librarian' }] })),
      'search A': () => page.evaluate(() => { const i = document.getElementById('ple-a'); i.value = 'doctor'; i.dispatchEvent(new Event('change')); }),
      'search B': () => page.evaluate(() => { const i = document.getElementById('ple-b'); i.value = 'chef'; i.dispatchEvent(new Event('change')); }),
      'model llama': () => page.evaluate(() => { const s = document.getElementById('ple-model'); s.value = 'llama'; s.dispatchEvent(new Event('change')); }),
      'axis X=PC4': () => page.evaluate(() => { const s = document.getElementById('ple-x'); s.value = '4'; s.dispatchEvent(new Event('change')); }),
      'model qwen': () => page.evaluate(() => { const s = document.getElementById('ple-model'); s.value = 'qwen'; s.dispatchEvent(new Event('change')); }),
    };
    for (const [name, fn] of Object.entries(act)) { await fn(); await page.waitForTimeout(900); steps3d.push({ step: name, grey: await grey3d(), ...(await glState()) }); }
    // restore 2D defaults for screenshots
    await page.evaluate(() => { const S = window.PLE.state; S.ax = [1, 2, 3]; S.model = 'qwen'; S.dim = 2;
      window.PLE.setPersona('a', 'poet'); window.PLE.setPersona('b', 'auditor'); S.tap = 'A';
      document.getElementById('ple-notice').style.display = 'none'; window.PLE.draw(); });
    await page.waitForTimeout(300);
    ple.steps3d = steps3d;
    if (shots) {
      await page.screenshot({ path: `${shots}/${label}_top.png` });
      const ex = page.locator('#ple'); await ex.scrollIntoViewIfNeeded(); await ex.screenshot({ path: `${shots}/${label}_explorer.png` });
      for (const id of ['H', '1.1', 'tmap', 'elbow', '1.3', '6.1', '2.1', 'E.4', '2.2', '2.3', '3.2', 'G.1', 'G.3b', 'G.4', '4.2', '4.3', 'E.2', 'F.1', '5a', '5b', '5c', '5d.2', '5d.3', '5e.1', '5e.3']) {
        const el = page.locator(`[id="wrap-${id}"]`);
        await el.scrollIntoViewIfNeeded();
        await el.screenshot({ path: `${shots}/${label}_fig_${id}.png` });
      }
    }
    results[label] = { ...info, ...extra, ple, interactions: interact.n, interactionErrors: interact.bad, realClick: clicked, consoleErrors: errors, blockedRequests: blocked,
                       pred43, pred43ok };
    await ctx.close();
  }
  let ipad = null;
  // iOS-Safari-like profile: WebKit is not installed here, so this uses Chromium with Playwright's iPad device descriptor
  // (Safari user agent, touch, mobile viewport). It checks that choosing from the native <select> updates the chart.
  {
    const { devices } = require('playwright');
    const ctx = await browser.newContext({ ...devices['iPad (gen 7)'], offline: true });
    const page = await ctx.newPage(); const errs = [];
    page.on('pageerror', e => errs.push(String(e)));
    await page.goto('file://' + file, { waitUntil: 'load' }); await page.waitForTimeout(1500);
    const before = await page.evaluate(() => document.getElementById('ple-root').dataset.top);
    await page.locator('#ple-a').scrollIntoViewIfNeeded();
    await page.selectOption('#ple-a', 'judge'); await page.waitForTimeout(300);
    await page.selectOption('#ple-b', 'librarian'); await page.waitForTimeout(300);
    const after = await page.evaluate(() => { const r = document.getElementById('ple-root'); return { a: r.dataset.a, b: r.dataset.b, top: r.dataset.top }; });
    ipad = { ua: await page.evaluate(() => navigator.userAgent), touch: await page.evaluate(() => 'ontouchstart' in window),
                     a: after.a, b: after.b, chartChanged: after.top !== before, errors: errs };
    await ctx.close();
  }
  await browser.close();
  console.log(JSON.stringify({ ...results, ipad }, null, 1));
  const ok = Object.values(results).every(r => r.plotly === 'object' || r.plotly === 'function') &&
    Object.values(results).every(r => r.plots === r.rendered && r.plots > 0 && !r.consoleErrors.length && !r.blockedRequests.length &&
      !r.interactionErrors.length && r.scrollW <= r.innerW && r.codeOpen === 0 && r.realClick === true &&
      r.detailInitial === 'E1__N2' && r.pred43ok &&
      r.s5.labels.length === 27 && /^Iteration \d+ · [0-9a-f]{7} · /.test(r.s5.stamp) && r.s5.gok && r.s5.no32 && r.s5.sec32 && !r.s5.formatWords.length && !r.s5.formatHeaders.length && r.s5.mainHeaders > 20 && r.s5.labels.some(t => t.startsWith('Figure 4.1. Trait-pair correlations in people and in Qwen')) && r.s5.labels[0].startsWith('Figure 1.1.') &&
      r.s5.labels.every(t => /^Figure [0-9A-H][0-9a-z.]*\. \S/.test(t)) && r.s5.labelPx.every(px => px >= 16 && px <= 17) &&
      r.s5.labelPx[0] > r.s5.bodyPx && r.s5.labelBold.every(w => +w >= 700) && r.s5.plotTitles.length === 0 &&
      r.matrix.label0 === 'Figure 4.2. Trait correlations (r)' && r.matrix.labelDomain === 'Figure 4.2. Trait correlations (r)' && r.s5.outlines === 0 && r.s5.outlineLabels === 0 && r.s5.contents && r.s5.tocEntries === 18 &&
      !r.s5.brokenLinks.length && r.s5.sourceTags === 5 && r.s5.matrixLabels.length === 6 &&
      !r.s5.matrixLabels.some(l => /ordinary/.test(l)) && r.s5.headlineMenus === 0 && r.s5.headlineTraces === 6 && r.s5.m21ok && r.s5.h21ok && r.s5.c23ok && r.s5.f12ok && r.s5.f13ok && r.s5.f61ok && r.s5.newok && r.s5.f31ok &&
      r.s5.headlineNote.includes('agreement r = .44 · Qwen links 2.0x as strong as people') &&
      !/scenario|survey/.test(r.s5.headlineNote) && r.s5.detailRows === 3 && r.s5.avgNN === 0.89 && r.s5.avgAN === -0.537 && r.s5.fitTraces === 3 &&
      r.s5.fitPoints.every(n => n === 26) && r.s5.fitBands === 5 &&
      r.s5.predBands === 5 && r.s5.predBandShapes === 5 && r.matrix.upperFilled && r.matrix.lowerFilled && r.matrix.diagBlank && r.matrix.guided === 0 && r.matrix.revBoxes === 26 && r.matrix.revBoxesDomain === 0 &&
      r.matrix.domainEdge === 10 && r.matrix.bandShapes === 10 && r.matrix.domainX2 && r.matrix.domainCells === 25 && r.detailAfterClick === 'E2__E1' && r.detailNote && r.techFigWidth > 200 &&
      !r.placeholders.length && r.detailsOpenByDefault === 0) &&
    results.phone.phoneOnlyDisplay.every(d => d === 'block') && results.desktop.phoneOnlyDisplay.every(d => d === 'none') &&
    Object.values(results).every(r => r.ple.steps3d.every(st => st.n === 275 && st.opacity === 1 && st.glPoints === 275 &&
      st.grey >= Math.max(800, 0.5 * r.ple.steps3d[0].grey))) &&
    Object.values(results).every(r => { const p = r.ple; return p.mapRendered && p.barsRendered && p.defaultA === 'poet' &&
      p.defaultB === 'auditor' && p.model0 === 'qwen' && p.dim0 === '2' && p.bars0 === 16 && p.afterTapA === 'judge' &&
      p.afterTapB === 'librarian' && p.modelAfter === 'llama' && p.keptA === 'judge' && p.keptB === 'librarian' &&
      p.notice.includes('Qwen PC1 and Llama PC1 are different axes') && p.notice.includes('r = +0.68') &&
      p.noticeLG.includes('No saved') && p.dim3 === '3' && p.gl > 0 && p.scaleButtons === 0 &&
      p.modeButtons.join(',') === 'A,B,Difference' && p.modeA.n === 16 && p.modeA.sorted && p.modeA.divider === 1 &&
      p.modeA.note.includes('8 highest and 8 lowest') && p.modeA.title.includes('standard deviations from the average character') &&
      p.modeB.n === 16 && p.modeB.title.startsWith('Trait score of B:') && p.zTitle.startsWith('Trait score difference, A − B') &&
      p.selects.every(x => x.startsWith('SELECT:') && x.endsWith(':275')) && p.filtered.includes('judge') && p.filtered.length < 10 && p.allView === 'all' && p.allBars === 240 && p.allHeight >= 22 * 240 && p.scrollBox <= 602 && p.scrollable &&
      p.firstByName === 'absolutist' && p.searchBars >= 1 && p.searchBars < 240 && p.backView === 'top' && p.barNote.includes('most higher for A'); }) &&
    results.desktop.ple.sideBySide && results.phone.ple.stacked;
  const ipadOk = ipad && ipad.a === 'judge' && ipad.b === 'librarian' && ipad.chartChanged && !ipad.errors.length;
  process.exit(ok && ipadOk ? 0 : 1);
})();
