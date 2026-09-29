// ── Teacher exam selection ──
async function loadExams() {
  const res = await api('GET', '/teachers/exams');
  showResponse('examListResp', res.data, res.ok);
  if (!res.ok) return toast(res.data.error ?? 'Failed to load exams.', 'error');

  $('exam_list').innerHTML = res.data.length
    ? res.data.map(({ exam: e, attempts_left: left }) => {
        const attempts = left === Infinity ? '∞' : left;
        const canStart = left > 0;
        return `
          <div class="exam-list-item">
            <div>
              <div class="exam-list-title">
                <strong>${escapeExamText(e.subject)}</strong>
                <span class="badge badge-blue">${e.questions?.length ?? 0} questions</span>
              </div>
              <div class="hint">${e.time_limit} min · ${attempts} attempts remaining</div>
            </div>
            ${canStart
              ? `<a class="btn btn-sm" href="/app/teacher/exam?exam_id=${e.id}">Start Exam</a>`
              : '<span class="badge badge-red">No attempts left</span>'}
          </div>`;
      }).join('')
    : emptyState('📭', 'No exams available.');
}

function escapeExamText(value) {
  const el = document.createElement('span');
  el.textContent = value ?? '';
  return el.innerHTML;
}

document.addEventListener('DOMContentLoaded', loadExams);
