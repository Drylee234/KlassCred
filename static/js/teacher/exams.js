let activeQuestions = [];
let activeTimeLimit = 0;
let examTimer = null;

async function loadExams() {
  const res = await api('GET', '/teachers/exams');
  if (!res.ok) return toast(res.data.error ?? 'Could not load exams', 'error');
  $('exam_list').innerHTML = res.data.length ? res.data.map(({ exam: e, attempts_left: left }) => `
    <div class="card" data-time-limit="${e.time_limit}" style="margin-bottom:12px">
      <div class="flex-between">
        <div>
          <strong>${e.subject}</strong>
          <span class="badge badge-blue" style="margin-left:8px">${e.questions?.length ?? 0} questions</span>
        </div>
        <div class="flex-row">
          <span class="hint">${left === Infinity ? 'Unlimited' : left} attempts left</span>
          ${left > 0 ? `<button class="btn btn-sm" onclick="startExam(${e.id})">Start</button>` : '<span class="badge badge-red">No attempts left</span>'}
        </div>
      </div>
      <div class="hint" style="margin-top:8px">Time limit: ${e.time_limit} minutes</div>
    </div>`).join('') : emptyState('📭', 'No exams available.');
}

async function startExam(examId) {
  const res = await api('POST', '/teachers/exams/start', { exam_id: examId });
  if (!res.ok) return toast(res.data.error ?? 'Could not start exam', 'error');

  activeQuestions = res.data.questions ?? [];
  const exam = [...document.querySelectorAll('#exam_list .card')].find(card => card.querySelector('button')?.getAttribute('onclick') === `startExam(${examId})`);
  activeTimeLimit = Number(exam?.dataset.timeLimit ?? 0);
  $('submit_attempt_id').value = res.data.attempt?.id ?? '';
  $('active_exam_title').textContent = 'Active Exam';
  $('active_exam').style.display = 'block';
  renderQuestions();
  startExamTimer(res.data.attempt?.started_at, res.data.questions);
  $('active_exam').scrollIntoView({ behavior: 'smooth', block: 'start' });
  toast('Exam started. Good luck.');
}

function renderQuestions() {
  $('exam_questions').innerHTML = activeQuestions.map((q, i) => {
    const options = q.options ?? q.choices ?? {};
    const entries = Array.isArray(options)
      ? options.map((v, n) => [String.fromCharCode(65 + n), v])
      : Object.entries(options);
    return `
      <div class="card" style="margin-bottom:12px">
        <strong>${i + 1}. ${q.question ?? q.text ?? 'Question'}</strong>
        <div style="margin-top:12px">
          ${entries.map(([key, value]) => `
            <label style="display:block;margin:8px 0;cursor:pointer">
              <input type="radio" name="q_${i + 1}" value="${key}">
              <span style="margin-left:6px">${key}. ${value}</span>
            </label>`).join('')}
        </div>
      </div>`;
  }).join('');
}

function startExamTimer(startedAt) {
  clearInterval(examTimer);
  const text = $('exam_timer');
  if (!text || !activeTimeLimit || !startedAt) return;
  const end = new Date(startedAt).getTime() + activeTimeLimit * 60000;
  const tick = () => {
    const left = Math.max(0, end - Date.now());
    const mins = Math.floor(left / 60000);
    const secs = Math.floor((left % 60000) / 1000);
    text.textContent = `Time remaining: ${mins}:${String(secs).padStart(2, '0')}`;
    if (!left) {
      clearInterval(examTimer);
      toast('Time is up. Submit your exam.', 'error');
    }
  };
  tick();
  examTimer = setInterval(tick, 1000);
}

async function doSubmitExam() {
  const attemptId = parseInt($('submit_attempt_id').value);
  if (!attemptId) return toast('No active exam attempt', 'error');

  const answers = {};
  activeQuestions.forEach((_, i) => {
    const selected = document.querySelector(`input[name="q_${i + 1}"]:checked`);
    if (selected) answers[String(i + 1)] = selected.value;
  });

  if (Object.keys(answers).length !== activeQuestions.length) {
    return toast(`Answer all ${activeQuestions.length} questions before submitting`, 'error');
  }

  const res = await api('POST', '/teachers/exams/submit', { attempt_id: attemptId, answers });
  if (!res.ok) return toast(res.data.error ?? 'Could not submit exam', 'error');

  clearInterval(examTimer);
  $('active_exam').style.display = 'none';
  toast(`Exam submitted — score: ${res.data.score?.toFixed(1) ?? '0.0'}%`);
  loadExams();
}
