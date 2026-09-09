/* Run with Node and Playwright installed; serves no files and blocks networking. */
const {chromium, devices} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {createHash} = require('node:crypto');
const here = __dirname;
const url = pathToFileURL(path.join(here, 'persona_emotion_surface_viewer.html')).href;

async function main() {
  const browser = await chromium.launch({headless:true});
  const result = {status:'running', browser:await browser.version(), generated_utc:new Date().toISOString(),
    html_sha256:createHash('sha256').update(fs.readFileSync(path.join(here,'persona_emotion_surface_viewer.html'))).digest('hex'),
    checks:[], render_milliseconds:[], network_attempts:[], errors:[]};
  const context = await browser.newContext({viewport:{width:1440,height:1080}});
  await context.route(/^https?:/, route=>{result.network_attempts.push(route.request().url());return route.abort();});
  const page = await context.newPage();
  page.on('pageerror', e=>result.errors.push(e.message));
  const ready = async p=>{await p.waitForFunction(()=>window.__emotionViewer?.ready);};
  const checkData = async p=>assert.equal(await p.evaluate(()=>{
    const v=window.__emotionViewer,trace=document.querySelector('#plot').data[4],s=v.snapshot();
    return v.data.roles.every((r,i)=>trace.x[i]===r.pcs[v.state.x]&&trace.y[i]===r.pcs[v.state.y]&&trace.z[i]===s.heights[i]);
  }),true);
  const clickEmotion = async (p, index)=>{await p.locator('#emotion-stops button').nth(index).click();await ready(p);await checkData(p);};
  await page.goto(url);await ready(page);await checkData(page);
  result.checks.push('Offline file:// initial WebGL render; exact 275 node coordinates and scores');
  await page.locator('#persona-picker').selectOption('25');await ready(page);
  const camera = {eye:{x:1.3,y:-1.1,z:1.1},up:{x:0,y:0,z:1},center:{x:0,y:0,z:0}};
  await page.evaluate(c=>Plotly.relayout(document.querySelector('#plot'),{'scene.camera':c}),camera);
  const liveCamera=await page.evaluate(()=>document.querySelector('#plot')._fullLayout.scene._scene.getCamera());
  for(let i=0;i<6;i++) {
    await clickEmotion(page,i);
    assert.equal(await page.locator('#persona-picker').inputValue(),'25');
    const actualCamera=await page.evaluate(()=>document.querySelector('#plot')._fullLayout.scene._scene.getCamera());
    for(const part of ['eye','up','center']) for(const axis of ['x','y','z'])
      assert.ok(Math.abs(actualCamera[part][axis]-liveCamera[part][axis])<1e-8);
    assert.deepEqual(await page.evaluate(()=>document.querySelector('#plot').layout.scene.zaxis.range),
      await page.evaluate(()=>[-__emotionViewer.data.z_limit,__emotionViewer.data.z_limit]));
    result.render_milliseconds.push({emotion:i,ms:await page.evaluate(()=>__emotionViewer.lastRenderMilliseconds)});
  }
  result.checks.push('All six categorical stops preserve camera, fixed z range, selected persona and exact scores');
  await page.locator('#emotion-slider').focus();await page.keyboard.press('Home');await ready(page);
  await page.keyboard.press('ArrowRight');await ready(page);
  assert.equal(await page.locator('#emotion-slider').inputValue(),'1');
  // Native range pointer selection, not only the label buttons.
  const slider=await page.locator('#emotion-slider').boundingBox();
  await page.mouse.click(slider.x+slider.width-5,slider.y+slider.height/2);await ready(page);
  assert.equal(await page.locator('#emotion-slider').inputValue(),'5');
  result.checks.push('Native range keyboard and pointer interaction');
  await page.evaluate(()=>{
    const slider=document.querySelector('#emotion-slider');
    for(const i of [0,5,1,4,2]) {slider.value=i;slider.dispatchEvent(new Event('input',{bubbles:true}));}
  });
  await ready(page);await checkData(page);
  assert.equal(await page.locator('#emotion-slider').inputValue(),'2');
  result.checks.push('Rapid slider-input burst settles on the latest emotion with matching node values');
  for(const [x,y] of [[0,1],[0,2],[1,2],[1,0],[2,0],[2,1]]) {
    if(await page.locator('#x-axis').inputValue()!==String(x)) {await page.locator('#x-axis').selectOption(String(x));await ready(page);}
    if(await page.locator('#y-axis').inputValue()!==String(y)) {await page.locator('#y-axis').selectOption(String(y));await ready(page);}
    await checkData(page);
    assert.equal(await page.locator(`#x-axis option[value="${y}"]`).evaluate(option=>option.disabled),true);
    assert.equal(await page.locator(`#y-axis option[value="${x}"]`).evaluate(option=>option.disabled),true);
    const actual=await page.evaluate(()=>document.querySelector('#plot').data[1].z);
    assert.deepEqual(actual,await page.evaluate(()=>__emotionViewer.snapshot().grid));
  }
  result.checks.push('All six ordered PC pairs; same-axis choices disabled; reversed surface transposed');
  for(let level=0;level<3;level++) {await page.locator('#smoothing').selectOption(String(level));await ready(page);await checkData(page);}
  await page.locator('#show-surface').uncheck();await ready(page);
  assert.equal(await page.evaluate(()=>document.querySelector('#plot').data[1].visible),false);
  await page.locator('#show-surface').check();await ready(page);
  await page.locator('#show-connectors').uncheck();await ready(page);
  assert.equal(await page.evaluate(()=>document.querySelector('#plot').data[3].visible),false);
  await page.locator('#show-connectors').check();await ready(page);
  result.checks.push('Three smoothing levels and visibility toggles never move scored nodes');
  await page.locator('#x-axis').selectOption('0');await ready(page);
  await page.locator('#smoothing').selectOption('1');await ready(page);
  await page.locator('#clear-selection').click();await ready(page);
  await clickEmotion(page,0);await page.locator('#reset-view').click();
  // Find a real rendered node with pointer movement, then test the same point's click.
  const box=await page.locator('#plot').boundingBox();let hovered=null,hoverLocation=null;
  for(let dy=-90;dy<=100&&hoverLocation===null;dy+=14) for(let dx=-180;dx<=180&&hoverLocation===null;dx+=14) {
    const x=box.x+box.width/2+dx,y=box.y+box.height*0.54+dy;
    await page.mouse.move(x,y);await page.waitForTimeout(35);
    hovered=await page.evaluate(()=>__emotionViewer.state.hovered);
    if(hovered!==null) {hoverLocation={x,y};break;}
  }
  assert.notEqual(hovered,null,'A rendered persona must be hoverable');
  const hoverName=await page.evaluate(i=>__emotionViewer.data.roles[i].name,hovered);
  assert.equal(await page.locator('#selected-name').textContent(),hoverName.replaceAll('_',' '));
  await page.mouse.click(hoverLocation.x,hoverLocation.y);
  await page.waitForFunction(i=>__emotionViewer.state.selected===i,hovered,{timeout:5000});await ready(page);
  assert.equal(await page.evaluate(()=>__emotionViewer.state.selected),hovered);
  result.checks.push(`Real pointer hover and click identify/pin ${hoverName}`);
  await page.locator('#persona-picker').selectOption({label:'playwright'});await ready(page);
  await page.mouse.move(20,20);
  await page.screenshot({path:path.join(here,'persona_emotion_surface_desktop.png'),fullPage:true});
  await clickEmotion(page,3);
  const pinned=await page.evaluate(()=>__emotionViewer.state.selected);
  const before=await page.evaluate(()=>JSON.stringify(__emotionViewer.state.camera));
  await page.mouse.move(box.x+box.width*.6,box.y+box.height*.5);await page.mouse.down();
  await page.mouse.move(box.x+box.width*.6+90,box.y+box.height*.5-40,{steps:12});await page.mouse.up();
  await page.waitForTimeout(250);
  assert.notEqual(await page.evaluate(()=>JSON.stringify(__emotionViewer.state.camera)),before);
  assert.equal(await page.evaluate(()=>__emotionViewer.state.selected),pinned);
  const preZoom=await page.evaluate(()=>JSON.stringify(__emotionViewer.state.camera));
  await page.mouse.wheel(0,-240);
  await page.waitForFunction(c=>JSON.stringify(__emotionViewer.state.camera)!==c,preZoom,{timeout:3000});
  assert.notEqual(await page.evaluate(()=>JSON.stringify(__emotionViewer.state.camera)),preZoom);
  const zoomed=await page.evaluate(()=>document.querySelector('#plot')._fullLayout.scene._scene.getCamera());
  await clickEmotion(page,4);
  const afterSlider=await page.evaluate(()=>document.querySelector('#plot')._fullLayout.scene._scene.getCamera());
  for(const part of ['eye','up','center']) for(const axis of ['x','y','z'])
    assert.ok(Math.abs(afterSlider[part][axis]-zoomed[part][axis])<1e-8);
  result.checks.push('Real pointer drag rotates and scroll zooms the scene');
  result.checks.push('Live wheel-zoom camera survives the next emotion change');
  await clickEmotion(page,3);
  await page.locator('#reset-view').click();await page.mouse.move(20,20);
  await page.screenshot({path:path.join(here,'persona_emotion_surface_fear.png'),fullPage:true});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  const mobileContext = await browser.newContext({...devices['iPhone 13'],defaultBrowserType:undefined,reducedMotion:'reduce'});
  await mobileContext.route(/^https?:/,route=>{result.network_attempts.push(route.request().url());return route.abort();});
  const mobile=await mobileContext.newPage();mobile.on('pageerror',e=>result.errors.push(e.message));
  await mobile.goto(url);await ready(mobile);
  await mobile.locator('#emotion-stops button').nth(4).tap();await ready(mobile);await checkData(mobile);
  assert.equal(await mobile.locator('#emotion-slider').inputValue(),'4');
  assert.equal(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  await mobile.screenshot({path:path.join(here,'persona_emotion_surface_mobile.png'),fullPage:true});
  result.checks.push('390px mobile emulation: touch emotion selection, reduced motion, no horizontal overflow');
  assert.deepEqual(result.errors,[]);assert.deepEqual(result.network_attempts,[]);
  result.status='passed';
  fs.writeFileSync(path.join(here,'persona_emotion_surface_browser_checks.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result,null,2));await browser.close();
}
main().catch(e=>{console.error(e);process.exit(1);});
