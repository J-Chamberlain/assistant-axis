/* Qwen/Llama/Gemma category surface explorer. All data are embedded. */
(() => {
  "use strict";
  window.viewerBoot.stage("Reading the prepared persona data");
  if(!window.Plotly || typeof window.Plotly.react!=="function") throw new Error("The embedded chart engine did not load.");
  const data = JSON.parse(document.getElementById("viewer-data").textContent);
  const el = id => document.getElementById(id);
  const plot = el("plot");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const initialCamera = {eye: {x: 1.26, y: 1.29, z: 0.94}, up: {x: 0, y: 0, z: 1}, center: {x: 0, y: 0, z: -0.04}};
  if(window.innerWidth<600) for(const axis of ["x","y","z"]) initialCamera.eye[axis]*=1.35;
  const state = {model: data.default_model, profileSet: data.default_profile_set, x: 0, y: 1, category: 0, smoothing: 1, surface: true, flat: true, flatOnly: false, connectors: true, nodes: true,
    selected: null, hovered: null, camera: structuredClone(initialCamera), transitioning: false};
  let requestVersion = 0, renderedVersion = -1, running = false, initialized = false, previous = null;
  let cameraVersion=0,cameraApplied=0,cameraBusy=false;
  const cameraKeys=["yaw","pitch","roll","zoom"];
  const colors = [[0,"#173d9e"],[0.2,"#198bcc"],[0.4,"#74d9d0"],[0.5,"#f4f1dc"],[0.65,"#ffd04a"],[0.8,"#ef7529"],[1,"#b21932"]];
  const transpose = matrix => matrix[0].map((_, i) => matrix.map(row => row[i]));
  const signed = (v, n=2) => `${v >= 0 ? "+" : ""}${v.toFixed(n)}`;
  const escapeText = text => String(text).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const range = a => { const lo=Math.min(...a), hi=Math.max(...a), pad=(hi-lo)*0.04; return [lo-pad,hi+pad]; };
  const baseModelData = () => data.models[state.model];
  const modelData = () => {
    const base=baseModelData();
    return state.profileSet==="big_five" ? {...base,...base.big_five} : base;
  };

  function snapshot() {
    const model=modelData();
    const lower=Math.min(state.x,state.y), upper=Math.max(state.x,state.y);
    const view=model.views[`${lower}_${upper}`], level=view.levels[state.smoothing];
    const reversed=state.x > state.y, category=model.categories[state.category];
    return {x: reversed?view.y:view.x, y: reversed?view.x:view.y,
      grid: reversed?transpose(level.grids[state.category]):level.grids[state.category],
      flat: reversed?transpose(view.flat_grids[state.category]):view.flat_grids[state.category],
      flatAdherence: level.flat_adherence[state.category], flatPlane: view.flat_plane[state.category],
      fitCenter: reversed?[...view.fit_center].reverse():view.fit_center,
      fitScale: view.fit_common_scale, reversed,
      fitted: level.fitted_nodes[state.category], heights: category.values,
      model: state.model, profileSet: state.profileSet, axisX: state.x, axisY: state.y, category: state.category, smoothing: state.smoothing,
      fitRmse: level.fit_rmse[state.category], support: view.supported_grid_fraction};
  }

  function blend(a,b,t) {
    return {...b, heights: b.heights.map((v,i)=>a.heights[i]+t*(v-a.heights[i])),
      fitted: b.fitted.map((v,i)=>a.fitted[i]+t*(v-a.fitted[i])),
      grid: b.grid.map((row,j)=>row.map((v,i)=>v===null?null:a.grid[j][i]+t*(v-a.grid[j][i]))),
      flat: b.flat.map((row,j)=>row.map((v,i)=>v===null?null:a.flat[j][i]+t*(v-a.flat[j][i])))};
  }

  function weave(s) {
    const x=[],y=[],z=[];
    const add=(i,j)=>{x.push(s.x[i]);y.push(s.y[j]);z.push(s.grid[j][i]===null?null:s.grid[j][i]+0.13);};
    for(let j=0;j<s.y.length;j+=3) {for(let i=0;i<s.x.length;i++) add(i,j);x.push(null);y.push(null);z.push(null);}
    for(let i=0;i<s.x.length;i+=3) {for(let j=0;j<s.y.length;j++) add(i,j);x.push(null);y.push(null);z.push(null);}
    return {x,y,z};
  }

  function extendedPlane(s) {
    const x=range(s.x),y=range(s.y),c=s.flatPlane.coefficients;
    const a=c[s.reversed?2:1]/s.fitScale,b=c[s.reversed?1:2]/s.fitScale;
    const intercept=c[0]-a*s.fitCenter[0]-b*s.fitCenter[1];
    const height=(u,v)=>intercept+a*u+b*v;
    const corners=[[x[0],y[0]],[x[1],y[0]],[x[1],y[1]],[x[0],y[1]]];
    const crossings=[];
    for(let i=0;i<4;i++) {
      const p=corners[i],q=corners[(i+1)%4],hp=height(...p),hq=height(...q);
      if(Math.abs(hp)<1e-10) crossings.push(p);
      if(hp*hq<0) {const t=hp/(hp-hq);crossings.push([p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])]);}
    }
    return {x,y,z:y.map(v=>x.map(u=>height(u,v))),
      intersection:{x:crossings.map(p=>p[0]),y:crossings.map(p=>p[1]),z:crossings.map(()=>0)}};
  }

  function traces(s, transition=false) {
    const model=modelData();
    const plane=extendedPlane(s);
    const category=model.categories[s.category], names=model.roles.map(r=>r.name);
    const xs=model.roles.map(r=>r.pcs[s.axisX]),ys=model.roles.map(r=>r.pcs[s.axisY]);
    const lines={x:[],y:[],z:[]};
    for(let i=0;i<names.length;i++) if(Math.abs(s.fitted[i]-s.heights[i])>0.03) {
      lines.x.push(xs[i],xs[i],null);lines.y.push(ys[i],ys[i],null);lines.z.push(s.heights[i],s.fitted[i],null);
    }
    const selected=state.selected===null?[]:[state.selected];
    const rawScores=category.raw_score||category.mean_z;
    const custom=model.roles.map((r,i)=>[escapeText(r.name),category.values[i],rawScores[i],i,state.model,state.profileSet]);
    const scoreDetail=state.profileSet==="big_five" ? "Raw composite projection" : "Mean member z";
    return [
      {type:"surface",name:"Zero reference",visible:true,x:plane.x,y:plane.y,z:[[0,0],[0,0]],
        colorscale:[[0,"#6eb5ca"],[1,"#6eb5ca"]],opacity:0.3,showscale:false,hoverinfo:"skip"},
      {type:"surface",name:"Fitted fabric",x:s.x,y:s.y,z:s.grid,connectgaps:false,visible:state.surface&&!state.flatOnly,
        colorscale:colors,cmin:0,cmax:100,showscale:true,colorbar:{title:{text:state.profileSet==="big_five"?"Big Five<br>percentile":"Mean trait<br>percentile"},tickvals:[0,25,50,75,100],thickness:12,len:0.55,x:0.94,tickfont:{size:10}},opacity:1,hoverinfo:"skip",
        lighting:{ambient:0.88,diffuse:0.35,specular:0.05,roughness:0.93,fresnel:0.1},
        lightposition:{x:100,y:100,z:200},contours:{z:{show:false}}},
      {type:"scatter3d",name:"Fabric weave",mode:"lines",...weave(s),visible:state.surface&&!state.flatOnly,
        line:{color:"rgba(47,48,45,0.36)",width:1},hoverinfo:"skip",connectgaps:false},
      {type:"scatter3d",name:"Node-to-fabric gaps",mode:"lines",...lines,
        visible:state.surface&&state.connectors&&state.nodes&&!state.flatOnly,line:{color:"rgba(225,218,201,0.42)",width:1},hoverinfo:"skip",connectgaps:false},
      {type:"scatter3d",name:"Persona nodes",mode:"markers",x:xs,y:ys,z:s.heights,visible:state.nodes&&!state.flatOnly,
        marker:{size:3.3,color:"#fff5df",opacity:1,line:{color:"#242424",width:0.6}},customdata:custom,
        hoverinfo:transition?"skip":undefined,
        hovertemplate:transition?undefined:`<b>%{customdata[0]}</b><br>${category.label}: %{customdata[1]:.1f}/100<br>`+
          `${scoreDetail}: %{customdata[2]:+.4f}<br>`+
          `PC${s.axisX+1}: %{x:.2f} | PC${s.axisY+1}: %{y:.2f}<extra></extra>`},
      {type:"scatter3d",name:"Pinned persona",mode:"markers+text",visible:state.nodes&&!state.flatOnly,x:selected.map(i=>xs[i]),y:selected.map(i=>ys[i]),
        z:selected.map(i=>s.heights[i]),text:selected.map(i=>escapeText(names[i])),textposition:"top center",
        textfont:{size:12,color:"#e8e8e8"},marker:{size:6,color:"#78c6e8",line:{color:"#09202c",width:1}},
        customdata:selected.map(i=>custom[i]),hoverinfo:"skip"},
      {type:"surface",name:"Best-fit flat plane",x:plane.x,y:plane.y,z:plane.z,connectgaps:false,
        visible:state.flat||state.flatOnly,colorscale:[[0,"#f5edd7"],[1,"#f5edd7"]],showscale:false,opacity:0.38,hoverinfo:"skip",
        lighting:{ambient:0.9,diffuse:0.25,specular:0.05,roughness:0.98,fresnel:0.05},
        lightposition:{x:100,y:100,z:200},contours:{z:{show:false}}},
      {type:"scatter3d",name:"Plane / zero intersection",mode:"lines",...plane.intersection,
        visible:state.flat||state.flatOnly,line:{color:"#ffffff",width:6},hoverinfo:"skip"}
    ];
  }

  function layout(s) {
    const planeHeights=extendedPlane(s).z.flat();
    const zRange=state.flat||state.flatOnly?[Math.min(-5,...planeHeights)-3,Math.max(100,...planeHeights)+3]:[-5,100];
    const xRange=range(s.x),yRange=range(s.y),longest=Math.max(xRange[1]-xRange[0],yRange[1]-yRange[0]);
    const axis={color:"#aaa6a0",gridcolor:"#303033",zerolinecolor:"#55555a",showbackground:false,
      tickfont:{size:11},nticks:5,showspikes:false};
    return {paper_bgcolor:"rgba(0,0,0,0)",plot_bgcolor:"rgba(0,0,0,0)",showlegend:false,
      margin:{l:10,r:45,t:55,b:15},font:{family:'Menlo, Consolas, monospace',color:"#e8e8e8"},
      uirevision:"category-landscape",hoverlabel:{bgcolor:"#1b1b1b",bordercolor:"#76746e",font:{size:12,color:"#eee"}},
      scene:{uirevision:"category-landscape-camera",bgcolor:"rgba(0,0,0,0)",dragmode:"orbit",camera:state.camera,
        aspectmode:"manual",aspectratio:{x:1.25*(xRange[1]-xRange[0])/longest,y:1.25*(yRange[1]-yRange[0])/longest,z:0.75},
        xaxis:{...axis,title:{text:`PC${s.axisX+1}`},range:xRange},yaxis:{...axis,title:{text:`PC${s.axisY+1}`},range:yRange},
        zaxis:{...axis,title:{text:state.profileSet==="big_five"?"Big Five score percentile":"Mean trait percentile",font:{size:11}},range:zRange,nticks:5}}};
  }

  function updatePanel() {
    const model=modelData();
    const i=state.selected===null?state.hovered:state.selected, s=snapshot();
    const category=model.categories[state.category];
    el("member-scores").replaceChildren();
    category.members.forEach(member=>{
      const row=document.createElement("div"),name=document.createElement("span"),value=document.createElement("span");
      if(state.profileSet==="big_five") {
        name.textContent=`${member.polarity==="negative"?"−":"+"} ${member.trait.replaceAll("_"," ")}`;
        value.textContent=member.facet||member.tier||"";
      } else {
        name.textContent=member.label;value.textContent=i===null?"--":`${member.percentile[i].toFixed(1)} / 100`;
      }
      row.append(name,value);el("member-scores").appendChild(row);
    });
    el("selected-x-label").textContent=`PC${state.x+1}`;el("selected-y-label").textContent=`PC${state.y+1}`;
    el("clear-selection").hidden=state.selected===null;
    el("flat-score").textContent=s.flatAdherence.fabric_flat_score===null?"--":`${s.flatAdherence.fabric_flat_score.toFixed(1)} / 100`;
    el("flat-rmse").textContent=s.flatAdherence.fabric_flat_rmse===null?"--":`${s.flatAdherence.fabric_flat_rmse.toFixed(2)} points`;
    el("flat-plane-r2").textContent=s.flatPlane.node_r2===null?"--":s.flatPlane.node_r2.toFixed(3);
    el("surface-fit-note").textContent=`Fabric fit gap: ${s.fitRmse.toFixed(2)} percentile points RMS. Rolling fabric gap from flat plane: ${s.flatAdherence.fabric_flat_rmse.toFixed(2)} RMS. Flat adherence is descriptive, not predictive validation.`;
    if(i===null) {
      el("selected-name").textContent="Explore the fabric";el("selection-kind").textContent="Hover a node or choose a name";
      for(const id of ["selected-score","selected-percentile","selected-raw","selected-x","selected-y","selected-gap"]) el(id).textContent="--";
      return;
    }
    const role=model.roles[i];
    el("selected-name").textContent=role.name.replaceAll("_"," ");
    el("selection-kind").textContent=state.selected===null?"Hover preview":"Pinned persona";
    el("selected-score").textContent=category.values[i].toFixed(1);
    el("selected-percentile").textContent=state.profileSet==="big_five"?model.construction_label:"3 equally weighted traits";
    el("selected-raw").textContent=state.profileSet==="big_five"?signed(category.raw_score[i],4):signed(category.mean_z[i]);
    el("selected-x").textContent=role.pcs[state.x].toFixed(2);el("selected-y").textContent=role.pcs[state.y].toFixed(2);
    el("selected-gap").textContent=`${signed(category.values[i]-s.fitted[i])} points`;
  }

  function updateControls() {
    const model=modelData();
    for(const [id,other] of [["x-axis",state.y],["y-axis",state.x]])
      [...el(id).options].forEach(option=>option.disabled=Number(option.value)===other);
    el("model-select").value=state.model;
    el("profile-set-select").value=state.profileSet;
    el("active-model-name").textContent=model.short_label;
    el("active-profile-name").textContent=state.profileSet==="big_five"?"Big Five":"editorial groups";
    el("model-provenance").textContent=model.coordinate_source==="canonical_geometry_viz_data" ?
      "Canonical Qwen coordinates / exact saved Qwen cosines" :
      `${model.short_label} own-vector PCA / signs oriented to Qwen reference`;
    el("plot-category").textContent=model.categories[state.category].label;
    el("category-current").textContent=model.categories[state.category].label;
    el("plane-caption").textContent=`${model.short_label} | PC${state.x+1} / PC${state.y+1} | height = within-model ${state.profileSet==="big_five"?"Big Five score":"mean trait"} percentile`;
    el("group-label").textContent=state.profileSet==="big_five"?"Big Five domain":"Trait group";
    el("score-label").textContent=state.profileSet==="big_five"?"Big Five score percentile / 100":"mean trait percentile / 100";
    el("raw-label").textContent=state.profileSet==="big_five"?"Raw composite projection":"Mean member z";
    el("profile-note").textContent=state.profileSet==="big_five"?
      "Big Five domains use the frozen human-anchored strict construction. Percentiles are within-model ranks; external anchoring is not independent psychometric validation.":
      "50 is the selected model's population mean for each editorial group. Higher means higher average within-model percentile, not a probability.";
    el("show-flat").checked=state.flat;el("show-flat-only").checked=state.flatOnly;
    el("show-flat").disabled=state.flatOnly;el("show-surface").disabled=state.flatOnly;
    el("show-nodes").disabled=state.flatOnly;
    el("show-connectors").disabled=state.flatOnly||!state.nodes||!state.surface;
    el("category-slider").value=state.category;
    el("category-slider").setAttribute("aria-valuetext",model.categories[state.category].label);
    [...el("category-stops").children].forEach((button,i)=>button.setAttribute("aria-pressed",String(i===state.category)));
    updatePanel();
  }

  function rebuildCategoryStops() {
    el("category-stops").replaceChildren();
    modelData().categories.forEach((category,i)=>{const button=document.createElement("button");button.type="button";button.textContent=category.label;
      button.setAttribute("aria-pressed",String(i===state.category));button.addEventListener("click",()=>{state.category=i;scheduleRender();});el("category-stops").appendChild(button);});
  }

  function fail(error) {
    console.error(error);window.viewerBoot.fail(error);
  }

  function captureCamera() {
    if(cameraBusy||running||cameraVersion!==cameraApplied) return;
    // Plotly 3.5 can emit a wheel relayout before the GL camera finishes zooming.
    const live=plot._fullLayout?.scene?._scene?.getCamera?.();
    if(live) {state.camera=structuredClone(live);syncCameraControls();}
  }

  function syncCameraControls() {
    const angles=TraitCamera.fromCamera(state.camera,Number(el("camera-yaw").value));
    for(const key of cameraKeys) {
      const value=Number(angles[key].toFixed(1));
      el(`camera-${key}`).value=value;el(`number-${key}`).value=value;
      el(`camera-${key}`).setAttribute("aria-valuetext",`${value}${key==="zoom"?" percent":" degrees"}`);
      el(`dial-${key}`).style.transform=`rotate(${key==="zoom"?(value-100)*.8:value}deg)`;
    }
  }

  async function flushCamera() {
    if(!initialized||running||cameraBusy||cameraApplied===cameraVersion) return;
    cameraBusy=true;
    try {
      while(cameraApplied!==cameraVersion) {
        const version=cameraVersion;
        await Plotly.relayout(plot,{"scene.camera":structuredClone(state.camera)});
        cameraApplied=version;
      }
    } catch(error) {fail(error);} finally {
      cameraBusy=false;
      if(renderedVersion!==requestVersion) scheduleRender();
    }
  }

  function requestCamera(camera) {
    state.camera=structuredClone(camera);cameraVersion++;syncCameraControls();
    requestAnimationFrame(flushCamera);
  }

  function bindPlotEvents() {
    const pin = i => {
      if(!state.nodes || state.transitioning || i===null || state.selected===i) return;
      state.selected=i;el("persona-picker").value=i;scheduleRender();
    };
    // Some WebGL/browser combinations report hover but omit plotly_click.
    // Use that same picked node only when the pointer gesture was not a drag.
    let gesture=null;
    plot.addEventListener("pointerdown",e=>{gesture={x:e.clientX,y:e.clientY,dragged:false};});
    plot.addEventListener("pointermove",e=>{
      if(gesture && Math.hypot(e.clientX-gesture.x,e.clientY-gesture.y)>4) gesture.dragged=true;
    });
    plot.addEventListener("pointercancel",()=>{gesture=null;});
    plot.addEventListener("click",()=>{
      if(gesture && !gesture.dragged) pin(state.hovered);
      gesture=null;
    });
    plot.addEventListener("wheel",()=>{
      requestAnimationFrame(captureCamera);
      setTimeout(captureCamera,150);
    },{passive:true});
    plot.on("plotly_relayout", event=>{
      if(!cameraBusy&&!running&&cameraVersion===cameraApplied&&event["scene.camera"]) {
        state.camera=structuredClone(event["scene.camera"]);syncCameraControls();
      }
    });
    plot.on("plotly_hover", event=>{
      if(!state.nodes||state.transitioning) return;
      const p=event.points?.find(p=>p.curveNumber===4);if(!p) return;
      state.hovered=p.customdata[3];updatePanel();
    });
    plot.on("plotly_unhover",()=>{state.hovered=null;updatePanel();});
    plot.on("plotly_click", event=>{
      if(state.transitioning) return;
      const p=event.points?.find(p=>p.curveNumber===4||p.curveNumber===5);if(!p) return;
      pin(p.customdata[3]);
    });
    plot.on("plotly_webglcontextlost",()=>fail(new Error("WebGL context was lost; reload the local viewer.")));
  }

  async function scheduleRender() {
    if(initialized&&!running) captureCamera();
    requestVersion++;updateControls();
    if(running||cameraBusy) return;
    running=true;
    try {
      while(renderedVersion!==requestVersion) {
        const version=requestVersion,target=snapshot();
        const animate=initialized&&!reducedMotion.matches&&previous&&previous.model===target.model&&previous.profileSet===target.profileSet&&previous.category!==target.category&&
          previous.axisX===target.axisX&&previous.axisY===target.axisY&&previous.smoothing===target.smoothing;
        state.transitioning=Boolean(animate);
        if(!initialized) window.viewerBoot.stage("Rendering the prepared 3D landscape");
        else el("render-status").textContent=animate?"Visual transition...":"Updating...";
        const started=performance.now();
        const steps=animate?[0.5,1]:[1];
        for(const t of steps) {
          if(version!==requestVersion) break;
          const current=t===1?target:blend(previous,target,t);
          await Plotly.react(plot,traces(current,t!==1),layout(current),{responsive:true,displayModeBar:false,scrollZoom:true});
          if(!initialized) {bindPlotEvents();initialized=true;window.viewerBoot.ready();}
          if(t!==1) await new Promise(resolve=>requestAnimationFrame(resolve));
        }
        previous=target;renderedVersion=version;state.transitioning=false;
        if(version===requestVersion) {
          el("render-status").textContent=`${modelData().short_label} | 275 personas | use dials or drag`;
          window.__traitViewer.lastRenderMilliseconds=performance.now()-started;
        }
      }
    } catch(error) {fail(error);} finally {running=false;state.transitioning=false;flushCamera();}
  }

  data.models[data.default_model].roles.forEach((role,i)=>{const option=document.createElement("option");option.value=i;option.textContent=role.name.replaceAll("_"," ");el("persona-picker").appendChild(option);});
  rebuildCategoryStops();
  el("model-select").addEventListener("change",()=>{
    const old=modelData(),selectedName=state.selected===null?null:old.roles[state.selected].name;
    state.model=el("model-select").value;state.hovered=null;previous=null;
    state.selected=selectedName===null?null:modelData().roles.findIndex(role=>role.name===selectedName);
    if(state.selected<0)state.selected=null;
    el("persona-picker").value=state.selected===null?"":state.selected;
    scheduleRender();
  });
  el("profile-set-select").addEventListener("change",()=>{
    const old=modelData(),selectedName=state.selected===null?null:old.roles[state.selected].name;
    state.profileSet=el("profile-set-select").value;state.category=0;state.hovered=null;previous=null;
    state.selected=selectedName===null?null:modelData().roles.findIndex(role=>role.name===selectedName);
    if(state.selected<0)state.selected=null;
    el("persona-picker").value=state.selected===null?"":state.selected;
    rebuildCategoryStops();scheduleRender();
  });
  el("category-slider").addEventListener("input",()=>{state.category=Number(el("category-slider").value);scheduleRender();});
  for(const [id,key] of [["x-axis","x"],["y-axis","y"],["smoothing","smoothing"]])
    el(id).addEventListener("change",()=>{state[key]=Number(el(id).value);scheduleRender();});
  for(const [id,key] of [["show-surface","surface"],["show-flat","flat"],["show-connectors","connectors"],["show-nodes","nodes"]])
    el(id).addEventListener("change",()=>{state[key]=el(id).checked;if(!state.nodes) state.hovered=null;scheduleRender();});
  el("show-flat-only").addEventListener("change",()=>{state.flatOnly=el("show-flat-only").checked;if(state.flatOnly) state.flat=true;scheduleRender();});
  el("persona-picker").addEventListener("change",()=>{state.selected=el("persona-picker").value===""?null:Number(el("persona-picker").value);scheduleRender();});
  el("clear-selection").addEventListener("click",()=>{state.selected=null;state.hovered=null;el("persona-picker").value="";scheduleRender();});
  for(const key of cameraKeys) for(const prefix of ["camera","number"]) {
    const input=el(`${prefix}-${key}`);
    input.addEventListener(prefix==="camera"?"input":"change",()=>{
      if(input.value.trim()===""||!Number.isFinite(Number(input.value))) {syncCameraControls();return;}
      const angles=TraitCamera.fromCamera(state.camera,Number(el("camera-yaw").value));
      angles[key]=Math.max(Number(input.min),Math.min(Number(input.max),Number(input.value)));
      requestCamera(TraitCamera.toCamera(angles,state.camera.center));
    });
  }
  document.querySelectorAll("[data-view]").forEach(button=>button.addEventListener("click",()=>{
    const views={iso:TraitCamera.defaults,top:{yaw:-90,pitch:90,roll:0,zoom:100},
      front:{yaw:-90,pitch:0,roll:0,zoom:100},side:{yaw:0,pitch:0,roll:0,zoom:100}};
    requestCamera(TraitCamera.toCamera(views[button.dataset.view]));
  }));
  el("reset-view").addEventListener("click",()=>{
    const selectedName=state.selected===null?null:modelData().roles[state.selected].name;
    state.model=data.default_model;state.profileSet=data.default_profile_set;state.category=0;state.hovered=null;previous=null;
    state.selected=selectedName===null?null:modelData().roles.findIndex(role=>role.name===selectedName);
    el("persona-picker").value=state.selected===null?"":state.selected;
    rebuildCategoryStops();requestCamera(initialCamera);scheduleRender();
  });
  window.__traitViewer={data,state,snapshot,modelData,get selectedPersona(){return state.selected===null?null:modelData().roles[state.selected].name;},get ready(){return initialized&&!running&&!cameraBusy&&cameraVersion===cameraApplied;},get rendering(){return running;},lastRenderMilliseconds:null};
  syncCameraControls();
  scheduleRender();
})();
