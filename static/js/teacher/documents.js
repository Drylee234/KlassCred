// ── Teacher documents (teacher.documents JSON) ──
async function loadDocs() {
  const res = await api('GET', '/teachers/profile');
  if (!res.ok) return;
  const docs = Object.entries(res.data.documents ?? {});
  $('docs_view').innerHTML = docs.length
    ? docs.map(([k, v]) => `
        <div class="profile-field" style="margin-bottom:12px">
          <div class="label">${k.replace(/_/g, ' ')}</div>
          <div class="val"><a href="${v}" target="_blank" style="color:var(--accent)">${v}</a></div>
        </div>`).join('')
    : emptyState('📄', 'No documents uploaded yet.');
}

function doUpdateDocs() {
  const front = val('doc_front'), back = val('doc_back'), cert = val('doc_cert');
  if (!front || !back) return toast('Front and back ID card URLs required', 'error');
  const documents = { id_card_front: front, id_card_back: back, ...(cert && { certificate: cert }) };
  return send('PUT', '/teachers/profile', { documents }, { resp: 'docsResp', msg: 'Documents saved', done: loadDocs });
}

loadDocs();
