/* Sign form modal for mobile */
(function () {
  'use strict';

  let modal;
  function ensureModal() {
    if (modal) return modal;
    modal = document.createElement('div');
    modal.className = 'petition-sign-modal';
    modal.innerHTML = '<div class="modal-backdrop"></div><div class="modal-body"></div>';
    document.body.appendChild(modal);
    modal.querySelector('.modal-backdrop').addEventListener('click', close);
    return modal;
  }
  function open() {
    ensureModal();
    const form = document.querySelector('.petition-sign');
    if (!form) return;
    modal.querySelector('.modal-body').innerHTML = form.innerHTML;
    modal.classList.add('open');
  }
  function close() { if (modal) modal.classList.remove('open'); }

  document.addEventListener('petition:sign:open', open);
})();
