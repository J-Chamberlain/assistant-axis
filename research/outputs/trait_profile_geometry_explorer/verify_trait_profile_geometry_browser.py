#!/usr/bin/env python3
"""Run live Chrome interaction checks against the generated companion viewer."""

from __future__ import annotations

import argparse
import contextlib
import functools
import http.server
import json
import math
import socket
import subprocess
import tempfile
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any

import websocket


HERE = Path(__file__).resolve().parent
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
REPORT = HERE / "browser_verification_report.json"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        del format, args


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class Cdp:
    def __init__(self, url: str) -> None:
        self.ws = websocket.create_connection(url, timeout=30, origin="http://localhost")
        self.next_id = 0

    def close(self) -> None:
        self.ws.close()

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.next_id += 1
        message_id = self.next_id
        self.ws.send(json.dumps({"id": message_id, "method": method, "params": params or {}}))
        while True:
            response = json.loads(self.ws.recv())
            if response.get("id") != message_id:
                continue
            if "error" in response:
                raise RuntimeError(f"CDP {method} failed: {response['error']}")
            return response.get("result", {})

    def evaluate(self, expression: str, await_promise: bool = True) -> Any:
        result = self.call("Runtime.evaluate", {
            "expression": expression,
            "awaitPromise": await_promise,
            "returnByValue": True,
            "userGesture": True,
        })
        remote = result.get("result", {})
        if remote.get("subtype") == "error":
            raise RuntimeError(remote.get("description", "Browser evaluation error"))
        if "exceptionDetails" in result:
            raise RuntimeError(json.dumps(result["exceptionDetails"], indent=2))
        return remote.get("value")


def wait_json(url: str, timeout: float = 20.0) -> Any:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                return json.load(response)
        except Exception as error:  # pragma: no cover - timing dependent
            last_error = error
            time.sleep(0.15)
    raise RuntimeError(f"Timed out waiting for {url}: {last_error}")


def wait_condition(cdp: Cdp, expression: str, timeout: float = 35.0) -> Any:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        last = cdp.evaluate(expression)
        if last:
            return last
        time.sleep(0.2)
    raise RuntimeError(f"Timed out waiting for browser condition; last value={last!r}")


def max_abs(a: list[float], b: list[float]) -> float:
    return max(abs(x - y) for x, y in zip(a, b))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    if not CHROME.exists():
        raise SystemExit(f"Chrome is unavailable: {CHROME}")
    cases = json.loads((HERE / "browser_python_reference_cases.json").read_text(encoding="utf-8"))["cases"]
    test_case = next(case for case in cases if not any(edit["clamped"] for edit in case["edits"]))
    http_port = free_port()
    debug_port = free_port()
    handler = functools.partial(QuietHandler, directory=str(HERE))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", http_port), handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    target_url = f"http://127.0.0.1:{http_port}/trait_profile_geometry_explorer.html"
    with tempfile.TemporaryDirectory(prefix="trait-equalizer-chrome-") as profile_dir:
        process = subprocess.Popen(
            [
                str(CHROME),
                "--headless=new",
                "--enable-unsafe-swiftshader",
                "--use-angle=swiftshader",
                "--use-gl=angle",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-background-networking",
                "--remote-allow-origins=*",
                f"--remote-debugging-port={debug_port}",
                f"--user-data-dir={profile_dir}",
                "--window-size=1440,1000",
                target_url,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        cdp: Cdp | None = None
        try:
            pages = wait_json(f"http://127.0.0.1:{debug_port}/json", timeout=25)
            page = next(item for item in pages if item.get("type") == "page")
            cdp = Cdp(page["webSocketDebuggerUrl"])
            cdp.call("Runtime.enable")
            wait_condition(cdp, "document.getElementById('app-status')?.dataset.ready === 'true'", timeout=45)
            counts = cdp.evaluate("({personas: window.__TRAIT_EQUALIZER_TEST__.data().personas.length, traits: window.__TRAIT_EQUALIZER_TEST__.data().traits.length, models: Object.keys(window.__TRAIT_EQUALIZER_TEST__.models()).length})")
            initial = cdp.evaluate("window.__TRAIT_EQUALIZER_TEST__.snapshot()")
            axes_hidden_in_3d = cdp.evaluate("document.getElementById('axis-controls').hidden && getComputedStyle(document.getElementById('axis-controls')).display === 'none'")

            all_lopo_browser_error = cdp.evaluate("""(() => {
              const api=window.__TRAIT_EQUALIZER_TEST__, data=api.data(), models=api.models(), core=window.TraitProfileGeometryCore;
              let maximum=0;
              for (const persona of data.personas) {
                const prediction=core.predictRidge(persona.profile,models[persona.name]);
                prediction.forEach((value,index)=>{maximum=Math.max(maximum,Math.abs(value-persona.saved_lopo_prediction[index]));});
              }
              return maximum;
            })()""")

            baseline_error = cdp.evaluate("(() => { const s=window.__TRAIT_EQUALIZER_TEST__.snapshot(); const saved=window.__TRAIT_EQUALIZER_TEST__.data().personas.find(p=>p.name===s.persona).saved_lopo_prediction; return Math.max(...s.prediction.map((v,i)=>Math.abs(v-saved[i]))); })()")

            expression = f"""(async () => {{
              const api=window.__TRAIT_EQUALIZER_TEST__;
              await api.selectPersona({json.dumps(test_case['persona'])});
              const edits={json.dumps(test_case['edits'])};
              for (const edit of edits) api.setTraitPercentile(edit.trait, edit.modified_percentile, false);
              await api.updatePrediction();
              return api.snapshot();
            }})()"""
            modified = cdp.evaluate(expression)
            modified_prediction_error = max_abs(modified["prediction"], test_case["expected_prediction"])
            ood_error = max(
                abs(modified["ood"][key] - test_case["expected_ood"][key])
                for key in (
                    "nearest_neighbor_distance",
                    "mean_5nn_distance",
                    "distance_percentile_vs_canonical_loo",
                    "profile_pca_reconstruction_error",
                    "reconstruction_error_percentile_vs_canonical",
                )
            )

            cdp.evaluate("(async()=>{await window.__TRAIT_EQUALIZER_TEST__.setView('2d'); await window.__TRAIT_EQUALIZER_TEST__.setAxes(2,0); return true;})()")
            projected = cdp.evaluate("window.__TRAIT_EQUALIZER_TEST__.snapshot()")
            axes_visible_in_2d = cdp.evaluate("!document.getElementById('axis-controls').hidden && getComputedStyle(document.getElementById('axis-controls')).display !== 'none'")
            projection_error = max_abs(
                projected["projected_prediction"],
                [projected["prediction"][2], projected["prediction"][0]],
            )

            reset = cdp.evaluate("(async()=>{await window.__TRAIT_EQUALIZER_TEST__.resetAll(); return window.__TRAIT_EQUALIZER_TEST__.snapshot();})()")
            reset_profile_error = max_abs(reset["current_profile"], reset["baseline_profile"])
            saved_prediction = cdp.evaluate("(() => { const s=window.__TRAIT_EQUALIZER_TEST__.snapshot(); return window.__TRAIT_EQUALIZER_TEST__.data().personas.find(item=>item.name===s.persona).saved_lopo_prediction; })()")
            reset_prediction_error = max_abs(reset["prediction"], saved_prediction)

            camera_error = cdp.evaluate("""(async()=>{
              const api=window.__TRAIT_EQUALIZER_TEST__;
              await api.setView('3d');
              const camera={eye:{x:1.73,y:-1.21,z:.84},center:{x:.08,y:-.04,z:.02},up:{x:0,y:0,z:1}};
              await Plotly.relayout('geometry-plot',{'scene.camera':camera});
              await new Promise(resolve=>setTimeout(resolve,80));
              const before=api.snapshot().camera;
              api.setTraitPercentile(7,Math.min(100,api.snapshot().current_percentiles[7]+4),false);
              await api.updatePrediction();
              const after=document.getElementById('geometry-plot')._fullLayout.scene.camera;
              const values=(c)=>[c.eye.x,c.eye.y,c.eye.z,c.center.x,c.center.y,c.center.z,c.up.x,c.up.y,c.up.z];
              return Math.max(...values(before).map((value,index)=>Math.abs(value-values(after)[index])));
            })()""")

            # Exercise the real search/load button and plot-click handler rather than only the test API.
            cdp.evaluate("document.getElementById('persona-input').value='actor'; document.getElementById('load-persona').click(); true", await_promise=False)
            wait_condition(cdp, "window.__TRAIT_EQUALIZER_TEST__.snapshot().persona === 'actor'")
            dom_selected = cdp.evaluate("window.__TRAIT_EQUALIZER_TEST__.snapshot().persona")
            cdp.evaluate("document.getElementById('geometry-plot').emit('plotly_click',{points:[{customdata:'spy'}]}); true", await_promise=False)
            wait_condition(cdp, "window.__TRAIT_EQUALIZER_TEST__.snapshot().persona === 'spy'")
            plot_selected = cdp.evaluate("window.__TRAIT_EQUALIZER_TEST__.snapshot().persona")

            # Exercise a native slider event, changed-only filtering, and Reset all.
            dom_interaction = cdp.evaluate("""(async()=>{
              const slider=document.querySelector('.trait-row input[type=range]');
              slider.value=String(Math.min(100,Number(slider.value)+7));
              slider.dispatchEvent(new Event('input',{bubbles:true}));
              await new Promise(resolve=>setTimeout(resolve,250));
              document.getElementById('changed-only').checked=true;
              document.getElementById('changed-only').dispatchEvent(new Event('change',{bubbles:true}));
              const visible=[...document.querySelectorAll('.trait-row')].filter(row=>!row.hidden).length;
              const changed=window.__TRAIT_EQUALIZER_TEST__.snapshot().changed_traits.length;
              document.getElementById('reset-all').click();
              await new Promise(resolve=>setTimeout(resolve,250));
              return {visible,changed,afterReset:window.__TRAIT_EQUALIZER_TEST__.snapshot().changed_traits.length};
            })()""")
            layout = cdp.evaluate("""(() => {
              const canvas=document.querySelector('#geometry-plot canvas');
              let renderer='unavailable';
              try {
                const gl=canvas && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
                const extension=gl && gl.getExtension('WEBGL_debug_renderer_info');
                if (extension) renderer=gl.getParameter(extension.UNMASKED_RENDERER_WEBGL);
              } catch (_) {}
              return {bodyOverflow:document.body.scrollWidth-document.documentElement.clientWidth,plotTraces:document.getElementById('geometry-plot').data.length,canvasCount:document.querySelectorAll('#geometry-plot canvas').length,webglError:document.getElementById('geometry-plot').textContent.includes('WebGL is not supported'),webglRenderer:renderer,userAgent:navigator.userAgent};
            })()""")

            checks = {
                "live_browser": True,
                "browser_user_agent": layout["userAgent"],
                "persona_count": counts["personas"],
                "trait_count": counts["traits"],
                "held_out_model_count": counts["models"],
                "initial_persona": initial["persona"],
                "axis_controls_hidden_in_3d": axes_hidden_in_3d,
                "axis_controls_visible_in_2d": axes_visible_in_2d,
                "maximum_all_275_browser_lopo_error": all_lopo_browser_error,
                "maximum_initial_baseline_lopo_error": baseline_error,
                "modified_case_id": test_case["case_id"],
                "modified_prediction_python_agreement_error": modified_prediction_error,
                "modified_ood_python_agreement_error": ood_error,
                "projection_2d_from_3d_error": projection_error,
                "reset_profile_error": reset_profile_error,
                "reset_prediction_error": reset_prediction_error,
                "camera_preservation_error_after_edit": camera_error,
                "persona_list_selection_result": dom_selected,
                "scatter_selection_result": plot_selected,
                "native_slider_changed_count": dom_interaction["changed"],
                "changed_only_visible_count": dom_interaction["visible"],
                "reset_all_changed_count": dom_interaction["afterReset"],
                "body_horizontal_overflow_pixels": layout["bodyOverflow"],
                "rendered_plot_trace_count": layout["plotTraces"],
                "rendered_plot_canvas_count": layout["canvasCount"],
                "webgl_error_visible": layout["webglError"],
                "webgl_renderer": layout["webglRenderer"],
                "hardware_gpu_used": False,
            }
            passed = (
                counts == {"personas": 275, "traits": 240, "models": 275}
                and baseline_error <= 1e-9
                and axes_hidden_in_3d
                and axes_visible_in_2d
                and all_lopo_browser_error <= 1e-9
                and modified_prediction_error <= 1e-9
                and ood_error <= 1e-9
                and projection_error == 0
                and reset_profile_error == 0
                and reset_prediction_error <= 1e-9
                and camera_error <= 1e-12
                and dom_selected == "actor"
                and plot_selected == "spy"
                and dom_interaction["changed"] == 1
                and dom_interaction["visible"] == 1
                and dom_interaction["afterReset"] == 0
                and layout["bodyOverflow"] <= 0
                and layout["plotTraces"] >= 10
                and layout["canvasCount"] >= 1
                and not layout["webglError"]
                and "swiftshader" in layout["webglRenderer"].lower()
            )
            report = {
                "schema_version": "1.0",
                "test_type": "Live headless Google Chrome interaction test over a local HTTP server",
                "checks": checks,
                "passed": passed,
            }
            if args.write_report:
                REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(json.dumps(report, indent=2, sort_keys=True))
            if not passed:
                raise SystemExit(1)
        finally:
            if cdp is not None:
                with contextlib.suppress(Exception):
                    cdp.close()
            process.terminate()
            with contextlib.suppress(subprocess.TimeoutExpired):
                process.wait(timeout=5)
            if process.poll() is None:
                process.kill()
    server.shutdown()
    server.server_close()


if __name__ == "__main__":
    main()
