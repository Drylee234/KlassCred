// ── Employer: applications from teachers ──
async function loadApplications() {
  const st = $('app_status').value;
  const list = asList(await api('GET', `/employers/applications${st ? `?status=${st}` : ''}`));
  $('app_list').innerHTML = list.length ? list.map(a => `
    <div class="card" style="margin-bottom:12px">
      <div class="flex-between">
        <div><strong>${a.teacher?.full_name ?? a.teacher_name ?? 'Teacher #' + a.teacher_id}</strong><div class="hint">${a.position ?? ''}</div></div>
        ${badge(a.status, STATUS_COLORS)}
      </div>
      ${a.message ? `<p style="margin-top:8px;font-size:13px;color:var(--text-dim)">${a.message}</p>` : ''}
      <div class="flex-between" style="margin-top:10px">
        <span class="hint">Applied: ${a.created_at?.slice(0, 10) ?? '—'}</span>
        ${a.status === 'pending' ? `<div class="flex-row">
          <button class="btn btn-sm" onclick="setApp(${a.id},'accepted')">Accept</button>
          <button class="btn btn-danger-sm" onclick="setApp(${a.id},'rejected')">Reject</button></div>` : ''}
      </div>
    </div>`).join('') : emptyState('📭', 'No applications.');
}

const setApp = (id, status) => send('PUT', `/employers/applications/${id}`, { status },
  { msg: `Application ${status}`, done: loadApplications });

loadApplications();
