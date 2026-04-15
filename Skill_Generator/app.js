/* ══════════════════════════════════════════════════════════════════════════════
   SkillForge — app.js
   Application logic: state, navigation, rendering, clipboard, ZIP export.
   Depends on: prompts.js (loaded first), JSZip (loaded via CDN)
   ══════════════════════════════════════════════════════════════════════════════ */

(function () {
  "use strict";

  // ── Constants ────────────────────────────────────────────────────────────

  const FILE_EXTS    = { skill: "SKILL.md", agent: "system-prompt.md", script: "main.py" };
  const BADGE_CLASSES = { skill: "badge-skill", agent: "badge-agent", script: "badge-script" };
  const BADGE_LABELS  = { skill: "SKILL", agent: "AGENT", script: "SCRIPT" };

  const PHASE_IDS = ["phase-describe", "phase-blueprint", "phase-generate"];


  // ── State ────────────────────────────────────────────────────────────────

  let currentPhase    = 0;
  let problemText     = "";
  let blueprint       = null;
  let activeTabIdx    = -1;
  let componentOutputs = {};   // idx → saved content string


  // ── Utilities ────────────────────────────────────────────────────────────

  function esc(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function $(id) { return document.getElementById(id); }

  function copyToClipboard(text, btn) {
    navigator.clipboard.writeText(text).then(function () {
      if (!btn) return;
      var orig = btn.textContent;
      btn.textContent = "✓ Copied";
      btn.classList.add("copied");
      setTimeout(function () {
        btn.textContent = orig;
        btn.classList.remove("copied");
      }, 2000);
    });
  }


  // ── Navigation ───────────────────────────────────────────────────────────

  function goToPhase(n) {
    currentPhase = n;

    PHASE_IDS.forEach(function (id) {
      $(id).classList.add("hidden");
    });
    $(PHASE_IDS[n]).classList.remove("hidden");

    document.querySelectorAll(".step").forEach(function (el, i) {
      var label = el.textContent.replace(/^✓\s*/, "");
      if (i < n) {
        el.className = "step done";
        el.textContent = "✓ " + label;
      } else if (i === n) {
        el.className = "step active";
        el.textContent = label;
      } else {
        el.className = "step";
        el.textContent = label;
      }
    });
  }


  // ── Phase 0: Describe ────────────────────────────────────────────────────

  function loadExample(idx) {
    var textarea = $("problem-input");
    textarea.value = EXAMPLES[idx].text;
    problemText = EXAMPLES[idx].text;
  }

  function renderExamplePills() {
    var container = $("example-pills");
    container.innerHTML = EXAMPLES.map(function (ex, i) {
      return '<button class="example-pill" data-idx="' + i + '">' + esc(ex.title) + "</button>";
    }).join("");

    container.addEventListener("click", function (e) {
      var pill = e.target.closest(".example-pill");
      if (pill) loadExample(Number(pill.dataset.idx));
    });
  }

  function generateAnalysisPrompt() {
    problemText = $("problem-input").value.trim();
    if (!problemText) return;

    var prompt = ANALYSIS_PROMPT_TEMPLATE + problemText;
    $("analysis-prompt-output").textContent = prompt;
    goToPhase(1);
  }


  // ── Phase 1: Blueprint ───────────────────────────────────────────────────

  function parseBlueprint() {
    var raw   = $("blueprint-paste").value.trim();
    var errEl = $("blueprint-error");
    errEl.textContent = "";

    if (!raw) {
      errEl.textContent = "Please paste Copilot's JSON response.";
      return;
    }

    try {
      var jsonStr = raw;
      // Extract JSON from markdown fences if present
      var fenceMatch = raw.match(/```(?:json)?\s*([\s\S]*?)```/);
      if (fenceMatch) jsonStr = fenceMatch[1].trim();

      blueprint = JSON.parse(jsonStr);

      if (!blueprint.title || !blueprint.components || !Array.isArray(blueprint.components)) {
        throw new Error("Missing required fields: title, components");
      }

      componentOutputs = {};
      activeTabIdx = -1;
      renderBlueprintSummary();
      goToPhase(2);
    } catch (e) {
      errEl.textContent = "Failed to parse JSON: " + e.message;
    }
  }


  // ── Phase 2: Generate ────────────────────────────────────────────────────

  function renderBlueprintSummary() {
    var summary      = $("blueprint-summary");
    var complexClass = "complexity-" + (blueprint.complexity || "medium");

    summary.innerHTML =
      '<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px">' +
        "<div>" +
          '<h2 style="color:var(--accent);margin-bottom:6px">' + esc(blueprint.title) + "</h2>" +
          '<p style="font-size:13px;color:var(--text-muted);max-width:600px">' + esc(blueprint.summary) + "</p>" +
        "</div>" +
        '<div style="display:flex;gap:6px;flex-wrap:wrap">' +
          '<span class="complexity ' + complexClass + '">' + esc(blueprint.complexity || "medium") + "</span>" +
          (blueprint.tags || []).map(function (t) {
            return '<span class="tag">' + esc(t) + "</span>";
          }).join("") +
        "</div>" +
      "</div>";

    // Component count heading
    $("comp-count").textContent = "Components to Generate (" + blueprint.components.length + ")";

    // Component list
    $("comp-list").innerHTML = blueprint.components.map(function (c) {
      return (
        '<div class="comp-row">' +
          '<span class="badge ' + BADGE_CLASSES[c.type] + '">' + BADGE_LABELS[c.type] + "</span>" +
          '<div style="flex:1">' +
            '<div class="comp-name">' + esc(c.name) + "</div>" +
            '<div class="comp-purpose">' + esc(c.purpose) + "</div>" +
          "</div>" +
          '<span class="comp-ext">' + (FILE_EXTS[c.type] || "txt") + "</span>" +
        "</div>"
      );
    }).join("");

    renderTabs();
  }

  function renderTabs() {
    var tabsEl = $("comp-tabs");

    tabsEl.innerHTML = blueprint.components.map(function (c, i) {
      var status = componentOutputs[i] ? "done" : activeTabIdx === i ? "ready" : "pending";
      var active = activeTabIdx === i ? " active" : "";
      return (
        '<button class="tab' + active + '" data-tab="' + i + '">' +
          '<span class="status-dot ' + status + '"></span>' +
          '<span class="badge ' + BADGE_CLASSES[c.type] + '" style="font-size:10px;padding:1px 6px">' +
            BADGE_LABELS[c.type] +
          "</span>" +
          esc(c.name) +
          (componentOutputs[i] ? ' <span style="color:var(--success)">✓</span>' : "") +
        "</button>"
      );
    }).join("");

    // Delegate click
    tabsEl.onclick = function (e) {
      var tab = e.target.closest(".tab");
      if (tab) selectTab(Number(tab.dataset.tab));
    };

    // Show/hide export bar
    var allDone = blueprint.components.every(function (_, i) { return !!componentOutputs[i]; });
    $("export-bar").classList.toggle("hidden", !allDone);
  }

  function selectTab(idx) {
    activeTabIdx = idx;
    renderTabs();

    var comp  = blueprint.components[idx];
    var panel = $("active-panel");
    panel.classList.remove("hidden");

    var genPrompt = buildGenerationPrompt(comp, blueprint, problemText);
    var existing  = componentOutputs[idx] || "";
    var promptId  = "gen-prompt-" + idx;
    var pasteId   = "output-paste-" + idx;
    var previewId = "preview-" + idx;

    panel.innerHTML =
      '<div class="panel-header">' +
        "<div>" +
          '<span class="panel-title">' + esc(comp.name) + "</span>" +
          '<span class="panel-ext">' + (FILE_EXTS[comp.type] || "txt") + "</span>" +
        "</div>" +
      "</div>" +

      // Generation prompt
      '<div style="margin-bottom:20px">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">' +
          '<span class="section-label">Generation Prompt → copy to Copilot Chat</span>' +
          '<button class="btn-copy" data-copy="' + promptId + '">Copy</button>' +
        "</div>" +
        '<pre class="code-block" id="' + promptId + '" ' +
          'style="border-radius:8px;border:1px solid var(--border);max-height:250px;font-size:12px;">' +
          esc(genPrompt) +
        "</pre>" +
      "</div>" +

      // Paste area
      "<div>" +
        '<span class="section-label">Paste Copilot\'s Output</span>' +
        '<textarea class="paste-area" id="' + pasteId + '" ' +
          'placeholder="Paste the generated ' + comp.type + ' content from Copilot Chat here...">' +
          esc(existing) +
        "</textarea>" +
        '<div style="display:flex;gap:10px;margin-top:10px">' +
          '<button class="save-btn" data-save="' + idx + '">✓ Save ' + BADGE_LABELS[comp.type] + "</button>" +
          (existing
            ? '<button class="btn-copy" data-copy="' + pasteId + '" style="margin-top:0">Copy Output</button>'
            : "") +
        "</div>" +
      "</div>" +

      // Saved preview
      (existing
        ? '<div style="margin-top:20px">' +
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">' +
              '<span class="section-label">Saved Output Preview</span>' +
              '<button class="btn-copy" data-copy-raw="' + idx + '">Copy</button>' +
            "</div>" +
            '<pre class="code-block" id="' + previewId + '" ' +
              'style="border-radius:8px;border:1px solid var(--border);max-height:300px;">' +
              esc(existing) +
            "</pre>" +
          "</div>"
        : "");

    // Delegate clicks within panel
    panel.onclick = function (e) {
      var btn = e.target.closest("button");
      if (!btn) return;

      if (btn.dataset.copy) {
        var el = $(btn.dataset.copy);
        var text = el.tagName === "TEXTAREA" ? el.value : el.textContent;
        copyToClipboard(text, btn);
      }
      if (btn.dataset.copyRaw !== undefined) {
        copyToClipboard(componentOutputs[Number(btn.dataset.copyRaw)] || "", btn);
      }
      if (btn.dataset.save !== undefined) {
        saveOutput(Number(btn.dataset.save));
      }
    };
  }

  function saveOutput(idx) {
    var el  = $("output-paste-" + idx);
    var val = el.value.trim();
    if (!val) return;

    // Strip markdown fences if present
    var content = val;
    var fenceMatch = val.match(/^```[\w]*\n([\s\S]*?)\n```$/);
    if (fenceMatch) content = fenceMatch[1];

    componentOutputs[idx] = content;
    selectTab(idx);   // re-render tab panel
    renderTabs();     // update status dots + export bar
  }


  // ── Export ───────────────────────────────────────────────────────────────

  function exportAll() {
    if (typeof JSZip === "undefined") {
      alert("JSZip not loaded. Please check your internet connection.");
      return;
    }

    var zip        = new JSZip();
    var folderName = (blueprint.title || "skillforge-output")
      .toLowerCase().replace(/[^a-z0-9]+/g, "-");
    var folder = zip.folder(folderName);

    blueprint.components.forEach(function (comp, i) {
      if (!componentOutputs[i]) return;
      var safeName = comp.name.toLowerCase().replace(/[^a-z0-9]+/g, "-");
      var fileName;
      if (comp.type === "script")     fileName = safeName + ".py";
      else if (comp.type === "skill") fileName = safeName + "-SKILL.md";
      else                            fileName = safeName + "-system-prompt.md";
      folder.file(fileName, componentOutputs[i]);
    });

    // README
    var readme =
      "# " + blueprint.title + "\n\n" +
      blueprint.summary + "\n\n" +
      "Complexity: " + blueprint.complexity + "\n" +
      "Tags: " + (blueprint.tags || []).join(", ") + "\n\n" +
      "## Components\n\n" +
      blueprint.components.map(function (c) {
        return "- **" + c.name + "** (" + c.type + "): " + c.purpose;
      }).join("\n") +
      "\n\nGenerated by SkillForge\n";
    folder.file("README.md", readme);

    zip.generateAsync({ type: "blob" }).then(function (blob) {
      var url = URL.createObjectURL(blob);
      var a   = document.createElement("a");
      a.href     = url;
      a.download = folderName + ".zip";
      a.click();
      URL.revokeObjectURL(url);
    });
  }


  // ── Copy helper (for HTML onclick attributes) ────────────────────────────

  function copyText(elementId, btn) {
    var el   = $(elementId);
    var text = el.tagName === "TEXTAREA" || el.tagName === "INPUT" ? el.value : el.textContent;
    copyToClipboard(text, btn);
  }


  // ── Init ─────────────────────────────────────────────────────────────────

  function init() {
    renderExamplePills();

    $("problem-input").addEventListener("input", function () {
      problemText = this.value;
    });

    goToPhase(0);
  }

  document.addEventListener("DOMContentLoaded", init);


  // ── Public API (exposed on window for HTML onclick handlers) ──────────────

  window.SkillForge = {
    goToPhase:              goToPhase,
    generateAnalysisPrompt: generateAnalysisPrompt,
    parseBlueprint:         parseBlueprint,
    exportAll:              exportAll,
    copyText:               copyText,
    loadExample:            loadExample
  };

})();
