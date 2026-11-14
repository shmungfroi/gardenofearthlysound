// Export the map's input (data.json) from the Garden's data file: node src/export_data.js
const path = require('path'), fs = require('fs'); global.window = {};
require(path.join(__dirname, '..', 'gx_data.js')); const G = window.GX;
fs.writeFileSync(path.join(__dirname, 'data.json'), JSON.stringify({nodes: G.DATA.nodes.map(n => ({id: n.id, t: n.t, y: n.y, period: n.period, lane: n.lane})), links: G.DATA.links, periods: G.DATA.periods,
  genres: G.MIN.genres.map(g => ({id: g.id, t: g.t, great: g.great, l: g.lanterns}))}));
console.log('data.json written');
