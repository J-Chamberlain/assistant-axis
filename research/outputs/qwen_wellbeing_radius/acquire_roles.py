"""Download hash-verified public role tensors; safely decode this tensor-only archive format."""
import collections,concurrent.futures,hashlib,io,json,pickle,urllib.request,zipfile
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
CACHE=Path('/tmp/qwen_roles');CACHE.mkdir(exist_ok=True)
def rebuild(storage,offset,size,stride,*rest):
    assert offset==0 and tuple(size)==(64,5120) and tuple(stride)==(5120,1)
    return storage.reshape(size)
class TensorReader(pickle.Unpickler):
    def find_class(self,module,name):
        allowed={('torch._utils','_rebuild_tensor_v2'):rebuild,('torch','BFloat16Storage'):'bfloat16',('collections','OrderedDict'):collections.OrderedDict}
        if (module,name) not in allowed:raise ValueError((module,name))
        return allowed[module,name]
    def persistent_load(self,pid):
        kind,dtype,key,device,count=pid
        assert kind=='storage' and dtype=='bfloat16' and device=='cpu' and count==327680
        raw=self.archive.read(self.prefix+'data/'+key)
        return (np.frombuffer(raw,dtype='<u2').astype(np.uint32)<<16).view(np.float32)
def read_tensor(p):
    with zipfile.ZipFile(p) as z:
        key=next(n for n in z.namelist() if n.endswith('/data.pkl'))
        u=TensorReader(io.BytesIO(z.read(key)));u.archive=z;u.prefix=key[:-8];return u.load().mean(0,dtype=np.float32).astype(float)
def main():
    api='https://huggingface.co/api/datasets/lu-christina/assistant-axis-vectors/tree/main/qwen-3-32b/role_vectors?limit=1000'
    entries=json.load(urllib.request.urlopen(api,timeout=40));assert len(entries)==275
    def get(e):
        p=CACHE/Path(e['path']).name
        for attempt in range(3):
            try:
                if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=e['lfs']['oid']:
                    data=urllib.request.urlopen('https://huggingface.co/datasets/lu-christina/assistant-axis-vectors/resolve/main/'+e['path'],timeout=50).read();assert hashlib.sha256(data).hexdigest()==e['lfs']['oid'];p.write_bytes(data)
                return p.stem,read_tensor(p)
            except Exception:
                if attempt==2:raise
    rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        for i,r in enumerate(pool.map(get,entries)):
            rows.append(r)
            if i%50==0:print('verified',i+1,flush=True)
    rows.sort();np.savez_compressed(HERE/'qwen_mean_roles.npz',personas=[x[0] for x in rows],vectors=np.stack([x[1] for x in rows]).astype(np.float32))
    (HERE/'role_download_manifest.json').write_text(json.dumps(entries,indent=2)+'\n')
    print('complete',len(rows),flush=True)
if __name__=='__main__':main()
