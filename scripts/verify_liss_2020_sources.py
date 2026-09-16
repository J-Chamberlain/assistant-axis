#!/usr/bin/env python3
from liss_common import *

require_files(*EXPECTED_FILES)
payload = {"status": "files_present",
           "files": {p.name: {"bytes": p.stat().st_size, "sha256": sha256(p)} for p in EXPECTED_FILES},
           "environment": environment_record()}
target = write_local_json("source_hashes_and_environment.json", payload)
print(json.dumps({**payload, "local_output": str(target)}, indent=2))
