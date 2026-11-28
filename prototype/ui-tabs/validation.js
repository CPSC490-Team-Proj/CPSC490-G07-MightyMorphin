// Page 3 "Validate extracted information" (#88). Talks to the FastAPI
// prototype in prototype/validation/. The screen only mirrors the rules;
// the backend enforces every one of them (sequence diagram #87).
'use strict';

const el = (id) => document.getElementById(id);
const STATUS_TEXT = { PENDING: 'Pending', FLAGGED: 'Flagged', APPROVED: 'Approved', REJECTED: 'Rejected' };
const DOC_TYPE_TEXT = { COC: 'CoC', TEST_REPORT: 'Test report' };

let current = null;     // last record loaded from GET /records/{id}
let busy = false;

function text(tag, value, className) {
    const node = document.createElement(tag);
    node.textContent = value;
    if (className) node.className = className;
    return node;
}

function showFeedback(kind, message, items) {
    const box = el('feedback');
    box.className = kind || '';
    box.replaceChildren(text('span', message));
    if (items && items.length) {
        const list = document.createElement('ul');
        items.forEach((item) => list.appendChild(text('li', item)));
        box.appendChild(list);
    }
}

async function api(method, path, body) {
    const options = { method, headers: {} };
    if (method !== 'GET') {
        // The backend accepts writes only as JSON (blocks cross-site form posts).
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(body === undefined ? {} : body);
    }
    const response = await fetch(path, options);
    let data = null;
    try { data = await response.json(); } catch (_) { data = null; }
    return { status: response.status, data };
}

function selectedId() {
    const id = new URLSearchParams(window.location.search).get('id');
    return /^\d+$/.test(id || '') ? id : '1';
}

async function fillPicker() {
    const { status, data } = await api('GET', '/records');
    if (status !== 200) throw new Error('records');
    const picker = el('record-picker');
    picker.replaceChildren();
    data.forEach((r) => {
        const option = text('option', `#${r.record_id} ${r.filename} (${STATUS_TEXT[r.review_status]})`);
        option.value = String(r.record_id);
        picker.appendChild(option);
    });
    picker.value = selectedId();
}

function fieldRow(label, inputId, value, opts) {
    const row = document.createElement('tr');
    row.dataset.key = opts.key;
    row.appendChild(text('th', label)).scope = 'row';

    const cell = document.createElement('td');
    const input = document.createElement('input');
    input.type = 'text';
    input.id = inputId;
    input.value = value === null || value === undefined ? '' : value;
    input.defaultValue = input.value;
    input.setAttribute('aria-label', label);
    input.disabled = opts.readOnly;
    if (opts.numeric) input.inputMode = 'decimal';
    cell.appendChild(input);
    if (opts.unit) cell.appendChild(text('span', opts.unit, 'unit'));
    cell.appendChild(text('div', '', 'field-error'));
    row.appendChild(cell);

    const flagCell = document.createElement('td');
    if (opts.flag) {
        flagCell.appendChild(text('span', opts.flag, 'flag'));
        if (!opts.readOnly && opts.flag !== 'Missing value') {
            const confirm = document.createElement('label');
            confirm.className = 'confirm';
            const box = document.createElement('input');
            box.type = 'checkbox';
            box.id = `${inputId}-confirm`;
            confirm.append(box, ' Checked against PDF');
            flagCell.appendChild(confirm);
        }
    } else {
        flagCell.appendChild(text('span', '--', 'flag none'));
    }
    if (opts.confidence !== undefined) {
        flagCell.appendChild(text('div', `Confidence ${Math.round(opts.confidence * 100)}%`, 'confirm'));
    }
    row.appendChild(flagCell);
    return row;
}

function render(data) {
    current = data;
    const r = data.record;
    const readOnly = data.read_only;
    el('title').textContent = `Review: ${r.filename}`;

    const flags = data.open_flags.length;
    const sub = el('subline');
    sub.replaceChildren(
        `Material ${r.material_code}  |  ${DOC_TYPE_TEXT[r.doc_type] || r.doc_type}  |  Status: `,
        text('span', STATUS_TEXT[r.review_status], `badge ${r.review_status}`),
        `  |  ${flags} field${flags === 1 ? '' : 's'} require${flags === 1 ? 's' : ''} attention`,
    );
    if (r.review_status === 'APPROVED') {
        sub.append(`  |  Approved by ${r.approved_by} at ${r.approved_at}`);
    }

    const rows = el('field-rows');
    rows.replaceChildren(
        fieldRow('Material ID', 'f-material', r.material_code, { key: 'material_code', readOnly }),
        fieldRow('Lot number', 'f-lot', r.lot_number, { key: 'lot_number', readOnly }),
        ...data.fields.map((f) => fieldRow(f.property_name, `f-value-${f.value_id}`, f.value, {
            key: `value:${f.value_id}`, unit: f.standard_unit, flag: f.flag_reason,
            confidence: f.confidence, numeric: true, readOnly,
        })),
    );

    const source = data.source || {};
    el('pdf-frame').classList.toggle('hidden', !source.available);
    el('pdf-missing').classList.toggle('hidden', readOnly || source.available);
    el('pdf-readonly').classList.toggle('hidden', !readOnly);
    if (source.available) {
        el('pdf-frame').src = source.pdf_url;
        el('open-pdf').href = source.pdf_url;
        el('open-pdf').removeAttribute('aria-disabled');
    } else {
        el('pdf-frame').removeAttribute('src');
        el('open-pdf').removeAttribute('href');
        el('open-pdf').setAttribute('aria-disabled', 'true');
        el('pdf-missing').textContent =
            `Source PDF ${source.problem}. The values cannot be checked against their source, so Approve is disabled.`;
    }

    el('note').value = '';
    el('note').disabled = readOnly;
    el('save-draft').disabled = readOnly;
    el('approve').disabled = readOnly || !source.available;

    el('loading').classList.add('hidden');
    el('screen').classList.remove('hidden');
}

function clearErrors() {
    document.querySelectorAll('#field-rows tr').forEach((row) => {
        row.classList.remove('has-error');
        row.querySelector('.field-error').textContent = '';
    });
}

function showErrors(errors) {
    Object.entries(errors).forEach(([key, message]) => {
        const row = document.querySelector(`#field-rows tr[data-key="${CSS.escape(key)}"]`);
        if (!row) return;
        row.classList.add('has-error');
        row.querySelector('.field-error').textContent = message;
    });
}

function isDirty() {
    const inputs = [...document.querySelectorAll('#field-rows input')];
    return inputs.some((i) => (i.type === 'checkbox' ? i.checked : i.value !== i.defaultValue))
        || el('note').value.trim() !== '';
}

function draftPayload() {
    return {
        material_code: el('f-material').value,
        lot_number: el('f-lot').value,
        note: el('note').value,
        values: current.fields.map((f) => {
            const box = el(`f-value-${f.value_id}-confirm`);
            return {
                value_id: f.value_id,
                value: el(`f-value-${f.value_id}`).value,
                unit: f.standard_unit,
                confirm: Boolean(box && box.checked),
            };
        }),
    };
}

function flagItems(flags) {
    return (flags || []).map((f) => `${f.property_name}: ${f.flag_reason}`);
}

async function load(id, keepFeedback) {
    el('loading').classList.remove('hidden');
    el('loading').textContent = 'Loading record...';
    try {
        const { status, data } = await api('GET', `/records/${id}`);
        if (status !== 200) {
            el('loading').textContent = (data && data.message) || `Could not load record ${id}.`;
            el('screen').classList.add('hidden');
            return;
        }
        render(data);
        if (!keepFeedback) {
            if (data.read_only) {
                showFeedback('', `This record is ${STATUS_TEXT[data.record.review_status].toLowerCase()} and opens read-only.`);
            } else if (!data.source.available) {
                showFeedback('err', 'Approval feedback: the source PDF cannot be checked, so this record cannot be approved.');
            } else if (data.open_flags.length) {
                showFeedback('warn', 'Approval feedback: resolve required flags first.', flagItems(data.open_flags));
            } else {
                showFeedback('', 'No open flags. Review the values against the PDF, then approve.');
            }
        }
    } catch (_) {
        el('loading').textContent =
            'The backend is not reachable. Start it from prototype/ with: uvicorn validation.app:create_app --factory';
        el('screen').classList.add('hidden');
    }
}

const DEMO_CONTROLS = ['record-picker', 'fail-next', 'reset-demo'];

function setBusy(on) {
    busy = on;
    DEMO_CONTROLS.forEach((id) => { el(id).disabled = on; });
    // Lock the fields too, so nothing typed during a request is lost when the
    // record is reloaded afterwards.
    const readOnly = !current || current.read_only;
    document.querySelectorAll('#field-rows input').forEach((input) => { input.disabled = on || readOnly; });
    el('note').disabled = on || readOnly;
    if (on) {
        el('save-draft').disabled = true;
        el('approve').disabled = true;
    }
}

async function refreshArmed() {
    // The simulated failure lives on the server; show what the server says.
    try {
        const { status, data } = await api('GET', '/demo/state');
        if (status === 200) el('fail-armed').classList.toggle('hidden', !data.fail_next_write);
    } catch (_) { /* leave the indicator as it is */ }
}

async function refreshPicker() {
    try { await fillPicker(); } catch (_) { /* the picker is only a demo aid */ }
}

async function run(action) {
    if (busy) return;
    setBusy(true);
    try {
        await action();
    } catch (_) {
        showFeedback('err', 'The backend did not answer. Reload the record to see what was saved.');
    } finally {
        setBusy(false);
        await refreshArmed();
        if (current && !current.read_only) {
            el('save-draft').disabled = false;
            el('approve').disabled = !current.source.available;
        }
    }
}

async function saveDraft(event) {
    event.preventDefault();
    if (busy) return;
    clearErrors();
    const id = current.record.record_id;
    await run(async () => {
        const payload = draftPayload();
        const { status, data } = await api('PUT', `/records/${id}/draft`, payload);
        if (status === 200) {
            await load(id, true);
            await refreshPicker();
            const noteOnly = data.events_recorded === 0 && payload.note.trim() !== '';
            if (noteOnly) {
                showFeedback('warn', 'Nothing changed, so nothing was recorded. A correction note is saved with a corrected or confirmed value.');
            } else if (data.open_flags.length) {
                showFeedback('warn', 'Draft saved. It is not approved. Flags still open:', flagItems(data.open_flags));
            } else {
                showFeedback('ok', 'Draft saved. All flags are resolved; the record can now be approved.');
            }
        } else if (status === 422 && data && data.errors) {
            showErrors(data.errors);
            showFeedback('err', `${data.message}.`);
        } else if (status === 422) {
            showFeedback('err', `${(data && data.message) || 'The request was not accepted'}.`);
        } else if (status === 409) {
            await load(id, true);
            showFeedback('err', `${data.message}. The record was reloaded read-only.`);
        } else {
            showFeedback('err', (data && data.message) || `Draft not saved (HTTP ${status}).`);
        }
    });
}

async function approve() {
    clearErrors();
    if (isDirty()) {
        showFeedback('warn', 'You have unsaved changes. Save the draft first; approval uses the saved values.');
        return;
    }
    const id = current.record.record_id;
    await run(async () => {
        const { status, data } = await api('POST', `/records/${id}/approve`);
        if (status === 200) {
            await load(id, true);
            await refreshPicker();
            showFeedback('ok', `Approved by ${data.approved_by} at ${data.approved_at}. The record is now approved and is returned by the approved-records API (GET /materials) that Materials (page 4) is meant to read.`);
        } else if (status === 409 && data.code === 'flags_open') {
            showFeedback('warn', 'Not approved. Resolve required flags first:', flagItems(data.open_flags));
        } else if (status === 409 && data.code === 'already_decided') {
            await load(id, true);
            showFeedback('err', `${data.message}. The record was reloaded read-only.`);
        } else {
            showFeedback('err', (data && data.message) || `Not approved (HTTP ${status}).`);
        }
    });
}

async function start() {
    el('review-form').addEventListener('submit', saveDraft);
    el('approve').addEventListener('click', approve);
    el('record-picker').addEventListener('change', async (e) => {
        const shown = current ? String(current.record.record_id) : selectedId();
        if (current && !current.read_only && isDirty()
                && !window.confirm('Discard your unsaved changes to this record?')) {
            e.target.value = shown;
            return;
        }
        history.replaceState(null, '', `?id=${e.target.value}`);
        setBusy(true);
        try { await load(e.target.value); } finally { setBusy(false); }
    });
    el('fail-next').addEventListener('click', async () => {
        try {
            await api('POST', '/demo/fail-next-write');
        } catch (_) {
            showFeedback('err', 'The backend is not reachable.');
        }
        await refreshArmed();
    });
    el('reset-demo').addEventListener('click', async () => {
        if (busy) return;
        if (current && !current.read_only && isDirty()
                && !window.confirm('Reset the demo and discard your unsaved changes?')) {
            return;
        }
        setBusy(true);
        try {
            const { status, data } = await api('POST', '/demo/reset');
            if (status !== 200) {
                showFeedback('err', (data && data.message) || `Reset failed (HTTP ${status}).`);
                return;
            }
            await refreshPicker();
            await load(selectedId());
            showFeedback('ok', 'Demo data reset.');
        } catch (_) {
            showFeedback('err', 'The backend is not reachable. Nothing was reset.');
        } finally {
            setBusy(false);
            await refreshArmed();
        }
    });
    await refreshPicker();
    await load(selectedId());
    await refreshArmed();
}

start();
