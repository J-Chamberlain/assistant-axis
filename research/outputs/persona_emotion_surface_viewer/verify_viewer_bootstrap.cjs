/* DOM-double tests for startup diagnostics, without opening a browser. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'viewer_bootstrap.js'),'utf8');
function boot() {
  const elements=Object.fromEntries(['render-status','error','startup-preview'].map(id=>[id,{style:{},hidden:false,textContent:''}]));
  const events={},timers=new Map();let serial=0;
  const context={document:{getElementById:id=>elements[id],addEventListener:(k,f)=>events[k]=f},
    setTimeout:f=>{timers.set(++serial,f);return serial;},clearTimeout:id=>timers.delete(id)};
  context.window=context;context.addEventListener=(k,f)=>events[k]=f;
  vm.runInNewContext(source,context);
  return {elements,events,timers,api:context.viewerBoot};
}
let b=boot();assert.match(b.elements['render-status'].textContent,/Loading the embedded/);
b.api.stage('Rendering');assert.match(b.elements['render-status'].textContent,/Rendering/);
b.api.ready();assert.equal(b.elements['startup-preview'].hidden,true);assert.equal(b.timers.size,0);
b=boot();b.events.error({message:'Example startup failure'});assert.match(b.elements.error.textContent,/Example startup failure/);
assert.equal(b.elements.error.style.display,'block');assert.equal(b.elements['startup-preview'].hidden,false);
b=boot();b.events.unhandledrejection({reason:new Error('Rejected render')});assert.match(b.elements.error.textContent,/Rejected render/);
b=boot();[...b.timers.values()][0]();assert.match(b.elements.error.textContent,/15 seconds/);
b.api.ready();assert.equal(b.elements.error.style.display,'none');assert.equal(b.elements['startup-preview'].hidden,true);
const html=fs.readFileSync(path.join(__dirname,'persona_emotion_surface_viewer.html'),'utf8');
assert.ok(html.includes('<noscript>')&&html.includes('data:image/png;base64,'));
assert.ok(html.indexOf('Independent startup guard')<html.indexOf('plotly.js v'));
assert.ok(html.indexOf('id="startup-preview"')<html.indexOf('plotly.js v'));
const result={status:'passed',test_type:'Node VM / DOM double; not a browser test',
  checks:['progress stages','runtime-error capture','promise rejection capture','15-second watchdog',
    'successful startup removes preview','late success recovers from timeout','noscript warning',
    'embedded static preview','guard and preview precede chart library']};
fs.writeFileSync(path.join(__dirname,'viewer_bootstrap_checks.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
