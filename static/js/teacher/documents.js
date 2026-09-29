// ── Teacher identity documents ──
const MAX_ID_MB = 10;

function previewId(side, file) {
  if (!file) return;
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type))
    return toast('Choose a JPG, PNG or WEBP image', 'error');
  if (file.size > MAX_ID_MB * 1024 * 1024)
    return toast('ID image must be 10 MB or smaller', 'error');

  const preview = $(`${side}_preview`);
  const name = $(`${side}_file_name`);
  preview.src = URL.createObjectURL(file);
  preview.hidden = false;
  name.textContent = file.name;
}

async function loadDocs() {
  const res = await api('GET', '/teachers/profile');
  if (!res.ok) return;

  const docs = Object.entries(res.data.documents ?? {});
  $('docs_view').innerHTML = docs.length
    ? docs.map(([key, value]) => `
        <div class="profile-field" style="margin-bottom:12px">
          <div class="label">${key.replace(/_/g, ' ')}</div>
          <div class="val"><a href="${value}" target="_blank" rel="noopener" style="color:var(--accent)">View document</a></div>
        </div>`).join('')
    : emptyState('📄', 'No documents submitted yet.');
}

async function doUpdateDocs() {
  const front = val('doc_front_file');
  const back = val('doc_back_file');

  // The current API stores document URLs, so the UI accepts already-hosted
  // files through the same document model rather than pretending it uploads
  // binary files directly.
  if (!front || !back) {
    return toast('Select both sides of your ID card first', 'error');
  }

  toast('The current document API expects hosted document URLs. Use the upload service to host these images, then save their URLs here.', 'error');
}

async function saveCertificate() {
  const cert = val('doc_cert');
  if (!cert) return toast('Enter a certificate URL first', 'error');

  const res = await api('PUT', '/teachers/profile', {
    documents: { certificate: cert }
  });
  showResponse('docsResp', res.data, res.ok);
  if (!res.ok) return toast(res.data.error ?? 'Could not save certificate', 'error');

  toast('Certificate saved');
  loadDocs();
}

loadDocs();
