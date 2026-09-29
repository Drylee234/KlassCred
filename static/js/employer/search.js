// ── Employer: search teachers ──
$('s_subject').innerHTML = subjectOptions();
let found = {};                                        // id → teacher, for the Hire / Interview buttons

async function doSearch() {
  const params = new URLSearchParams({ verified_only: $('s_verified').value });
  [['subject', 's_subject'], ['min_rating', 's_min_rating'], ['min_experience', 's_min_exp'],
   ['location', 's_location'], ['radius_km', 's_radius']].forEach(([k, id]) => { const v = val(id); if (v) params.set(k, v); });

  const res = await api('GET', `/employers/search?${params}`);
  showResponse('searchResp', res.data, res.ok);
  const box = $('search_results');
  if (!res.ok) { box.innerHTML = emptyState('⚠️', res.data.error ?? 'Search failed'); return; }

  const teachers = asList(res);
  found = Object.fromEntries(teachers.map(t => [t.id, t]));
  box.innerHTML = teachers.length ? teachers.map(t => `
    <div class="card" style="margin-bottom:12px">
      <div class="flex-between">
        <div>
          <strong>${t.full_name ?? '—'}</strong>
          <span style="color:var(--text-dim);font-size:12px;margin-left:8px">#${t.id}</span>
          ${t.id_verified ? '<span class="badge badge-green" style="margin-left:8px">Verified</span>' : ''}
        </div>
        <div class="flex-row">
          ${t.rating?.composite != null ? `<span class="badge badge-blue">★ ${t.rating.composite.toFixed(1)}</span>` : ''}
          <button class="btn btn-sm" onclick="sendToPage('hire', found[${t.id}])">Hire</button>
          <button class="btn btn-sm" onclick="sendToPage('iv', found[${t.id}])">Interview</button>
        </div>
      </div>
      <div class="chip-list" style="margin-top:8px">${(t.subjects ?? []).map(s => `<span class="chip">${s}</span>`).join('')}</div>
      <div style="font-size:12px;color:var(--text-dim);margin-top:6px">${t.experience_years ?? '—'} yrs experience</div>
    </div>`).join('') : emptyState('🔍', 'No teachers found.');
}
