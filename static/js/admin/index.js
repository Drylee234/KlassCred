const METRIC_KEYS = [
  'accounts',
  'disabled_accounts',
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

function renderAccounts(accounts) {
  $('admin_accounts').innerHTML = accounts.length ? accounts.map(account => {
    const verification = account.can_verify
      ? `<span class="badge ${account.id_verified ? 'badge-green' : 'badge-yellow'}">${account.id_verified ? 'Verified' : 'Unverified'}</span>`
      : '—';
    const verifyButton = account.can_verify
      ? `<button class="btn btn-sm" data-action="verify" data-id="${account.id}" data-verified="${account.id_verified}">${account.id_verified ? 'Unverify' : 'Verify'}</button>`
      : '';
    const accessButton = account.is_admin
      ? '<span class="hint">Admin protected</span>'
      : `<button class="btn ${account.account_enabled ? 'btn-danger-sm' : 'btn-sm'}" data-action="account-status" data-id="${account.id}" data-enabled="${account.account_enabled}">${account.account_enabled ? 'Deactivate' : 'Reactivate'}</button>`;
    return `<tr>
      <td><strong>${escapeHtml(account.name || account.email)}</strong><div class="hint">${escapeHtml(account.email)}</div></td>
      <td>${escapeHtml(account.type)}</td>
      <td><span class="badge ${account.account_enabled ? 'badge-green' : 'badge-red'}">${account.account_enabled ? 'Active' : 'Deactivated'}</span></td>
      <td>${verification}</td>
      <td><div class="admin-actions">${verifyButton}${accessButton}</div></td>
    </tr>`;
  }).join('') : '<tr><td colspan="5" class="admin-empty">No matching accounts.</td></tr>';
}

async function loadAccounts() {
  const status = $('account_status');
  status.textContent = 'Loading accounts…';
  const result = await api('GET', `/admin/accounts?q=${encodeURIComponent(val('account_search'))}`);
  if (!result.ok) {
    status.textContent = result.data.error ?? 'Could not load accounts.';
    return;
  }
  renderAccounts(result.data);
  status.textContent = `${result.data.length} account${result.data.length === 1 ? '' : 's'} shown (maximum 50).`;
}

function renderReviewAssignments(assignments, reviewers) {
  $('admin_review_assignments').innerHTML = assignments.length ? assignments.map(assignment => `
    <tr>
      <td>#${escapeHtml(assignment.id)} · video #${escapeHtml(assignment.video_id)}</td>
      <td>${escapeHtml(assignment.teacher)}</td>
      <td>
        <select id="reviewer_${escapeHtml(assignment.id)}" aria-label="Reviewer for assignment ${escapeHtml(assignment.id)}">
          ${reviewers.map(reviewer => `<option value="${reviewer.id}" ${reviewer.id === assignment.reviewer_id ? 'selected' : ''}>${escapeHtml(reviewer.name)}</option>`).join('')}
        </select>
      </td>
      <td>${escapeHtml(assignment.status)}</td>
      <td><div class="admin-actions">
        <button class="btn btn-sm" data-action="reassign" data-id="${escapeHtml(assignment.id)}">Reassign</button>
        <button class="btn btn-danger-sm" data-action="cancel-review" data-id="${escapeHtml(assignment.id)}">Cancel</button>
      </div></td>
    </tr>`).join('') : '<tr><td colspan="5" class="admin-empty">No open review assignments.</td></tr>';
}

async function loadReviewQueue() {
  const status = $('review_queue_status');
  status.textContent = 'Loading review queue…';
  const [assignmentResult, reviewerResult] = await Promise.all([
    api('GET', '/admin/review-assignments'),
    api('GET', '/admin/reviewers'),
  ]);
  if (!assignmentResult.ok || !reviewerResult.ok) {
    status.textContent = assignmentResult.data.error
      ?? reviewerResult.data.error
      ?? 'Could not load the review queue.';
    return;
  }
  renderReviewAssignments(assignmentResult.data, reviewerResult.data);
  status.textContent = `${assignmentResult.data.length} open assignment${assignmentResult.data.length === 1 ? '' : 's'}.`;
}

async function handleAdminAction(event) {
  const button = event.target.closest('button[data-action]');
  if (!button) return;
  const id = button.dataset.id;
  let result;

  if (button.dataset.action === 'verify') {
    result = await api('PATCH', `/admin/accounts/${id}/verification`, {
      verified: button.dataset.verified !== 'true',
    });
  } else if (button.dataset.action === 'account-status') {
    const enabled = button.dataset.enabled !== 'true';
    if (!enabled && !confirm('Deactivate this account? It can be reactivated later.')) return;
    result = await api('PATCH', `/admin/accounts/${id}/status`, { enabled });
  } else if (button.dataset.action === 'reassign') {
    const reviewerId = Number($(`reviewer_${id}`).value);
    result = await api('PATCH', `/admin/review-assignments/${id}/reviewer`, {
      reviewer_id: reviewerId,
    });
  } else if (button.dataset.action === 'cancel-review') {
    if (!confirm('Cancel this review assignment?')) return;
    result = await api('POST', `/admin/review-assignments/${id}/cancel`);
  }

  if (!result?.ok) {
    toast(result?.data?.error ?? 'Admin action failed.', 'error');
    return;
  }
  toast('Admin action completed.');
  await Promise.all([loadAdminDashboard(), loadAccounts(), loadReviewQueue()]);
}

$('admin_accounts').addEventListener('click', handleAdminAction);
$('admin_review_assignments').addEventListener('click', handleAdminAction);
$('search_accounts').addEventListener('click', loadAccounts);
$('account_search').addEventListener('keydown', event => {
  if (event.key === 'Enter') loadAccounts();
});
$('refresh_dashboard').addEventListener('click', () => {
  Promise.all([loadAdminDashboard(), loadAccounts(), loadReviewQueue()]);
});
Promise.all([loadAdminDashboard(), loadAccounts(), loadReviewQueue()]);
