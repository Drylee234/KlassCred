// ── Reviewer dashboard ──
async function loadDashboard() {
  const res = await api('GET', '/reviewer/assignments');
  if (!res.ok) return;
  const all = asList(res);
  const open = all.filter(a => a.status === 'assigned' || a.status === 'in_progress');
  $('ds_open').textContent = open.length;
  $('ds_completed').textContent = all.filter(a => a.status === 'completed').length;
  $('ds_total').textContent = all.length;

  $('dash_assignments').innerHTML = open.length ? `
    <div class="table-wrap">
      <table>
        <thead><tr><th>ID</th><th>Video ID</th><th>Status</th><th>Assigned</th><th></th></tr></thead>
        <tbody>${open.map(a => `
          <tr>
            <td>#${a.id}</td><td>${a.video_id}</td><td>${badge(a.status, STATUS_COLORS)}</td>
            <td>${a.assigned_at?.slice(0, 10) ?? '—'}</td>
            <td><button class="btn btn-sm" onclick="openReviewModal(${a.id})">Review</button></td>
          </tr>`).join('')}
        </tbody>
      </table>
    </div>` : emptyState('✅', 'No open assignments.');
}

onReviewed = loadDashboard;
loadDashboard();
