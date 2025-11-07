/* Responsibilities:
   - Live user search and 'invite' action via fetch()
   - Add member: show success/error alerts with BS5 markup
   - Delete member buttons: call server, then redirect/reload; show error modal on failure
   - Small UX touches: spinner while loading, debounced input, safe DOM updates
*/

/** Debounce utility */
function debounce(fn, delay = 250) {
    let t;
    return (...args) => {
        clearTimeout(t);
        t = setTimeout(() => fn.apply(null, args), delay);
    };
}

/** Render a Bootstrap 5 alert (dismissible) */
function renderAlert(kind, html) {
    // kind: 'success' | 'danger' | 'warning' | 'info'
    return [
        `<div class="alert alert-${kind} alert-dismissible fade show" role="alert">`,
        `  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`,
        '  <div class="row g-2">',
        '    <div class="col-1 alert-icon-col" aria-hidden="true">',
        kind === 'success' ? '      <span class="oi oi-check"></span>' :
            kind === 'warning' ? '      <span class="oi oi-warning"></span>' :
                kind === 'danger' ? '      <span class="oi oi-warning"></span>' : '      <span class="oi oi-info"></span>',
        '    </div>',
        `    <div class="col">${html}</div>`,
        '  </div>',
        '</div>'
    ].join('\n');
}

/** Helper to GET JSON or text depending on expected type */
async function httpGet(url, expect = 'json') {
    const resp = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return expect === 'json' ? resp.json() : resp.text();
}

/** Add a user to the organization */
async function addUser(user) {
    const result = document.getElementById('user_search_result');
    if (!result) return;
    // Spinner (Open Iconic fallback)
    result.innerHTML = '<span class="oi oi-cog" title="waiting" aria-hidden="true"></span>';

    httpGet(`${window.ORG_ADD_URL}?user=${encodeURIComponent(user)}`, 'json')
        .then((data) => {
            result.innerHTML = '';
            result.insertAdjacentHTML('beforeend', renderAlert('success', data.message));
        })
        .catch(async (err) => {
            result.innerHTML = '';
            let html;
            // Try to get error JSON from response if available
            try {
                // Try to fetch error body (assuming server returns JSON error)
                const resp = await fetch(`${window.ORG_ADD_URL}?user=${encodeURIComponent(user)}`, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const errorData = await resp.json();
                html = errorData?.message;
            } catch (_) {
                html = null;
            }
            if (!html) {
                html = window.TRANS_INVITE_GENERIC_ERROR || 'An unknown error happened. We could not invite this user.';
            }
            result.insertAdjacentHTML('beforeend', renderAlert('danger', html));
        });
}

/** Wire live search input */
function bindLiveSearch() {
    const input = document.getElementById('invite_user');
    const result = document.getElementById('user_search_result');
    if (!input || !result) return;

    const onType = debounce(async () => {
        const q = input.value.trim();
        if (!q) {
            result.innerHTML = '';
            return;
        }
        try {
            const data = await httpGet(`${window.SEARCH_USERS_URL}?q=${encodeURIComponent(q)}`, 'json');
            result.innerHTML = '';
            (data.values || []).forEach((item) => {
                const id = `addUser_${CSS.escape(item)}`;
                const a = document.createElement('a');
                a.href = '#';
                a.id = id;
                a.className = 'list-group-item list-group-item-success list-group-item-action';
                a.innerHTML = `<span class="oi oi-plus" title="plus" aria-hidden="true"></span> ${item}`;
                a.addEventListener('click', (e) => {
                    e.preventDefault();
                    addUser(item);
                    input.value = '';
                    result.innerHTML = '';
                });
                result.appendChild(a);
            });
        } catch (e) {
            // Silent fail: keep previous content or clear
            result.innerHTML = '';
        }
    }, 250);

    input.addEventListener('keyup', onType);
}

/** Bind delete-member buttons */
function bindDeleteMember() {
    document.querySelectorAll('[data-action="delete-member"]').forEach((btn) => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const container = btn.closest('[data-member]');
            const memberName = container?.getAttribute('data-member');
            if (!memberName) return;
            try {
                await httpGet(`${window.ORG_DELETE_URL}?member=${encodeURIComponent(memberName)}`, 'text');
                if (memberName === (window.CURRENT_USERNAME || '')) {
                    window.location = window.DASHBOARD_URL || '/';
                } else {
                    window.location = window.location.href;
                }
            } catch (err) {
                // Show failure modal (Bootstrap 5)
                const modalEl = document.getElementById('member_delete_error_modal');
                if (modalEl) {
                    // eslint-disable-next-line no-undef
                    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
                    modal.show();
                }
            }
        });
    });
}


import(window.staticUrl("js/dashboard.js"));
// .then(({ initDashboard }) => initDashboard());


export function initOrg() {
    bindLiveSearch();
    bindDeleteMember();
}

window.onReady?.(initOrg);
