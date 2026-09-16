"""Shared, local-only helpers for the pre-data LISS 2020 pipeline."""
from pathlib import Path
import hashlib
import json
import os
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_external" / "liss_2020"
OUTPUT = DATA / "aggregate_outputs"
CP = DATA / "cp20l_EN_1.0p.dta"
SS = DATA / "ss20a_EN_1.0p.dta"
CP_CODEBOOK = DATA / "codebook_cp20l_EN_1.1.pdf"
SS_CODEBOOK = DATA / "codebook_ss20a_EN_1.0.pdf"
EXPECTED_FILES = (CP, SS, CP_CODEBOOK, SS_CODEBOOK)
BIG_FIVE_KEY = DATA / "big_five_scoring_key_verified.json"
SEED = 11011

def require_files(*paths):
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        print(json.dumps({"status": "blocked_missing_authorized_data", "missing": missing,
            "message": "Obtain files through Centerdata, then place them in gitignored data_external/liss_2020/. No respondent data were accessed."}, indent=2), file=sys.stderr)
        raise SystemExit(2)

def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def read_stata(path):
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit(f"pandas is required after authorized data arrive: {exc}")
    return pd.read_stata(path, convert_categoricals=False)

def numeric(frame, columns):
    import pandas as pd
    out = frame.loc[:, columns].apply(pd.to_numeric, errors="coerce")
    return out.mask(out < 0)

def environment_record():
    versions = {"python": platform.python_version(), "platform": platform.platform()}
    for package in ("pandas", "numpy", "sklearn", "semopy"):
        try:
            module = __import__(package)
            versions[package] = getattr(module, "__version__", "unknown")
        except ImportError:
            versions[package] = None
    versions.update(seed=SEED, git_commit=os.environ.get("GIT_COMMIT", "capture-with-git-rev-parse-at-run"))
    return versions

def write_local_json(name, payload):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    target = OUTPUT / name
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return target

def load_joined():
    require_files(CP, SS)
    cp, ss = read_stata(CP), read_stata(SS)
    if "nomem_encr" not in cp or "nomem_encr" not in ss:
        raise SystemExit("schema error: nomem_encr must occur in both source files")
    return cp.merge(ss, on="nomem_encr", how="inner", validate="one_to_one")

def score_big_five(frame):
    # The signed item key is intentionally supplied only after authorized codebook verification.
    require_files(BIG_FIVE_KEY)
    key = json.loads(BIG_FIVE_KEY.read_text())
    scored = {}
    for domain, spec in key["domains"].items():
        values = numeric(frame, spec["items"])
        for item in spec.get("reverse", []):
            values[item] = 6 - values[item]
        scored[domain] = values.mean(axis=1, skipna=True).where(values.notna().sum(axis=1) >= 8)
    return __import__("pandas").DataFrame(scored, index=frame.index)

def hifwb_item_map():
    import pandas as pd
    return pd.read_csv(ROOT / "research/outputs/liss_hifwb_prior_evidence/liss_2020_mhc_hifwb_item_crosswalk.csv")

def score_hifwb(frame):
    """Return content scores while preserving randomized form and timeframe."""
    import pandas as pd
    mapping = hifwb_item_map()
    allowed = mapping[mapping["mapping_status"].isin(["DIRECT", "CLOSE"])]
    parts = []
    for version, version_rows in allowed.groupby("questionnaire_version"):
        routed = frame.loc[pd.to_numeric(frame["ss20a001"], errors="coerce") == int(version)]
        timeframe = version_rows["timeframe"].iloc[0]
        block = pd.DataFrame(index=routed.index)
        for content, rows in version_rows.groupby("hifwb_content"):
            cols = [c for c in rows["variable"] if c in routed.columns]
            if cols:
                vals = numeric(routed, cols)
                block[content] = vals.mean(axis=1, skipna=True)
                block[f"{content}__valid_items"] = vals.notna().sum(axis=1)
        block["questionnaire_version"] = int(version)
        block["timeframe"] = timeframe
        parts.append(block)
    return pd.concat(parts).sort_index() if parts else pd.DataFrame()
