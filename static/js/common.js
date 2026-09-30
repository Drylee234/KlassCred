// ── KlassCred — shared utilities (loaded on every page) ──
var liveUrl = 'https://klasscred.pxxlspace.cv';
var localUrl = 'http://localhost:8080';
const BASE = liveUrl;                       // API origin — switch to localUrl when running locally

// Page routes are served by Flask under this prefix (see app.py)
const APP = '/app';
const LOGIN = `${APP}/`;
const HOME = {
  teacher: `${APP}/teacher/`,
  organization: `${APP}/employer/`,
  parent: `${APP}/employer/`,
  reviewer: `${APP}/reviewer/`,
};
const goHome = type => { if (HOME[type]) location.href = HOME[type]; };

const $ = id => document.getElementById(id);
const val = id => $(id).value.trim();
const asList = res => (res.ok && Array.isArray(res.data) ? res.data : []);

// ── Session ──────────────────────────────────────────────────
const session = {
  save(token, type) { localStorage.setItem('kc_token', token); localStorage.setItem('kc_type', type); },
  token() { return localStorage.getItem('kc_token'); },
  type()  { return localStorage.getItem('kc_type'); },
  clear() { localStorage.removeItem('kc_token'); localStorage.removeItem('kc_type'); },
};
const logout = () => { session.clear(); location.href = LOGIN; };

// Portal pages carry <body data-role="…"> — no session means back to the login page
if (document.body.dataset.role && !session.token()) location.replace(LOGIN);

// ── API ──────────────────────────────────────────────────────
async function api(method, path, body, auth = true) {
  const headers = { 'Content-Type': 'application/json' };
  const t = auth && session.token();
  if (t) headers.Authorization = `Bearer ${t}`;
  const opts = { method, headers };
  if (body !== undefined) opts.body = JSON.stringify(body);
  try {
    const res = await fetch(BASE + path, opts);
    const data = await res.json().catch(() => ({}));
    return { ok: res.ok, status: res.status, data };
  } catch (e) {
    return { ok: false, status: 0, data: { error: e.message } };
  }
}

// api() + the usual follow-up: show the JSON in `resp`, toast `msg` on success, run `done(res)`; toast the error otherwise
async async function send(method, path, body, { msg, done } = {}) {
  const res = await api(method, path, body);
  if (res.ok) { if (msg) toast(msg); done?.(res); }
  else toast(res.data.error ?? 'Failed', 'error');
  return res;
}

// ── UI helpers ───────────────────────────────────────────────
function toast(msg, type = 'success') {
  let el = $('toast');
  if (!el) { el = document.createElement('div'); el.id = 'toast'; document.body.appendChild(el); }
  el.textContent = msg;
  el.className = `show ${type}`;
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.className = ''; }, 3200);
}

const openModal = id => $(id)?.classList.add('open');
const closeModal = id => $(id)?.classList.remove('open');
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('open');
});

const emptyState = (icon, text) => `<div class="empty-state"><div class="icon">${icon}</div><p>${text}</p></div>`;

// Fill a <tbody> from a list, or show a centred message when it's empty
function fillRows(id, cols, list, row, empty = 'Nothing here yet.') {
  $(id).innerHTML = list.length ? list.map(row).join('')
    : `<tr><td colspan="${cols}" style="text-align:center;color:var(--text-dim);padding:24px">${empty}</td></tr>`;
}

const STATUS_COLORS = {
  pending: 'badge-yellow', accepted: 'badge-green', rejected: 'badge-red',
  active: 'badge-green', suspended: 'badge-yellow', terminated: 'badge-red',
  assigned: 'badge-blue', in_progress: 'badge-yellow', completed: 'badge-green', cancelled: 'badge-red',
  uploaded: 'badge-blue', ai_reviewed: 'badge-yellow', failed: 'badge-red',
};
function badge(value, map) {
  return `<span class="badge ${map[value] ?? 'badge-gray'}">${value ?? '—'}</span>`;
}

// Same for every role's profile page
const doChangePassword = () => send('POST', '/auth/change-password',
  { old_password: $('cp_old').value, new_password: $('cp_new').value }, { resp: 'cpResp', msg: 'Password changed' });

// ── Fixed subject vocabulary (keep in sync with backend SUBJECTS) ──
const SUBJECTS = ['Mathematics','Further Mathematics','English','Literature','Physics','Chemistry','Biology','Computer Science','Economics','Government','Geography','History','Civic Education','Commerce','Accounting','Agricultural Science'];
const subjectChecks = (id, sel = []) => `<div id="${id}" class="subject-grid">${SUBJECTS.map(s =>
  `<label class="subj"><input type="checkbox" value="${s}" ${sel.includes(s) ? 'checked' : ''}> ${s}</label>`).join('')}</div>`;
const checkedSubjects = id => [...document.querySelectorAll(`#${id} input:checked`)].map(i => i.value);
const subjectOptions = (any = true) => (any ? '<option value="">Any</option>' : '') + SUBJECTS.map(s => `<option>${s}</option>`).join('');

// ── Teacher row + searchable picker (employer and reviewer pages) ──
function teacherRow(tc, actions) {
  const d = document.createElement('div');
  d.className = 'tp-item';
  d.innerHTML = `<div><strong>${tc.full_name ?? '—'}</strong> <span class="hint">#${tc.id}${tc.email ? ' · ' + tc.email : ''}</span>
    <div class="chip-list">${(tc.subjects ?? []).map(s => `<span class="chip">${s}</span>`).join('')}</div>
    <div class="hint">${tc.rating?.composite != null ? '★ ' + tc.rating.composite.toFixed(1) + ' · ' : ''}${tc.verification_status ?? (tc.id_verified ? 'verified' : 'unverified')}</div></div>
    <div class="flex-row"></div>`;
  actions.forEach(a => {
    const b = document.createElement('button');
    b.className = 'btn btn-sm'; b.textContent = a.label; b.onclick = () => a.fn(tc);
    d.lastElementChild.appendChild(b);
  });
  return d;
}

function teacherPicker(mountId, { path, actions }) {
  const m = $(mountId);
  m.innerHTML = '<input placeholder="Search name, email or subject…"><div class="tp-results"></div>';
  const inp = m.querySelector('input'), out = m.querySelector('.tp-results');
  let t;
  const run = async () => {
    const list = asList(await api('GET', `${path}${path.includes('?') ? '&' : '?'}q=${encodeURIComponent(inp.value.trim())}`));
    out.innerHTML = list.length ? '' : '<p class="hint">No teachers found.</p>';
    list.forEach(tc => out.appendChild(teacherRow(tc, actions)));
  };
  inp.addEventListener('input', () => { clearTimeout(t); t = setTimeout(run, 300); });
  inp.addEventListener('focus', () => { if (!out.children.length) run(); });
  return { refresh: run };
}
