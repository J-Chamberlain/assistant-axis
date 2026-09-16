/* AA-14 sibling of persona_trait_surface_viewer: same shell, Plotly, camera math. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const data = JSON.parse($('viewer-data').textContent);
  const plot = $('plot');
  const initCamera = TraitCamera.toCamera(TraitCamera.defaults);
  const state = {model:'qwen',x:0,y:1,z:2,layer:'both',labels:'selected',size:5,opacity:.85,camera:initCamera,selected:null,hovered:null,searchPersona:'',searchTrait:''};
  const model = () => data.models[state.model];
  const esc = s => String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt = n => Number(n).toFixed(2);
  const kinds = [['personas','#fff5df',1],['traits','#8eb8d0',.62]];
  function point(kind,index) { return model()[kind][index]; }
  function selectedPoint() { const ref=state.selected||state.hovered; return ref?point(ref.kind,ref.index):null; }
  function updatePanel() {
    const ref=state.selected||state.hovered, p=selectedPoint();
    $('clear-selection').hidden=!state.selected;
    $('selected-name').textContent=p?p.name.replaceAll('_',' '):'Explore trait space';
    $('selection-kind').textContent=p?`${state.model.toUpperCase()} · ${ref.kind==='personas'?'projected persona':'fitted trait landmark'}`:'Hover a marker or choose a name';
    $('selected-score').textContent=p?fmt(p.pcs[state.z]):'--';
    $('score-label').textContent=p?`Trait PC${state.z+1} coordinate`:'trait-space projection';
    for (const [id,axis] of [['selected-x',state.x],['selected-y',state.y],['selected-z',state.z]]) $(id).textContent=p?fmt(p.pcs[axis]):'--';
    $('selected-captured').textContent=p&&ref.kind==='personas'?`${(p.captured*100).toFixed(1)}%`:'--';
    $('selected-residual').textContent=p&&ref.kind==='personas'?fmt(p.residual):'--';
    if(p&&ref.kind==='personas'){
      const nearest=model().traits.map(t=>({name:t.name,d:Math.hypot(...[state.x,state.y,state.z].map(axis=>t.pcs[axis]-p.pcs[axis]))})).sort((a,b)=>a.d-b.d).slice(0,5);
      $('selected-nearest').textContent=nearest.map(t=>t.name.replaceAll('_',' ')).join(', ');
    }else if(p){
      const axis=[state.x,state.y,state.z].sort((a,b)=>Math.abs(p.pcs[b])-Math.abs(p.pcs[a]))[0];
      const poles=model().axis_poles?.[`PC${axis+1}`];
      $('selected-nearest').textContent=poles?`PC${axis+1} poles: ${poles.low.slice(0,2).join(', ')} ↔ ${poles.high.slice(0,2).join(', ')}`:'--';
    }else $('selected-nearest').textContent='--';
    $('ood-note').textContent=p&&p.ood?'Outside the trait-cloud reference range in the first 20 PCs.':'';
    $('point-picker').value=state.selected?`${state.selected.kind}:${state.selected.index}`:'';
  }
  function syncCamera() {
    const a=TraitCamera.fromCamera(state.camera,Number($('camera-yaw').value));
    for(const key of ['yaw','pitch','roll','zoom']){
      const v=Math.round(a[key]*10)/10;
      $(`camera-${key}`).value=v;$(`number-${key}`).value=v;
      $(`dial-${key}`).style.transform=`rotate(${key==='zoom'?v*1.2:v}deg)`;
    }
  }
  function updatePickers() {
    const picker=$('point-picker'); picker.replaceChildren(new Option('Hover, search, or choose a point',''));
    for(const [kind] of kinds) for(const [i,p] of model()[kind].entries()) picker.add(new Option(`${kind==='personas'?'Persona':'Trait'} · ${p.name.replaceAll('_',' ')}`,`${kind}:${i}`));
    updatePanel();
  }
  function render() {
    const m=model();
    const axes=[state.x,state.y,state.z];
    const displayed=axes.reduce((sum,i)=>sum+m.variance[i],0);
    $('active-model-name').textContent=m.label;
    $('category-current').textContent=axes.map(i=>`PC${i+1}`).join(' / ');
    $('plane-caption').textContent=`X Trait PC${state.x+1} / Y Trait PC${state.y+1} / Z Trait PC${state.z+1}`;
    $('variance-summary').textContent=`Trait variance: ${axes.map(i=>`${(m.variance[i]*100).toFixed(1)}%`).join(' / ')} · displayed sum ${(displayed*100).toFixed(1)}%`;
    $('stability-warning').textContent=axes.some(i=>!m.axis_stability[i])?'One or more selected individual axes are bootstrap-unstable; interpret the broader subspace cautiously.':'';
    const traces=[];
    for (const [kind,color,scale] of kinds) {
      if(state.layer!=='both' && state.layer!==kind) continue;
      const query=kind==='personas'?state.searchPersona:state.searchTrait;
      const points=m[kind].map((p,i)=>({...p,index:i})).filter(p=>!query||p.name.toLowerCase().includes(query));
      const chosen=state.selected?.kind===kind?state.selected.index:-1;
      traces.push({type:'scatter3d',name:kind==='personas'?'Projected personas':'Trait landmarks',mode:state.labels==='all'?'markers+text':'markers',
        x:points.map(p=>p.pcs[state.x]),y:points.map(p=>p.pcs[state.y]),z:points.map(p=>p.pcs[state.z]),
        text:points.map(p=>p.name.replaceAll('_',' ')),customdata:points.map(p=>[kind,p.index]),
        marker:{size:state.size*scale,color,opacity:state.opacity*(kind==='personas'?1:.58),line:{color:'#101010',width:.5}},
        hovertemplate:`<b>%{text}</b><br>${m.label} · ${kind==='personas'?'projected persona':'trait landmark'}<br>X %{x:.2f} · Y %{y:.2f} · Z %{z:.2f}<extra></extra>`});
      if(chosen>=0 && points.some(p=>p.index===chosen)){
        const p=m[kind][chosen];
        traces.push({type:'scatter3d',name:'Selected',mode:'markers+text',x:[p.pcs[state.x]],y:[p.pcs[state.y]],z:[p.pcs[state.z]],
          text:[p.name.replaceAll('_',' ')],textposition:'top center',textfont:{color:'#fff5df',size:12},marker:{size:state.size+5,color:'#f4d572',line:{color:'#fff',width:2}},hoverinfo:'skip',showlegend:false});
      }
    }
    const layout={paper_bgcolor:'#0d0d0d',plot_bgcolor:'#0d0d0d',margin:{l:0,r:0,t:25,b:0},showlegend:true,
      legend:{x:.02,y:.03,font:{family:'Menlo, monospace',color:'#aaa6a0',size:11},bgcolor:'rgba(0,0,0,.2)'},
      hoverlabel:{bgcolor:'#1b1b1b',bordercolor:'#76746e',font:{size:12,color:'#eee'}},uirevision:'trait-pc-view',
      scene:{uirevision:'trait-pc-camera',bgcolor:'rgba(0,0,0,0)',dragmode:'orbit',camera:state.camera,aspectmode:'data',
        xaxis:{title:{text:`Trait PC${state.x+1}`},color:'#aaa6a0',gridcolor:'#3b3b3b',zerolinecolor:'#555'},
        yaxis:{title:{text:`Trait PC${state.y+1}`},color:'#aaa6a0',gridcolor:'#3b3b3b',zerolinecolor:'#555'},
        zaxis:{title:{text:`Trait PC${state.z+1}`},color:'#aaa6a0',gridcolor:'#3b3b3b',zerolinecolor:'#555'}}};
    Plotly.react(plot,traces,layout,{responsive:true,displayModeBar:false,scrollZoom:true}).then(()=>{
      if(!plot._aa14Bound){
        plot._aa14Bound=true;
        plot.on('plotly_hover',e=>{const cd=e.points?.[0]?.customdata;if(cd){state.hovered={kind:cd[0],index:cd[1]};updatePanel();}});
        plot.on('plotly_unhover',()=>{state.hovered=null;updatePanel();});
        plot.on('plotly_click',e=>{const cd=e.points?.[0]?.customdata;if(cd) select({kind:cd[0],index:cd[1]});});
        plot.on('plotly_relayout',e=>{if(e['scene.camera']){state.camera=e['scene.camera'];syncCamera();}});
      }
      $('startup-preview').hidden=true;$('render-status').textContent=`${m.label} · 275 personas · 240 traits · drag or use dials`;
    });
    updatePanel();
  }
  function select(ref){state.selected=ref;state.hovered=null;render();}
  for(const [id,key] of [['model-select','model'],['x-axis','x'],['y-axis','y'],['z-axis','z'],['layer-select','layer'],['label-select','labels']]){
    $(id).addEventListener('change',()=>{state[key]=['x','y','z'].includes(key)?Number($(id).value):$(id).value;if(key==='model'){state.selected=null;state.hovered=null;updatePickers();}render();});
  }
  for(const [id,key] of [['marker-size','size'],['marker-opacity','opacity']]) $(id).addEventListener('input',()=>{state[key]=key==='opacity'?Number($(id).value)/100:Number($(id).value);render();});
  for(const [id,key] of [['persona-search','searchPersona'],['trait-search','searchTrait']]) $(id).addEventListener('input',()=>{state[key]=$(id).value.trim().toLowerCase();render();});
  $('point-picker').addEventListener('change',()=>{const val=$('point-picker').value;if(!val){select(null);return;}const [kind,index]=val.split(':');select({kind,index:Number(index)});});
  $('clear-selection').addEventListener('click',()=>select(null));
  $('reset-view').addEventListener('click',()=>{state.camera=TraitCamera.toCamera(TraitCamera.defaults);syncCamera();render();});
  for(const button of document.querySelectorAll('[data-view]')) button.addEventListener('click',()=>{
    const v=button.dataset.view;
    const a=v==='top'?{yaw:0,pitch:90,roll:0,zoom:100}:v==='front'?{yaw:0,pitch:0,roll:0,zoom:100}:v==='side'?{yaw:90,pitch:0,roll:0,zoom:100}:TraitCamera.defaults;
    state.camera=TraitCamera.toCamera(a);syncCamera();render();
  });
  for(const key of ['yaw','pitch','roll','zoom']) for(const prefix of ['camera','number']) $(`${prefix}-${key}`).addEventListener(prefix==='camera'?'input':'change',()=>{
    const a=TraitCamera.fromCamera(state.camera,Number($('camera-yaw').value));a[key]=Number($(`${prefix}-${key}`).value);
    state.camera=TraitCamera.toCamera(a,state.camera.center);syncCamera();render();
  });
  for(const key of ['x','y','z']){
    const select=$(`${key}-axis`);for(let i=0;i<20;i++) select.add(new Option(`Trait PC${i+1}`,i));select.value=state[key];
  }
  updatePickers();syncCamera();render();
})();
