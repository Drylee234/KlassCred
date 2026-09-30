// ── Reviewer assignments ──
async function loadAssignments() {
  const res = await api('GET', '/reviewer/assignments');

  if (!res.ok) toast(res.data.error ?? 'Failed', 'error');
  fillRows('assign_table', 6, asList(res), a => `
    <tr>
      <td>#${a.id}</td><td>${a.video_id}</td><td>${badge(a.status, STATUS_COLORS)}</td>
      <td>${a.assigned_at?.slice(0, 10) ?? '—'}</td><td>${a.completed_at?.slice(0, 10) ?? '—'}</td>
      <td>${a.status === 'assigned' || a.status === 'in_progress'
        ? `<button class="btn btn-sm" onclick="openReviewModal(${a.id})">Review</button>`
        : badge(a.status === 'completed' ? 'done' : 'cancelled', { done: 'badge-green', cancelled: 'badge-red' })}</td>
    </tr>`, res.ok ? 'No assignments.' : 'Error');
}

onReviewed = loadAssignments;
loadAssignments();
