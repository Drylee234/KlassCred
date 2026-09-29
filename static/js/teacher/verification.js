// ── Teacher verification ──
const VER_LABEL = {
  not_requested: ['Not submitted', 'badge-gray'], pending: ['Pending', 'badge-yellow'],
  rejected: ['Rejected', 'badge-red'], approved: ['Verified', 'badge-green'],
};

async function loadVerification() {
  const [st, pr] = await Promise.all([api('GET', '/teachers/verification/status'), api('GET', '/teachers/profile')]);
  const s = st.ok ? st.data.status : 'not_requested';
  const [label, cls] = VER_LABEL[s] ?? VER_LABEL.not_requested;
  const p = pr.ok ? pr.data : {}, d = p.documents ?? {};
  const reqs = [
    ['Profile complete', !!p.profile_complete],
    ['ID card front and back uploaded', !!(d.id_card_front && d.id_card_back)],
    ['At least one reference', (p.references ?? []).length > 0],
  ];
  $('ver_status').innerHTML = `<span class="badge ${cls}">${label}</span>` +
    (s === 'rejected' && st.data.rejection_reason ? `<p style="margin-top:10px;color:var(--red)">Reason: ${st.data.rejection_reason}</p>` : '');
  $('ver_reqs').innerHTML = reqs.map(r => `<li class="${r[1] ? 'done' : ''}">${r[1] ? '✓' : '○'} ${r[0]}</li>`).join('');
  const btn = $('ver_apply_btn');
  btn.style.display = (s === 'not_requested' || s === 'rejected') ? 'inline-flex' : 'none';
  btn.disabled = !reqs.every(r => r[1]);
  btn.textContent = s === 'rejected' ? 'Re-apply' : 'Apply for verification';
}

const applyVerification = () => send('POST', '/teachers/verification/apply', {},
  { resp: 'verResp', msg: 'Application submitted', done: loadVerification });

loadVerification();
