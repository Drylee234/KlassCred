// ── Employer: recruitment history + hire ──
async function loadRecruitment() {
  const res = await api('GET', '/employers/recruitment');

  fillRows('rec_table', 7, asList(res), r => `
    <tr>
      <td>#${r.id}</td><td>${r.teacher_id}</td><td>${r.position}</td><td>${r.hired_at}</td><td>${r.ended_at ?? '—'}</td>
      <td>${badge(r.status, STATUS_COLORS)}</td>
      <td>${r.status !== 'terminated' ? `<button class="btn btn-sm" onclick="openStatusModal(${r.id}, '${r.status}')">Update</button>` : '—'}</td>
    </tr>`, res.ok ? 'No records yet.' : 'Error loading');
}

function openStatusModal(id, current) {
  $('status_rec_id').value = id;
  $('status_rec_label').textContent = '#' + id;
  $('new_status').innerHTML = (current === 'active' ? '<option value="suspended">Suspended</option>' : '') +
    '<option value="terminated">Terminated</option>';

  openModal('statusModal');
}

const doHireTeacher = () => send('POST', '/employers/hire', {
  teacher_id: parseInt($('hire_teacher_id').value), position: val('hire_position'), hired_at: $('hire_date').value,
}, { resp: 'hireModalResp', msg: 'Teacher hired!', done: () => { closeModal('hireModal'); loadRecruitment(); } });

const doUpdateStatus = () => send('PUT', `/employers/recruitment/${$('status_rec_id').value}`, { status: $('new_status').value },
  { resp: 'statusModalResp', msg: 'Status updated', done: () => { closeModal('statusModal'); loadRecruitment(); } });

initPicker('hire', 'hireModal');
loadRecruitment();
