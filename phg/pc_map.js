(function () {
  // Figure 1.1 (iteration 25; 1.2 until iteration 27): model, vertical-axis and trait menus. The trait menu is rebuilt for each model and axis:
  // PC1 high, PC1 low, axis high, axis low, PC1-axis diagonal. __DATA__ is replaced by the Python payload.
  var D = __DATA__;
  var g = document.getElementById('fig-1.1');
  var st = {m: 'qwen', ax: 'PC2', tr: null};
  function sg(v) { return (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(2).replace(/^0\./, '.'); }
  function opts() { return D.models[st.m].opts[st.ax]; }
  function fill() {
    var s = document.getElementById('pm-tr');
    s.innerHTML = opts().map(function (o) { return '<option value="' + o[0] + '">' + o[1] + '</option>'; }).join('');
    if (!opts().some(function (o) { return o[0] === st.tr; })) st.tr = opts()[0][0];
    s.value = st.tr;
  }
  function draw() {
    var M = D.models[st.m], x = M.pc.PC1, y = M.pc[st.ax], z = M.z[st.tr], r = M.r[st.tr], L = D.label[st.m];
    var nx = D.idx.map(function (i) { return x[i]; }), ny = D.idx.map(function (i) { return y[i]; });
    Plotly.restyle(g, {x: [x, nx], y: [y, ny]}, [0, 1]);
    Plotly.restyle(g, {'marker.color': [z],
      hovertemplate: ['%{customdata}<br>' + st.tr.replace(/_/g, ' ') + ' %{marker.color:+.2f} SD<extra></extra>']}, [0]);
    var a = (g.layout.annotations || []).slice();
    a[0] = Object.assign({}, a[0], {text: 'r with PC1 ' + sg(r[0]) + ' · PC2 ' + sg(r[1]) + ' · PC3 ' + sg(r[2])});
    Plotly.relayout(g, {'xaxis.title.text': 'Position on ' + L + "'s PC1",
                        'yaxis.title.text': 'Position on ' + L + "'s " + st.ax, annotations: a});
    var w = document.getElementById('wrap-1.1');
    w.dataset.model = st.m; w.dataset.axis = st.ax; w.dataset.trait = st.tr;
  }
  function init() {
    if (!window.Plotly || !g || !g.data || !g._fullLayout) { return setTimeout(init, 80); }
    var c = document.createElement('div');
    c.className = 'pm-ctl'; c.id = 'pm-ctl';
    c.innerHTML = '<label>Model <select id="pm-m">' + Object.keys(D.models).map(function (m) {
        return '<option value="' + m + '">' + D.label[m] + '</option>'; }).join('') + '</select></label>' +
      '<label>Up <select id="pm-ax"><option value="PC2">PC2</option><option value="PC3">PC3</option></select></label>' +
      '<label>Trait <select id="pm-tr"></select></label>';
    // Insert above Plotly's fixed-height wrapper, not inside it, so the plot keeps its full height (iteration 26).
    var host = g.parentNode; host.parentNode.insertBefore(c, host);
    fill();
    document.getElementById('pm-m').onchange = function (e) { st.m = e.target.value; fill(); draw(); };
    document.getElementById('pm-ax').onchange = function (e) { st.ax = e.target.value; fill(); draw(); };
    document.getElementById('pm-tr').onchange = function (e) { st.tr = e.target.value; draw(); };
    if (window.innerWidth < 600) {
      Plotly.restyle(g, {'marker.showscale': false}, [0]);
      Plotly.relayout(g, {'margin.r': 8});
    }
    draw();
    window.PM = {state: st, draw: draw, fill: fill, data: D};
  }
  init();
})();
