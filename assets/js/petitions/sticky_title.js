(function () {
    'use strict';

    const titles = document.querySelectorAll('.petition-title');
    if (!titles.length || !('IntersectionObserver' in window)) return;

    // Sentinel sits just above the title; when it leaves the viewport (top),
    // we consider the title "stuck".
    titles.forEach((title) => {
        const sentinel = document.createElement('div');
        sentinel.setAttribute('aria-hidden', 'true');
        sentinel.style.position = 'absolute';
        sentinel.style.top = `${(title.offsetTop || 0) - 1}px`;
        sentinel.style.left = '0';
        sentinel.style.width = '1px';
        sentinel.style.height = '1px';
        // title.parentElement?.style.position = 'relative';
        title.parentElement?.appendChild(sentinel);

        const io = new IntersectionObserver(
            (entries) => {
                const e = entries[0];
                const isStuck = e.boundingClientRect.top < 56 && e.intersectionRatio === 0;
                // Toggle sticky class on both display and input titles
                document.querySelectorAll('.petition-title').forEach((el) => {
                    el.classList.toggle('is-sticky', isStuck);
                });
            },
            { root: null, threshold: [0], rootMargin: `-56px 0px 0px 0px` }
        );

        io.observe(sentinel);

    });
})();
