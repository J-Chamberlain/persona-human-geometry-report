// PHG report bundle: plotly.js 3.7.0 cartesian traces + scatter3d.
var Plotly = require('plotly.js/lib/core');
Plotly.register([
  require('plotly.js/lib/bar'), require('plotly.js/lib/box'), require('plotly.js/lib/heatmap'),
  require('plotly.js/lib/histogram'), require('plotly.js/lib/scatter3d'),
]);
window.Plotly = Plotly;
