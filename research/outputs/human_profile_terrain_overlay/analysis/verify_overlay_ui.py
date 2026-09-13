#!/usr/bin/env python3
"""Headless Chrome checks for local or public human terrain overlay."""

import argparse, base64, json, shutil, subprocess, tempfile, time
from pathlib import Path
import requests, websocket

HERE=Path(__file__).resolve().parent; OUT=HERE.parent
CHROME=Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')

class CDP:
    def __init__(self,url,port): self.ws=websocket.create_connection(url,timeout=30,origin=f'http://127.0.0.1:{port}');self.i=0;self.events=[]
    def call(self,m,p=None):
        self.i+=1; i=self.i; self.ws.send(json.dumps({'id':i,'method':m,'params':p or {}}))
        while True:
            x=json.loads(self.ws.recv())
            if x.get('id')==i:
                if 'error' in x: raise RuntimeError(x['error'])
                return x.get('result',{})
            self.events.append(x)
    def eval(self,s):
        result=self.call('Runtime.evaluate',{'expression':s,'returnByValue':True,'awaitPromise':True})
        if result.get('exceptionDetails'): raise RuntimeError(result['exceptionDetails'])
        return result.get('result',{}).get('value')

def run(url,port,width,tag):
    profile=Path(tempfile.mkdtemp(prefix='aa12-human-terrain-')); log=(OUT/f'browser_{tag}.log').open('w')
    cmd=[str(CHROME),'--headless=new','--no-sandbox','--allow-file-access-from-files','--enable-webgl','--ignore-gpu-blocklist','--use-angle=swiftshader','--enable-unsafe-swiftshader','--remote-allow-origins=*',f'--remote-debugging-port={port}',f'--user-data-dir={profile}',f'--window-size={width},1000',url]
    proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT); c=None; checks=[]
    def check(name,value,observed):
        checks.append({'check':name,'passed':bool(value),'observed':observed})
        if not value: raise AssertionError(f'{name}: {observed}')
    try:
        deadline=time.time()+40; ws=None
        while time.time()<deadline:
            try:
                pages=requests.get(f'http://127.0.0.1:{port}/json',timeout=1).json(); ws=next((p['webSocketDebuggerUrl'] for p in pages if p.get('type')=='page'),None)
                if ws: break
            except Exception: pass
            time.sleep(.2)
        if not ws: raise TimeoutError('Chrome page unavailable')
        c=CDP(ws,port);c.call('Runtime.enable');c.call('Log.enable')
        for _ in range(240):
            if c.eval("typeof Plotly!=='undefined'&&document.getElementById('plot').data&&document.getElementById('plot').data.length>0&&typeof HUMAN!=='undefined'"): break
            time.sleep(.25)
        initial=c.eval("({types:PLOT.data.map(x=>x.type),humans:PLOT.data.some(x=>x.name==='Predicted human profiles'),k:document.getElementById('humanK').value,t:document.getElementById('traitSet').value,mode:document.getElementById('projectionMode').value,title:document.title})")
        check('initial render',initial and initial['humans'],initial);check('default K6 primary Ridge',initial['k']=='6' and initial['t']=='12' and initial['mode']=='ridge',initial)
        def act(js): c.eval(f"(async()=>{{{js};await new Promise(r=>setTimeout(r,1000));return true;}})()")
        act("let e=document.getElementById('model');e.value='llama';e.dispatchEvent(new Event('change',{bubbles:true}))")
        check('model switch',c.eval("document.getElementById('status').textContent.includes('LLaMA')"),c.eval("document.getElementById('status').textContent"))
        act("let e=document.getElementById('humanK');e.value='10';e.dispatchEvent(new Event('change',{bubbles:true}));let t=document.getElementById('traitSet');t.value='45';t.dispatchEvent(new Event('change',{bubbles:true}))")
        check('K and trait switch',c.eval("state.humanK==='10'&&state.traitSet==='45'&&PLOT.data.some(x=>x.name==='Predicted human profiles')"),c.eval("({k:state.humanK,t:state.traitSet})"))
        act("let e=document.getElementById('projectionMode');e.value='knn';e.dispatchEvent(new Event('change',{bubbles:true}));let v=document.getElementById('view');v.value='pc1_pc2';v.dispatchEvent(new Event('change',{bubbles:true}))")
        check('kNN 2D mode',c.eval("state.projectionMode==='knn'&&PLOT.data.some(x=>x.type==='contour')&&PLOT.data.some(x=>x.name==='Predicted human profiles')"),c.eval("PLOT.data.map(x=>[x.name,x.type])"))
        act("let v=document.getElementById('view');v.value='compare_aligned';v.dispatchEvent(new Event('change',{bubbles:true}))")
        check('aligned comparison',c.eval("PLOT.layout.title.text.includes('non-native')&&PLOT.data.filter(x=>x.name==='Predicted human profiles').length===3"),c.eval("PLOT.layout.title.text"))
        act("document.getElementById('showHumans').checked=false;document.getElementById('showHumans').dispatchEvent(new Event('change',{bubbles:true}))")
        check('human overlay toggle',c.eval("!PLOT.data.some(x=>x.name==='Predicted human profiles')"),c.eval("PLOT.data.map(x=>x.name)"))
        check('no local paths in page',not bool(c.eval("document.documentElement.innerHTML.includes('/Users/')")),c.eval("location.href"))
        shot=c.call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False}); path=OUT/f'figures/viewer_{tag}.png';path.write_bytes(base64.b64decode(shot['data']));check('screenshot',path.stat().st_size>40000,path.stat().st_size)
        errors=[e for e in c.events if e.get('method')=='Runtime.exceptionThrown' or (e.get('method')=='Log.entryAdded' and e.get('params',{}).get('entry',{}).get('level')=='error')]
        check('no JavaScript errors',not errors,errors)
    finally:
        if c: c.ws.close()
        proc.terminate();
        try: proc.wait(timeout=5)
        except subprocess.TimeoutExpired: proc.kill()
        log.close();shutil.rmtree(profile,ignore_errors=True)
    return checks

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--url');args=ap.parse_args();url=args.url or (OUT/'human_profile_terrain_overlay.html').resolve().as_uri()
    desktop=run(url,9243,1600,'desktop');mobile=run(url,9244,430,'mobile')
    payload={'status':'PASS','url':url,'browser':subprocess.check_output([str(CHROME),'--version'],text=True).strip(),'desktop':desktop,'mobile':mobile,'passed':len(desktop)+len(mobile)}
    (OUT/'browser_verification.json').write_text(json.dumps(payload,indent=2)+'\n');print(json.dumps({'status':'PASS','checks':payload['passed']}))
if __name__=='__main__': main()
