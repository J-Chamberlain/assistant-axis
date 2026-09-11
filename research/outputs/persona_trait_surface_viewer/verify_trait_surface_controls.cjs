/* Plotly/DOM-double UI tests, including repeated model switches; not live WebGL. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const camera=require('./camera_controls.js'),here=__dirname,models=['qwen','llama','gemma'];
const close=(a,b,tol=1e-7)=>assert.ok(Math.abs(a-b)<tol,`${a} != ${b}`);
const plain=value=>JSON.parse(JSON.stringify(value));
let mathCases=0;
for(const yaw of [-179,-90,0,46,179])for(const pitch of [-89,-30,0,35,89])
for(const roll of [-170,0,85])for(const zoom of [25,100,300]){
  const input={yaw,pitch,roll,zoom},c=camera.toCamera(input),back=camera.fromCamera(c,yaw);
  for(const k of Object.keys(input))close(input[k],back[k]);
  close(Math.hypot(c.up.x,c.up.y,c.up.z),1);close(c.up.x*c.eye.x+c.up.y*c.eye.y+c.up.z*c.eye.z,0);mathCases++;
}
for(const pitch of [-90,90]){const c=camera.toCamera({yaw:-90,pitch,roll:30,zoom:100});const b=camera.fromCamera(c,-90);close(b.pitch,pitch);close(b.roll,30);}

const editorial=JSON.parse(fs.readFileSync(path.join(here,'persona_trait_surface_data.json'))),bigFive=JSON.parse(fs.readFileSync(path.join(here,'big_five_trait_surface_data.json')));
const data={...editorial,schema_version:3,default_profile_set:'editorial',default_big_five_construction:bigFive.default_construction,profile_sets:['editorial','big_five'],
  models:Object.fromEntries(models.map(key=>[key,{...editorial.models[key],big_five:bigFive.models[key]}]))};
const html=fs.readFileSync(path.join(here,'viewer_template.html'),'utf8');
const compiled=fs.readFileSync(path.join(here,'persona_trait_surface_viewer.html'),'utf8');
const scripts=[...compiled.matchAll(/<script(?:[^>]*)>([\s\S]*?)<\/script>/g)].map(match=>match[1]);
assert.equal(scripts.length,5,'Complete embedded script tags');assert.deepEqual(JSON.parse(scripts[2]),data,'Embedded data matches saved bundle');
scripts.forEach((source,index)=>{if(index!==2)new vm.Script(source);});
const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(match=>match[1]);assert.equal(new Set(ids).size,ids.length,'Unique IDs');

class Element{
  constructor(id=''){this.id=id;this.value='';this.min='';this.max='';this.children=[];this.style={};this.events={};this.textContent='';this.checked=true;this.disabled=false;this.hidden=false;this.options=[];}
  addEventListener(event,fn){(this.events[event]??=[]).push(fn);}on(event,fn){this.addEventListener(event,fn);}
  emit(event,arg={}){for(const fn of this.events[event]||[])fn(arg);}setAttribute(k,v){this[k]=v;}
  appendChild(element){this.children.push(element);this.options=this.children;}append(...elements){this.children.push(...elements);}
  replaceChildren(...elements){this.children=elements;}
}
const elements=Object.fromEntries(ids.map(id=>[id,new Element(id)]));elements['viewer-data'].textContent=JSON.stringify(data);
for(const id of ['x-axis','y-axis'])elements[id].options=[0,1,2].map(value=>({value:String(value)}));
elements['model-select'].options=models.map(value=>({value}));
elements['profile-set-select'].options=['editorial','big_five'].map(value=>({value}));
const bounds={yaw:[-180,180],pitch:[-90,90],roll:[-180,180],zoom:[25,300]};
for(const [key,[min,max]]of Object.entries(bounds))for(const prefix of ['camera','number'])Object.assign(elements[`${prefix}-${key}`],{min:String(min),max:String(max),value:String(camera.defaults[key])});
const presets=['iso','top','front','side'].map(view=>Object.assign(new Element(),{dataset:{view}}));
const document={getElementById(id){assert.ok(elements[id],`Missing element ${id}`);return elements[id];},
  createElement(){return new Element();},querySelectorAll(selector){assert.equal(selector,'[data-view]');return presets;}};
const plot=elements.plot;let liveCamera,reactCount=0,relayoutCount=0,error=null;
plot._fullLayout={scene:{_scene:{getCamera(){return liveCamera;}}}};const tick=()=>new Promise(resolve=>setTimeout(resolve,1));
const Plotly={async react(target,traces,layout){reactCount++;target.data=traces;target.layout=layout;liveCamera=structuredClone(layout.scene.camera);await tick();},
  async relayout(target,update){relayoutCount++;liveCamera=structuredClone(update['scene.camera']);target.emit('plotly_relayout',update);await tick();}};
const window={Plotly,TraitCamera:camera,innerWidth:1400,matchMedia:()=>({matches:false}),viewerBoot:{stage(){},ready(){},fail(problem){error=problem;}}};
const context={window,document,Plotly,TraitCamera:camera,structuredClone,performance,console,setTimeout,requestAnimationFrame:fn=>setTimeout(fn,0)};
vm.runInNewContext(fs.readFileSync(path.join(here,'viewer.js'),'utf8'),context);
async function ready(){for(let i=0;i<2000;i++){if(error)throw error;if(window.__traitViewer.ready)return;await tick();}throw Error('Render did not settle');}
async function set(id,value,event='change'){elements[id].value=String(value);elements[id].emit(event);await ready();}

function assertSelectedModelTraces(modelKey){
  const api=window.__traitViewer,base=data.models[modelKey],model=api.state.profileSet==='big_five'?{...base,...base.big_five}:base,snapshot=api.snapshot();
  assert.equal(api.state.model,modelKey);assert.equal(snapshot.model,modelKey);assert.equal(elements['active-model-name'].textContent,model.short_label);
  assert.equal(snapshot.profileSet,api.state.profileSet);
  assert.deepEqual(Array.from(plot.data[4].x),model.roles.map(role=>role.pcs[api.state.x]));
  assert.deepEqual(Array.from(plot.data[4].y),model.roles.map(role=>role.pcs[api.state.y]));
  assert.deepEqual(Array.from(plot.data[4].z),model.categories[api.state.category].values);
  const lower=Math.min(api.state.x,api.state.y),upper=Math.max(api.state.x,api.state.y),view=model.views[`${lower}_${upper}`];
  const expected=api.state.x<api.state.y?view.levels[api.state.smoothing].grids[api.state.category]:
    view.levels[api.state.smoothing].grids[api.state.category][0].map((_,index)=>view.levels[api.state.smoothing].grids[api.state.category].map(row=>row[index]));
  assert.deepEqual(plain(plot.data[1].z),plain(expected),'Surface grid must belong to selected model');
  close(snapshot.flatAdherence.fabric_flat_rmse,view.levels[api.state.smoothing].flat_adherence[api.state.category].fabric_flat_rmse);
}

async function check(){
  await ready();const api=window.__traitViewer;assert.equal(api.state.model,'qwen');assert.equal(api.state.profileSet,'editorial');assert.equal(elements['model-select'].value,'qwen');
  assert.equal(plot.data[4].x.length,275);assert.equal(elements['category-stops'].children.length,5);assert.equal(elements['persona-picker'].children.length,275);
  for(let group=0;group<5;group++){await set('category-slider',group,'input');assert.equal(api.state.category,group);assertSelectedModelTraces('qwen');assert.equal(plot.data[1].cmin,0);assert.equal(plot.data[1].cmax,100);}
  assert.equal(plot.data[6].name,'Best-fit flat plane');assert.equal(plot.data[6].visible,true);assert.ok(Number.isFinite(api.snapshot().flatAdherence.fabric_flat_rmse));
  elements['show-flat'].checked=false;elements['show-flat'].emit('change');await ready();assert.equal(plot.data[6].visible,false);
  elements['show-flat'].checked=true;elements['show-flat'].emit('change');await ready();elements['show-flat-only'].checked=true;elements['show-flat-only'].emit('change');await ready();
  assert.equal(plot.data[6].visible,true);for(const index of [1,2,3,4,5])assert.equal(plot.data[index].visible,false);assert.equal(plot.data[0].visible,true);
  elements['show-flat-only'].checked=false;elements['show-flat-only'].emit('change');await ready();
  const playwright=data.models.qwen.roles.findIndex(role=>role.name==='playwright');await set('persona-picker',playwright);assert.equal(api.selectedPersona,'playwright');
  assert.equal(elements['member-scores'].children.length,3);assert.equal(plot.data[5].x.length,1);
  elements['show-nodes'].checked=false;elements['show-nodes'].emit('change');await ready();for(const index of [3,4,5])assert.equal(plot.data[index].visible,false);
  elements['show-nodes'].checked=true;elements['show-nodes'].emit('change');await ready();
  for(const [key,value]of Object.entries({yaw:-40,pitch:52,roll:23,zoom:145}))await set(`camera-${key}`,value,'input');
  let angles=camera.fromCamera(api.state.camera);for(const [key,value]of Object.entries({yaw:-40,pitch:52,roll:23,zoom:145}))close(angles[key],value);
  const kept=JSON.stringify(api.state.camera);await set('category-slider',2,'input');await set('smoothing',2);assert.equal(JSON.stringify(api.state.camera),kept);
  for(const [x,y]of [[2,1],[2,0],[1,0],[1,2],[0,2],[0,1]]){if(api.state.x!==x)await set('x-axis',x);if(api.state.y!==y)await set('y-axis',y);assert.equal(JSON.stringify(api.state.camera),kept);assertSelectedModelTraces('qwen');}
  const qwenX=Array.from(plot.data[4].x),qwenHeight=Array.from(plot.data[4].z);
  for(const model of ['llama','gemma','qwen','gemma','llama']){
    await set('model-select',model);assert.equal(api.selectedPersona,'playwright');assert.equal(JSON.stringify(api.state.camera),kept);assertSelectedModelTraces(model);
  }
  assert.notDeepEqual(Array.from(plot.data[4].x),qwenX);assert.notDeepEqual(Array.from(plot.data[4].z),qwenHeight);
  const editorialHeight=Array.from(plot.data[4].z),selectedBeforeProfile=api.selectedPersona,cameraBeforeProfile=JSON.stringify(api.state.camera);
  await set('profile-set-select','big_five');assert.equal(api.state.profileSet,'big_five');assert.equal(api.selectedPersona,selectedBeforeProfile);assert.equal(JSON.stringify(api.state.camera),cameraBeforeProfile);assertSelectedModelTraces('llama');
  assert.equal(elements['category-stops'].children.length,5);assert.equal(elements['category-stops'].children[3].textContent,'Agreeableness');assert.equal(elements['member-scores'].children.length,data.models.llama.big_five.categories[0].members.length);
  assert.notDeepEqual(Array.from(plot.data[4].z),editorialHeight,'Profile switch must replace node heights');
  const llamaBigFive=Array.from(plot.data[4].z);await set('model-select','gemma');assertSelectedModelTraces('gemma');assert.notDeepEqual(Array.from(plot.data[4].z),llamaBigFive,'Big Five model switch must replace node heights');
  await set('profile-set-select','editorial');assert.equal(api.state.profileSet,'editorial');assert.equal(api.selectedPersona,selectedBeforeProfile);assertSelectedModelTraces('gemma');
  // Queue model changes before the current render settles; final selected model must own every trace.
  elements['model-select'].value='qwen';elements['model-select'].emit('change');elements['model-select'].value='gemma';elements['model-select'].emit('change');
  elements['model-select'].value='llama';elements['model-select'].emit('change');await ready();assertSelectedModelTraces('llama');assert.equal(api.selectedPersona,'playwright');
  for(let yaw=-70;yaw<=70;yaw+=10){elements['camera-yaw'].value=String(yaw);elements['camera-yaw'].emit('input');}
  elements['category-slider'].value='4';elements['category-slider'].emit('input');await ready();close(camera.fromCamera(api.state.camera).yaw,70);assert.equal(api.state.category,4);assertSelectedModelTraces('llama');
  liveCamera=camera.toCamera({yaw:125,pitch:10,roll:-14,zoom:80});plot.emit('plotly_relayout',{'scene.camera':liveCamera});close(Number(elements['number-yaw'].value),125);
  await set('number-zoom',175);close(camera.fromCamera(api.state.camera).zoom,175);for(const preset of presets){preset.emit('click');await ready();assert.ok(Number.isFinite(camera.fromCamera(liveCamera).pitch));}
  elements['reset-view'].emit('click');await ready();assert.equal(api.state.model,'qwen');assert.equal(api.state.profileSet,'editorial');assert.equal(api.selectedPersona,'playwright');close(camera.fromCamera(api.state.camera).zoom,100);assertSelectedModelTraces('qwen');
  await set('number-zoom','');close(camera.fromCamera(api.state.camera).zoom,100);
  const result={status:'pass',camera_roundtrip_cases:mathCases,poles_checked:true,models_tested:models,
    checks:['Compiled HTML scripts parse and embedded multimodel data matches','Default and reset model are Qwen','All five groups and fixed color limits',
      'Exact 275 selected-model nodes and three member scores','All six ordered axis views','Selected-model surfaces, support masks, flat planes and diagnostics replace prior traces',
      'Repeated and queued Qwen/Llama/Gemma switches converge without stale traces','Editorial/Big Five profile switching replaces nodes, meshes, planes and details without stale traces','Selection persists by persona name across models and profile sets','Yaw/pitch/roll/zoom survive model, profile, axis, group and smoothing changes',
      'Flat-plane-only and node visibility','Drag relayout, presets, reset and numeric entry'],react_count:reactCount,relayout_count:relayoutCount,
    live_browser_test:false,note:'Plotly/DOM double tests state and camera math; actual browser verification is recorded separately.'};
  fs.writeFileSync(path.join(here,'trait_surface_control_checks.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
}
check().catch(error=>{console.error(error);process.exitCode=1;});
