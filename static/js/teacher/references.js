// ── Teacher references ──
async function loadReferences() {
  const res = await api('GET', '/teachers/profile');
  fillRows('ref_table', 7, res.ok ? (res.data.references ?? []) : [], r => `
    <tr>
      <td>${r.full_name}</td><td>${r.organization ?? '—'}</td><td>${r.role ?? '—'}</td>
      <td>${r.email}</td><td>${r.phone}</td><td>${r.relationship_type}</td>
      <td><button class="btn btn-danger-sm" onclick="deleteRef(${r.id})">Delete</button></td>
    </tr>`, res.ok ? 'No references yet.' : 'Error');
}

const doAddRef = () => send('POST', '/teachers/profile/references', {
  full_name: val('ref_full_name'),
  organization: val('ref_org') || null,
  role: val('ref_role') || null,
  email: val('ref_email'),
  phone: val('ref_phone'),
  relationship_type: val('ref_rel'),
}, { resp: 'addRefModalResp', msg: 'Reference added', done: () => { closeModal('addRefModal'); loadReferences(); } });

function deleteRef(id) {
  if (confirm('Remove this reference?'))
    send('DELETE', `/teachers/profile/references/${id}`, undefined, { msg: 'Deleted', done: loadReferences });
}

loadReferences();
