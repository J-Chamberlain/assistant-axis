/* Scientific mesh preview only. Pure SVG/Sharp; no browser or WebGL execution. */
const fs=require('node:fs'),path=require('node:path'),sharp=require('sharp'),assert=require('node:assert/strict');
const here=__dirname,d=JSON.parse(fs.readFileSync(path.join(here,'persona_trait_surface_data.json'))),m=d.models[d.default_model];
const colors=[[0,'173d9e'],[.2,'198bcc'],[.4,'74d9d0'],[.5,'f4f1dc'],[.65,'ffd04a'],[.8,'ef7529'],[1,'b21932']];
function color(v){
  const t=Math.max(0,Math.min(1,v/100)),j=Math.min(colors.length-2,colors.findIndex((c,i)=>i<colors.length-1&&t<=colors[i+1][0]));
  const [a,b]=[colors[j],colors[j+1]],f=(t-a[0])/(b[0]-a[0]);
  const rgb=s=>[0,2,4].map(i=>parseInt(s.slice(i,i+2),16));
  return '#'+rgb(a[1]).map((c,i)=>Math.round(c+(rgb(b[1])[i]-c)*f).toString(16).padStart(2,'0')).join('');
}
const view=m.views['0_1'],level=view.levels[1],lo=[view.x[0],view.y[0]],hi=[view.x.at(-1),view.y.at(-1)];
const longest=Math.max(hi[0]-lo[0],hi[1]-lo[1]);
const yaw=46*Math.PI/180,pitch=28*Math.PI/180;
const right=[-Math.sin(yaw),Math.cos(yaw),0],up=[-Math.sin(pitch)*Math.cos(yaw),-Math.sin(pitch)*Math.sin(yaw),Math.cos(pitch)];
const eye=[Math.cos(pitch)*Math.cos(yaw),Math.cos(pitch)*Math.sin(yaw),Math.sin(pitch)];
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
function project(x,y,z){const w=[(x-(lo[0]+hi[0])/2)/longest*1.25,(y-(lo[1]+hi[1])/2)/longest*1.25,(z-50)/100*.75];return [300+320*dot(w,right),280-320*dot(w,up),dot(w,eye)];}
const svg=['<svg xmlns="http://www.w3.org/2000/svg" width="3000" height="555" viewBox="0 0 3000 555">',
  '<rect width="3000" height="555" fill="#0d0d0d"/><g font-family="DejaVu Sans, sans-serif" fill="#e8e8e8">'];
let triangles=0;
for(let g=0;g<5;g++){
  svg.push(`<g transform="translate(${g*600},0)"><text x="24" y="34" font-size="23">${m.categories[g].label}</text>`,
    `<text x="24" y="59" font-size="11" fill="#aaa6a0">${m.categories[g].members.map(member=>member.label).join(' / ')}</text>`);
  const grid=level.grids[g],faces=[];
  for(let j=0;j<60;j++)for(let i=0;i<60;i++)for(const corners of [[[i,j],[i+1,j],[i,j+1]],[[i+1,j],[i+1,j+1],[i,j+1]]]){
    if(corners.some(([x,y])=>grid[y][x]===null))continue;
    const points=corners.map(([x,y])=>project(view.x[x],view.y[y],grid[y][x]));
    const mean=corners.reduce((s,[x,y])=>s+grid[y][x],0)/3;
    faces.push({depth:points.reduce((s,p)=>s+p[2],0)/3,points:points.map(p=>p.slice(0,2).map(v=>v.toFixed(2)).join(',')).join(' '),color:color(mean)});
  }
  faces.sort((a,b)=>a.depth-b.depth);triangles+=faces.length;
  for(const face of faces)svg.push(`<polygon points="${face.points}" fill="${face.color}" stroke="${face.color}" stroke-width=".4"/>`);
  const corners=[[lo[0],lo[1],0],[hi[0],lo[1],0],[lo[0],hi[1],0],[lo[0],lo[1],100]].map(p=>project(...p));
  for(let a=1;a<4;a++){
    const [p,q]=[corners[0],corners[a]];svg.push(`<path d="M${p[0]},${p[1]} L${q[0]},${q[1]}" stroke="#888" fill="none"/>`);
    svg.push(`<text x="${q[0]+5}" y="${q[1]}" font-size="11" fill="#ccc">${['','PC1','PC2','100'][a]}</text>`);
  }
  svg.push('<text x="24" y="476" font-size="12" fill="#aaa6a0">Height / color = mean trait percentile (0-100)</text>');
  for(let i=0;i<100;i++)svg.push(`<rect x="${24+i*4}" y="493" width="4.1" height="8" fill="${color(i+.5)}"/>`);
  svg.push('<text x="24" y="519" font-size="11">0</text><text x="215" y="519" font-size="11">50</text><text x="400" y="519" font-size="11">100</text></g>');
}
svg.push('<text x="24" y="545" font-size="10" fill="#aaa6a0">Static orthographic preview of prepared PC1-PC2 surfaces; not a browser screenshot. Exact nodes and interactive camera controls are in the HTML viewer.</text></g></svg>');
async function main(){
  const source=svg.join('');fs.writeFileSync(path.join(here,'trait_surface_preview.svg'),source);
  const out=path.join(here,'trait_surface_preview.png');await sharp(Buffer.from(source)).png().toFile(out);
  const stats=await sharp(out).stats();assert.ok(stats.channels.slice(0,3).every(c=>c.stdev>20));
  fs.writeFileSync(path.join(here,'trait_surface_preview_checks.json'),JSON.stringify({status:'pass',triangles,groups:5,
    renderer:'Pure SVG orthographic projection rasterized with Sharp',browser_screenshot:false},null,2)+'\n');
  console.log({triangles,output:out});
}
main().catch(e=>{console.error(e);process.exitCode=1;});
