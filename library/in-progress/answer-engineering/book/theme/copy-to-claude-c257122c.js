// Answer Engineering — per-lesson "Copy for Claude Code" handoff.
// Finds every <div class="claude-handoff" data-exercise="..."> in a lesson and adds a button that
// copies a structured payload to the clipboard. Paste it into Claude Code (repo open) to run the
// lesson's exercise and resume exactly where you left off.
(function () {
  "use strict";

  const COURSE = "Answer Engineering — The AI Engineer's Interview Framework";

  function buildPayload(node) {
    const h1 = document.querySelector("main h1");
    const title = h1 ? h1.textContent.trim() : document.title;
    const path = decodeURIComponent(location.pathname.replace(/\.html$/, ".md"));
    const exercise = node.getAttribute("data-exercise") || "";
    // The handoff text is the div's own prose, minus the button we inject.
    const task = node.getAttribute("data-task") ||
      Array.from(node.querySelectorAll("p")).map((p) => p.textContent.trim()).join("\n");

    return [
      `Course: ${COURSE}`,
      `Lesson: ${title}`,
      `Lesson file: ${path}`,
      exercise ? `Exercise: ${exercise}` : null,
      ``,
      `Task: ${task}`,
      ``,
      `The course repo is open. Read the lesson file and the exercise folder above, then start (or `,
      `resume) this lesson's exercise. Pick up from where the last session left off.`,
    ].filter((l) => l !== null).join("\n");
  }

  function addButton(node) {
    const btn = document.createElement("button");
    btn.className = "claude-handoff-btn";
    btn.type = "button";
    btn.textContent = "Copy for Claude Code";
    btn.addEventListener("click", async function () {
      const payload = buildPayload(node);
      try {
        await navigator.clipboard.writeText(payload);
      } catch (e) {
        // Fallback for non-secure contexts.
        const ta = document.createElement("textarea");
        ta.value = payload;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
      }
      const original = btn.textContent;
      btn.textContent = "Copied ✓";
      btn.classList.add("copied");
      setTimeout(function () {
        btn.textContent = original;
        btn.classList.remove("copied");
      }, 1600);
    });
    node.appendChild(btn);
  }

  function init() {
    document.querySelectorAll(".claude-handoff").forEach(addButton);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
