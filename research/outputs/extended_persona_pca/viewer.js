(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const svg = $("plot");
  const NS = "http://www.w3.org/2000/svg";
  const colors = VIEWER_DATA.metadata.cluster_colors;
  const defaults = {model:"qwen",mode:"2d",x:1,y:2,z:3,fixed:true,yaw:35,pitch:22,zoom:100,selectedPersona:"assistant"};
  let state = {...defaults};
  try { state = {...state,...JSON.parse(localStorage.getItem("extendedPersonaPcaState") || "{}")}; } catch (_) {}
  const save = () => localStorage.setItem("extendedPersonaPcaState", JSON.stringify(state));
  const node = (tag, attrs={}) => { const n=document.createElementNS(NS,tag); Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,String(v))); return n; };
  const fmt = x => Number(x).toLocaleString(undefined,{maximumFractionDigits:3});
  const pcOptions = () => Array.from({length:10},(_,i)=>`<option value="${i+1}">PC${i+1}</option>`).join("");
  $("pc-x").innerHTML=pcOptions(); $("pc-y").innerHTML=pcOptions(); $("pc-z").innerHTML=pcOptions();
  $("model").innerHTML=Object.entries(VIEWER_DATA.models).map(([k,v])=>`<option value="${k}">${v.label}</option>`).join("");
  const syncControls = () => {
    $("model").value=state.model; $("mode").value=state.mode; $("pc-x").value=state.x; $("pc-y").value=state.y; $("pc-z").value=state.z;
    $("fixed").checked=state.fixed; $("yaw").value=state.yaw; $("pitch").value=state.pitch; $("zoom").value=state.zoom;
    document.querySelectorAll(".mode-3d-only,.pc-z-wrap").forEach(el=>el.classList.toggle("hidden",state.mode!=="3d"));
  };
  const enforceDistinct = changed => {
    const axes=[state.x,state.y,state.z];
    if (state.x===state.y) state[changed==="x"?"y":"x"]=(state[changed]%10)+1;
    if (state.mode==="3d") {
      if (state.z===state.x || state.z===state.y) state.z=Array.from({length:10},(_,i)=>i+1).find(v=>v!==state.x&&v!==state.y);
    }
  };
  const extent = (values,fixed) => {
    const lo=Math.min(...values), hi=Math.max(...values);
    if (fixed) { const m=Math.max(Math.abs(lo),Math.abs(hi))||1; return [-m,m]; }
    const pad=(hi-lo||1)*.06; return [lo-pad,hi+pad];
  };
  const scale = (value,[lo,hi],a,b) => a+(value-lo)/(hi-lo)*(b-a);
  const rotate = (x,y,z) => {
    const yaw=state.yaw*Math.PI/180, pitch=state.pitch*Math.PI/180;
    const x1=x*Math.cos(yaw)-z*Math.sin(yaw), z1=x*Math.sin(yaw)+z*Math.cos(yaw);
    const y1=y*Math.cos(pitch)-z1*Math.sin(pitch), z2=y*Math.sin(pitch)+z1*Math.cos(pitch);
    return [x1,y1,z2];
  };
  const axisDiagnostic = (model,pc) => {
    const d=model.diagnostics[pc-1];
    return `<div class="diag"><div class="status">PC${pc}: ${d.retention_status}</div>`+
      `<div class="metric"><span>Explained</span><span>${(100*d.explained_variance_ratio).toFixed(3)}%</span></div>`+
      `<div class="metric"><span>Cumulative</span><span>${(100*d.cumulative_explained_variance).toFixed(3)}%</span></div>`+
      `<div class="metric"><span>Parallel analysis</span><span>${d.parallel_retain?"retain":"do not retain"}</span></div>`+
      `<div class="metric"><span>Bootstrap cosine</span><span>${d.bootstrap_median_loading_cosine?.toFixed(3) ?? "n/a"}</span></div></div>`;
  };
  const showDetails = point => {
    if (!point) { $("details").textContent="Select a role point."; return; }
    const axes=state.mode==="3d"?[state.x,state.y,state.z]:[state.x,state.y];
    $("details").innerHTML=`<strong>${point.persona}</strong><br><span style="color:${colors[point.cluster]}">${point.cluster.replaceAll("_"," ")}</span>`+
      axes.map(pc=>`<div class="metric"><span>PC${pc}</span><span>${fmt(point.coordinates[pc-1])}</span></div>`).join("");
  };
  const drawAxes = labels => {
    [[80,610,930,610],[80,610,80,55]].forEach(v=>svg.appendChild(node("line",{x1:v[0],y1:v[1],x2:v[2],y2:v[3],class:"axis"})));
    for(let i=1;i<5;i++){
      const x=80+i*850/5,y=610-i*555/5;
      svg.appendChild(node("line",{x1:x,y1:55,x2:x,y2:610,class:"grid"}));
      svg.appendChild(node("line",{x1:80,y1:y,x2:930,y2:y,class:"grid"}));
    }
    const tx=node("text",{x:505,y:660,"text-anchor":"middle",fill:"#b7c6d9"});tx.textContent=labels[0];svg.appendChild(tx);
    const ty=node("text",{x:22,y:330,transform:"rotate(-90 22 330)","text-anchor":"middle",fill:"#b7c6d9"});ty.textContent=labels[1];svg.appendChild(ty);
  };
  const render = () => {
    enforceDistinct("render"); syncControls(); save();
    const model=VIEWER_DATA.models[state.model], points=model.points;
    svg.replaceChildren();
    const xs=points.map(p=>p.coordinates[state.x-1]), ys=points.map(p=>p.coordinates[state.y-1]), zs=points.map(p=>p.coordinates[state.z-1]);
    const ex=extent(xs,state.fixed), ey=extent(ys,state.fixed), ez=extent(zs,state.fixed);
    let plotted;
    if(state.mode==="2d"){
      plotted=points.map((p,i)=>({p,x:scale(xs[i],ex,80,930),y:scale(ys[i],ey,610,55),depth:0}));
      drawAxes([`PC${state.x}`,`PC${state.y}`]);
    } else {
      plotted=points.map((p,i)=>{
        const nx=scale(xs[i],ex,-1,1),ny=scale(ys[i],ey,-1,1),nz=scale(zs[i],ez,-1,1);
        const [rx,ry,depth]=rotate(nx,ny,nz), zoom=2.25*state.zoom/100;
        return {p,x:505+rx*185*zoom,y:335-ry*185*zoom,depth};
      }).sort((a,b)=>a.depth-b.depth);
      drawAxes([`rotated PC${state.x}`,`rotated PC${state.y} / PC${state.z}`]);
    }
    plotted.forEach(({p,x,y,depth})=>{
      const c=node("circle",{cx:x,cy:y,r:state.mode==="3d"?3.6+Math.max(-1,Math.min(1,depth))*.7:4.1,fill:colors[p.cluster]||"#94a3b8",class:`role ${p.persona===state.selectedPersona?"selected":""}`});
      const title=node("title");title.textContent=`${p.persona} · ${p.cluster} · PC${state.x} ${fmt(p.coordinates[state.x-1])} · PC${state.y} ${fmt(p.coordinates[state.y-1])}${state.mode==="3d"?` · PC${state.z} ${fmt(p.coordinates[state.z-1])}`:""}`;c.appendChild(title);
      c.addEventListener("click",()=>{state.selectedPersona=p.persona;render();});svg.appendChild(c);
    });
    const selected=points.find(p=>p.persona===state.selectedPersona); showDetails(selected);
    const axes=state.mode==="3d"?[state.x,state.y,state.z]:[state.x,state.y];
    $("diagnostics").innerHTML=axes.map(pc=>axisDiagnostic(model,pc)).join("");
  };
  Object.entries(colors).forEach(([cluster,color])=>{$("legend").insertAdjacentHTML("beforeend",`<span><i class="swatch" style="background:${color}"></i>${cluster.replaceAll("_"," ")}</span>`);});
  [["model","model"],["mode","mode"]].forEach(([id,key])=>$(id).addEventListener("change",e=>{state[key]=e.target.value;render();}));
  [["pc-x","x"],["pc-y","y"],["pc-z","z"]].forEach(([id,key])=>$(id).addEventListener("change",e=>{state[key]=Number(e.target.value);enforceDistinct(key);render();}));
  $("fixed").addEventListener("change",e=>{state.fixed=e.target.checked;render();});
  [["yaw","yaw"],["pitch","pitch"],["zoom","zoom"]].forEach(([id,key])=>$(id).addEventListener("input",e=>{state[key]=Number(e.target.value);render();}));
  $("reset").addEventListener("click",()=>{const keep={model:state.model,selectedPersona:state.selectedPersona};state={...defaults,...keep};render();});
  let drag=null;
  svg.addEventListener("pointerdown",e=>{if(state.mode==="3d"){drag={x:e.clientX,y:e.clientY,yaw:state.yaw,pitch:state.pitch};svg.setPointerCapture(e.pointerId);}});
  svg.addEventListener("pointermove",e=>{if(drag){state.yaw=drag.yaw+(e.clientX-drag.x)*.45;state.pitch=Math.max(-80,Math.min(80,drag.pitch-(e.clientY-drag.y)*.35));render();}});
  svg.addEventListener("pointerup",()=>{drag=null;save();});
  svg.addEventListener("wheel",e=>{if(state.mode==="3d"){e.preventDefault();state.zoom=Math.max(55,Math.min(170,state.zoom-e.deltaY*.08));render();}},{passive:false});
  render();
})();
