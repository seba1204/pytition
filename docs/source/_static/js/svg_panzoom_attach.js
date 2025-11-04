(function () {
    const INLINE_SVG = 'svg.zoomable-svg';
    const OBJ_SVG = 'object.zoomable-svg[type="image/svg+xml"]';

    function ensureViewBox(svg) {
        if (!svg.getAttribute('viewBox')) {
            const w = parseFloat(svg.getAttribute('width')) || svg.clientWidth || 800;
            const h = parseFloat(svg.getAttribute('height')) || svg.clientHeight || 600;
            if (w && h) svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
        }
    }

    function attachPanZoomToSvg(svg) {
        if (!svg || svg.__panzoomApplied) return;
        if (typeof window.svgPanZoom !== 'function') return;
        ensureViewBox(svg);
        window.svgPanZoom(svg, {
            zoomEnabled: true,
            controlIconsEnabled: true,
            fit: true,
            center: true,
            dblClickZoomEnabled: true,
            mouseWheelZoomEnabled: true,
            preventMouseEventsDefault: true,
            minZoom: 0.5,
            maxZoom: 20
        });
        svg.__panzoomApplied = true;
        svg.style.touchAction = 'none';
        svg.classList.add('is-panzoom-enabled');
    }

    function scanInline() {
        document.querySelectorAll(INLINE_SVG).forEach(attachPanZoomToSvg);
    }

    function scanObjects() {
        document.querySelectorAll(OBJ_SVG).forEach(obj => {
            if (obj.__observer) return;
            const onLoad = () => {
                try {
                    const doc = obj.contentDocument;
                    if (!doc) return;
                    const svg = doc.querySelector('svg');
                    if (!svg) return;

                    const SVG_NS = 'http://www.w3.org/2000/svg';
                    const style = doc.createElementNS(SVG_NS, 'style');
                    style.setAttribute('type', 'text/css');
                    style.textContent = `
                    svg { display: block; max-width: 100%; height: auto; }
                    svg.is-panzoom-enabled { cursor: grab; }
                    `;

                    if (!doc.__zoomStyleInjected) {
                        svg.insertBefore(style, svg.firstChild);
                        doc.__zoomStyleInjected = true;
                    }

                    attachPanZoomToSvg(svg);

                    svg.addEventListener('mousedown', () => svg.style.cursor = 'grabbing');
                    svg.addEventListener('mouseup', () => svg.style.cursor = 'grab');
                    svg.addEventListener('mouseleave', () => svg.style.cursor = 'grab');
                } catch (e) {
                    // probably a cross-origin issue; ignore
                }
            };

            obj.addEventListener('load', onLoad);
            if (obj.contentDocument) onLoad();

            const mo = new MutationObserver(() => onLoad());
            mo.observe(obj, { childList: true, subtree: true });
            obj.__observer = mo;
        });
    }

    function scanAll() { scanInline(); scanObjects(); }

    function onReady(cb) {
        if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', cb);
        else cb();
    }

    const pageObserver = new MutationObserver((muts) => {
        for (const m of muts) {
            if ([...m.addedNodes].some(n =>
                (n.nodeType === 1) && (
                    n.matches?.(INLINE_SVG) || n.querySelector?.(INLINE_SVG) ||
                    n.matches?.(OBJ_SVG) || n.querySelector?.(OBJ_SVG)
                )
            )) { scanAll(); break; }
        }
    });

    onReady(() => {
        scanAll();
        pageObserver.observe(document.body, { childList: true, subtree: true });
    });

    window.__attachSvgPanZoom = scanAll;
})();
