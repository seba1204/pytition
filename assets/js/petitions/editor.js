/* Petition editor controller (vanilla JS)
 * - Only fields with [data-field][data-editable="true"] are editable.
 * - TinyMCE inline editor opens on focus for the petition body (data-field="text").
 * - Placeholders are shown for empty fields (title, tagline, text).
 * - Emits 'petition:save' events with { field, value } on blur/changes.
 */
(function () {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const container = $('.petition-layout');
  if (!container) return;
  const petitionId = container.dataset.petitionId;
  const t = (s) => (typeof gettext === 'function' ? gettext(s) : s);

  const EDITABLE_SELECTOR = '[data-field][data-editable="true"]';
  const BODY_SELECTOR = '[data-field="text"][data-editable="true"]';

  const DEFAULT_PLACEHOLDERS = {
    title: t('Click to add a title'),
    tagline: t('Add a tagline'),
    text: t('Write your petition here...'),
  };

  function ensurePlaceholder(el) {
    const field = el.dataset.field;
    if (!field) return;
    const html = el.innerHTML.trim();
    if (!html || html === '&nbsp;' || html === '<br>') {
      el.classList.add('placeholder', 'text-muted');
      const ph = el.dataset.placeholder || DEFAULT_PLACEHOLDERS[field] || t('Click to edit');
      el.dataset._placeholderActive = '1';
      el.innerHTML = ph;
    }
  }

  function clearPlaceholder(el) {
    if (el.dataset._placeholderActive === '1') {
      el.innerHTML = '';
    }
    el.classList.remove('placeholder', 'text-muted');
    el.dataset._placeholderActive = '0';
  }

  function restorePlaceholderIfEmpty(el) {
    const html = (el.innerHTML || '').trim();
    if (!html || html === '<br>') ensurePlaceholder(el);
  }

  function emitSave(el, customValue) {
    const field = el.dataset.field;
    if (!field) return;
    const value = (customValue !== undefined) ? customValue : el.innerHTML.trim();
    const detail = { petitionId, field, value };
    document.dispatchEvent(new CustomEvent('petition:save', { detail }));
  }

  function setEditable(el, on) {
    if (!el) return;
    if (on) {
      el.setAttribute('contenteditable', 'true');
      const singleLine = !el.matches(BODY_SELECTOR);
      el._keydownHandler = (e) => {
        if (singleLine && e.key === 'Enter') {
          e.preventDefault();
          el.blur();
        }
      };
      el.addEventListener('keydown', el._keydownHandler);
      el._blurHandler = () => {
        emitSave(el);
        restorePlaceholderIfEmpty(el);
      };
      el.addEventListener('blur', el._blurHandler);
    } else {
      el.removeAttribute('contenteditable');
      if (el._keydownHandler) el.removeEventListener('keydown', el._keydownHandler);
      if (el._blurHandler) el.removeEventListener('blur', el._blurHandler);
      delete el._keydownHandler;
      delete el._blurHandler;
    }
  }

  function attachInlineTinyMCE(el) {
    if (!el.matches(BODY_SELECTOR)) return;
    if (typeof window.tinymce === 'undefined' || !window.tinymce) return;

    const existing = window.tinymce.get(el.id);
    if (existing) return;
    if (!el.id) el.id = 'pet-body-' + Math.random().toString(36).slice(2);

    const startEditor = () => {
      window.AppEditors.initTinyMCE(textInput, {
        plugins: 'link lists table media image autoresize',
        min_height: 480,
        autoresize_bottom_margin: 16,
        autoresize_overflow_padding: 8,
        toolbar_sticky: true,
        mobile: {
          toolbar_sticky: true,
          toolbar_sticky_offset: 56,
        },
        setup: (ed) => {
          editor = ed;
          ed.on('blur', () => {
            setTimeout(() => { if (editor) leaveTextEdit(); }, 0);
          });
        },
      });
    };
  }

  function applyPlaceholders() {
    const allFields = $$('[data-field]');
    allFields.forEach((el) => {
      const editable = el.getAttribute('data-editable') === 'true';
      const hasContent = (el.textContent || '').trim() !== '';
      if (!hasContent) {
        const key = el.dataset.field;
        const ph = el.dataset.placeholder || DEFAULT_PLACEHOLDERS[key] || t('Click to edit');
        if (editable) {
          el.classList.add('text-muted', 'placeholder');
          el.dataset._placeholderActive = '1';
          el.innerHTML = ph;
        } else {
          el.classList.add('text-muted');
          if (!el.innerHTML.trim()) el.innerHTML = ph;
        }
      }
    });
  }

  function onBodyFocus(ev) {
    const el = ev.currentTarget;
    clearPlaceholder(el);
    attachInlineTinyMCE(el);
  }

  function applyMode() {
    const isEdit = (container.dataset.mode || 'view') === 'edit';
    const editables = $$(EDITABLE_SELECTOR, container);
    editables.forEach((el) => setEditable(el, isEdit));
    const bodyEl = $(BODY_SELECTOR, container);
    if (bodyEl) {
      if (isEdit) bodyEl.addEventListener('focus', onBodyFocus);
      else bodyEl.removeEventListener('focus', onBodyFocus);
    }
    applyPlaceholders();
  }

  const editBtn = $('#petition-edit-toggle');
  if (editBtn) {
    editBtn.addEventListener('click', () => {
      const current = container.dataset.mode || 'view';
      const next = current === 'edit' ? 'view' : 'edit';
      container.dataset.mode = next;
      document.dispatchEvent(new CustomEvent('petition:mode', { detail: { mode: next } }));
    });
  }

  document.addEventListener('petition:mode', applyMode);
  applyMode();
})();
