/* Minimal social sharing */
(function () {
  'use strict';
  const container = document.querySelector('.petition-share');
  if (!container) return;
  const url = encodeURIComponent(container.dataset.shareUrl || window.location.href);

  function openWin(href) {
    window.open(href, '_blank', 'noopener,noreferrer,width=600,height=500');
  }

  container.addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    const kind = btn.dataset.kind;
    if (kind === 'copy') {
      navigator.clipboard.writeText(decodeURIComponent(url)).then(() => {
        alert(gettext('Link copied to clipboard'));
      });
    } else if (kind === 'twitter') {
      openWin('https://twitter.com/intent/tweet?url=' + url);
    } else if (kind === 'facebook') {
      openWin('https://www.facebook.com/sharer/sharer.php?u=' + url);
    } else if (kind === 'linkedin') {
      openWin('https://www.linkedin.com/sharing/share-offsite/?url=' + url);
    } else if (kind === 'email') {
      window.location.href = 'mailto:?subject=' + encodeURIComponent(document.title) + '&body=' + url;
    }
  });
})();
