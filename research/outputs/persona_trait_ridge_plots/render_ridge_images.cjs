/* Static rasterization plus model-switch DOM-double tests; not a live browser. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),vm=require('node:vm');
const here=__dirname,models=['qwen','llama','gemma'];

async function raster(base,suffix) {
  const sharp=require('sharp');
  const source=fs.readFileSync(base+'.svg');
  await sharp(source,{limitInputPixels:30000000}).png().toFile(base+'.png');
  const image=sharp(base+'.png'),metadata=await image.metadata(),stats=await image.stats();
  assert.ok(stats.channels.slice(0,3).every(channel=>channel.stdev>15),'Figure must not be blank');
  assert.equal(metadata.width,suffix==='overview'?3000:1000);
  assert.equal(metadata.height,suffix==='overview'?940:12380);
  return {file:path.basename(base+'.png'),width:metadata.width,height:metadata.height};
}

function domChecks(html) {
  const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].at(-1)[1];new vm.Script(script);
  const markup=html.split('<script>')[0];
  assert.equal((markup.match(/class="ridge-row"/g)||[]).length,2475,'All editorial model/PC rows are pre-rendered');
  assert.equal((markup.match(/data-profile-set="editorial"/g)||[]).length,2478,'Rows plus model views identify editorial mode');
  for(const token of ['id="model-select"','id="profile-set-select"','id="construction-select"','value="big_five"','human_anchored_strict','external_taxonomy_expanded','renderBigFive()','window.__traitRidgeViewer'])assert.ok(html.includes(token),token);
  return {checks:['Inline interaction script parses','All Qwen/Llama/Gemma editorial rows remain pre-rendered',
    'Editorial default plus Big Five profile selector are present','All four frozen Big Five construction keys are embedded',
    'Dynamic Big Five renderer and public test API are present; live interaction is tested separately in Chrome']};
}

async function main() {
  const results=[];
  const domOnly=process.argv.includes('--dom-only');
  if(!domOnly){
    for(const model of models)for(const suffix of ['pc1','pc2','pc3','overview'])
      results.push(await raster(path.join(here,`persona_trait_ridges_${model}_${suffix}`),suffix));
    for(const suffix of ['pc1','pc2','pc3','overview'])
      results.push(await raster(path.join(here,`persona_trait_ridges_${suffix}`),suffix));
  }
  const interaction=domChecks(fs.readFileSync(path.join(here,'persona_trait_ridges.html'),'utf8'));
  const result={status:'pass',static_renders:results,static_rasterization:domOnly?'not rerun; unchanged editorial SVGs/PNGs retained':'rerun with Sharp',interaction_unit_checks:interaction.checks,browser_test:false,
    note:'Static markup/script checks are deterministic; actual model/profile interaction is verified separately in real Chrome.'};
  fs.writeFileSync(path.join(here,'ridge_render_checks.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result,null,2));
}
main().catch(error=>{console.error(error);process.exitCode=1;});
