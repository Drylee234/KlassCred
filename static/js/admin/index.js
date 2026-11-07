const METRIC_KEYS = [
  'accounts',
  'teachers',
  'employers',
  'verified_accounts',
  'pending_verifications',
  'video_reviews',
  'open_reviews',
  'pending_interviews',
  'new_accounts',
];

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, character => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  })[character]);
}

function formatActivityTime(value) {
  if (!value) return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleString();
}

async function loadAdminDashboard() {
  const status = $('activity_status');
  status.textContent = 'Loading dashboard…';

  const result = await api('GET', '/admin/overview');
  if (!result.ok) {
    status.textContent = result.data.error ?? 'Could not load dashboard data.';
    return;
  }

  METRIC_KEYS.forEach(key => {
    $(`metric_${key}`).textContent = result.data.metrics[key].toLocaleString();
  });

  const rows = result.data.activity.map(event => `
    <tr>
      <td>${escapeHtml(event.summary)}</td>
      <td>${escapeHtml(event.type)}</td>
      <td>${escapeHtml(event.status)}</td>
      <td>${escapeHtml(formatActivityTime(event.occurred_at))}</td>
    </tr>`).join('');
  $('admin_activity').innerHTML = rows || `
    <tr><td colspan="4" class="admin-empty">No activity yet.</td></tr>`;
  status.textContent = `Updated ${new Date().toLocaleTimeString()}`;
}

$('refresh_dashboard').addEventListener('click', loadAdminDashboard);
loadAdminDashboard();
