"""Persona Landscape Explorer: offline HTML + inline JS (no kernel needed).

Left: persona geometry (Plotly 2D/3D). Right: trait profiles of two selected
personas (Plotly bars + sortable, searchable list). A small inline module keeps
selections in sync across models and re-sorts the bars.
"""
from __future__ import annotations

import html
import json

from . import landscape as LS

CSS = """
<style>
.ple{border:1px solid #dde1e7;border-radius:8px;padding:10px;margin:8px 0 6px}
.ple-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px}
@media (max-width:699px){.ple-grid{grid-template-columns:minmax(0,1fr)}}
.ple-ctl{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;font-size:13px;margin:4px 0}
.ple-ctl label{color:#3b475a}
.ple-ctl select,.ple-ctl input{font-size:13px;padding:2px 4px;max-width:100%}
.ple-ctl input[type=search]{width:11em}
.ple-ctl select#ple-a,.ple-ctl select#ple-b{max-width:11em}
.ple-seg button{font-size:12px;padding:3px 8px;border:1px solid #9aa4b2;background:#fff;cursor:pointer}
.ple-seg button:first-child{border-radius:4px 0 0 4px}.ple-seg button:last-child{border-radius:0 4px 4px 0}
.ple-seg button.on{background:#3b475a;color:#fff;border-color:#3b475a}
.ple-chip{display:inline-block;border-radius:10px;padding:0 7px;color:#fff;font-weight:600;font-size:12px}
.ple-chip.a{background:#1b7f79}.ple-chip.b{background:#d9822b}
.ple-tapto button.on{outline:2px solid #3b475a}
.ple-notice{font-size:13px;background:#fff8e6;border:1px solid #e8d49a;border-radius:6px;padding:4px 8px;margin:4px 0;display:none}
.ple-notice .r{color:#5b6b82}
.ple-axisnote{font-size:12px;color:#5b6b82;margin:2px 0}
.ple-scroll{margin-top:4px}
.ple-scroll.all{max-height:600px;overflow-y:auto;border:1px solid #dde1e7;border-radius:6px;-webkit-overflow-scrolling:touch}
.ple-barnote{font-size:12px;color:#5b6b82;margin:2px 0;min-height:1em}
.ple-credit{font-size:12px;color:#5b6b82;margin:4px 0 0}
</style>
"""

JS = r"""
(function(){
const D = __DATA__;
const S = D.scale, P = D.personas, T = D.traits, M = ['qwen','llama','gemma'];
const CA = '#1b7f79', CB = '#d9822b', GREY = '#9aa4b2', GREY3D = '#c3c9d2';
const st = {model:'qwen', dim:2, ax:[1,2,3], a:P.indexOf(D.default[0]), b:P.indexOf(D.default[1]),
            tap:'A', mode:'diff', q:'', pq:'', view:'top', sort:'diff'};
const AZ = P.slice().sort((x,y)=>x.localeCompare(y));   // alphabetical list for the dropdowns
const $ = id => document.getElementById('ple-'+id);
const val = (m, kind, i, j) => D.models[m][kind][i][j] / S;
const lab = m => D.labels[m];
function axisTitle(k){
  const tag = (D.tags[st.model]||{})[k];
  const base = 'Position on component '+k+' (PC'+k+', '+lab(st.model)+')';
  return tag ? base+'<br><span style="font-size:10px">'+tag+'</span>' : base;
}
function fmt(x){ return (x>=0?'+':'−')+Math.abs(x).toFixed(2); }
function pcCol(k){ return D.models[st.model].pcs.map(r => r[k-1]/S); }
function mapTraces(){
  const xs = pcCol(st.ax[0]), ys = pcCol(st.ax[1]), zs = pcCol(st.ax[2]);
  const t3 = st.dim===3, type = t3 ? 'scatter3d' : 'scatter';
  const base = {type, mode:'markers', x:xs, y:ys, text:P, name:'Characters', hovertemplate:'%{text}<extra></extra>',
                marker: t3 ? {size:3, color:GREY3D, opacity:1} : {size:6, color:GREY, opacity:0.75}};  // 3D: opaque (WebGL can drop translucent points on redraw)
  if (t3) base.z = zs;
  const mx = xs.reduce((u,v)=>u+v,0)/xs.length;
  const sel = (i, c, n) => { const t = {type, mode:'markers+text', x:[xs[i]], y:[ys[i]], text:[n+': '+P[i]],
      textposition: t3 ? 'top center' : (xs[i] > mx ? 'top left' : 'top right'), textfont:{color:c, size:12}, name:n+': '+P[i], hovertemplate:'%{text}<extra></extra>',
      marker:{size:t3?6:12, color:c, line:{color:'#fff', width:1.5}}}; if (t3) t.z=[zs[i]]; return t; };
  return [base, sel(st.a, CA, 'A'), sel(st.b, CB, 'B')];
}
function mapLayout(){
  const ttl = k => ({text:axisTitle(k), font:{size:11}});
  const L = {margin:{l:50,r:10,t:10,b:50}, height:440, showlegend:false, template:'plotly_white',
             font:{size:11}, hoverlabel:{font:{size:12}}, uirevision:st.model+st.dim+st.ax.join()};
  if (st.dim===3) L.scene = {xaxis:{title:ttl(st.ax[0])}, yaxis:{title:ttl(st.ax[1])}, zaxis:{title:ttl(st.ax[2])}};
  else { L.xaxis = {title:ttl(st.ax[0]), zeroline:true, zerolinecolor:'#ccc'}; L.yaxis = {title:ttl(st.ax[1]), zeroline:true, zerolinecolor:'#ccc'}; }
  return L;
}
function rows(){
  const k = 'z', m = st.model, out = [];   // standardized scores only
  for (let j=0;j<T.length;j++){
    const a = val(m,k,st.a,j), b = val(m,k,st.b,j);
    out.push({t:T[j], a, b, d:a-b});
  }
  const q = st.q.trim().toLowerCase();
  return q ? out.filter(r => r.t.toLowerCase().includes(q)) : out;
}
const AXIS = '(standard deviations from the average character)';   // second line of the bar-axis title (fits phones)
const v = o => st.mode==='a' ? o.a : st.mode==='b' ? o.b : o.d;   // value shown in the current mode
const PER_SIDE = 8, PX_PER_BAR = 22;
function selectBars(){
  // Expanded: every (filtered) trait. Condensed: Difference = 8 most positive and 8 most negative A - B;
  // A or B = that character's 8 highest and 8 lowest traits.
  const r = rows(); let note = '';
  const who = st.mode==='a' ? 'A ('+P[st.a]+')' : st.mode==='b' ? 'B ('+P[st.b]+')' : 'A − B';
  if (st.view==='all'){
    if (st.sort==='name') r.sort((x,y)=>x.t.localeCompare(y.t)); else r.sort((x,y)=>v(y)-v(x));
    note = 'Showing '+r.length+' of '+T.length+' traits for '+who+', sorted by '+(st.sort==='name'?'name':'value')+'. Scroll the chart.';
    return {r, nPos:null, note};
  }
  if (st.mode!=='diff'){
    const s2 = r.slice().sort((x,y)=>v(y)-v(x));
    if (s2.length <= 2*PER_SIDE) return {r:s2, nPos:null, note:'All '+s2.length+' matching traits for '+who+'.'};
    return {r:s2.slice(0,PER_SIDE).concat(s2.slice(-PER_SIDE)), nPos:PER_SIDE,
            note:who+': the 8 highest and 8 lowest of '+r.length+' traits.'};
  }
  const pos = r.filter(o=>o.d>0).sort((x,y)=>y.d-x.d), neg = r.filter(o=>o.d<0).sort((x,y)=>y.d-x.d);
  const P8 = pos.slice(0,PER_SIDE), N8 = neg.slice(Math.max(0, neg.length-PER_SIDE));
  const short = [];
  if (pos.length < PER_SIDE) short.push('only '+pos.length+' trait'+(pos.length===1?'':'s')+' score higher for A (all shown)');
  if (neg.length < PER_SIDE) short.push('only '+neg.length+' trait'+(neg.length===1?'':'s')+' score higher for B (all shown)');
  note = 'The '+P8.length+' traits most higher for A and the '+N8.length+' most higher for B'+(short.length?'; '+short.join('; '):'')+'.';
  return {r:P8.concat(N8), nPos:P8.length, note};
}
function barFig(){
  const sel = selectBars(), r = sel.r, y = r.map(o=>o.t);
  const tall = st.view==='all', n = Math.max(r.length,1);
  const H = tall ? Math.max(300, PX_PER_BAR*n + 90) : 470;
  const title = (st.mode==='diff' ? 'Trait score difference, A − B' : st.mode==='a' ? 'Trait score of A: '+P[st.a]
                 : 'Trait score of B: '+P[st.b]) + '<br>' + AXIS;
  const L = {margin:{l:120,r:10,t:30,b:78}, height:H, template:'plotly_white', font:{size:11}, bargap:0.25, showlegend:false,
             yaxis:{autorange:'reversed', tickfont:{size:11}, automargin:true},
             xaxis:{title:{text:title, font:{size:11}}, zeroline:true, zerolinecolor:'#555', zerolinewidth:1,
                    side: tall ? 'top' : 'bottom'}, shapes:[]};
  if (tall) L.margin = {l:120,r:10,t:90,b:20};
  if (sel.nPos!==null && sel.nPos>0 && sel.nPos<r.length)   // thin divider between the two groups
    L.shapes.push({type:'line', xref:'paper', x0:0, x1:1, yref:'y', y0:sel.nPos-0.5, y1:sel.nPos-0.5, line:{color:'#777', width:1, dash:'dot'}});
  const color = st.mode==='a' ? CA : st.mode==='b' ? CB : r.map(o=>o.d>=0?CA:CB);
  const data = [{type:'bar', orientation:'h', x:r.map(v), y, name:title, marker:{color}, customdata:r.map(o=>[o.a,o.b,o.d]),
      hovertemplate:'%{y}<br>A %{customdata[0]:+.2f} · B %{customdata[1]:+.2f} · A − B %{customdata[2]:+.2f}<extra></extra>'}];
  if (!r.length) L.annotations = [{text:'No trait matches the search', showarrow:false, xref:'paper', yref:'paper', x:0.5, y:0.5}];
  return {data, layout:L, note:sel.note};
}
function fillSelects(){
  // Native <select> menus (work on iPad Safari); the filter box narrows the options, keeping the current choice.
  const q = st.pq.trim().toLowerCase();
  ['a','b'].forEach(slot => {
    const cur = P[st[slot]], names = AZ.filter(n => !q || n.toLowerCase().includes(q) || n===cur);
    const el = $(slot), html = names.map(n=>'<option value="'+n+'"'+(n===cur?' selected':'')+'>'+n+'</option>').join('');
    if (el.dataset.html !== html){ el.innerHTML = html; el.dataset.html = html; }
    el.value = cur;
  });
}
function syncControls(){
  $('model').value = st.model; fillSelects();
  ['x','y','z'].forEach((c,i)=>{ $(c).value = st.ax[i]; });
  $('zwrap').style.display = st.dim===3 ? '' : 'none';
  document.querySelectorAll('#ple [data-dim]').forEach(b=>b.classList.toggle('on', +b.dataset.dim===st.dim));
  document.querySelectorAll('#ple [data-mode]').forEach(b=>b.classList.toggle('on', b.dataset.mode===st.mode));
  document.querySelectorAll('#ple [data-tap]').forEach(b=>b.classList.toggle('on', b.dataset.tap===st.tap));
  document.querySelectorAll('#ple [data-sort]').forEach(b=>b.classList.toggle('on', b.dataset.sort===st.sort));
  $('sortwrap').style.display = st.view==='all' ? '' : 'none';
  $('all').textContent = st.view==='all' ? 'Show top 8 + 8' : 'Show all 240';
  $('scroll').classList.toggle('all', st.view==='all');
  $('chipa').textContent = 'A: '+P[st.a]; $('chipb').textContent = 'B: '+P[st.b];
  const tagged = Object.keys(D.tags[st.model]||{}).length;
  $('axisnote').textContent = 'Axis tags: the three traits most correlated with each end (low ↔ high; see Figure 1.1)' +
    (st.model==='qwen' ? '. PC4–PC6 tags use the saved trait table.' : '. PC4–PC6 are untagged for ' + lab(st.model) + '.');
}
function draw(){
  syncControls();
  Plotly.react($('map'), mapTraces(), mapLayout(), {responsive:true, displaylogo:false});
  const f = barFig(); Plotly.react($('bars'), f.data, f.layout, {responsive:true, displaylogo:false});
  $('barnote').textContent = f.note;
  const root = $('root'); root.dataset.model = st.model; root.dataset.a = P[st.a]; root.dataset.b = P[st.b];
  root.dataset.dim = st.dim; root.dataset.top = f.data[0].y.join('|'); root.dataset.view = st.view;
}
function notice(prev, next){
  const pair = [prev,next].sort().join('-'), keyQ = prev==='qwen' ? 'qwen-'+next : next==='qwen' ? 'qwen-'+prev : null;
  const r = keyQ ? D.xmodel[keyQ] : null;
  const el = $('notice');
  el.innerHTML = 'Each model has its own PCA. '+lab(prev)+' PC1 and '+lab(next)+' PC1 are different axes. ' +
    '<span class="r" title="Saved cross-model persona PC score correspondence (extended_persona_pca)">' +
    (r===null ? '(No saved '+lab(prev)+'–'+lab(next)+' PC correlation.)' : '(Saved PC1 correlation between them: r = '+fmt(r)+'.)') + '</span>';
  el.style.display = 'block';
}
function setPersona(slot, name){ const i = P.indexOf(name); if (i<0) return false; st[slot]=i; draw(); return true; }
function init(){
  const gd = $('map'); if (!window.Plotly || !gd) return setTimeout(init, 60);
  const opts = n => Array.from({length:D.n_pcs},(_,k)=>'<option value="'+(k+1)+'">PC'+(k+1)+'</option>').join('');
  ['x','y','z'].forEach(c=>$(c).innerHTML = opts());
  $('model').onchange = e => { const prev = st.model; st.model = e.target.value; notice(prev, st.model); draw(); };
  ['x','y','z'].forEach((c,i)=> $(c).onchange = e => { st.ax[i] = +e.target.value; draw(); });
  document.querySelectorAll('#ple [data-dim]').forEach(b=>b.onclick=()=>{ st.dim=+b.dataset.dim; draw(); });
  document.querySelectorAll('#ple [data-mode]').forEach(b=>b.onclick=()=>{ st.mode=b.dataset.mode; draw(); });
  document.querySelectorAll('#ple [data-tap]').forEach(b=>b.onclick=()=>{ st.tap=b.dataset.tap; syncControls(); });
  ['a','b'].forEach(s => $(s).onchange = e => { if (!setPersona(s, e.target.value)) e.target.value = P[st[s]]; });
  $('psearch').oninput = e => { st.pq = e.target.value; fillSelects(); };
  $('q').oninput = e => { st.q = e.target.value; draw(); };
  $('all').onclick = () => { st.view = st.view==='all' ? 'top' : 'all'; draw(); $('scroll').scrollTop = 0; };
  document.querySelectorAll('#ple [data-sort]').forEach(b=>b.onclick=()=>{ st.sort=b.dataset.sort; draw(); });
  draw();
  gd.on('plotly_click', e => { const p = e.points && e.points[0]; if (!p) return;
    const i = P.indexOf(String(p.text).replace(/^[AB]: /,'')); if (i<0) return;
    if (st.tap==='A'){ st.a=i; st.tap='B'; } else { st.b=i; st.tap='A'; } draw(); });
  window.PLE = {state:st, setPersona, draw, notice};
}
init();
})();
"""


def explorer_html() -> str:
    data = LS.payload()
    js = JS.replace("__DATA__", json.dumps(data, separators=(",", ":")))
    seg = lambda attr, items: "<span class='ple-seg'>" + "".join(
        f"<button type='button' data-{attr}='{v}'>{html.escape(t)}</button>" for v, t in items) + "</span>"
    models = "".join(f"<option value='{m}'>{LS.MODEL_LABEL[m]}</option>" for m in LS.MODELS)
    return CSS + f"""
<div class='ple' id='ple'><div id='ple-root'>
<div class='ple-notice' id='ple-notice' role='status'></div>
<div class='ple-grid'>
 <div class='ple-left'>
  <div class='ple-ctl'><label>Model <select id='ple-model'>{models}</select></label>{seg('dim', [(2, '2D'), (3, '3D')])}
   <label>X <select id='ple-x'></select></label><label>Y <select id='ple-y'></select></label>
   <label id='ple-zwrap'>Z <select id='ple-z'></select></label></div>
  <div class='ple-ctl'><input type='search' id='ple-psearch' placeholder='Filter characters' aria-label='Filter the character lists'></div>
  <div class='ple-ctl'><label><span class='ple-chip a'>A</span> <select id='ple-a' aria-label='Character A'></select></label>
   <label><span class='ple-chip b'>B</span> <select id='ple-b' aria-label='Character B'></select></label>
   <span class='ple-tapto'>Tap sets {seg('tap', [('A', 'A'), ('B', 'B')])}</span></div>
  <div id='ple-map'></div>
  <div class='ple-axisnote' id='ple-axisnote'></div>
 </div>
 <div class='ple-right'>
  <div class='ple-ctl'><span class='ple-chip a' id='ple-chipa'></span><span class='ple-chip b' id='ple-chipb'></span></div>
  <div class='ple-ctl'>{seg('mode', [('a', 'A'), ('b', 'B'), ('diff', 'Difference')])}</div>
  <div class='ple-ctl'><input type='search' id='ple-q' placeholder='Search traits' aria-label='Search traits'>
   <button type='button' id='ple-all'>Show all 240</button>
   <span id='ple-sortwrap'>Sort {seg('sort', [('diff', 'By A − B'), ('name', 'By name')])}</span></div>
  <div class='ple-barnote' id='ple-barnote'></div>
  <div class='ple-scroll' id='ple-scroll'><div id='ple-bars'></div></div>
 </div>
</div></div></div>
<p class='ple-credit'>Personas, trait list and released vectors: Lu et al. (2026), The Assistant Axis. PC coordinates,
standardization and this display: PHG.</p>
<script>{js}</script>"""
