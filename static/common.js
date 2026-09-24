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
    if (!t) { window.location.href = '/index.html'; return null; }
    return t;
},
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
  window.location.href = '/index.html';
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

// ── Extras (shared by all portals) ───────────────────────────
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const isUrl = u => typeof u === 'string' && /^https?:\/\//i.test(u);
const isImageUrl = u => /\.(png|jpe?g|gif|webp|avif)(\?|$)/i.test(u || '');

function fmtTime(ms) {
  const t = Math.max(0, Math.floor(ms / 1000));
  const h = Math.floor(t / 3600), m = Math.floor(t % 3600 / 60), s = t % 60;
  const p = n => String(n).padStart(2, '0');
  return (h ? h + ':' : '') + p(m) + ':' + p(s);
}

// Backend timestamps are usually naive UTC — treat them as UTC unless they carry an offset
function parseUTC(v) {
  if (!v) return null;
  if (typeof v === 'number') return v;
  let s = String(v);
  if (!/[zZ]$|[+-]\d\d:?\d\d$/.test(s) || /^\d{4}-\d\d-\d\d$/.test(s)) s += /^\d{4}-\d\d-\d\d$/.test(s) ? '' : 'Z';
  const t = Date.parse(s);
  return isNaN(t) ? null : t;
}

// Render any object as label/value rows. URLs become links (images get thumbnails).
function kv(obj) {
  if (obj == null || typeof obj !== 'object') return `<p>${esc(obj ?? '—')}</p>`;
  return Object.entries(obj).map(([k, v]) => {
    let val;
    if (isUrl(v)) val = isImageUrl(v)
      ? `<a href="${esc(v)}" target="_blank" rel="noopener"><img src="${esc(v)}" class="thumb" alt=""></a>`
      : `<a href="${esc(v)}" target="_blank" rel="noopener" style="color:var(--accent)">${esc(v)}</a>`;
    else if (v && typeof v === 'object') val = `<pre class="mini-pre">${esc(JSON.stringify(v, null, 2))}</pre>`;
    else val = esc(v ?? '—');
    return `<div class="profile-field" style="margin-bottom:10px"><div class="label">${esc(k.replace(/_/g, ' '))}</div><div class="val">${val}</div></div>`;
  }).join('');
}

// Direct-to-Byteship browser upload.
// Backend returns a short-lived upload_token.
function byteshipUpload(file, uploadData, onProgress) {
  const token = uploadData?.upload_token;

  if (!token) {
    return {
      promise: Promise.reject(
        new Error('Backend response has no Byteship upload token')
      ),
      abort: () => {}
    };
  }

  const controller = new AbortController();

  const promise = (async () => {
    if (!window.ByteshipClient) {
      throw new Error('Byteship SDK is not loaded');
    }

    const byteship = new ByteshipClient({
      uploadToken: token
    });

    const uploaded = await byteship.upload(file, {
      path: `${uploadData.folder}/${file.name}`,
      visibility: 'public',
      method: 'auto',
      signal: controller.signal,
      onProgress: progress => {
        if (progress?.percent != null) {
          onProgress?.(Math.round(progress.percent));
        } else if (
          progress?.loaded != null &&
          progress?.total
        ) {
          onProgress?.(
            Math.round((progress.loaded / progress.total) * 100)
          );
        }
      }
    });

    if (!uploaded?.url) {
      throw new Error('Byteship upload completed without a file URL');
    }

    return uploaded;
  })();

  return {
    promise,
    abort: () => controller.abort()
  };
}


// Pick a file → ask backend for signed URL → upload → onDone(url)
function pickAndUpload({ endpoint, kind, accept = 'image/*,application/pdf', onProgress, onDone, token }) {
  const inp = document.createElement('input');
  inp.type = 'file'; inp.accept = accept;
  inp.onchange = async () => {
    const f = inp.files[0]; if (!f) return;
    const s = await api('POST', endpoint, { kind, filename: f.name, content_type: f.type }, token);
    if (!s.ok) { toast(s.data.error ?? 'Could not get upload URL', 'error'); return; }
    try {
      const r = await byteshipUpload(f, s.data, onProgress).promise;
      onDone(r.secure_url ?? r.url);
      toast('File uploaded');
    } catch (e) { toast(e.message, 'error'); }
  };
  inp.click();
}
