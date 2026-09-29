// ── Reviewer: verify users ──
const VACT = [
  { label: 'Inspect', fn: async tc => { const r = await api('GET', `/reviewer/verification/teachers/${tc.id}`); showResponse('vTeacherResp', r.data, r.ok); } },
  { label: 'Verify', fn: tc => send('POST', `/reviewer/verification/teachers/${tc.id}/approve`, {}, { msg: 'Teacher verified ✓', done: refreshVerify }) },
  { label: 'Reject', fn: tc => {
      const reason = prompt('Rejection reason?');
      if (reason) send('POST', `/reviewer/verification/teachers/${tc.id}/reject`, { reason }, { msg: 'Teacher rejected', done: refreshVerify });
  } },
];

const vPicker = teacherPicker('v_picker', { path: '/reviewer/teachers', actions: VACT });
const refreshVerify = () => { loadPending(); vPicker.refresh(); };

async function loadPending() {
  const box = $('v_pending'), list = asList(await api('GET', '/reviewer/verification/pending'));
  box.innerHTML = list.length ? '' : '<p class="hint">Nothing pending.</p>';
  list.forEach(tc => box.appendChild(teacherRow(tc, VACT)));
}

// Organizations and parents are verified by employer ID
function doVerify(type) {
  const org = type === 'organization', id = $(org ? 'v_org_id' : 'v_parent_id').value;
  if (!id) return toast('Enter an ID', 'error');
  return send('POST', `/verify/${type}/${id}`, undefined, { resp: org ? 'vOrgResp' : 'vParentResp', msg: `${type} verified ✓` });
}

loadPending();
