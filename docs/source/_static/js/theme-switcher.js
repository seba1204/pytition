(function () {
    const SEL = 'object.themed-diagram[type="image/svg+xml"], img.themed-diagram';

    function currentTheme() {
        const t = document.documentElement.getAttribute('data-theme');
        if (t === 'dark' || t === 'light') return t;
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark' : 'light';
    }

    function pickSrc(el, theme) {
        const light = el.getAttribute('data-src-light');
        const dark = el.getAttribute('data-src-dark');
        if (theme === 'dark' && dark) return dark;
        if (theme === 'light' && light) return light;
        return (theme === 'dark' ? dark || light : light || dark) || null;
    }

    function apply(el, theme) {
        const next = pickSrc(el, theme);
        if (!next) return;

        if (el.tagName === 'OBJECT') {
            if (el.getAttribute('data') !== next) el.setAttribute('data', next);
        } else if (el.tagName === 'IMG') {
            if (el.getAttribute('src') !== next) el.setAttribute('src', next);
        }
    }

    function applyAll() {
        const theme = currentTheme();
        document.querySelectorAll(SEL).forEach(el => apply(el, theme));
    }

    function onReady(cb) {
        if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', cb);
        else cb();
    }

    onReady(() => {
        applyAll();

        const mo = new MutationObserver(muts => {
            if (muts.some(m => m.type === 'attributes' && m.attributeName === 'data-theme')) {
                applyAll();
            }
        });
        mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

        const pageMO = new MutationObserver(muts => {
            if (muts.some(m => [...m.addedNodes].some(n =>
                n?.nodeType === 1 && (n.matches?.(SEL) || n.querySelector?.(SEL))
            ))) applyAll();
        });
        pageMO.observe(document.body, { childList: true, subtree: true });

        if (window.matchMedia) {
            const mq = window.matchMedia('(prefers-color-scheme: dark)');
            mq.addEventListener?.('change', applyAll);
            mq.addListener?.(applyAll); // Safari <14
        }
    });
})();
