/* Static rasterization plus model-switch DOM-double tests; not a live browser. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),vm=require('node:vm'),sharp=require('sharp');
const here=__dirname,models=['qwen','llama','gemma'];

async function raster(base,suffix) {
  const source=fs.readFileSync(base+'.svg');
  await sharp(source,{limitInputPixels:30000000}).png().toFile(base+'.png');
  const image=sharp(base+'.png'),metadata=await image.metadata(),stats=await image.stats();
  assert.ok(stats.channels.slice(0,3).every(channel=>channel.stdev>15),'Figure must not be blank');
  assert.equal(metadata.width,suffix==='overview'?3000:1000);
  assert.equal(metadata.height,suffix==='overview'?940:12380);
  return {file:path.basename(base+'.png'),width:metadata.width,height:metadata.height};
}

function domChecks(html) {
  const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].at(-1)[1];
  const viewMatches=[...html.matchAll(/<div class="model-view" data-model-view="([^"]+)"( hidden)?>/g)];
  const views=viewMatches.map(match=>({dataset:{modelView:match[1]},hidden:Boolean(match[2])}));
  const rowMatches=[...html.matchAll(/<div class="ridge-row" data-model="([^"]+)" data-axis="([^"]+)" data-persona="([^"]+)" data-rank="([^"]+)" data-pc="([^"]+)">/g)];
  const rows=rowMatches.map((match,index)=>({dataset:{model:match[1],axis:match[2],persona:match[3],rank:match[4],pc:match[5]},
    offsetTop:(index%275)*44,parentElement:{offsetTop:0,scrollTop:0},classList:{toggle(_,active){this.active=active;}}}));
  const buttonMatches=[...html.matchAll(/<button class="name" type="button" data-name="([^"]+)">/g)];
  const buttons=buttonMatches.map(match=>({dataset:{name:match[1]},addEventListener(_,fn){this.click=fn;}}));
  const element=()=>({value:'',textContent:'',events:{},addEventListener(event,fn){this.events[event]=fn;}});
  const elements={'model-select':element(),'find-persona':element(),'selection-status':element(),'active-model-name':element(),
    'model-provenance':element(),'reset-view':element()};
  const document={getElementById(id){assert.ok(elements[id],`Missing ${id}`);return elements[id];},querySelectorAll(selector){
    if(selector==='[data-model-view]')return views;if(selector==='.ridge-row')return rows;if(selector==='[data-name]')return buttons;
    throw new Error(`Unexpected selector ${selector}`);
  }};
  const window={};new vm.Script(script).runInNewContext({document,window});
  const api=window.__traitRidgeViewer;
  assert.equal(api.model,'qwen');assert.deepEqual(views.map(view=>view.hidden),[false,true,true]);
  const qwenPCs=api.activeRows().map(row=>row.dataset.pc);
  elements['find-persona'].value='playwright';elements['find-persona'].events.change();
  assert.equal(api.selectedPersona,'playwright');assert.equal(rows.filter(row=>row.classList.active).length,3);
  elements['model-select'].value='llama';elements['model-select'].events.change();
  assert.equal(api.model,'llama');assert.equal(api.selectedPersona,'playwright');
  assert.deepEqual(views.map(view=>view.hidden),[true,false,true]);
  assert.equal(rows.filter(row=>row.classList.active).length,3);
  assert.notDeepEqual(api.activeRows().map(row=>row.dataset.pc),qwenPCs,'Model switch must replace coordinate rows');
  elements['model-select'].value='gemma';elements['model-select'].events.change();
  assert.equal(api.model,'gemma');assert.equal(api.selectedPersona,'playwright');
  buttons.find((_,index)=>rows[index].dataset.model==='gemma').click();
  assert.equal(api.selectedPersona,rows.find(row=>row.dataset.model==='gemma').dataset.persona);
  elements['reset-view'].events.click();assert.equal(api.model,'qwen');assert.equal(api.selectedPersona,'');
  assert.equal(rows.filter(row=>row.classList.active).length,0);
  return {checks:['Default is Qwen','Qwen/Llama/Gemma views switch without reload','Coordinate rows change with model',
    'Selection persists by persona name across model switches','Persona buttons link all three PC panels','Reset restores Qwen and clears selection']};
}

async function main() {
  const results=[];
  for(const model of models)for(const suffix of ['pc1','pc2','pc3','overview'])
    results.push(await raster(path.join(here,`persona_trait_ridges_${model}_${suffix}`),suffix));
  for(const suffix of ['pc1','pc2','pc3','overview'])
    results.push(await raster(path.join(here,`persona_trait_ridges_${suffix}`),suffix));
  const interaction=domChecks(fs.readFileSync(path.join(here,'persona_trait_ridges.html'),'utf8'));
  const result={status:'pass',static_renders:results,interaction_unit_checks:interaction.checks,browser_test:false,
    note:'Sharp rasterization and a Node DOM double test static/model-switch state; actual browser verification is recorded separately.'};
  fs.writeFileSync(path.join(here,'ridge_render_checks.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result,null,2));
}
main().catch(error=>{console.error(error);process.exitCode=1;});
