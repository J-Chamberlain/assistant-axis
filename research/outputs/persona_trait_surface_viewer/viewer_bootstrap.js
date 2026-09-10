/* Independent startup guard: runs before Plotly and the main viewer script. */
(function () {
  "use strict";
  var phase = "Loading the embedded chart engine";
  var problem = "";
  var complete = false;
  var timer;
  function paint() {
    var status = document.getElementById("render-status");
    var error = document.getElementById("error");
    var preview = document.getElementById("startup-preview");
    if (status && !complete) status.textContent = problem ? "Interactive view unavailable" : phase + "...";
    if (error) {
      error.style.display = problem ? "block" : "none";
      error.textContent = problem;
    }
    if (preview) preview.hidden = complete;
  }
  function fail(error) {
    complete = false;
    clearTimeout(timer);
    problem = "The prepared data is available, but the interactive view could not start. " +
      "Stage: " + phase + ". " + String(error && error.message ? error.message : error) +
      " Open the completed persona_trait_surface_viewer.html rather than the template. No new generation is running.";
    paint();
  }
  window.viewerBoot = {
    stage: function (name) { phase = name; paint(); },
    ready: function () { complete = true; problem = ""; clearTimeout(timer); paint(); },
    fail: fail,
    status: function () { return { phase: phase, complete: complete, problem: problem }; }
  };
  window.addEventListener("error", function (event) {
    if (!complete && event.message) fail(event.message);
  });
  window.addEventListener("unhandledrejection", function (event) {
    if (!complete) fail(event.reason || "An asynchronous startup operation failed.");
  });
  document.addEventListener("DOMContentLoaded", paint);
  timer = setTimeout(function () {
    if (!complete) fail("Startup exceeded 15 seconds. JavaScript may be blocked, or the 3D renderer may be unavailable.");
  }, 15000);
  paint();
})();
