# Disk inspection and preservation

Initial preservation-follow-up inspection: APFS disk3 total245,107,195,904bytes; unallocated176,713,728bytes. The affected Data volume is mounted at /System/Volumes/Data. Free space temporarily rose to241,762,304bytes and writes succeeded, then fell to122,114,048bytes and even a tiny probe failed with ENOSPC.

The audit bundle is about4.6MB uncompressed. No cleanup was initially needed to preserve it. Exact minimum free space for a later Git commit could not be guaranteed because available space was changing concurrently. A single specifically presented pip cache entry was selected to restore a practical working margin; the two smaller proposed cache entries were left intact.

Deleted only the SciPy1.18.1 downloaded wheel cache and its metadata:20,467,992 logical bytes (20,471,808 allocated bytes). Wheel identity, platform tag and SHA256 are in disk_preservation.json. This is an installation-download cache, not installed package code. Re-download of the same artifact can recreate it subject to remote availability; availability was not checked. No broad cleanup occurred.

Measured directory allocation (KiB): original checkout5,037,504; its downloads1,220,116; research386,032; Git334,372; main virtualenv1,122,920; other inspected virtualenvs475,164/98,088/410,684/579,352. These were not cleanup targets. User Library/Caches reported2,717,564KiB and ~/.cache2,751,332KiB across accessible entries; /private/tmp50,580KiB. Several protected Apple cache directories returned Operation not permitted, so these are partial visible totals, not exhaustive usage.

Candidate paths and sizes were presented in conversation before deletion. No activations, responses, extraction logs, provenance, Git history, installed environments or unrelated work were deleted. No model runs or pushing occurred.
