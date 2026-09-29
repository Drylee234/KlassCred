// ── Employer portal — loaded on every employer page ──
$('sbar_type').textContent = session.type() === 'organization' ? 'Organization Portal' : 'Parent Portal';

// Search → Hire / Interview hand-off. Pages don't share memory, so the chosen teacher travels in sessionStorage.
const PICK_KEY = 'kc_pick';

function sendToPage(kind, tc) {                       // kind: 'hire' → recruitment page, 'iv' → interviews page
  sessionStorage.setItem(PICK_KEY, JSON.stringify({ kind, tc }));
  location.href = `${APP}/employer/${kind === 'hire' ? 'recruitment' : 'interviews'}`;
}

function pickTeacher(kind, tc) {
  $(`${kind}_teacher_id`).value = tc.id;
  const box = $(`${kind}_picked`);
  box.style.display = 'block';
  box.innerHTML = `<strong>${tc.full_name}</strong> · ${(tc.subjects ?? []).join(' · ')}<div class="hint">${tc.rating?.composite != null ? '★ ' + tc.rating.composite.toFixed(1) + ' · ' : ''}${tc.id_verified ? 'Verified' : 'Unverified'}</div>`;
}

// Wire up a modal's teacher picker; if the teacher was chosen on the Search page, preselect them and open the modal
function initPicker(kind, modalId) {
  teacherPicker(`${kind}_picker`, { path: '/employers/search', actions: [{ label: 'Select', fn: tc => pickTeacher(kind, tc) }] });
  const p = JSON.parse(sessionStorage.getItem(PICK_KEY) || 'null');
  if (p?.kind !== kind) return;
  sessionStorage.removeItem(PICK_KEY);
  pickTeacher(kind, p.tc);
  openModal(modalId);
}
