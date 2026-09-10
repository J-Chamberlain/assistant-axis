/* Pure camera math for the emotion viewer. Angles are degrees. */
(function(root) {
  "use strict";
  const RAD=Math.PI/180, distance=Math.hypot(1.26,1.29,0.94);
  const dot=(a,b)=>a.x*b.x+a.y*b.y+a.z*b.z;
  const defaults={yaw:Math.atan2(1.29,1.26)/RAD,pitch:Math.asin(0.94/distance)/RAD,roll:0,zoom:100};
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  function toCamera(angles,center={x:0,y:0,z:-0.04}) {
    const y=angles.yaw*RAD,p=clamp(angles.pitch,-90,90)*RAD,r=angles.roll*RAD;
    const radius=distance*100/clamp(angles.zoom,25,300);
    const forward={x:Math.cos(p)*Math.cos(y),y:Math.cos(p)*Math.sin(y),z:Math.sin(p)};
    const up={x:-Math.sin(p)*Math.cos(y),y:-Math.sin(p)*Math.sin(y),z:Math.cos(p)};
    const right={x:-Math.sin(y),y:Math.cos(y),z:0};
    return {eye:Object.fromEntries(['x','y','z'].map(k=>[k,forward[k]*radius])),
      up:Object.fromEntries(['x','y','z'].map(k=>[k,up[k]*Math.cos(r)+right[k]*Math.sin(r)])),center:{...center}};
  }
  function fromCamera(camera,fallbackYaw=defaults.yaw) {
    const e=camera.eye,n=Math.hypot(e.x,e.y,e.z);
    if(!Number.isFinite(n)||n<1e-8) return {...defaults};
    const yaw=Math.hypot(e.x,e.y)>1e-8?Math.atan2(e.y,e.x)/RAD:fallbackYaw;
    const pitch=Math.asin(clamp(e.z/n,-1,1))/RAD,y=yaw*RAD,p=pitch*RAD;
    const up={x:-Math.sin(p)*Math.cos(y),y:-Math.sin(p)*Math.sin(y),z:Math.cos(p)};
    const right={x:-Math.sin(y),y:Math.cos(y),z:0},u=camera.up||{x:0,y:0,z:1};
    return {yaw,pitch,roll:Math.atan2(dot(u,right),dot(u,up))/RAD,zoom:distance/n*100};
  }
  const api={toCamera,fromCamera,defaults,distance};
  if(typeof module!=='undefined'&&module.exports) module.exports=api;
  else root.EmotionCamera=api;
})(typeof window==='undefined'?globalThis:window);
