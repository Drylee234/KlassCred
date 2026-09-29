// ── Teacher exams ──
async function loadExams() {
  const res = await api('GET', '/teachers/exams');
  showResponse('examListResp', res.data, res.ok);
  if (!res.ok) return toast(res.data.error ?? 'Failed', 'error');
  $('exam_list').innerHTML = res.data.length ? res.data.map(({ exam: e, attempts_left: left }) => `
    <div class="card" style="margin-bottom:12px">
      <div class="flex-between">
        <div>
          <strong>${e.subject}</strong>
          <span class="badge badge-blue" style="margin-left:8px">${e.questions?.length ?? 0} questions</span>
        </div>
        <div class="flex-row">
          <span style="font-size:12px;color:var(--text-dim)">${left === Infinity ? '∞' : left} attempts left</span>
          ${left > 0 ? `<button class="btn btn-sm" onclick="startExam(${e.id})">Start</button>` : `<span class="badge badge-red">No attempts left</span>`}
        </div>
      </div>
      <div style="margin-top:8px;font-size:12px;color:var(--text-dim)">Time limit: ${e.time_limit} min &nbsp;·&nbsp; Max attempts: ${e.max_attempts ?? '∞'}</div>
    </div>`).join('') : emptyState('📭', 'No exams available.');
}

const startExam = examId => send('POST', '/teachers/exams/start', { exam_id: examId }, {
  resp: 'examListResp',
  done: res => { toast(`Exam started — attempt ID: ${res.data.attempt?.id}`); $('submit_attempt_id').value = res.data.attempt?.id ?? ''; },
});

function doSubmitExam() {
  let answers;
  try { answers = JSON.parse($('submit_answers').value); }
  catch { return toast('Invalid JSON in answers', 'error'); }
  return send('POST', '/teachers/exams/submit', { attempt_id: parseInt($('submit_attempt_id').value), answers },
    { resp: 'submitExamResp', done: res => toast(`Score: ${res.data.score?.toFixed(1) ?? '—'}%`) });
}
