/* Qwen emotion surface explorer. All data are embedded; no network requests. */
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
  const state = {x: 0, y: 1, emotion: 0, smoothing: 1, surface: true, connectors: true, nodes: true,
    selected: null, hovered: null, camera: structuredClone(initialCamera), transitioning: false};
  let requestVersion = 0, renderedVersion = -1, running = false, initialized = false, previous = null;
  let cameraVersion=0,cameraApplied=0,cameraBusy=false;
  const cameraKeys=["yaw","pitch","roll","zoom"];
  const colors = [[0,"#173d9e"],[0.2,"#198bcc"],[0.4,"#74d9d0"],[0.5,"#f4f1dc"],[0.65,"#ffd04a"],[0.8,"#ef7529"],[1,"#b21932"]];
  const transpose = matrix => matrix[0].map((_, i) => matrix.map(row => row[i]));
  const signed = (v, n=2) => `${v >= 0 ? "+" : ""}${v.toFixed(n)}`;
  const escapeText = text => String(text).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const range = a => { const lo=Math.min(...a), hi=Math.max(...a), pad=(hi-lo)*0.04; return [lo-pad,hi+pad]; };

  function snapshot() {
    const lower=Math.min(state.x,state.y), upper=Math.max(state.x,state.y);
    const view=data.views[`${lower}_${upper}`], level=view.levels[state.smoothing];
    const reversed=state.x > state.y, emotion=data.emotions[state.emotion];
    return {x: reversed?view.y:view.x, y: reversed?view.x:view.y,
      grid: reversed?transpose(level.grids[state.emotion]):level.grids[state.emotion],
      fitted: level.fitted_nodes[state.emotion], heights: emotion.z,
      axisX: state.x, axisY: state.y, emotion: state.emotion, smoothing: state.smoothing,
      fitRmse: level.fit_rmse[state.emotion], support: view.supported_grid_fraction};
  }

  function blend(a,b,t) {
    return {...b, heights: b.heights.map((v,i)=>a.heights[i]+t*(v-a.heights[i])),
      fitted: b.fitted.map((v,i)=>a.fitted[i]+t*(v-a.fitted[i])),
      grid: b.grid.map((row,j)=>row.map((v,i)=>v===null?null:a.grid[j][i]+t*(v-a.grid[j][i])))};
  }

  function weave(s) {
    const x=[],y=[],z=[];
    const add=(i,j)=>{x.push(s.x[i]);y.push(s.y[j]);z.push(s.grid[j][i]===null?null:s.grid[j][i]+0.006);};
    for(let j=0;j<s.y.length;j+=3) {for(let i=0;i<s.x.length;i++) add(i,j);x.push(null);y.push(null);z.push(null);}
    for(let i=0;i<s.x.length;i+=3) {for(let j=0;j<s.y.length;j++) add(i,j);x.push(null);y.push(null);z.push(null);}
    return {x,y,z};
  }

  function traces(s, transition=false) {
    const emotion=data.emotions[s.emotion], names=data.roles.map(r=>r.name);
    const xs=data.roles.map(r=>r.pcs[s.axisX]),ys=data.roles.map(r=>r.pcs[s.axisY]);
    const lines={x:[],y:[],z:[]};
    for(let i=0;i<names.length;i++) if(Math.abs(s.fitted[i]-s.heights[i])>0.03) {
      lines.x.push(xs[i],xs[i],null);lines.y.push(ys[i],ys[i],null);lines.z.push(s.heights[i],s.fitted[i],null);
    }
    const selected=state.selected===null?[]:[state.selected];
    const custom=data.roles.map((r,i)=>[escapeText(r.name),emotion.z[i],emotion.percentile[i],emotion.raw[i],i]);
    return [
      {type:"surface",name:"Zero reference",visible:state.nodes,x:[s.x[0],s.x.at(-1)],y:[s.y[0],s.y.at(-1)],z:[[0,0],[0,0]],
        colorscale:[[0,"#777777"],[1,"#777777"]],opacity:0.055,showscale:false,hoverinfo:"skip"},
      {type:"surface",name:"Fitted fabric",x:s.x,y:s.y,z:s.grid,connectgaps:false,visible:state.surface,
        colorscale:colors,cmin:-data.z_limit,cmax:data.z_limit,showscale:true,colorbar:{title:{text:"Affinity<br>z-score"},tickvals:[-data.z_limit,0,data.z_limit],thickness:12,len:0.55,x:0.94,tickfont:{size:10}},opacity:1,hoverinfo:"skip",
        lighting:{ambient:0.88,diffuse:0.35,specular:0.05,roughness:0.93,fresnel:0.1},
        lightposition:{x:100,y:100,z:200},contours:{z:{show:false}}},
      {type:"scatter3d",name:"Fabric weave",mode:"lines",...weave(s),visible:state.surface,
        line:{color:"rgba(47,48,45,0.36)",width:1},hoverinfo:"skip",connectgaps:false},
      {type:"scatter3d",name:"Node-to-fabric gaps",mode:"lines",...lines,
        visible:state.surface&&state.connectors&&state.nodes,line:{color:"rgba(225,218,201,0.42)",width:1},hoverinfo:"skip",connectgaps:false},
      {type:"scatter3d",name:"Persona nodes",mode:"markers",x:xs,y:ys,z:s.heights,visible:state.nodes,
        marker:{size:3.3,color:"#fff5df",opacity:1,line:{color:"#242424",width:0.6}},customdata:custom,
        hoverinfo:transition?"skip":undefined,
        hovertemplate:transition?undefined:`<b>%{customdata[0]}</b><br>${emotion.label}: %{customdata[1]:+.2f} SD<br>`+
          `Percentile: %{customdata[2]:.1f}<br>Raw cosine: %{customdata[3]:.5f}<br>`+
          `PC${s.axisX+1}: %{x:.2f} | PC${s.axisY+1}: %{y:.2f}<extra></extra>`},
      {type:"scatter3d",name:"Pinned persona",mode:"markers+text",visible:state.nodes,x:selected.map(i=>xs[i]),y:selected.map(i=>ys[i]),
        z:selected.map(i=>s.heights[i]),text:selected.map(i=>escapeText(names[i])),textposition:"top center",
        textfont:{size:12,color:"#e8e8e8"},marker:{size:6,color:"#78c6e8",line:{color:"#09202c",width:1}},
        customdata:selected.map(i=>custom[i]),hoverinfo:"skip"}
    ];
  }

  function layout(s) {
    const xRange=range(s.x),yRange=range(s.y),longest=Math.max(xRange[1]-xRange[0],yRange[1]-yRange[0]);
    const axis={color:"#aaa6a0",gridcolor:"#303033",zerolinecolor:"#55555a",showbackground:false,
      tickfont:{size:11},nticks:5,showspikes:false};
    return {paper_bgcolor:"rgba(0,0,0,0)",plot_bgcolor:"rgba(0,0,0,0)",showlegend:false,
      margin:{l:10,r:45,t:48,b:15},font:{family:'Menlo, Consolas, monospace',color:"#e8e8e8"},
      uirevision:"emotion-landscape",hoverlabel:{bgcolor:"#1b1b1b",bordercolor:"#76746e",font:{size:12,color:"#eee"}},
      scene:{uirevision:"emotion-landscape-camera",bgcolor:"rgba(0,0,0,0)",dragmode:"orbit",camera:state.camera,
        aspectmode:"manual",aspectratio:{x:1.25*(xRange[1]-xRange[0])/longest,y:1.25*(yRange[1]-yRange[0])/longest,z:0.75},
        xaxis:{...axis,title:{text:`PC${s.axisX+1}`},range:xRange},yaxis:{...axis,title:{text:`PC${s.axisY+1}`},range:yRange},
        zaxis:{...axis,title:{text:"Affinity (SD)",font:{size:11}},range:[-data.z_limit,data.z_limit],nticks:5}}};
  }

  function updatePanel() {
    const i=state.selected===null?state.hovered:state.selected, s=snapshot();
    el("selected-x-label").textContent=`PC${state.x+1}`;el("selected-y-label").textContent=`PC${state.y+1}`;
    el("clear-selection").hidden=state.selected===null;
    el("surface-fit-note").textContent=`Fabric fit gap: ${s.fitRmse.toFixed(2)} SD RMS. Smoothing changes the fabric, never the nodes.`;
    if(i===null) {
      el("selected-name").textContent="Explore the fabric";el("selection-kind").textContent="Hover a node or choose a name";
      for(const id of ["selected-score","selected-percentile","selected-raw","selected-x","selected-y","selected-gap"]) el(id).textContent="--";
      return;
    }
    const emotion=data.emotions[state.emotion],role=data.roles[i];
    el("selected-name").textContent=role.name.replaceAll("_"," ");
    el("selection-kind").textContent=state.selected===null?"Hover preview":"Pinned persona";
    el("selected-score").textContent=signed(emotion.z[i]);
    el("selected-percentile").textContent=`${emotion.percentile[i].toFixed(1)} / 100`;
    el("selected-raw").textContent=emotion.raw[i].toFixed(5);
    el("selected-x").textContent=role.pcs[state.x].toFixed(2);el("selected-y").textContent=role.pcs[state.y].toFixed(2);
    el("selected-gap").textContent=`${signed(emotion.z[i]-s.fitted[i])} SD`;
  }

  function updateControls() {
    for(const [id,other] of [["x-axis",state.y],["y-axis",state.x]])
      [...el(id).options].forEach(option=>option.disabled=Number(option.value)===other);
    el("plot-emotion").textContent=data.emotions[state.emotion].label;
    el("emotion-current").textContent=data.emotions[state.emotion].label;
    el("plane-caption").textContent=`PC${state.x+1} / PC${state.y+1} | height = relative affinity`;
    el("show-connectors").disabled=!state.nodes||!state.surface;
    el("emotion-slider").value=state.emotion;
    el("emotion-slider").setAttribute("aria-valuetext",data.emotions[state.emotion].label);
    [...el("emotion-stops").children].forEach((button,i)=>button.setAttribute("aria-pressed",String(i===state.emotion)));
    updatePanel();
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
    const angles=EmotionCamera.fromCamera(state.camera,Number(el("camera-yaw").value));
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
      state.hovered=p.customdata[4];updatePanel();
    });
    plot.on("plotly_unhover",()=>{state.hovered=null;updatePanel();});
    plot.on("plotly_click", event=>{
      if(state.transitioning) return;
      const p=event.points?.find(p=>p.curveNumber===4||p.curveNumber===5);if(!p) return;
      pin(p.customdata[4]);
    });
    plot.on("plotly_webglcontextlost",()=>fail(new Error("WebGL context was lost; reload the local viewer.")));
  }

  async function scheduleRender() {
    if(initialized&&!running) captureCamera();
    requestVersion++;updateControls();
    if(running) return;
    running=true;
    try {
      while(renderedVersion!==requestVersion) {
        const version=requestVersion,target=snapshot();
        const animate=initialized&&!reducedMotion.matches&&previous&&previous.emotion!==target.emotion&&
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
          el("render-status").textContent="275 personas | use dials or drag";
          window.__emotionViewer.lastRenderMilliseconds=performance.now()-started;
        }
      }
    } catch(error) {fail(error);} finally {running=false;state.transitioning=false;flushCamera();}
  }

  data.roles.forEach((role,i)=>{const option=document.createElement("option");option.value=i;option.textContent=role.name.replaceAll("_"," ");el("persona-picker").appendChild(option);});
  data.emotions.forEach((emotion,i)=>{const button=document.createElement("button");button.type="button";button.textContent=emotion.label;
    button.setAttribute("aria-pressed",String(i===0));button.addEventListener("click",()=>{state.emotion=i;scheduleRender();});el("emotion-stops").appendChild(button);});
  el("emotion-slider").addEventListener("input",()=>{state.emotion=Number(el("emotion-slider").value);scheduleRender();});
  for(const [id,key] of [["x-axis","x"],["y-axis","y"],["smoothing","smoothing"]])
    el(id).addEventListener("change",()=>{state[key]=Number(el(id).value);scheduleRender();});
  for(const [id,key] of [["show-surface","surface"],["show-connectors","connectors"],["show-nodes","nodes"]])
    el(id).addEventListener("change",()=>{state[key]=el(id).checked;if(!state.nodes) state.hovered=null;scheduleRender();});
  el("persona-picker").addEventListener("change",()=>{state.selected=el("persona-picker").value===""?null:Number(el("persona-picker").value);scheduleRender();});
  el("clear-selection").addEventListener("click",()=>{state.selected=null;state.hovered=null;el("persona-picker").value="";scheduleRender();});
  for(const key of cameraKeys) for(const prefix of ["camera","number"]) {
    const input=el(`${prefix}-${key}`);
    input.addEventListener(prefix==="camera"?"input":"change",()=>{
      if(input.value.trim()===""||!Number.isFinite(Number(input.value))) {syncCameraControls();return;}
      const angles=EmotionCamera.fromCamera(state.camera,Number(el("camera-yaw").value));
      angles[key]=Math.max(Number(input.min),Math.min(Number(input.max),Number(input.value)));
      requestCamera(EmotionCamera.toCamera(angles,state.camera.center));
    });
  }
  document.querySelectorAll("[data-view]").forEach(button=>button.addEventListener("click",()=>{
    const views={iso:EmotionCamera.defaults,top:{yaw:-90,pitch:90,roll:0,zoom:100},
      front:{yaw:-90,pitch:0,roll:0,zoom:100},side:{yaw:0,pitch:0,roll:0,zoom:100}};
    requestCamera(EmotionCamera.toCamera(views[button.dataset.view]));
  }));
  el("reset-view").addEventListener("click",()=>requestCamera(initialCamera));
  window.__emotionViewer={data,state,snapshot,get ready(){return initialized&&!running&&!cameraBusy&&cameraVersion===cameraApplied;},get rendering(){return running;},lastRenderMilliseconds:null};
  syncCameraControls();
  scheduleRender();
})();
