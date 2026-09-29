// ── Employer: interview requests ──
async function loadInterviews() {
  const status = $('iv_status_filter').value;
  const res = await api('GET', `/employers/interviews${status ? `?status=${status}` : ''}`);
  showResponse('ivResp', res.data, res.ok);
  fillRows('iv_table', 5, asList(res), r => `
    <tr>
      <td>#${r.id}</td><td>${r.teacher_id}</td><td>${r.contact_method}</td>
      <td>${badge(r.status, STATUS_COLORS)}</td><td>${r.created_at?.slice(0, 10) ?? '—'}</td>
    </tr>`, res.ok ? 'No requests.' : 'Error');
}

const doSendInterviewRequest = () => send('POST', '/employers/interviews',
  { teacher_id: parseInt($('iv_teacher_id').value), contact_method: $('iv_contact').value },
  { resp: 'sendIvModalResp', msg: 'Interview request sent', done: () => { closeModal('sendIvModal'); loadInterviews(); } });

initPicker('iv', 'sendIvModal');
loadInterviews();
