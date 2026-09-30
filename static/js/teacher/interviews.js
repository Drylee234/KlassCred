// ── Teacher interview requests ──
async function loadInterviews() {
  const status = $('iv_status_filter').value;
  const res = await api('GET', `/teachers/interviews${status ? `?status=${status}` : ''}`);

  if (!res.ok) toast(res.data.error ?? 'Failed', 'error');
  fillRows('iv_table', 6, asList(res), r => `
    <tr>
      <td>#${r.id}</td><td>${r.employer_id}</td><td>${r.contact_method}</td>
      <td>${badge(r.status, STATUS_COLORS)}</td><td>${r.created_at?.slice(0, 10) ?? '—'}</td>
      <td>${r.status === 'pending' ? `<button class="btn btn-sm" onclick="openRespond(${r.id})">Respond</button>` : '—'}</td>
    </tr>`, res.ok ? 'No requests.' : 'Error');
}

function openRespond(id) {
  $('respond_req_id').value = id;
  $('respond_req_label').textContent = '#' + id;

  openModal('respondModal');
}

const doRespond = action => send('POST', `/teachers/interviews/${$('respond_req_id').value}/respond`, { action },
  { resp: 'respondModalResp', msg: `Request ${action}`, done: () => { closeModal('respondModal'); loadInterviews(); } });

fillRows('iv_table', 6, [], null, 'Click Load to fetch requests.');
