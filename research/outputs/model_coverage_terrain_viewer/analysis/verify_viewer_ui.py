#!/usr/bin/env python3
"""Headless Chrome/CDP interaction checks for the standalone terrain viewer."""

from __future__ import annotations

import base64
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import requests
import websocket


HERE = Path(__file__).resolve().parent
OUT = HERE.parent
HTML = OUT / "model_coverage_terrain_viewer.html"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
PORT = 9237


class CDP:
    def __init__(self, socket_url: str):
        self.ws = websocket.create_connection(socket_url, timeout=20, origin=f"http://127.0.0.1:{PORT}")
        self.counter = 0
        self.events: list[dict] = []

    def call(self, method: str, params: dict | None = None) -> dict:
        self.counter += 1
        message_id = self.counter
        self.ws.send(json.dumps({"id": message_id, "method": method, "params": params or {}}))
        while True:
            payload = json.loads(self.ws.recv())
            if payload.get("id") == message_id:
                if "error" in payload:
                    raise RuntimeError(payload["error"])
                return payload.get("result", {})
            self.events.append(payload)

    def evaluate(self, expression: str) -> object:
        result = self.call(
            "Runtime.evaluate",
            {"expression": expression, "returnByValue": True, "awaitPromise": True, "userGesture": True},
        )
        remote = result.get("result", {})
        if remote.get("subtype") == "error":
            raise RuntimeError(remote.get("description", "browser evaluation error"))
        return remote.get("value")

    def close(self) -> None:
        self.ws.close()


def wait_for_page() -> str:
    deadline = time.time() + 25
    endpoint = f"http://127.0.0.1:{PORT}/json"
    while time.time() < deadline:
        try:
            pages = requests.get(endpoint, timeout=1).json()
            candidates = [page for page in pages if page.get("type") == "page" and "model_coverage_terrain_viewer" in page.get("url", "")]
            if candidates:
                return candidates[0]["webSocketDebuggerUrl"]
        except Exception:
            pass
        time.sleep(0.2)
    raise TimeoutError("Chrome DevTools page did not become available")


def main() -> None:
    if not CHROME.exists():
        raise FileNotFoundError(CHROME)
    profile = Path(tempfile.mkdtemp(prefix="aa12-terrain-chrome-"))
    log_path = OUT / "browser_console.log"
    command = [
        str(CHROME), "--headless=new", "--no-sandbox", "--allow-file-access-from-files",
        "--enable-webgl", "--ignore-gpu-blocklist", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
        "--remote-allow-origins=*", f"--remote-debugging-port={PORT}", f"--user-data-dir={profile}",
        "--window-size=1600,1100", HTML.resolve().as_uri(),
    ]
    checks: list[dict] = []
    log_file = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(command, stdout=log_file, stderr=subprocess.STDOUT)
    cdp: CDP | None = None

    def check(name: str, passed: bool, observed: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "observed": observed})
        if not passed:
            raise AssertionError(f"{name}: {observed}")

    try:
        cdp = CDP(wait_for_page())
        cdp.call("Runtime.enable")
        cdp.call("Log.enable")
        ready = False
        for _ in range(80):
            ready = bool(cdp.evaluate("typeof Plotly !== 'undefined' && document.getElementById('plot').data && document.getElementById('plot').data.length > 0"))
            if ready:
                break
            time.sleep(0.25)
        check("initial Plotly render completed", ready, ready)
        initial = cdp.evaluate("({types:PLOT.data.map(t=>t.type),status:document.getElementById('status').textContent,errors:document.querySelectorAll('.plotly-notifier').length})")
        check("initial native view includes role points", "scatter3d" in initial["types"], initial)
        check("initial occupancy view includes KDE isosurface", "isosurface" in initial["types"], initial)
        check("initial status identifies Qwen and 80% level", "Qwen" in initial["status"] and "coverage 80" in initial["status"], initial["status"])

        def act(script: str, delay_ms: int = 900) -> object:
            return cdp.evaluate(f"(async()=>{{{script};await new Promise(r=>setTimeout(r,{delay_ms}));return true;}})()")

        act("let e=document.getElementById('model');e.value='llama';e.dispatchEvent(new Event('change',{bubbles:true}))")
        llama = cdp.evaluate("({status:document.getElementById('status').textContent,models:[...new Set(PLOT.data.flatMap(t=>t.customdata||[]).filter(Array.isArray).map(d=>d[1]))]})")
        check("model switch renders only LLaMA role metadata", llama["models"] == ["llama"], llama)
        check("no stale Qwen status after LLaMA switch", "LLaMA" in llama["status"] and "Qwen" not in llama["status"], llama["status"])

        act("let e=document.getElementById('view');e.value='pc1_pc2';e.dispatchEvent(new Event('change',{bubbles:true}))")
        types_2d = cdp.evaluate("PLOT.data.map(t=>t.type)")
        check("2D mode renders role-only density contour", "contour" in types_2d, types_2d)
        check("2D mode renders sampled role points", any(value in types_2d for value in ["scatter", "scattergl"]), types_2d)

        act("let e=document.getElementById('view');e.value='compare_native';e.dispatchEvent(new Event('change',{bubbles:true}))")
        compare = cdp.evaluate("({scenes:['scene','scene2','scene3'].filter(k=>PLOT.layout[k]).length,models:[...new Set(PLOT.data.flatMap(t=>t.customdata||[]).filter(Array.isArray).map(d=>d[1]))].sort()})")
        check("linked native comparison has three separate scenes", compare["scenes"] == 3, compare)
        check("linked native comparison carries all three model labels", compare["models"] == ["gemma", "llama", "qwen"], compare)

        act("let e=document.getElementById('view');e.value='compare_aligned';e.dispatchEvent(new Event('change',{bubbles:true}))")
        aligned = cdp.evaluate("({title:PLOT.layout.title.text,models:[...new Set(PLOT.data.flatMap(t=>t.customdata||[]).filter(Array.isArray).map(d=>d[1]))].sort()})")
        check("display-aligned overlay is explicitly labeled non-native", "non-native" in aligned["title"], aligned)
        check("display-aligned overlay retains all models", aligned["models"] == ["gemma", "llama", "qwen"], aligned)

        act("let e=document.getElementById('view');e.value='3d';e.dispatchEvent(new Event('change',{bubbles:true}));let m=document.getElementById('mode');m.value='families';m.dispatchEvent(new Event('change',{bubbles:true}));document.getElementById('showHulls').checked=true;document.getElementById('showHulls').dispatchEvent(new Event('change',{bubbles:true}))")
        family = cdp.evaluate("({mesh:PLOT.data.filter(t=>t.type==='mesh3d').length,families:PLOT.data.filter(t=>t.type==='scatter3d').map(t=>t.name),model:document.getElementById('model').value})")
        check("family mode renders eligible family sample envelopes", family["mesh"] >= 4, family)
        check("family mode retains anonymous family labels", any("Family A" == x for x in family["families"]), family)

        act("document.getElementById('roleSearch').value='mystic';document.getElementById('selectRole').click()")
        role = cdp.evaluate("({title:document.getElementById('detailTitle').textContent,rows:document.querySelectorAll('#roleDetail tbody tr').length,selected:PLOT.data.some(t=>t.name==='Selected role')})")
        check("role search selects and labels mystic", role["title"] == "mystic" and role["selected"], role)
        check("role detail links the same role across three models", role["rows"] == 3, role)

        act("let e=document.getElementById('model');e.value='qwen';e.dispatchEvent(new Event('change',{bubbles:true}));document.getElementById('showTraits').checked=true;document.getElementById('traitSearch').value='abstract';document.getElementById('addTrait').click()")
        traits = cdp.evaluate("({hasTrait:PLOT.data.some(t=>t.name==='Trait landmarks'),selectedTitle:document.getElementById('detailTitle').textContent})")
        check("optional Qwen trait landmark layer executes", traits["hasTrait"], traits)
        check("selected role persists across model switch", traits["selectedTitle"] == "mystic", traits)

        act("document.getElementById('showPoints').checked=false;document.getElementById('showPoints').dispatchEvent(new Event('change',{bubbles:true}))")
        hidden = cdp.evaluate("PLOT.data.map(t=>t.name)")
        check("persona-node toggle hides family point traces", not any(name in ["Family A", "Family B", "Family C", "Family D", "Family E", "Unassigned"] for name in hidden), hidden)
        act("document.getElementById('showPoints').checked=true;document.getElementById('showPoints').dispatchEvent(new Event('change',{bubbles:true}));document.getElementById('resetCamera').click()", 400)

        data_checks = cdp.evaluate("({q:TERRAIN.models.qwen.points.length,l:TERRAIN.models.llama.points.length,g:TERRAIN.models.gemma.points.length,eL:TERRAIN.models.llama.points.filter(p=>p.family==='MFamily_E').length,eG:TERRAIN.models.gemma.points.filter(p=>p.family==='MFamily_E').length,eLHull:Object.hasOwn(TERRAIN.models.llama.family_hulls,'MFamily_E'),eGHull:Object.hasOwn(TERRAIN.models.gemma.family_hulls,'MFamily_E')})")
        check("viewer embeds exactly 275 roles per model", data_checks["q"] == data_checks["l"] == data_checks["g"] == 275, data_checks)
        check("small E groups stay points-only", data_checks["eL"] == 3 and data_checks["eG"] == 4 and not data_checks["eLHull"] and not data_checks["eGHull"], data_checks)

        screenshot = cdp.call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
        screenshot_path = OUT / "figures/viewer_headless_chrome.png"
        screenshot_path.write_bytes(base64.b64decode(screenshot["data"]))
        check("headless Chrome captured rendered viewer", screenshot_path.stat().st_size > 50_000, screenshot_path.stat().st_size)

        exception_events = [event for event in cdp.events if event.get("method") in {"Runtime.exceptionThrown", "Log.entryAdded"} and (event.get("method") == "Runtime.exceptionThrown" or event.get("params", {}).get("entry", {}).get("level") == "error")]
        check("no browser JavaScript exceptions or console errors", len(exception_events) == 0, exception_events)
    finally:
        if cdp is not None:
            cdp.close()
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        log_file.close()
        shutil.rmtree(profile, ignore_errors=True)

    payload = {
        "status": "PASS",
        "browser": subprocess.check_output([str(CHROME), "--version"], text=True).strip(),
        "viewer": str(HTML.relative_to(OUT.parents[2])),
        "checks": checks,
        "passed": sum(item["passed"] for item in checks),
        "failed": sum(not item["passed"] for item in checks),
    }
    (OUT / "browser_verification.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    inventory_path = OUT / "figure_inventory.csv"
    rows = []
    if inventory_path.exists():
        import csv

        with inventory_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        if not any(row["figure_id"] == "viewer_headless_chrome" for row in rows):
            rows.append(
                {
                    "figure_id": "viewer_headless_chrome",
                    "files": "figures/viewer_headless_chrome.png",
                    "description": "Headless Chrome diagnostic render of interactive viewer controls and WebGL terrain",
                    "source_data": "model_coverage_terrain_viewer.html;terrain_viewer_data.json",
                }
            )
            with inventory_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["figure_id", "files", "description", "source_data"])
                writer.writeheader()
                writer.writerows(rows)
    print(json.dumps({"status": "PASS", "checks": len(checks), "screenshot_bytes": (OUT / "figures/viewer_headless_chrome.png").stat().st_size}, indent=2))


if __name__ == "__main__":
    main()
