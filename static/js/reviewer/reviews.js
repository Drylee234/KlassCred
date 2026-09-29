// ── Reviewer: reviews submitted this browser session (written by shared.js) ──
const log = JSON.parse(sessionStorage.getItem(REVIEW_LOG) || '[]');
if (log.length) $('reviews_log').innerHTML = log.map(r => `
  <div class="card" style="margin-bottom:12px;background:var(--surface2)">
    <div class="flex-between">
      <div>
        <strong>Assignment #${r.assignmentId}</strong>
        <span class="badge badge-blue" style="margin-left:8px">Score: ${r.score}</span>
        ${r.flagged ? '<span class="badge badge-red" style="margin-left:4px">Flagged</span>' : ''}
      </div>
      <span style="font-size:11px;color:var(--text-dim)">${r.at.slice(0, 19).replace('T', ' ')}</span>
    </div>
    ${r.notes ? `<p style="margin-top:8px;font-size:13px;color:var(--text-dim)">${r.notes}</p>` : ''}
    ${r.flag_reason ? `<p style="margin-top:6px;font-size:12px;color:var(--red)">Flag reason: ${r.flag_reason}</p>` : ''}
  </div>`).join('');
