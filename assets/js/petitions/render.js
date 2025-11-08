/* Controls WYSIWYG-like inline editing for petitions. */
(function(){
  'use strict';

  const $ = (sel, root=document) => root.querySelector(sel);
  const $$ = (sel, root=document) => Array.from(root.querySelectorAll(sel));

  const container = $('.petition-layout');
  if (!container) return;
  const mode = container.dataset.mode || 'view';
  const petitionId = container.dataset.petitionId;

  // Toggle edit mode button (if present)
  const editBtn = $('#petition-edit-toggle');
  if (editBtn) {
    editBtn.addEventListener('click', () => {
      const newMode = container.dataset.mode === 'edit' ? 'view' : 'edit';
      container.dataset.mode = newMode;
      document.dispatchEvent(new CustomEvent('petition:mode', { detail: { mode: newMode } }));
    });
  }

  function makeEditable(el, {type='text', multiline=false} = {}){
    if (!el) return;
    el.setAttribute('contenteditable', 'true');
    el.addEventListener('blur', () => saveField(el));
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !multiline) {
        e.preventDefault();
        el.blur();
      }
    });
  }

  function saveField(el){
    const field = el.dataset.field;
    if (!field) return;
    const value = el.innerHTML.trim();
    // TODO: post to backend; placeholder emits event
    document.dispatchEvent(new CustomEvent('petition:save', { detail: { field, value } }));
  }

  // Activate editable fields when in edit mode
  function applyMode(){
    const isEdit = container.dataset.mode === 'edit';
    const fields = $$('.petition-main [data-field]');
    fields.forEach(el => {
      if (isEdit) makeEditable(el, { multiline: el.classList.contains('petition-body') });
      else el.removeAttribute('contenteditable');
    });
  }

  document.addEventListener('petition:mode', applyMode);
  applyMode();

  // Resources, Authors, News add/remove hooks (generic)
  function bindListActions(){
    // Authors
    $$('.author-remove').forEach(btn => btn.addEventListener('click', (e) => {
      const card = e.currentTarget.closest('.author-card');
      if (card) card.remove();
    }));
    const addAuthor = $('.author-add');
    if (addAuthor) addAuthor.addEventListener('click', () => {
      // Placeholder UI: emit event; actual modal should be provided by backend search view.
      alert(gettext('Open author picker modal'));
    });

    // Resources
    $$('.resource-remove').forEach(btn => btn.addEventListener('click', (e) => {
      const card = e.currentTarget.closest('.resource-card');
      if (card) card.remove();
    }));
    const addRes = $('.resource-add');
    if (addRes) addRes.addEventListener('click', () => {
      alert(gettext('Open file picker / uploader'));
    });

    // News
    const addNews = $('.news-add');
    if (addNews) addNews.addEventListener('click', () => {
      document.dispatchEvent(new CustomEvent('petition:news:add'));
    });
  }
  bindListActions();

  document.addEventListener('petition:news:add', () => {
    const list = $('.news-timeline');
    if (!list) return;
    const li = document.createElement('li');
    li.className = 'news-item';
    const today = new Date().toISOString().slice(0,10);
    li.innerHTML = '<div class="news-header"><time datetime="'+today+'">'+today+'</time> ' +
                   '<strong class="news-title">'+gettext('New update')+'</strong></div>' +
                   '<div class="news-body">'+gettext('Write your update here...')+'</div>';
    list.prepend(li);
  });

  // Sign FAB opens the sign form modal (handled in sign_modal.js)
  const signFab = $('#petition-sign-fab');
  if (signFab) signFab.addEventListener('click', () => {
    document.dispatchEvent(new CustomEvent('petition:sign:open'));
  });

})();