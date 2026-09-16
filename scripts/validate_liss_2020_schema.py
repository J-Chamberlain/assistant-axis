#!/usr/bin/env python3
from liss_common import *

require_files(*EXPECTED_FILES)
cp, ss = read_stata(CP), read_stata(SS)
required_cp = ["nomem_encr", "cp20l010", "cp20l011"] + [f"cp20l{i:03d}" for i in range(14, 80)] + [f"cp20l{i:03d}" for i in range(146, 166)]
required_ss = ["nomem_encr", "ss20a001"] + [f"ss20a{i:03d}" for i in range(2, 72)]
missing = {"cp": sorted(set(required_cp) - set(cp)), "ss": sorted(set(required_ss) - set(ss))}
duplicates = {"cp": int(cp["nomem_encr"].duplicated().sum()) if "nomem_encr" in cp else None,
              "ss": int(ss["nomem_encr"].duplicated().sum()) if "nomem_encr" in ss else None}
if missing["cp"] or missing["ss"] or any(duplicates.values()):
    print(json.dumps({"status": "schema_failed", "missing": missing, "duplicate_ids": duplicates}, indent=2)); raise SystemExit(3)
payload = {"status": "schema_ok", "rows": {"cp": len(cp), "ss": len(ss)}, "duplicate_ids": duplicates,
           "joinable_ids": int(cp[["nomem_encr"]].merge(ss[["nomem_encr"]], on="nomem_encr").shape[0])}
write_local_json("schema_validation.json", payload)
print(json.dumps(payload, indent=2))
