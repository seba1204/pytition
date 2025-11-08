/* Dynamically populate the owner_object <select> based on owner_content_type.
 *
 * How it works:
 * - Reads the AJAX endpoint from data-owner-objects-url on the owner_object widget.
 * - On change of #id_owner_content_type, fetches options and repopulates #id_owner_object.
 * - Keeps the hidden #id_owner_object_id in sync with the selected option.
 *
 * Assumptions:
 * - Form field IDs are Django-standard: id_owner_content_type, id_owner_object, id_owner_object_id.
 * - The admin endpoint returns: { results: [{ id: "123", label: "Foo (#123)" }, ...] }.
 */

(function () {
    function byId(id) {
        return /** @type {HTMLInputElement | HTMLSelectElement | null} */ (
            document.getElementById(id)
        );
    }

    function setOptions(selectEl, items) {
        // Clear previous options
        while (selectEl.options.length > 0) {
            selectEl.remove(0);
        }
        // Placeholder
        var placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "---------";
        selectEl.appendChild(placeholder);

        // Append results
        items.forEach(function (item) {
            var opt = document.createElement("option");
            opt.value = item.id;
            opt.textContent = item.label;
            selectEl.appendChild(opt);
        });
    }

    function fetchOwnerObjects(url, ctId, cb) {
        if (!url || !ctId) {
            cb([]);
            return;
        }
        var full = url + "?ct=" + encodeURIComponent(ctId);
        fetch(full, { credentials: "same-origin" })
            .then(function (r) {
                if (!r.ok) throw new Error("Network error");
                return r.json();
            })
            .then(function (data) {
                cb(Array.isArray(data.results) ? data.results : []);
            })
            .catch(function () {
                cb([]);
            });
    }

    function syncHidden(selected, hiddenInput) {
        // Keep hidden owner_object_id synchronized with selected owner object
        if (!hiddenInput) return;
        hiddenInput.value = selected ? String(selected.value) : "";
    }

    function init() {
        var ctSelect = /** @type {HTMLSelectElement|null} */ (byId("id_owner_content_type"));
        var objSelect = /** @type {HTMLSelectElement|null} */ (byId("id_owner_object"));
        var hiddenId = /** @type {HTMLInputElement|null} */ (byId("id_owner_object_id"));

        if (!ctSelect || !objSelect) return;

        // On owner_object change, sync hidden field.
        objSelect.addEventListener("change", function () {
            syncHidden(objSelect.selectedOptions[0], hiddenId);
        });

        // On owner_content_type change, reload options via AJAX.
        ctSelect.addEventListener("change", function () {
            var endpoint = objSelect.getAttribute("data-owner-objects-url") || "";
            var ctId = ctSelect.value;
            // Reset dropdown immediately with a placeholder
            setOptions(objSelect, []);
            syncHidden(null, hiddenId);
            if (!ctId) return;

            fetchOwnerObjects(endpoint, ctId, function (results) {
                setOptions(objSelect, results);
            });
        });

        // On initial load, ensure hidden field matches current selection.
        syncHidden(objSelect.selectedOptions[0], hiddenId);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
