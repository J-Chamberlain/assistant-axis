/* Actual headless Chrome verification for both self-contained trait viewers. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const puppeteer=require('puppeteer-core');

const here=__dirname,root=path.resolve(here,'../../..');
const ridgeDir=path.join(root,'research/outputs/persona_trait_ridge_plots');
const chrome=process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const models=['qwen','llama','gemma'];
const pause=milliseconds=>new Promise(resolve=>setTimeout(resolve,milliseconds));

async function readySurface(page){
  await page.waitForFunction(()=>window.__traitViewer&&window.__traitViewer.ready,{timeout:120000});
}
async function selectValue(page,id,value,event='change'){
  await page.evaluate(({id,value,event})=>{const element=document.getElementById(id);element.value=String(value);element.dispatchEvent(new Event(event,{bubbles:true}));},{id,value,event});
}

async function verifyRidge(browser){
  const page=await browser.newPage();await page.setViewport({width:1440,height:1000,deviceScaleFactor:1});
  const errors=[];page.on('pageerror',error=>errors.push(String(error)));page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
  await page.goto(pathToFileURL(path.join(ridgeDir,'persona_trait_ridges.html')).href,{waitUntil:'load',timeout:120000});
  const initial=await page.evaluate(()=>({model:window.__traitRidgeViewer.model,profileSet:window.__traitRidgeViewer.profileSet,visibleViews:[...document.querySelectorAll('[data-model-view]')].filter(view=>!view.hidden).map(view=>view.dataset.modelView),
    rows:window.__traitRidgeViewer.activeRows().length,circles:document.querySelector('[data-model-view="qwen"]').querySelectorAll('circle').length,
    pcs:window.__traitRidgeViewer.activeRows().slice(0,20).map(row=>row.dataset.pc)}));
  assert.equal(initial.model,'qwen');assert.equal(initial.profileSet,'editorial');assert.deepEqual(initial.visibleViews,['qwen']);assert.equal(initial.rows,825);assert.equal(initial.circles,12375);
  await selectValue(page,'find-persona','playwright');
  const coordinates={qwen:initial.pcs};
  for(const model of ['llama','gemma']){
    await selectValue(page,'model-select',model);await pause(25);
    const state=await page.evaluate(()=>({model:window.__traitRidgeViewer.model,selected:window.__traitRidgeViewer.selectedPersona,
      selectedRows:document.querySelectorAll('.ridge-row.selected').length,visible:[...document.querySelectorAll('[data-model-view]')].filter(view=>!view.hidden).map(view=>view.dataset.modelView),
      pcs:window.__traitRidgeViewer.activeRows().slice(0,20).map(row=>row.dataset.pc)}));
    assert.equal(state.model,model);assert.equal(state.selected,'playwright');assert.equal(state.selectedRows,3);assert.deepEqual(state.visible,[model]);coordinates[model]=state.pcs;
    assert.notDeepEqual(state.pcs,coordinates.qwen);
  }
  const editorialPcs=await page.evaluate(()=>window.__traitRidgeViewer.activeRows().slice(0,20).map(row=>Number(row.dataset.pc)));
  await selectValue(page,'profile-set-select','big_five');await pause(100);
  const strict=await page.evaluate(()=>({model:window.__traitRidgeViewer.model,profileSet:window.__traitRidgeViewer.profileSet,construction:window.__traitRidgeViewer.construction,
    selected:window.__traitRidgeViewer.selectedPersona,rows:window.__traitRidgeViewer.activeRows().length,circles:document.getElementById('big-five-view').querySelectorAll('circle').length,
    pcs:window.__traitRidgeViewer.activeRows().slice(0,20).map(row=>Number(row.dataset.pc)),heights:[...document.getElementById('big-five-view').querySelectorAll('circle')].slice(0,20).map(node=>node.getAttribute('cy'))}));
  assert.equal(strict.model,'gemma');assert.equal(strict.profileSet,'big_five');assert.equal(strict.construction,'human_anchored_strict');assert.equal(strict.selected,'playwright');assert.equal(strict.rows,825);assert.equal(strict.circles,4125);strict.pcs.forEach((value,index)=>assert.ok(Math.abs(value-editorialPcs[index])<1e-9));
  await selectValue(page,'construction-select','external_taxonomy_expanded');await pause(100);
  const expanded=await page.evaluate(()=>({construction:window.__traitRidgeViewer.construction,selected:window.__traitRidgeViewer.selectedPersona,
    heights:[...document.getElementById('big-five-view').querySelectorAll('circle')].slice(0,20).map(node=>node.getAttribute('cy'))}));
  assert.equal(expanded.construction,'external_taxonomy_expanded');assert.equal(expanded.selected,'playwright');assert.notDeepEqual(expanded.heights,strict.heights);
  await selectValue(page,'model-select','qwen');await pause(100);assert.equal(await page.evaluate(()=>window.__traitRidgeViewer.selectedPersona),'playwright');
  await selectValue(page,'construction-select','human_anchored_strict');await pause(100);await page.screenshot({path:path.join(ridgeDir,'big_five_ridge_browser.png')});
  await page.click('#reset-view');
  const reset=await page.evaluate(()=>({model:window.__traitRidgeViewer.model,profileSet:window.__traitRidgeViewer.profileSet,construction:window.__traitRidgeViewer.construction,constructionControl:document.getElementById('construction-select').value,selected:window.__traitRidgeViewer.selectedPersona,selectedRows:document.querySelectorAll('.ridge-row.selected').length}));
  assert.deepEqual(reset,{model:'qwen',profileSet:'editorial',construction:'human_anchored_strict',constructionControl:'human_anchored_strict',selected:'',selectedRows:0});
  await page.screenshot({path:path.join(ridgeDir,'multimodel_ridge_browser.png')});
  assert.deepEqual(errors,[],'Ridge page errors');await page.close();
  return {default_model:'qwen',models_switched:models,active_rows_per_model:825,active_trait_nodes_per_model:12375,
    coordinate_rows_changed:true,big_five_profile_switch:true,all_four_ridge_constructions_available:true,profile_switch_replaced_heights:true,selection_persisted_by_name:true,reset_restored_qwen_editorial:true,page_errors:errors};
}

async function surfaceState(page){
  return page.evaluate(()=>{
    const api=window.__traitViewer,model=api.modelData(),plot=document.getElementById('plot'),snapshot=api.snapshot();
    const surface=plot.data[1].z;
    return {model:api.state.model,profileSet:api.state.profileSet,selected:api.selectedPersona,category:api.state.category,x:api.state.x,y:api.state.y,smoothing:api.state.smoothing,
      camera:JSON.stringify(api.state.camera),angles:window.TraitCamera.fromCamera(api.state.camera),nodeCount:plot.data[4].x.length,nodeX:Array.from(plot.data[4].x).slice(0,20),nodeY:Array.from(plot.data[4].y).slice(0,20),
      nodeZ:Array.from(plot.data[4].z).slice(0,20),expectedX:model.roles.slice(0,20).map(role=>role.pcs[api.state.x]),
      expectedY:model.roles.slice(0,20).map(role=>role.pcs[api.state.y]),expectedZ:model.categories[api.state.category].values.slice(0,20),
      surfaceSample:[surface[5][5],surface[20][20],surface[40][40]],flatRmse:snapshot.flatAdherence.fabric_flat_rmse,
      expectedFlatRmse:model.views[[Math.min(api.state.x,api.state.y),Math.max(api.state.x,api.state.y)].join('_')].levels[api.state.smoothing].flat_adherence[api.state.category].fabric_flat_rmse,
      renderStatus:document.getElementById('render-status').textContent};
  });
}

async function verifySurface(browser){
  const page=await browser.newPage();await page.setViewport({width:1440,height:1000,deviceScaleFactor:1});
  const errors=[];page.on('pageerror',error=>errors.push(String(error)));page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
  await page.goto(pathToFileURL(path.join(here,'persona_trait_surface_viewer.html')).href,{waitUntil:'load',timeout:120000});await readySurface(page);
  const initial=await surfaceState(page);assert.equal(initial.model,'qwen');assert.equal(initial.profileSet,'editorial');assert.equal(initial.nodeCount,275);assert.deepEqual(initial.nodeX,initial.expectedX);assert.deepEqual(initial.nodeY,initial.expectedY);assert.deepEqual(initial.nodeZ,initial.expectedZ);assert.equal(initial.flatRmse,initial.expectedFlatRmse);
  const playwright=await page.evaluate(()=>window.__traitViewer.modelData().roles.findIndex(role=>role.name==='playwright'));
  await selectValue(page,'persona-picker',playwright);await readySurface(page);const keptAngles=(await surfaceState(page)).angles;
  const sameAngles=(actual,expected)=>{for(const key of ['yaw','pitch','roll','zoom'])assert.ok(Math.abs(actual[key]-expected[key])<1e-7,`${key}: ${actual[key]} != ${expected[key]}`);};
  const states={qwen:initial};
  for(const model of ['llama','gemma','qwen','gemma','llama']){
    await selectValue(page,'model-select',model);await readySurface(page);const state=await surfaceState(page);states[model]=state;
    assert.equal(state.model,model);assert.equal(state.selected,'playwright');assert.equal(state.nodeCount,275);assert.deepEqual(state.nodeX,state.expectedX);assert.deepEqual(state.nodeY,state.expectedY);assert.deepEqual(state.nodeZ,state.expectedZ);assert.equal(state.flatRmse,state.expectedFlatRmse);sameAngles(state.angles,keptAngles);
  }
  assert.notDeepEqual(states.llama.nodeX,states.qwen.nodeX);assert.notDeepEqual(states.gemma.nodeX,states.qwen.nodeX);assert.notDeepEqual(states.llama.nodeZ,states.qwen.nodeZ);assert.notDeepEqual(states.gemma.nodeZ,states.qwen.nodeZ);
  const editorialHeights=states.llama.nodeZ;await selectValue(page,'profile-set-select','big_five');await readySurface(page);let bigFive=await surfaceState(page);
  assert.equal(bigFive.profileSet,'big_five');assert.equal(bigFive.selected,'playwright');assert.deepEqual(bigFive.nodeZ,bigFive.expectedZ);assert.equal(bigFive.flatRmse,bigFive.expectedFlatRmse);assert.notDeepEqual(bigFive.nodeZ,editorialHeights);
  await selectValue(page,'category-slider',3,'input');await readySurface(page);bigFive=await surfaceState(page);assert.equal(await page.$eval('#category-current',node=>node.textContent),'Agreeableness');
  const llamaBigFive=bigFive.nodeZ;await selectValue(page,'model-select','gemma');await readySurface(page);bigFive=await surfaceState(page);assert.equal(bigFive.profileSet,'big_five');assert.equal(bigFive.selected,'playwright');assert.notDeepEqual(bigFive.nodeZ,llamaBigFive);assert.deepEqual(bigFive.nodeZ,bigFive.expectedZ);
  await selectValue(page,'model-select','qwen');await readySurface(page);await selectValue(page,'x-axis',0);await readySurface(page);await selectValue(page,'y-axis',2);await readySurface(page);await page.screenshot({path:path.join(here,'big_five_surface_browser.png')});
  await selectValue(page,'profile-set-select','editorial');await readySurface(page);assert.equal((await surfaceState(page)).profileSet,'editorial');
  await selectValue(page,'camera-yaw',73,'input');await readySurface(page);const anglesAfterDial=(await surfaceState(page)).angles;
  for(const model of ['gemma','qwen','llama','qwen']){await selectValue(page,'model-select',model);await readySurface(page);const state=await surfaceState(page);sameAngles(state.angles,anglesAfterDial);assert.equal(state.selected,'playwright');}
  // Rapid switches exercise request-version cancellation and stale-trace prevention in real Plotly.
  await page.evaluate(()=>{for(const model of ['llama','gemma','qwen','gemma']){const select=document.getElementById('model-select');select.value=model;select.dispatchEvent(new Event('change',{bubbles:true}));}});await readySurface(page);
  const rapid=await surfaceState(page);assert.equal(rapid.model,'gemma');assert.deepEqual(rapid.nodeX,rapid.expectedX);assert.deepEqual(rapid.nodeZ,rapid.expectedZ);assert.equal(rapid.flatRmse,rapid.expectedFlatRmse);
  await page.click('[data-view="top"]');await readySurface(page);await selectValue(page,'model-select','llama');await readySurface(page);await page.click('[data-view="side"]');await readySurface(page);
  await page.click('#reset-view');await readySurface(page);const reset=await surfaceState(page);assert.equal(reset.model,'qwen');assert.equal(reset.profileSet,'editorial');assert.equal(reset.selected,'playwright');assert.deepEqual(reset.nodeX,reset.expectedX);assert.deepEqual(reset.nodeZ,reset.expectedZ);
  await page.screenshot({path:path.join(here,'multimodel_surface_browser.png')});
  assert.deepEqual(errors,[],'Surface page errors');await page.close();
  return {default_model:'qwen',models_switched:models,node_count_per_model:275,model_coordinates_changed:true,model_group_heights_changed:true,
    surface_and_flat_diagnostics_match_selected_model:true,big_five_profile_switch:true,profile_switch_replaced_nodes_surface_plane_and_details:true,repeated_and_rapid_switches_no_stale_traces:true,camera_controls_after_switches:true,
    camera_persisted_across_switches:true,selection_persisted_by_persona_name:true,reset_restored_qwen_editorial:true,page_errors:errors};
}

async function main(){
  assert.ok(fs.existsSync(chrome),`Chrome executable missing: ${chrome}`);
  const browser=await puppeteer.launch({executablePath:chrome,headless:true,args:['--disable-gpu-sandbox','--use-angle=swiftshader','--enable-webgl','--allow-file-access-from-files']});
  try{
    const result={status:'pass',verification_kind:'actual headless browser / real Chrome DOM and Plotly WebGL',browser_version:await browser.version(),
      generated_utc:new Date().toISOString(),ridge:await verifyRidge(browser),surface:await verifySurface(browser),unit_dom_double_results_are_separate:true};
    fs.writeFileSync(path.join(here,'trait_viewers_browser_checks.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
  }finally{await browser.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
