// ── Teacher work history ──
async function loadWorkHistory() {
  const res = await api('GET', '/teachers/profile');
  fillRows('work_table', 5, res.ok ? (res.data.work_history ?? []) : [], w => `
    <tr>
      <td>${w.organization}</td><td>${w.role}</td><td>${w.start_date}</td><td>${w.end_date ?? '—'}</td>
      <td><button class="btn btn-danger-sm" onclick="deleteWork(${w.id})">Delete</button></td>
    </tr>`, res.ok ? 'No work history yet.' : 'Error loading');
}

const doAddWork = () => send('POST', '/teachers/profile/work-history', {
  organization: val('wh_org'), role: val('wh_role'),
  start_date: $('wh_start').value, end_date: $('wh_end').value || null,
}, { resp: 'addWorkModalResp', msg: 'Work history added', done: () => { closeModal('addWorkModal'); loadWorkHistory(); } });

function deleteWork(id) {
  if (confirm('Delete this work history entry?'))
    send('DELETE', `/teachers/profile/work-history/${id}`, undefined, { msg: 'Deleted', done: loadWorkHistory });
}

loadWorkHistory();
