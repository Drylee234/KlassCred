// ── Employer dashboard ──
async function loadDashboard() {
  $('ds_type').textContent = session.type();
  const [prof, rec, iv] = await Promise.all([
    api('GET', '/employers/profile'), api('GET', '/employers/recruitment'), api('GET', '/employers/interviews'),
  ]);

  if (prof.ok) {
    const p = prof.data;
    $('dash_greeting').textContent = `Welcome, ${p.org_name ?? p.name ?? p.email ?? 'Employer'}`;
    if (p.id_verified) { $('dash_verified').textContent = 'Verified'; $('dash_verified').className = 'badge badge-green'; }
  }

  if (rec.ok && Array.isArray(rec.data)) {
    const recs = rec.data, recent = recs.slice(-5).reverse();
    $('ds_total').textContent = recs.length;
    $('ds_active').textContent = recs.filter(r => r.status === 'active').length;
    $('dash_recruitment').innerHTML = recent.length ? `
      <div class="table-wrap">
        <table>
          <thead><tr><th>Teacher ID</th><th>Position</th><th>Status</th><th>Hired</th></tr></thead>
          <tbody>${recent.map(r => `
            <tr><td>${r.teacher_id}</td><td>${r.position}</td><td>${badge(r.status, STATUS_COLORS)}</td><td>${r.hired_at}</td></tr>`).join('')}
          </tbody>
        </table>
      </div>` : emptyState('📭', 'No recruitment records yet.');
  }

  if (iv.ok && Array.isArray(iv.data)) {
    const pending = iv.data.filter(r => r.status === 'pending').length;
    $('ds_interviews').textContent = `${iv.data.length} (${pending} pending)`;
  }
}

loadDashboard();
