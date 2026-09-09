/* Static SVG rasterization only: no browser, external resources, or GPU model. */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const sharp = require('sharp');
const here = __dirname;

async function main() {
  const results = [];
  for (const suffix of ['pc1', 'pc2', 'pc3', 'overview']) {
    const base = path.join(here, `persona_emotion_ridges_${suffix}`);
    const source = fs.readFileSync(base + '.svg');
    await sharp(source, {limitInputPixels: 30000000}).png().toFile(base + '.png');
    const image = sharp(base + '.png');
    const metadata = await image.metadata();
    const stats = await image.stats();
    assert.ok(stats.channels.slice(0, 3).every(c => c.stdev > 15), 'Figure must not be blank');
    assert.equal(metadata.width, suffix === 'overview' ? 2100 : 1000);
    assert.equal(metadata.height, suffix === 'overview' ? 1120 : 12340);
    results.push({file: path.basename(base + '.png'), width: metadata.width, height: metadata.height});
  }
  const html = fs.readFileSync(path.join(here, 'persona_emotion_ridges.html'), 'utf8');
  const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)][0][1];
  const data = JSON.parse(fs.readFileSync(path.join(here, 'persona_emotion_ridge_data.json')));
  const picker = {value: '', addEventListener(_, fn) {this.change = fn;}};
  const status = {textContent: ''};
  const rows = data.orders.flatMap(order => order.map((i, rank) => ({
    dataset: {persona: data.personas[i], rank: String(rank + 1)},
    offsetTop: rank * 44, parentElement: {offsetTop: 0, scrollTop: 0},
    classList: {toggle(_, active) {this.active = active;}}
  })));
  const buttons = rows.map(row => ({dataset: {name: row.dataset.persona}, addEventListener(_, fn) {this.click = fn;}}));
  const document = {
    getElementById(id) {return id === 'find-persona' ? picker : status;},
    querySelectorAll(selector) {return selector === '.ridge-row' ? rows : buttons;}
  };
  new vm.Script(script).runInNewContext({document});
  picker.value = 'playwright'; picker.change();
  assert.equal(rows.filter(r => r.classList.active).length, 3);
  assert.ok(status.textContent.startsWith('playwright | PC1 rank'));
  buttons[0].click();
  assert.equal(picker.value, rows[0].dataset.persona);
  assert.equal(rows.filter(r => r.classList.active).length, 3);
  picker.value = ''; picker.change();
  assert.equal(rows.filter(r => r.classList.active).length, 0);
  const result = {status: 'pass', static_renders: results,
    interaction_unit_checks: ['Dropdown selects exactly one row in each plot', 'Persona button links all plots', 'Clear selection'],
    browser_test: false, note: 'SVG rasterization and Node DOM-double unit tests, not a browser screenshot.'};
  fs.writeFileSync(path.join(here, 'ridge_render_checks.json'), JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result, null, 2));
}
main().catch(e => {console.error(e); process.exitCode = 1;});
