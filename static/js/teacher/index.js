// ── Teacher dashboard ──
async function loadDashboard() {
  const [prof, iv, exams] = await Promise.all([
    api('GET', '/teachers/profile'), api('GET', '/teachers/interviews'), api('GET', '/teachers/exams'),
  ]);

  if (prof.ok) {
    const p = prof.data;
    $('dash_greeting').textContent = `Welcome, ${p.full_name ?? p.email}`;
    $('ds_profile').textContent = p.profile_complete ? '✓' : '✗';
    $('ds_profile_sub').textContent = p.profile_complete ? 'Complete' : 'Incomplete';
    if (p.id_verified) { $('dash_verified').textContent = 'Verified'; $('dash_verified').className = 'badge badge-green'; }
    if (p.rating) {
      $('ds_rating').textContent = p.rating.composite != null ? p.rating.composite.toFixed(1) : '—';
      renderBreakdown(p.rating.breakdown);
    }
  }

  if (iv.ok) {
    const list = Array.isArray(iv.data) ? iv.data : [];
    const pending = list.filter(r => r.status === 'pending').length;
    $('ds_interviews').textContent = pending ? `${list.length} (${pending} pending)` : list.length;
  }

  if (exams.ok && Array.isArray(exams.data)) $('ds_exams').textContent = exams.data.length + ' available';
}

function renderBreakdown(breakdown) {
  if (!breakdown || !Object.keys(breakdown).length) return;
  const rows = Object.entries(breakdown).map(([k, v]) => `
    <tr>
      <td style="text-transform:capitalize">${k}</td>
      <td>${v.score?.toFixed(1) ?? '—'}</td>
      <td>${v.weight}%</td>
      <td>${(v.effective_weight * 100).toFixed(1)}%</td>
    </tr>`).join('');
  $('dash_breakdown').innerHTML = `
    <div class="table-wrap">
      <table>
        <thead><tr><th>Component</th><th>Score</th><th>Weight</th><th>Effective</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

loadDashboard();
