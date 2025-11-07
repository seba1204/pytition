/* All comments are in English. */
(function () {
    'use strict';
    const RESPONSIVE_IMG_CSS = 'img{max-width:100%;height:auto;display:block;}';

    // ---------- language helpers ----------
    function normalizeLang() {
        //
        const raw = (document.documentElement.getAttribute('lang') || 'en').toLowerCase(); // ex: fr, fr-fr
        const base = raw.replace('-', '_'); // fr_fr
        const full = base.includes('_')
            ? base.split('_')[0] + '_' + base.split('_')[1].toUpperCase() // fr_FR
            : base + '_' + base.toUpperCase();
        return { code: base.split('_')[0], full };
    }
    const lang = normalizeLang();
    const rtl = new Set(['ar', 'fa', 'he', 'ur']).has(lang.code);

    // ---------- tiny config merge ----------
    function deepMerge(target, source) {
        const isObj = (v) => v && typeof v === 'object' && !Array.isArray(v);
        const out = { ...target };
        for (const [k, v] of Object.entries(source || {})) {
            if (isObj(v) && isObj(out[k])) out[k] = deepMerge(out[k], v);
            else out[k] = v;
        }
        return out;
    }

    function getBaseConfig() {
        const el = document.getElementById('tinymce-config');
        if (!el) return {};
        try { return JSON.parse(el.textContent); } catch { return {}; }
    }

    const baseCfg = getBaseConfig();

    // ---------- public API ----------
    function initTinyMCE(target, overrides = {}) {
        if (!window.tinymce || !target) return;

        const uploadURL = window.TINYMCE_FILE_UPLOAD_URL || '/files/tinymce';

        // Defaults we always enforce globally
        const enforced = {
            language: lang.full,
            language_url: `/static/tinymce/langs/${lang.full}.js`,
            directionality: rtl ? 'rtl' : 'ltr',
            content_style: RESPONSIVE_IMG_CSS,
            images_upload_url: uploadURL,
        };

        const finalCfg = deepMerge(deepMerge(baseCfg, enforced), { target, ...overrides });
        window.tinymce.init(finalCfg);
    }

    // Expose a small namespace
    window.AppEditors = Object.freeze({
        initTinyMCE,
        lang, // {code, full}
        rtl,
    });

    // ---------- auto-init on simple usage ----------
    // If a page includes plain <textarea data-editor="tinymce">, init automatically:
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('textarea[data-editor="tinymce"]').forEach((ta) => {
            // Only auto-init if the textarea is actually visible (not for inline-edit hidden fields)
            const style = window.getComputedStyle(ta);
            const hidden = ta.classList.contains('d-none') || style.display === 'none' || style.visibility === 'hidden';
            if (!hidden) initTinyMCE(ta);
        });
    });
})();
