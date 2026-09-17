// ── KlassCred Test UI — shared utilities ──
var liveUrl = 'https://klasscred.pxxlspace.cv'
var localUrl = 'http://localhost:8080' 
const BASE = liveUrl ;

// ── Token / session ──────────────────────────────────────────
const session = {
  save(token, type) {
    localStorage.setItem('kc_token', token);
    localStorage.setItem('kc_type', type);
  },
  token() { return localStorage.getItem('kc_token'); },
  type()  { return localStorage.getItem('kc_type'); },
  clear() { localStorage.removeItem('kc_token'); localStorage.removeItem('kc_type'); },
  required() {
    const t = this.token();
    if (!t) { window.location.href = '/test-ui/'; return null; }
    return t;
  }
};

// ── API helper ───────────────────────────────────────────────
async function api(method, path, body, token) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
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

// ── Toast ────────────────────────────────────────────────────
function toast(msg, type = 'success') {
  let el = document.getElementById('toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.className = `show ${type}`;
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.className = ''; }, 3200);
}

// ── Response box ─────────────────────────────────────────────
function showResponse(boxId, data, ok) {
  const box = document.getElementById(boxId);
  if (!box) return;
  box.textContent = JSON.stringify(data, null, 2);
  box.className = `response-box show${ok ? '' : ' error'}`;
}

// ── Modal helpers ────────────────────────────────────────────
function openModal(id) { document.getElementById(id)?.classList.add('open'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }

// Close modal when clicking the overlay backdrop
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
  }
});

// ── Nav active state ─────────────────────────────────────────
function setActiveNav(pageId) {
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.page === pageId);
  });
}

// ── Section switcher ─────────────────────────────────────────
function showSection(id) {
  document.querySelectorAll('.page-section').forEach(s => {
    s.style.display = s.id === id ? 'block' : 'none';
  });
}

// ── Logout ───────────────────────────────────────────────────
function logout() {
  session.clear();
  window.location.href = '/test-ui/';
}

// ── Badge helper ─────────────────────────────────────────────
function badge(value, map) {
  const cls = map[value] ?? 'badge-gray';
  return `<span class="badge ${cls}">${value ?? '—'}</span>`;
}

const STATUS_COLORS = {
  pending:     'badge-yellow',
  accepted:    'badge-green',
  rejected:    'badge-red',
  active:      'badge-green',
  suspended:   'badge-yellow',
  terminated:  'badge-red',
  assigned:    'badge-blue',
  in_progress: 'badge-yellow',
  completed:   'badge-green',
  cancelled:   'badge-red',
  uploaded:    'badge-blue',
  ai_reviewed: 'badge-yellow',
  failed:      'badge-red',
};
