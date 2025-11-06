/* Responsibilities:
   - Initialize tooltips (data-bs-toggle="tooltip").
   - Handle delete actions for templates and petitions via GET fetch (server-side endpoints).
   - Toggle favorites with optional fast-UX (color change) when a hash is present.
   - Publish/unpublish toggle with spinner, label update, and error fallback.
*/

/** Initialize Bootstrap 5 tooltips */
function initTooltips() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
        new bootstrap.Tooltip(el);
    });
}

/** Helper to GET a URL and return text */
async function get(url) {
    const resp = await fetch(url, { method: "GET", headers: { "X-Requested-With": "XMLHttpRequest" } });
    if (!resp.ok) throw new Error(`Request failed: ${resp.status}`);
    return resp.text();
}

/** Toggle picture color (fast feedback while staying consistent with server) */
function toggleTemplatePictureClass(el) {
    const cls = el.classList;
    if (cls.contains("text-warning")) {
        cls.remove("text-warning");
        cls.add("text-dark");
    } else {
        cls.remove("text-dark");
        cls.add("text-warning");
    }
}

/** Attach handlers for template deletion */
function bindTemplateDelete() {
    document.querySelectorAll('[data-action="template-delete"]').forEach((btn) => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            const root = btn.closest("[data-template-delete]");
            const url = root?.getAttribute("data-template-delete");
            if (!url) return;
            try {
                await get(url);
                // If on /edit, go back to dashboard, else reload
                if (window.location.href.endsWith("/edit")) {
                    window.location = window.DASHBOARD_URL || "{{ dashboard }}"; // Template fallback if injected
                } else {
                    window.location = window.location.href;
                }
            } catch (_) {
                // Best-effort: soft reload to reflect server state
                window.location = window.location.href;
            }
        });
    });
}

/** Attach handlers for petition deletion */
function bindPetitionDelete() {
    document.querySelectorAll('[data-action="petition-delete"]').forEach((btn) => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            const root = btn.closest("[data-petition-delete]");
            const url = root?.getAttribute("data-petition-delete");
            if (!url) return;
            try {
                await get(url);
            } finally {
                window.location = window.location.href;
            }
        });
    });
}

/** Attach handlers for favorite toggle */
function bindFavoriteToggle() {
    document.querySelectorAll('[data-fav-toggle="true"]').forEach((el) => {
        console.log("Binding fav toggle", el);
        el.addEventListener("click", async (e) => {
            e.preventDefault();
            const root = el.closest("[data-template-fav]");
            const url = root?.getAttribute("data-template-fav");
            if (!url) return;
            try {
                await get(url);
                const hasHash = !!document.location.hash;
                if (hasHash) {
                    // there is a hash, so we can do fast-UX
                    toggleTemplatePictureClass(el);
                } else {
                    // No hash, just reload to reflect server state
                    window.location = window.location.href;
                }
            } catch (_) {
                // On error, do nothing drastic, user can retry
            }
        });
    });
}

/** Handle publish/unpublish switch interactions (Bootstrap 5 form-switch) */
function bindPublishToggle() {
    // Each switch is expected to be inside data-petition-[id|publish|unpublish] wrappers
    document.querySelectorAll('[data-action="publish"] input[type="checkbox"]').forEach((box) => {
        box.addEventListener("change", async () => {
            // Temporarily revert UI while processing
            const publishRequested = box.checked;
            box.checked = !publishRequested;

            const container = box.closest("[data-petition-id]");
            const petitionId = container?.getAttribute("data-petition-id");
            const publishUrl = box.closest("[data-petition-publish]")?.getAttribute("data-petition-publish");
            const unpublishUrl = box.closest("[data-petition-unpublish]")?.getAttribute("data-petition-unpublish");
            const label = box.parentElement?.querySelector("label") || box.labels?.[0];

            // Add spinner next to label
            const loaderId = `loader_${petitionId || Math.random().toString(36).slice(2)}`;
            const spinner = document.createElement("div");
            spinner.id = loaderId;
            spinner.className = "spinner-border spinner-border-sm ms-1";
            spinner.setAttribute("role", "status");
            const sr = document.createElement("span");
            sr.className = "visually-hidden";
            sr.textContent = "Loading...";
            spinner.appendChild(sr);
            label?.insertAdjacentElement("afterend", spinner);

            box.disabled = true;
            try {
                const url = publishRequested ? publishUrl : unpublishUrl;
                if (!url) throw new Error("Missing publish/unpublish URL");
                await get(url);

                // Toggle state after server confirms
                const nowChecked = !box.checked;
                box.checked = nowChecked;

                if (label) {
                    label.textContent = nowChecked ? "{{ _('Not published') }}" : "{{ _('Published') }}";
                }

                // Remove any previous failure alert for this petition
                const failure = document.getElementById(`failed_${petitionId}`);
                if (failure) failure.remove();
            } catch (_) {
                // Re-enable after a short delay and show a friendly alert
                setTimeout(() => {
                    box.disabled = false;
                    document.getElementById(loaderId)?.remove();
                    if (!document.getElementById(`failed_${petitionId}`)) {
                        const alert = document.createElement("div");
                        alert.id = `failed_${petitionId}`;
                        alert.className = "alert alert-danger mt-2";
                        alert.setAttribute("role", "alert");
                        const action = box.checked ? "unpublish" : "publish";
                        alert.textContent = `Failed to ${action} the petition, try again or refresh the page`;
                        label?.insertAdjacentElement("afterend", alert);
                    }
                }, 800);
                return;
            }
            // Success path teardown
            box.disabled = false;
            document.getElementById(loaderId)?.remove();
        });
    });
}


export function initDashboard() {
    initTooltips();
    bindTemplateDelete();
    bindPetitionDelete();
    bindFavoriteToggle();
    bindPublishToggle();
}

window.onReady?.(initDashboard);




