from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_external/liss_2020"
CP = DATA / "cp20l_EN_1.0p.dta"
SS = DATA / "ss20a_EN_1.0p.dta"

def require_files(*paths):
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        print(json.dumps({"status":"blocked_missing_authorized_data","missing":missing,"message":"Place approved LISS files in gitignored data_external/liss_2020/; no respondent data was accessed."}), file=sys.stderr)
        raise SystemExit(2)

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
