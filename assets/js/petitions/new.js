/* All comments are in English. */
/* global tinymce, gettext */

(function () {
  'use strict';


  const page = document.querySelector('[data-page="petition-inline-create"]');
  if (!page) return;

  // Illustration: click to open file dialog + live preview.
  const illusDisplay = page.querySelector('[data-illustration="display"]');
  const illusInput = illusDisplay.querySelector('[data-illustration="input"]');
  const illusImg = illusDisplay.querySelector('[data-illustration="img"]');
  const realWrapper = illusDisplay.querySelector('[data-real]');
  const placeholderEl = illusDisplay.querySelector('[data-placeholder]');

  illusDisplay.addEventListener('click', () => illusInput.click());
  illusInput.addEventListener('change', () => {
    const file = illusInput.files && illusInput.files[0];
    if (!file) return;

    const url = URL.createObjectURL(file);
    // Show image after it’s loaded to avoid flicker
    illusImg.onload = () => {
      placeholderEl.classList.add('d-none');  // hide placeholder
      realWrapper.classList.remove('d-none'); // show 16:9 wrapper
      URL.revokeObjectURL(url);
    };
    illusImg.src = url;
  });


  // Title: toggle display <-> input
  const titleDisplay = page.querySelector('[data-field="title-display"]');
  const titleInput = page.querySelector('[data-field="title-input"]');
  const titleError = page.querySelector('[data-field="title-error"]');
  const TITLE_PLACEHOLDER = gettext('Click to add a title');

  function showTitlePlaceholder() {
    titleDisplay.innerHTML = `<span class="text-muted">${TITLE_PLACEHOLDER}</span>`;
  }

  function syncTitleDisplayFromInput() {
    const v = titleInput.value.trim();
    if (v) {
      titleDisplay.textContent = v;
    } else {
      showTitlePlaceholder();
    }
  }

  function setTitleError(msg /* string|null */) {
    if (msg) {
      titleInput.classList.add('is-invalid');
      titleError.textContent = msg;
    } else {
      titleInput.classList.remove('is-invalid');
      titleError.textContent = '';
    }
  }

  const enterTitleEdit = () => {
    // If display shows the placeholder, start with an empty input
    const isPlaceholder = !!titleDisplay.querySelector('.text-muted');
    titleInput.value = isPlaceholder ? '' : titleDisplay.textContent.trim();

    titleDisplay.classList.add('d-none');
    titleInput.classList.remove('d-none');
    titleInput.focus();
    titleInput.select();
  };

  const leaveTitleEdit = () => {
    const v = titleInput.value.trim();

    if (v && typeof setTitleError === 'function') {
      setTitleError(null);
    }

    syncTitleDisplayFromInput();

    titleInput.classList.add('d-none');
    titleDisplay.classList.remove('d-none');
  };


  titleDisplay.addEventListener('click', enterTitleEdit);
  titleInput.addEventListener('blur', leaveTitleEdit);
  titleInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); titleInput.blur(); }
    if (e.key === 'Escape') { e.preventDefault(); titleInput.value = ''; titleInput.blur(); }
  });
  titleInput.addEventListener('input', () => {
    syncTitleDisplayFromInput();
  });


  // Text (body): toggle display <-> TinyMCE
  const textDisplay = page.querySelector('[data-field="text-display"]');
  const textInput = page.querySelector('[data-field="text-input"]');

  let editor; // tinymce.Editor | undefined
  let isLeaving = false;


  const enterTextEdit = () => {
    // Put initial HTML into textarea
    if (editor) return;

    const currentHTML = textDisplay.innerHTML.trim();
    const isPlaceholder = textDisplay.querySelector('.text-muted') !== null;
    textInput.value = isPlaceholder ? '' : currentHTML;

    textDisplay.classList.add('d-none');
    textInput.classList.remove('d-none');

    // get finalCfg from global AppEditors config
    const finalCfg = window.AppEditors && window.AppEditors.getFinalConfig && window.AppEditors.getFinalConfig();



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

  function leaveTextEdit() {
    if (!editor || isLeaving) return;
    isLeaving = true;

    const ed = editor;
    const content = ed.getContent().trim();

    ed.off('blur');
    ed.remove();
    editor = undefined;
    isLeaving = false;

    textDisplay.innerHTML = content
      ? content
      : `<p class="text-muted m-0">${gettext('Click here to start writing your petition...')}</p>`;
    textInput.classList.add('d-none');
    textDisplay.classList.remove('d-none');
  }


  textDisplay.addEventListener('click', enterTextEdit);

  // Before submit: sync current “display” to inputs if still in view mode
  const form = page.querySelector('[data-form="petition"]');
  form.addEventListener('submit', async (e) => {
    // Sync possible edits
    if (!titleInput.classList.contains('d-none')) {
      titleInput.blur();
    }
    if (!textInput.classList.contains('d-none')) {
      await leaveTextEdit();
    } else if (editor) {
      await leaveTextEdit();
    }

    // Validation: require title (no alert, Bootstrap visual error)
    const titleVal = titleInput.value.trim();

    // reset error if you use it
    if (typeof setTitleError === 'function') setTitleError(null);

    if (!titleVal) {
      e.preventDefault();
      if (typeof setTitleError === 'function') {
        setTitleError(gettext('This field is required.'));
      }
      // keep field empty and visible for editing
      titleInput.classList.remove('d-none');
      titleDisplay.classList.add('d-none');
      titleInput.focus();
      // ensure display shows placeholder
      showTitlePlaceholder();
      return false;
    }
  });

  // Ensure initial state shows placeholder
  showTitlePlaceholder();

})();
