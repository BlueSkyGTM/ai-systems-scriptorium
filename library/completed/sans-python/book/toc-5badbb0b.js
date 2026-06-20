// Populate the sidebar
//
// This is a script, and not included directly in the page, to control the total size of the book.
// The TOC contains an entry for each page, so if each page includes a copy of the TOC,
// the total size of the page becomes O(n**2).
class MDBookSidebarScrollbox extends HTMLElement {
    constructor() {
        super();
    }
    connectedCallback() {
        this.innerHTML = '<ol class="chapter"><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="preface.html">Preface</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="index.html">Introduction</a></span></li><li class="chapter-item expanded "><li class="spacer"></li></li><li class="chapter-item expanded "><li class="part-title">Module 1: Foundations</li></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module1/index.html"><strong aria-hidden="true">1.</strong> Overview</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module1/01-dev-environment.html"><strong aria-hidden="true">2.</strong> The Day-One Stack</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module1/02-your-first-llm-call.html"><strong aria-hidden="true">3.</strong> Your First LLM Call</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module1/03-attention.html"><strong aria-hidden="true">4.</strong> Attention</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module1/04-transformer-era-nlp.html"><strong aria-hidden="true">5.</strong> Transformer-Era NLP</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module1/05-retrieval-and-eval-foundations.html"><strong aria-hidden="true">6.</strong> Foundations of Retrieval and Evaluation</a></span></li><li class="chapter-item expanded "><li class="part-title">Module 2: LLM Engineering</li></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module2/index.html"><strong aria-hidden="true">7.</strong> Overview</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module2/01-prompt-engineering.html"><strong aria-hidden="true">8.</strong> Prompt Engineering</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module2/02-context-engineering.html"><strong aria-hidden="true">9.</strong> Context Engineering</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module2/03-rag-system.html"><strong aria-hidden="true">10.</strong> The RAG System</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module2/04-advanced-rag.html"><strong aria-hidden="true">11.</strong> Advanced RAG</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module2/05-evaluation.html"><strong aria-hidden="true">12.</strong> Evaluation</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module2/06-structured-output-and-tools.html"><strong aria-hidden="true">13.</strong> Structured Output &amp; Tools</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module2/07-the-complexity-ladder.html"><strong aria-hidden="true">14.</strong> The Complexity Ladder</a></span></li><li class="chapter-item expanded "><li class="part-title">Module 3: Agent Foundations</li></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module3/index.html"><strong aria-hidden="true">15.</strong> Overview</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module3/01-the-agent-loop.html"><strong aria-hidden="true">16.</strong> The Agent Loop</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module3/02-planning.html"><strong aria-hidden="true">17.</strong> Planning</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module3/03-learning-from-failure.html"><strong aria-hidden="true">18.</strong> Learning from Failure</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module3/04-typescript-break-in.html"><strong aria-hidden="true">19.</strong> TypeScript Break-In</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module3/05-typing-the-product-layer.html"><strong aria-hidden="true">20.</strong> Typing the Product Layer</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module3/06-tool-use.html"><strong aria-hidden="true">21.</strong> Tool Use</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module3/07-mcp-fundamentals.html"><strong aria-hidden="true">22.</strong> MCP Fundamentals</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module3/08-mcp-capabilities.html"><strong aria-hidden="true">23.</strong> MCP Capabilities</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module3/09-mcp-security-and-scale.html"><strong aria-hidden="true">24.</strong> MCP Security and Scale</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module3/10-memory-tiers-and-stores.html"><strong aria-hidden="true">25.</strong> Memory Tiers and Stores</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module3/11-memory-that-improves.html"><strong aria-hidden="true">26.</strong> Memory That Improves</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module3/12-frameworks-and-the-four-primitives.html"><strong aria-hidden="true">27.</strong> Frameworks and the Four Primitives</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module3/13-design-patterns-and-anti-patterns.html"><strong aria-hidden="true">28.</strong> Design Patterns and Anti-Patterns</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module3/14-the-workbench-surfaces-i.html"><strong aria-hidden="true">29.</strong> The Workbench Surfaces I</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module3/15-the-workbench-surfaces-ii-and-the-pack.html"><strong aria-hidden="true">30.</strong> The Workbench Surfaces II &amp; the Pack</a></span></li><li class="chapter-item expanded "><li class="part-title">Module 4: Multi-Agent Systems</li></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module4/index.html"><strong aria-hidden="true">31.</strong> Overview</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module4/01-why-multi-agent.html"><strong aria-hidden="true">32.</strong> Why Multi-Agent</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module4/02-communication-protocols.html"><strong aria-hidden="true">33.</strong> Communication Protocols</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module4/03-four-primitives-and-orchestration.html"><strong aria-hidden="true">34.</strong> The Four Primitives &amp; Orchestration</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module4/04-debate-and-failure-modes.html"><strong aria-hidden="true">35.</strong> Debate &amp; Failure Modes</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module4/05-long-horizon-durable-execution.html"><strong aria-hidden="true">36.</strong> Long-Horizon &amp; Durable Execution</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module4/06-action-budgets-and-cost-governors.html"><strong aria-hidden="true">37.</strong> Action Budgets &amp; Cost Governors</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module4/07-kill-switches-circuit-breakers-canary-tokens.html"><strong aria-hidden="true">38.</strong> Kill Switches, Circuit Breakers, Canary Tokens</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module4/08-hitl-and-checkpoints.html"><strong aria-hidden="true">39.</strong> HITL &amp; Checkpoints</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module4/09-guardrails.html"><strong aria-hidden="true">40.</strong> Guardrails</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module4/10-the-loop.html"><strong aria-hidden="true">41.</strong> The Loop</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module4/11-loop-patterns.html"><strong aria-hidden="true">42.</strong> Loop Patterns</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module4/12-the-fleet.html"><strong aria-hidden="true">43.</strong> The Fleet</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module4/13-fleet-patterns.html"><strong aria-hidden="true">44.</strong> Fleet Patterns &amp; Governance-as-Code</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module4/14-computer-use-and-coding-agents.html"><strong aria-hidden="true">45.</strong> Computer-Use &amp; Coding Agents</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module4/15-voice-and-benchmarks.html"><strong aria-hidden="true">46.</strong> Voice Agents &amp; Benchmarks</a></span></li><li class="chapter-item expanded "><li class="part-title">Module 5: Deploy &amp; Performance Engineering</li></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/index.html"><strong aria-hidden="true">47.</strong> Overview</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/01-serving-engines.html"><strong aria-hidden="true">48.</strong> Serving Engines</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/02-inside-the-engine.html"><strong aria-hidden="true">49.</strong> Inside the Engine</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/03-optimization-levers.html"><strong aria-hidden="true">50.</strong> Optimization Levers</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/04-inference-metrics-and-load-testing.html"><strong aria-hidden="true">51.</strong> Inference Metrics &amp; Load Testing</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/05-safe-rollout.html"><strong aria-hidden="true">52.</strong> Safe Rollout</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/06-observability-sre-for-ai.html"><strong aria-hidden="true">53.</strong> Observability &amp; SRE-for-AI</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/07-security-and-compliance.html"><strong aria-hidden="true">54.</strong> Security &amp; Compliance</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/08-token-finops.html"><strong aria-hidden="true">55.</strong> Token FinOps</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/09-measure-before-you-optimize.html"><strong aria-hidden="true">56.</strong> Measure Before You Optimize</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/10-the-performance-checklist.html"><strong aria-hidden="true">57.</strong> The Performance Checklist</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/11-data-ingestion-docling.html"><strong aria-hidden="true">58.</strong> Data Ingestion (Docling)</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/12-experiment-tracking.html"><strong aria-hidden="true">59.</strong> Experiment Tracking</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/13-fine-tuning-in-proportion.html"><strong aria-hidden="true">60.</strong> Fine-Tuning in Proportion</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/14-the-data-seam.html"><strong aria-hidden="true">61.</strong> The Data Seam</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/15-rust-break-in.html"><strong aria-hidden="true">62.</strong> Rust Break-In</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module5/16-async-rust-for-serving.html"><strong aria-hidden="true">63.</strong> async Rust for Serving</a></span></li><li class="chapter-item expanded "><li class="part-title">Module 6: Agent Artifacts</li></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module6/index.html"><strong aria-hidden="true">64.</strong> Overview</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module6/01-terminal-coding-agent.html"><strong aria-hidden="true">65.</strong> Terminal Coding Agent</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module6/02-production-rag-chatbot.html"><strong aria-hidden="true">66.</strong> Production RAG Chatbot</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module6/03-realtime-voice-assistant.html"><strong aria-hidden="true">67.</strong> Real-Time Voice Assistant</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module6/04-issue-to-pr-agent.html"><strong aria-hidden="true">68.</strong> Issue-to-PR Autonomous Agent</a></span></li><li class="chapter-item expanded "><li class="part-title">Module 7: Multi-Agent Artifacts</li></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module7/index.html"><strong aria-hidden="true">69.</strong> Overview</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module7/01-autonomous-research-agent.html"><strong aria-hidden="true">70.</strong> Autonomous Research Agent</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module7/02-devops-k8s-agent.html"><strong aria-hidden="true">71.</strong> DevOps K8s Troubleshooting Agent</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module7/03-governed-multi-agent-fleet.html"><strong aria-hidden="true">72.</strong> Governed Multi-Agent Fleet (Finale)</a></span></li><li class="chapter-item expanded "><li class="part-title">Module 8: Final Systems Engineering Exam</li></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module8/index.html"><strong aria-hidden="true">73.</strong> Overview</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module8/01-the-exam.html"><strong aria-hidden="true">74.</strong> The Exam</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module8/02-reference-architectures.html"><strong aria-hidden="true">75.</strong> Reference Architectures</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="module8/03-operating-and-grading.html"><strong aria-hidden="true">76.</strong> Operating and Grading</a></span></li><li class="chapter-item expanded "><span class="chapter-link-wrapper"><a href="conclusion.html"><strong aria-hidden="true">77.</strong> Conclusion</a></span></li></ol>';
        // Set the current, active page, and reveal it if it's hidden
        let current_page = document.location.href.toString().split('#')[0].split('?')[0];
        if (current_page.endsWith('/')) {
            current_page += 'index.html';
        }
        const links = Array.prototype.slice.call(this.querySelectorAll('a'));
        const l = links.length;
        for (let i = 0; i < l; ++i) {
            const link = links[i];
            const href = link.getAttribute('href');
            if (href && !href.startsWith('#') && !/^(?:[a-z+]+:)?\/\//.test(href)) {
                link.href = path_to_root + href;
            }
            // The 'index' page is supposed to alias the first chapter in the book.
            // Check both with and without the '.html' suffix to be robust against pretty URLs
            if (link.href.replace(/\.html$/, '') === current_page.replace(/\.html$/, '')
                || i === 0
                && path_to_root === ''
                && current_page.endsWith('/index.html')) {
                link.classList.add('active');
                let parent = link.parentElement;
                while (parent) {
                    if (parent.tagName === 'LI' && parent.classList.contains('chapter-item')) {
                        parent.classList.add('expanded');
                    }
                    parent = parent.parentElement;
                }
            }
        }
        // Track and set sidebar scroll position
        this.addEventListener('click', e => {
            if (e.target.tagName === 'A') {
                const clientRect = e.target.getBoundingClientRect();
                const sidebarRect = this.getBoundingClientRect();
                sessionStorage.setItem('sidebar-scroll-offset', clientRect.top - sidebarRect.top);
            }
        }, { passive: true });
        const sidebarScrollOffset = sessionStorage.getItem('sidebar-scroll-offset');
        sessionStorage.removeItem('sidebar-scroll-offset');
        if (sidebarScrollOffset !== null) {
            // preserve sidebar scroll position when navigating via links within sidebar
            const activeSection = this.querySelector('.active');
            if (activeSection) {
                const clientRect = activeSection.getBoundingClientRect();
                const sidebarRect = this.getBoundingClientRect();
                const currentOffset = clientRect.top - sidebarRect.top;
                this.scrollTop += currentOffset - parseFloat(sidebarScrollOffset);
            }
        } else {
            // scroll sidebar to current active section when navigating via
            // 'next/previous chapter' buttons
            const activeSection = document.querySelector('#mdbook-sidebar .active');
            if (activeSection) {
                activeSection.scrollIntoView({ block: 'center' });
            }
        }
        // Toggle buttons
        const sidebarAnchorToggles = document.querySelectorAll('.chapter-fold-toggle');
        function toggleSection(ev) {
            ev.currentTarget.parentElement.parentElement.classList.toggle('expanded');
        }
        Array.from(sidebarAnchorToggles).forEach(el => {
            el.addEventListener('click', toggleSection);
        });
    }
}
window.customElements.define('mdbook-sidebar-scrollbox', MDBookSidebarScrollbox);


// ---------------------------------------------------------------------------
// Support for dynamically adding headers to the sidebar.

(function() {
    // This is used to detect which direction the page has scrolled since the
    // last scroll event.
    let lastKnownScrollPosition = 0;
    // This is the threshold in px from the top of the screen where it will
    // consider a header the "current" header when scrolling down.
    const defaultDownThreshold = 150;
    // Same as defaultDownThreshold, except when scrolling up.
    const defaultUpThreshold = 300;
    // The threshold is a virtual horizontal line on the screen where it
    // considers the "current" header to be above the line. The threshold is
    // modified dynamically to handle headers that are near the bottom of the
    // screen, and to slightly offset the behavior when scrolling up vs down.
    let threshold = defaultDownThreshold;
    // This is used to disable updates while scrolling. This is needed when
    // clicking the header in the sidebar, which triggers a scroll event. It
    // is somewhat finicky to detect when the scroll has finished, so this
    // uses a relatively dumb system of disabling scroll updates for a short
    // time after the click.
    let disableScroll = false;
    // Array of header elements on the page.
    let headers;
    // Array of li elements that are initially collapsed headers in the sidebar.
    // I'm not sure why eslint seems to have a false positive here.
    // eslint-disable-next-line prefer-const
    let headerToggles = [];
    // This is a debugging tool for the threshold which you can enable in the console.
    let thresholdDebug = false;

    // Updates the threshold based on the scroll position.
    function updateThreshold() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;

        // The number of pixels below the viewport, at most documentHeight.
        // This is used to push the threshold down to the bottom of the page
        // as the user scrolls towards the bottom.
        const pixelsBelow = Math.max(0, documentHeight - (scrollTop + windowHeight));
        // The number of pixels above the viewport, at least defaultDownThreshold.
        // Similar to pixelsBelow, this is used to push the threshold back towards
        // the top when reaching the top of the page.
        const pixelsAbove = Math.max(0, defaultDownThreshold - scrollTop);
        // How much the threshold should be offset once it gets close to the
        // bottom of the page.
        const bottomAdd = Math.max(0, windowHeight - pixelsBelow - defaultDownThreshold);
        let adjustedBottomAdd = bottomAdd;

        // Adjusts bottomAdd for a small document. The calculation above
        // assumes the document is at least twice the windowheight in size. If
        // it is less than that, then bottomAdd needs to be shrunk
        // proportional to the difference in size.
        if (documentHeight < windowHeight * 2) {
            const maxPixelsBelow = documentHeight - windowHeight;
            const t = 1 - pixelsBelow / Math.max(1, maxPixelsBelow);
            const clamp = Math.max(0, Math.min(1, t));
            adjustedBottomAdd *= clamp;
        }

        let scrollingDown = true;
        if (scrollTop < lastKnownScrollPosition) {
            scrollingDown = false;
        }

        if (scrollingDown) {
            // When scrolling down, move the threshold up towards the default
            // downwards threshold position. If near the bottom of the page,
            // adjustedBottomAdd will offset the threshold towards the bottom
            // of the page.
            const amountScrolledDown = scrollTop - lastKnownScrollPosition;
            const adjustedDefault = defaultDownThreshold + adjustedBottomAdd;
            threshold = Math.max(adjustedDefault, threshold - amountScrolledDown);
        } else {
            // When scrolling up, move the threshold down towards the default
            // upwards threshold position. If near the bottom of the page,
            // quickly transition the threshold back up where it normally
            // belongs.
            const amountScrolledUp = lastKnownScrollPosition - scrollTop;
            const adjustedDefault = defaultUpThreshold - pixelsAbove
                + Math.max(0, adjustedBottomAdd - defaultDownThreshold);
            threshold = Math.min(adjustedDefault, threshold + amountScrolledUp);
        }

        if (documentHeight <= windowHeight) {
            threshold = 0;
        }

        if (thresholdDebug) {
            const id = 'mdbook-threshold-debug-data';
            let data = document.getElementById(id);
            if (data === null) {
                data = document.createElement('div');
                data.id = id;
                data.style.cssText = `
                    position: fixed;
                    top: 50px;
                    right: 10px;
                    background-color: 0xeeeeee;
                    z-index: 9999;
                    pointer-events: none;
                `;
                document.body.appendChild(data);
            }
            data.innerHTML = `
                <table>
                  <tr><td>documentHeight</td><td>${documentHeight.toFixed(1)}</td></tr>
                  <tr><td>windowHeight</td><td>${windowHeight.toFixed(1)}</td></tr>
                  <tr><td>scrollTop</td><td>${scrollTop.toFixed(1)}</td></tr>
                  <tr><td>pixelsAbove</td><td>${pixelsAbove.toFixed(1)}</td></tr>
                  <tr><td>pixelsBelow</td><td>${pixelsBelow.toFixed(1)}</td></tr>
                  <tr><td>bottomAdd</td><td>${bottomAdd.toFixed(1)}</td></tr>
                  <tr><td>adjustedBottomAdd</td><td>${adjustedBottomAdd.toFixed(1)}</td></tr>
                  <tr><td>scrollingDown</td><td>${scrollingDown}</td></tr>
                  <tr><td>threshold</td><td>${threshold.toFixed(1)}</td></tr>
                </table>
            `;
            drawDebugLine();
        }

        lastKnownScrollPosition = scrollTop;
    }

    function drawDebugLine() {
        if (!document.body) {
            return;
        }
        const id = 'mdbook-threshold-debug-line';
        const existingLine = document.getElementById(id);
        if (existingLine) {
            existingLine.remove();
        }
        const line = document.createElement('div');
        line.id = id;
        line.style.cssText = `
            position: fixed;
            top: ${threshold}px;
            left: 0;
            width: 100vw;
            height: 2px;
            background-color: red;
            z-index: 9999;
            pointer-events: none;
        `;
        document.body.appendChild(line);
    }

    function mdbookEnableThresholdDebug() {
        thresholdDebug = true;
        updateThreshold();
        drawDebugLine();
    }

    window.mdbookEnableThresholdDebug = mdbookEnableThresholdDebug;

    // Updates which headers in the sidebar should be expanded. If the current
    // header is inside a collapsed group, then it, and all its parents should
    // be expanded.
    function updateHeaderExpanded(currentA) {
        // Add expanded to all header-item li ancestors.
        let current = currentA.parentElement;
        while (current) {
            if (current.tagName === 'LI' && current.classList.contains('header-item')) {
                current.classList.add('expanded');
            }
            current = current.parentElement;
        }
    }

    // Updates which header is marked as the "current" header in the sidebar.
    // This is done with a virtual Y threshold, where headers at or below
    // that line will be considered the current one.
    function updateCurrentHeader() {
        if (!headers || !headers.length) {
            return;
        }

        // Reset the classes, which will be rebuilt below.
        const els = document.getElementsByClassName('current-header');
        for (const el of els) {
            el.classList.remove('current-header');
        }
        for (const toggle of headerToggles) {
            toggle.classList.remove('expanded');
        }

        // Find the last header that is above the threshold.
        let lastHeader = null;
        for (const header of headers) {
            const rect = header.getBoundingClientRect();
            if (rect.top <= threshold) {
                lastHeader = header;
            } else {
                break;
            }
        }
        if (lastHeader === null) {
            lastHeader = headers[0];
            const rect = lastHeader.getBoundingClientRect();
            const windowHeight = window.innerHeight;
            if (rect.top >= windowHeight) {
                return;
            }
        }

        // Get the anchor in the summary.
        const href = '#' + lastHeader.id;
        const a = [...document.querySelectorAll('.header-in-summary')]
            .find(element => element.getAttribute('href') === href);
        if (!a) {
            return;
        }

        a.classList.add('current-header');

        updateHeaderExpanded(a);
    }

    // Updates which header is "current" based on the threshold line.
    function reloadCurrentHeader() {
        if (disableScroll) {
            return;
        }
        updateThreshold();
        updateCurrentHeader();
    }


    // When clicking on a header in the sidebar, this adjusts the threshold so
    // that it is located next to the header. This is so that header becomes
    // "current".
    function headerThresholdClick(event) {
        // See disableScroll description why this is done.
        disableScroll = true;
        setTimeout(() => {
            disableScroll = false;
        }, 100);
        // requestAnimationFrame is used to delay the update of the "current"
        // header until after the scroll is done, and the header is in the new
        // position.
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                // Closest is needed because if it has child elements like <code>.
                const a = event.target.closest('a');
                const href = a.getAttribute('href');
                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);
                if (targetElement) {
                    threshold = targetElement.getBoundingClientRect().bottom;
                    updateCurrentHeader();
                }
            });
        });
    }

    // Takes the nodes from the given head and copies them over to the
    // destination, along with some filtering.
    function filterHeader(source, dest) {
        const clone = source.cloneNode(true);
        clone.querySelectorAll('mark').forEach(mark => {
            mark.replaceWith(...mark.childNodes);
        });
        dest.append(...clone.childNodes);
    }

    // Scans page for headers and adds them to the sidebar.
    document.addEventListener('DOMContentLoaded', function() {
        const activeSection = document.querySelector('#mdbook-sidebar .active');
        if (activeSection === null) {
            return;
        }

        const main = document.getElementsByTagName('main')[0];
        headers = Array.from(main.querySelectorAll('h2, h3, h4, h5, h6'))
            .filter(h => h.id !== '' && h.children.length && h.children[0].tagName === 'A');

        if (headers.length === 0) {
            return;
        }

        // Build a tree of headers in the sidebar.

        const stack = [];

        const firstLevel = parseInt(headers[0].tagName.charAt(1));
        for (let i = 1; i < firstLevel; i++) {
            const ol = document.createElement('ol');
            ol.classList.add('section');
            if (stack.length > 0) {
                stack[stack.length - 1].ol.appendChild(ol);
            }
            stack.push({level: i + 1, ol: ol});
        }

        // The level where it will start folding deeply nested headers.
        const foldLevel = 3;

        for (let i = 0; i < headers.length; i++) {
            const header = headers[i];
            const level = parseInt(header.tagName.charAt(1));

            const currentLevel = stack[stack.length - 1].level;
            if (level > currentLevel) {
                // Begin nesting to this level.
                for (let nextLevel = currentLevel + 1; nextLevel <= level; nextLevel++) {
                    const ol = document.createElement('ol');
                    ol.classList.add('section');
                    const last = stack[stack.length - 1];
                    const lastChild = last.ol.lastChild;
                    // Handle the case where jumping more than one nesting
                    // level, which doesn't have a list item to place this new
                    // list inside of.
                    if (lastChild) {
                        lastChild.appendChild(ol);
                    } else {
                        last.ol.appendChild(ol);
                    }
                    stack.push({level: nextLevel, ol: ol});
                }
            } else if (level < currentLevel) {
                while (stack.length > 1 && stack[stack.length - 1].level > level) {
                    stack.pop();
                }
            }

            const li = document.createElement('li');
            li.classList.add('header-item');
            li.classList.add('expanded');
            if (level < foldLevel) {
                li.classList.add('expanded');
            }
            const span = document.createElement('span');
            span.classList.add('chapter-link-wrapper');
            const a = document.createElement('a');
            span.appendChild(a);
            a.href = '#' + header.id;
            a.classList.add('header-in-summary');
            filterHeader(header.children[0], a);
            a.addEventListener('click', headerThresholdClick);
            const nextHeader = headers[i + 1];
            if (nextHeader !== undefined) {
                const nextLevel = parseInt(nextHeader.tagName.charAt(1));
                if (nextLevel > level && level >= foldLevel) {
                    const toggle = document.createElement('a');
                    toggle.classList.add('chapter-fold-toggle');
                    toggle.classList.add('header-toggle');
                    toggle.addEventListener('click', () => {
                        li.classList.toggle('expanded');
                    });
                    const toggleDiv = document.createElement('div');
                    toggleDiv.textContent = '❱';
                    toggle.appendChild(toggleDiv);
                    span.appendChild(toggle);
                    headerToggles.push(li);
                }
            }
            li.appendChild(span);

            const currentParent = stack[stack.length - 1];
            currentParent.ol.appendChild(li);
        }

        const onThisPage = document.createElement('div');
        onThisPage.classList.add('on-this-page');
        onThisPage.append(stack[0].ol);
        const activeItemSpan = activeSection.parentElement;
        activeItemSpan.after(onThisPage);
    });

    document.addEventListener('DOMContentLoaded', reloadCurrentHeader);
    document.addEventListener('scroll', reloadCurrentHeader, { passive: true });
})();

