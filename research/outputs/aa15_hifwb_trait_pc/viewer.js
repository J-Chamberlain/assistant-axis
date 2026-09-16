/* AA-15 minimal fork of AA-14 viewer.js; same Plotly shell and TraitCamera. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const data = JSON.parse($('viewer-data').textContent);
  const plot = $('plot');
  const state = {model:'qwen',x:0,y:1,z:2,layer:'personas+traits+indicators',labels:'selected',
    size:5,opacity:.85,camera:TraitCamera.toCamera(TraitCamera.defaults),selected:null,hovered:null,
    searchPersona:'',searchTrait:'',searchIndicator:'',form:'primary_positive_pole',
    wellbeingColor:'population',indicatorLabels:false,centroid:false,ray:false};
  const model = () => data.models[state.model];
  const collection = kind => kind==='indicators'?model().indicators_by_form[state.form]:model()[kind];
  const kinds = [['personas','#fff5df',1],['traits','#8eb8d0',.62],['indicators','#f4d572',1.45]];
  const domainColors = {'Affect':'#f4d572','Appraisal':'#d5a38b','Interpersonal relationships':'#9ecbac',
    'Meaning-making':'#a4a1d7','Self-concept':'#8eb8d0','Vitality':'#f5a17b'};
  const fmt = n => Number(n).toFixed(2);
  const label = p => p.shown_wording || p.name.replaceAll('_',' ');
  const point = (kind,index) => collection(kind)[index];
  function updatePanel() {
    const ref=state.selected||state.hovered, p=ref?point(ref.kind,ref.index):null;
    $('clear-selection').hidden=!state.selected;
    $('selected-name').textContent=p?label(p):'Explore trait space';
    $('selection-kind').textContent=p?`${model().label} · ${ref.kind==='indicators'?`HiFWB ${p.domain} · ${state.form.replaceAll('_',' ')}`:ref.kind==='personas'?'projected persona':'fitted trait landmark'}`:'Hover a marker or choose a name';
    $('selected-score').textContent=p?fmt(p.pcs[state.z]):'--';
    $('score-label').textContent=p?`Trait PC${state.z+1} coordinate`:'trait-space projection';
    for(const [id,axis] of [['selected-x',state.x],['selected-y',state.y],['selected-z',state.z]])
      $(id).textContent=p?fmt(p.pcs[axis]):'--';
    $('selected-captured').textContent=p&&ref.kind!=='traits'?`${(p.captured*100).toFixed(1)}%`:'--';
    $('selected-residual').textContent=p&&ref.kind!=='traits'?fmt(p.residual):'--';
    if(p&&ref.kind==='indicators') $('selected-nearest').textContent=p.nearest.map(s=>s.replaceAll('_',' ')).join(', ');
    else if(p&&ref.kind==='personas') {
      const nearest=model().traits.map(t=>({name:t.name,d:Math.hypot(...[state.x,state.y,state.z].map(axis=>t.pcs[axis]-p.pcs[axis]))})).sort((a,b)=>a.d-b.d).slice(0,5);
      $('selected-nearest').textContent=nearest.map(t=>t.name.replaceAll('_',' ')).join(', ');
    } else if(p) {
      const axis=[state.x,state.y,state.z].sort((a,b)=>Math.abs(p.pcs[b])-Math.abs(p.pcs[a]))[0];
      const poles=model().axis_poles?.[`PC${axis+1}`];
      $('selected-nearest').textContent=poles?`PC${axis+1} poles: ${poles.low.slice(0,2).join(', ')} ↔ ${poles.high.slice(0,2).join(', ')}`:'--';
    } else $('selected-nearest').textContent='--';
    const notes=[];
    if(p?.ood) notes.push('Outside the trait-cloud reference range in the first 20 PCs.');
    if(p&&ref.kind==='indicators') {
      if(p.reverse_keyed) notes.push(`Original reverse-keyed item: “${p.wording}” The primary marker uses a separately worded positive pole.`);
      if(p.prompt_cosine_to_primary!==null) notes.push(`Raw-vector cosine to primary: ${p.prompt_cosine_to_primary.toFixed(2)}; opposite orientation is expected for reverse-keyed original wording.`);
      if(p.bootstrap_pc90) notes.push(`Paired-unit bootstrap 90% intervals: PC1 ${p.bootstrap_pc90[0].join(' to ')}, PC2 ${p.bootstrap_pc90[1].join(' to ')}, PC3 ${p.bootstrap_pc90[2].join(' to ')}.`);
      if(p.cross_model.length) notes.push(`Aligned cross-model item cosine: ${p.cross_model.map(c=>`${c.model} ${c.aligned_cosine.toFixed(2)}`).join(' · ')}.`);
    }
    if(p&&ref.kind!=='indicators'&&!model().centroid.stable&&state.wellbeingColor==='alignment')
      notes.push('Wellbeing centroid direction did not pass the prespecified stability gate; alignment is descriptive only.');
    $('ood-note').textContent=notes.join(' ');
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
    const picker=$('point-picker');picker.replaceChildren(new Option('Hover, search, or choose a point',''));
    for(const [kind] of kinds) for(const [i,p] of collection(kind).entries())
      picker.add(new Option(`${kind==='indicators'?'HiFWB':kind==='personas'?'Persona':'Trait'} · ${label(p)}`,`${kind}:${i}`));
    updatePanel();
  }
  function markerColor(kind, points, fallback) {
    if(kind==='indicators'&&state.wellbeingColor==='domain')
      return {color:points.map(p=>domainColors[p.domain]||fallback)};
    const numeric = state.wellbeingColor==='proximity'&&kind==='personas'?'wellbeing_distance':
      state.wellbeingColor==='alignment'&&kind!=='indicators'?'wellbeing_alignment':null;
    if(!numeric) return {color:fallback};
    const values=points.map(p=>p[numeric]);
    return {color:values,colorscale:[[0,'#173d9e'],[.5,'#74d9d0'],[1,'#f4d572']],
      reversescale:numeric==='wellbeing_distance',showscale:false};
  }
  function render() {
    const m=model(), axes=[state.x,state.y,state.z];
    const displayed=axes.reduce((sum,i)=>sum+m.variance[i],0);
    $('active-model-name').textContent=m.label;
    $('category-current').textContent=axes.map(i=>`PC${i+1}`).join(' / ');
    $('plane-caption').textContent=`X Trait PC${state.x+1} / Y Trait PC${state.y+1} / Z Trait PC${state.z+1}`;
    $('variance-summary').textContent=`Trait variance: ${axes.map(i=>`${(m.variance[i]*100).toFixed(1)}%`).join(' / ')} · displayed sum ${(displayed*100).toFixed(1)}%`;
    const warnings=[];
    if(axes.some(i=>!m.axis_stability[i])) warnings.push('One or more selected individual axes are bootstrap-unstable.');
    if((state.centroid||state.ray||state.wellbeingColor==='alignment')&&!m.centroid.stable)
      warnings.push('The wellbeing centroid direction did not pass the prespecified stability gate.');
    if(state.form!=='primary_positive_pole') warnings.push('Robustness wording may represent the negative pole for reverse-keyed items.');
    $('stability-warning').textContent=warnings.join(' ');
    const traces=[];
    for(const [kind,color,scale] of kinds) {
      if(!state.layer.split('+').includes(kind)) continue;
      const query=kind==='personas'?state.searchPersona:kind==='traits'?state.searchTrait:state.searchIndicator;
      const points=collection(kind).map((p,i)=>({...p,index:i})).filter(p=>!query||label(p).toLowerCase().includes(query)||p.name.toLowerCase().includes(query)||p.wording?.toLowerCase().includes(query));
      const chosen=state.selected?.kind===kind?state.selected.index:-1;
      const showLabels=kind==='indicators'?state.indicatorLabels||state.labels==='all':state.labels==='all';
      traces.push({type:'scatter3d',name:kind==='personas'?'Projected personas':kind==='traits'?'Trait landmarks':'HiFWB indicators',
        mode:showLabels?'markers+text':'markers',
        x:points.map(p=>p.pcs[state.x]),y:points.map(p=>p.pcs[state.y]),z:points.map(p=>p.pcs[state.z]),
        text:points.map(p=>kind==='indicators'?p.name:label(p)),
        hovertext:points.map(p=>kind==='indicators'?p.shown_wording:label(p)),
        customdata:points.map(p=>[kind,p.index]),
        marker:{size:state.size*scale,opacity:state.opacity*(kind==='traits'?.58:1),
          line:{color:'#101010',width:.5},...markerColor(kind,points,color)},
        hovertemplate:`<b>%{hovertext}</b><br>${m.label} · ${kind==='indicators'?'HiFWB projected indicator':kind==='personas'?'projected persona':'trait landmark'}<br>X %{x:.2f} · Y %{y:.2f} · Z %{z:.2f}<extra></extra>`});
      if(chosen>=0&&points.some(p=>p.index===chosen)){
        const p=collection(kind)[chosen];
        traces.push({type:'scatter3d',name:'Selected',mode:'markers+text',x:[p.pcs[state.x]],y:[p.pcs[state.y]],z:[p.pcs[state.z]],
          text:[kind==='indicators'?p.name:label(p)],textposition:'top center',textfont:{color:'#fff5df',size:12},
          marker:{size:state.size+5,color:'#f4d572',line:{color:'#fff',width:2}},hoverinfo:'skip',showlegend:false});
      }
    }
    if(state.form==='primary_positive_pole'&&m.centroid.stable&&(state.centroid||state.ray)){
      const c=m.centroid.pcs;
      if(state.ray) traces.push({type:'scatter3d',name:'Validated centroid direction',mode:'lines',
        x:[0,c[state.x]],y:[0,c[state.y]],z:[0,c[state.z]],line:{color:'#f4d572',width:4},hoverinfo:'skip'});
      if(state.centroid) traces.push({type:'scatter3d',name:'HiFWB centroid',mode:'markers',
        x:[c[state.x]],y:[c[state.y]],z:[c[state.z]],marker:{size:state.size+4,color:'#f4d572',symbol:'diamond'},
        hovertemplate:'HiFWB centroid · projected from primary formulation<extra></extra>'});
    }
    const layout={paper_bgcolor:'#0d0d0d',plot_bgcolor:'#0d0d0d',margin:{l:0,r:0,t:25,b:0},showlegend:true,
      legend:{x:.02,y:.03,font:{family:'Menlo, monospace',color:'#aaa6a0',size:11},bgcolor:'rgba(0,0,0,.2)'},
      hoverlabel:{bgcolor:'#1b1b1b',bordercolor:'#76746e',font:{size:12,color:'#eee'}},uirevision:'trait-pc-view',
      scene:{uirevision:'trait-pc-camera',bgcolor:'rgba(0,0,0,0)',dragmode:'orbit',camera:state.camera,aspectmode:'data',
        xaxis:{title:{text:`Trait PC${state.x+1}`},color:'#aaa6a0',gridcolor:'#3b3b3b',zerolinecolor:'#555'},
        yaxis:{title:{text:`Trait PC${state.y+1}`},color:'#aaa6a0',gridcolor:'#3b3b3b',zerolinecolor:'#555'},
        zaxis:{title:{text:`Trait PC${state.z+1}`},color:'#aaa6a0',gridcolor:'#3b3b3b',zerolinecolor:'#555'}}};
    Plotly.react(plot,traces,layout,{responsive:true,displayModeBar:false,scrollZoom:true}).then(()=>{
      if(!plot._aa15Bound){
        plot._aa15Bound=true;
        plot.on('plotly_hover',e=>{const cd=e.points?.[0]?.customdata;if(cd){state.hovered={kind:cd[0],index:cd[1]};updatePanel();}});
        plot.on('plotly_unhover',()=>{state.hovered=null;updatePanel();});
        plot.on('plotly_click',e=>{const cd=e.points?.[0]?.customdata;if(cd) select({kind:cd[0],index:cd[1]});});
        plot.on('plotly_relayout',e=>{if(e['scene.camera']){state.camera=e['scene.camera'];syncCamera();}});
      }
      $('startup-preview').hidden=true;
      $('render-status').textContent=`${m.label} · 275 personas · 240 traits · 13 HiFWB indicators`;
    });
    updatePanel();
  }
  function select(ref){state.selected=ref;state.hovered=null;render();}
  for(const [id,key] of [['model-select','model'],['x-axis','x'],['y-axis','y'],['z-axis','z'],
    ['layer-select','layer'],['label-select','labels'],['formulation-select','form'],['wellbeing-color','wellbeingColor']])
    $(id).addEventListener('change',()=>{state[key]=['x','y','z'].includes(key)?Number($(id).value):$(id).value;
      if(key==='model'||key==='form'){state.selected=null;state.hovered=null;updatePickers();}render();});
  for(const [id,key] of [['marker-size','size'],['marker-opacity','opacity']])
    $(id).addEventListener('input',()=>{state[key]=key==='opacity'?Number($(id).value)/100:Number($(id).value);render();});
  for(const [id,key] of [['persona-search','searchPersona'],['trait-search','searchTrait'],['indicator-search','searchIndicator']])
    $(id).addEventListener('input',()=>{state[key]=$(id).value.trim().toLowerCase();render();});
  for(const [id,key] of [['indicator-labels','indicatorLabels'],['centroid-toggle','centroid'],['ray-toggle','ray']])
    $(id).addEventListener('change',()=>{state[key]=$(id).checked;render();});
  $('point-picker').addEventListener('change',()=>{const val=$('point-picker').value;if(!val){select(null);return;}
    const [kind,index]=val.split(':');select({kind,index:Number(index)});});
  $('clear-selection').addEventListener('click',()=>select(null));
  $('reset-view').addEventListener('click',()=>{state.camera=TraitCamera.toCamera(TraitCamera.defaults);syncCamera();render();});
  for(const button of document.querySelectorAll('[data-view]')) button.addEventListener('click',()=>{
    const v=button.dataset.view;
    const a=v==='top'?{yaw:0,pitch:90,roll:0,zoom:100}:v==='front'?{yaw:0,pitch:0,roll:0,zoom:100}:
      v==='side'?{yaw:90,pitch:0,roll:0,zoom:100}:TraitCamera.defaults;
    state.camera=TraitCamera.toCamera(a);syncCamera();render();
  });
  for(const key of ['yaw','pitch','roll','zoom']) for(const prefix of ['camera','number'])
    $(`${prefix}-${key}`).addEventListener(prefix==='camera'?'input':'change',()=>{
      const a=TraitCamera.fromCamera(state.camera,Number($('camera-yaw').value));a[key]=Number($(`${prefix}-${key}`).value);
      state.camera=TraitCamera.toCamera(a,state.camera.center);syncCamera();render();
    });
  for(const key of ['x','y','z']){
    const select=$(`${key}-axis`);for(let i=0;i<20;i++)select.add(new Option(`Trait PC${i+1}`,i));select.value=state[key];
  }
  updatePickers();syncCamera();render();
})();
