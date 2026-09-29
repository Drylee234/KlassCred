// ── Reviewer: rating override ──
async function pickForOverride(tc) {
  $('ov_teacher_id').value = tc.id;
  const r = await api('GET', `/reviewer/ratings/${tc.id}`);
  const box = $('ov_picked');
  box.style.display = 'block';
  box.innerHTML = `<strong>${tc.full_name}</strong> · Teacher #${tc.id}<div class="hint">Current rating: ${r.ok ? (r.data.composite ?? '—') : '—'}</div>`;
}

teacherPicker('ov_picker', { path: '/reviewer/teachers', actions: [{ label: 'Select', fn: pickForOverride }] });

function doOverride() {
  const teacher_id = parseInt($('ov_teacher_id').value), composite = parseFloat($('ov_composite').value), reason = val('ov_reason');
  if (!teacher_id || isNaN(composite) || !reason) return toast('All fields required', 'error');
  return send('POST', `/reviewer/ratings/${teacher_id}/override`, { composite, reason },
    { resp: 'ovResp', msg: `Rating overridden → ${composite}` });
}
