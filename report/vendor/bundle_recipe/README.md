# plotly-phg.min.js

Custom offline plotly.js bundle for the PHG report: core plus bar, box, heatmap, histogram and scatter3d traces
(scatter is part of core). Built from npm `plotly.js@3.7.0` (MIT; see ../PLOTLY_LICENSE) with `esbuild@0.25.0`:

```sh
npm install plotly.js@3.7.0 esbuild@0.25.0
npx esbuild entry.js --bundle --minify --format=iife --target=es2018 --outfile=plotly-phg.min.js --define:global=window
```

SHA-256: bb26ccd3771910c3123efdb9ff000498186d02f9a0de4e8193d95e87d9e9c0d8  (1742780 bytes)

Replaces the cartesian-only 3.7.0 build used in iteration 2, which lacks scatter3d.
