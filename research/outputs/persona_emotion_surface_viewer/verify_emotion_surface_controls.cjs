/* UI-state tests with a Plotly/DOM double, not a live-browser/WebGL test. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const camera=require('./camera_controls.js'),here=__dirname;
const close=(a,b,tol=1e-7)=>assert.ok(Math.abs(a-b)<tol,`${a} != ${b}`);
let mathCases=0;
for(const yaw of [-179,-90,0,46,179]) for(const pitch of [-89,-30,0,35,89])
for(const roll of [-170,0,85]) for(const zoom of [25,100,300]) {
  const input={yaw,pitch,roll,zoom},c=camera.toCamera(input),back=camera.fromCamera(c,yaw);
  for(const k of Object.keys(input)) close(input[k],back[k]);
  close(Math.hypot(c.up.x,c.up.y,c.up.z),1);
  close(c.up.x*c.eye.x+c.up.y*c.eye.y+c.up.z*c.eye.z,0);
  mathCases++;
}
for(const pitch of [-90,90]) {
  const c=camera.toCamera({yaw:-90,pitch,roll:30,zoom:100});
  const b=camera.fromCamera(c,-90);close(b.pitch,pitch);close(b.roll,30);
}
const data=JSON.parse(fs.readFileSync(path.join(here,'persona_emotion_surface_data.json')));
const html=fs.readFileSync(path.join(here,'viewer_template.html'),'utf8');
const compiled=fs.readFileSync(path.join(here,'persona_emotion_surface_viewer.html'),'utf8');
const scripts=[...compiled.matchAll(/<script(?:[^>]*)>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
assert.equal(scripts.length,5,'Complete embedded script tags');
const dataMatch=compiled.match(/<script id="viewer-data" type="application\/json">([\s\S]*?)<\/script>/);
assert.ok(dataMatch,'Compiled data script is present');
assert.deepEqual(JSON.parse(dataMatch[1]),data,'Embedded data matches saved bundle');
for(const source of [fs.readFileSync(path.join(here,'camera_controls.js'),'utf8'),fs.readFileSync(path.join(here,'viewer.js'),'utf8')]) new vm.Script(source);
const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
assert.equal(new Set(ids).size,ids.length,'Unique IDs');
class Element {
  constructor(id='') {this.id=id;this.value='';this.min='';this.max='';this.children=[];this.style={};this.events={};this.textContent='';this.checked=true;this.options=[];this.hidden=false;this.disabled=false;this.dataset={};}
  addEventListener(event,fn){(this.events[event]??=[]).push(fn);}
  on(event,fn){this.addEventListener(event,fn);}
  emit(event,arg={}){for(const fn of this.events[event]||[]) fn(arg);}
  setAttribute(k,v){this[k]=v;}
  appendChild(e){this.children.push(e);}
  append(...elements){this.children.push(...elements);}
}
const elements=Object.fromEntries(ids.map(id=>[id,new Element(id)]));
elements['viewer-data'].textContent=JSON.stringify(data);
for(const id of ['x-axis','y-axis']) elements[id].options=[0,1,2].map(value=>({value:String(value)}));
const bounds={yaw:[-180,180],pitch:[-90,90],roll:[-180,180],zoom:[25,300]};
for(const [k,[min,max]] of Object.entries(bounds)) for(const prefix of ['camera','number'])
  Object.assign(elements[`${prefix}-${k}`],{min:String(min),max:String(max),value:String(camera.defaults[k])});
const presets=['iso','top','front','side'].map(v=>Object.assign(new Element(),{dataset:{view:v}}));
const document={getElementById(id){assert.ok(elements[id],`Missing element ${id}`);return elements[id];},
  createElement(){return new Element();},querySelectorAll(selector){assert.equal(selector,'[data-view]');return presets;}};
const plot=elements.plot;let liveCamera,reactCount=0,relayoutCount=0,error=null;
plot._fullLayout={scene:{_scene:{getCamera(){return liveCamera;}}}};
const tick=()=>new Promise(r=>setTimeout(r,1));
const Plotly={async react(p,traces,layout){reactCount++;p.data=traces;p.layout=layout;liveCamera=structuredClone(layout.scene.camera);await tick();},
  async relayout(p,update){relayoutCount++;liveCamera=structuredClone(update['scene.camera']);p.emit('plotly_relayout',update);await tick();}};
const window={Plotly,EmotionCamera:camera,innerWidth:1400,matchMedia:()=>({matches:false}),
  viewerBoot:{stage(){},ready(){},fail(e){error=e;}}};
const context={window,document,Plotly,EmotionCamera:camera,structuredClone,performance,console,setTimeout,
  requestAnimationFrame:fn=>setTimeout(fn,0)};
vm.runInNewContext(fs.readFileSync(path.join(here,'viewer.js'),'utf8'),context);
async function ready(){for(let i=0;i<1000;i++){if(error) throw error;if(window.__emotionViewer.ready)return;await tick();}throw Error('Render did not settle');}
async function set(id,value,event='change'){elements[id].value=String(value);elements[id].emit(event);await ready();}
async function check(){
  await ready();const api=window.__emotionViewer;
  assert.equal(plot.data[4].x.length,275);assert.equal(elements['emotion-stops'].children.length,6);
  for(let e=0;e<6;e++){
    await set('emotion-slider',e,'input');assert.equal(api.state.emotion,e);
    assert.deepEqual(Array.from(plot.data[4].z),data.emotions[e].z);
    assert.equal(plot.data[1].cmin,-data.z_limit);assert.equal(plot.data[1].cmax,data.z_limit);assert.equal(plot.data[1].opacity,1);
  }
  await set('persona-picker',data.roles.findIndex(r=>r.name==='playwright'));
  assert.equal(plot.data[5].x.length,1);
  elements['show-nodes'].checked=false;elements['show-nodes'].emit('change');await ready();
  for(const i of [0,3,4,5]) assert.equal(plot.data[i].visible,false);
  assert.equal(plot.data[1].visible,true);assert.equal(plot.data[2].visible,true);assert.equal(elements['show-connectors'].disabled,true);
  elements['show-nodes'].checked=true;elements['show-nodes'].emit('change');await ready();
  assert.equal(plot.data[4].visible,true);assert.equal(plot.data[5].visible,true);
  for(const [k,value] of Object.entries({yaw:-40,pitch:52,roll:23,zoom:145})) await set(`camera-${k}`,value,'input');
  let angles=camera.fromCamera(api.state.camera);for(const [k,v] of Object.entries({yaw:-40,pitch:52,roll:23,zoom:145}))close(angles[k],v);
  const kept=JSON.stringify(api.state.camera);
  await set('emotion-slider',2,'input');await set('smoothing',2);assert.equal(JSON.stringify(api.state.camera),kept);
  for(const [x,y] of [[2,1],[2,0],[1,0],[1,2],[0,2],[0,1]]) {
    if(api.state.x!==x) await set('x-axis',x);
    if(api.state.y!==y) await set('y-axis',y);
    assert.equal(JSON.stringify(api.state.camera),kept);
    const s=api.snapshot(),v=data.views[[x,y].sort().join('_')].levels[2].grids[2];
    close(s.x[0],data.views[[x,y].sort().join('_')][x<y?'x':'y'][0]);
    assert.equal(s.grid[17][23],x<y?v[17][23]:v[23][17]);
  }
  for(let yaw=-70;yaw<=70;yaw+=10){elements['camera-yaw'].value=String(yaw);elements['camera-yaw'].emit('input');}
  elements['emotion-slider'].value='4';elements['emotion-slider'].emit('input');await ready();
  close(camera.fromCamera(api.state.camera).yaw,70);close(camera.fromCamera(liveCamera).yaw,70);assert.equal(api.state.emotion,4);
  liveCamera=camera.toCamera({yaw:125,pitch:10,roll:-14,zoom:80});plot.emit('plotly_relayout',{'scene.camera':liveCamera});
  close(Number(elements['number-yaw'].value),125);close(Number(elements['number-zoom'].value),80);
  await set('number-zoom',175);close(camera.fromCamera(api.state.camera).zoom,175);
  for(const preset of presets){preset.emit('click');await ready();assert.ok(Number.isFinite(camera.fromCamera(liveCamera).pitch));}
  elements['reset-view'].emit('click');await ready();close(camera.fromCamera(api.state.camera).zoom,100);
  await set('number-zoom','');close(camera.fromCamera(api.state.camera).zoom,100);
  const result={status:'pass',camera_roundtrip_cases:mathCases,poles_checked:true,
    checks:['Compiled HTML scripts parse and embedded data matches','All six emotion channels and fixed vivid symmetric color limits','Exact 275 nodes',
      'Fabric-only hides nodes, pins, connectors and reference plane','All six ordered axis views','Yaw/pitch/roll/zoom and numeric entry',
      'Drag relayout updates controls','Camera survives axes, emotion and smoothing changes','Rapid camera/emotion changes converge',
      'Top/front/side/isometric and reset','Empty numeric input restored'],react_count:reactCount,relayout_count:relayoutCount,live_browser_test:false,
    note:'Plotly/DOM double tests UI state and camera math, not actual WebGL rendering.'};
  fs.writeFileSync(path.join(here,'emotion_surface_control_checks.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
}
check().catch(e=>{console.error(e);process.exitCode=1;});
