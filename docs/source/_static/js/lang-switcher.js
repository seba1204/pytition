(function () {
    "use strict";

    /**
     * Compute and navigate to the page for the chosen language.
     * Exposed globally for manual calls if needed.
     * @param {string} docRoot - Path to the docs root from current page (e.g., "../../")
     * @param {string} pageName - Sphinx pagename (without .html)
     * @param {string} lang - Target language code (e.g., "fr")
     * @param {string} allLangsCsv - Comma-separated list of all language codes
     */
    function switchLanguage(pageName, lang, allLangsCsv) {
        const allLangs = (allLangsCsv || "")
            .split(",").map(s => s.trim()).filter(Boolean);

        // Normalize current path
        const path = window.location.pathname.replace(/\/+/g, "/");
        const segments = path.split("/").filter(Boolean); // ["en","guide","intro.html"] par ex.

        // Find current language segment
        let langIdx = segments.findIndex(s => allLangs.includes(s));

        let rest = [];
        if (langIdx !== -1) {
            // Everything after current lang is the rest of the page path
            rest = segments.slice(langIdx + 1);
        } else {
            // No explicit lang in URL; use pagename from Sphinx
            rest = (pageName || "").replace(/^\/+/, "").split("/").filter(Boolean);
        }

        // Ensure last segment has .html (Sphinx pages)
        if (rest.length === 0) {
            rest = ["index.html"];
        } else {
            const last = rest[rest.length - 1];
            if (!/\.html?$/.test(last)) {
                rest[rest.length - 1] = last + ".html";
            }
        }

        // Build new path: /<lang>/<rest...>
        const newSegments = [lang, ...rest];
        const newPath = "/" + newSegments.join("/");

        // Keep query/hash if present
        const target = new URL(window.location.href);
        target.pathname = newPath;
        window.location.href = target.toString();
    }

    // Auto-bind: find the select with data attributes and attach change handler
    function bindLangSelect() {
        const sel = document.querySelector(".lang-switcher select#lang-select");
        if (!sel) return;
        const container = sel.closest(".lang-switcher");
        const pageName = container?.dataset.pageName || "";
        const langsCsv = container?.dataset.langs || "";
        sel.addEventListener("change", function () {
            switchLanguage(pageName, this.value, langsCsv);
        });
    }

    // Expose function if you want to call it from template or console
    window.SphinxLangSwitch = { switchLanguage };

    // Ensure binding after DOM ready (and safe with deferred scripts)
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bindLangSelect);
    } else {
        bindLangSelect();
    }

})();
