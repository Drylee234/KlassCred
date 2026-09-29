// ── Simulated teacher exam ──
const ACTIVE_EXAM_KEY = 'kc_active_exam';

let examState = {
  attemptId: null,
  examId: null,
  subject: '',
  timeLimit: 0,
  startedAt: null,
  questions: [],
  answers: {},
  current: 0,
};

function saveExam() {
  localStorage.setItem(ACTIVE_EXAM_KEY, JSON.stringify(examState));
}

function clearExam() {
  localStorage.removeItem(ACTIVE_EXAM_KEY);
}

function showError(message) {
  const el = $('exam_error');
  el.textContent = message;
  el.style.display = 'block';
}

function formatTime(seconds) {
  seconds = Math.max(0, Math.floor(seconds));
  return String(Math.floor(seconds / 60)).padStart(2, '0') + ':' +
    String(seconds % 60).padStart(2, '0');
}

function remainingSeconds() {
  return examState.timeLimit * 60 -
    Math.floor((Date.now() - new Date(examState.startedAt).getTime()) / 1000);
}

function updateTimer() {
  const remaining = remainingSeconds();
  $('exam_timer').textContent = formatTime(remaining);

  if (remaining <= 0) {
    clearInterval(window.examTimer);
    $('exam_timer').classList.add('expired');
    submitExam(true);
  }
}

function renderQuestionNav() {
  $('question_nav').innerHTML = examState.questions.map((_, index) => {
    const answered = examState.answers[String(index + 1)] != null;
    const current = index === examState.current;
    return `<button class="question-dot${answered ? ' answered' : ''}${current ? ' current' : ''}"
      onclick="goToQuestion(${index})">${index + 1}</button>`;
  }).join('');
}

function escapeHtml(value) {
  const el = document.createElement('span');
  el.textContent = value ?? '';
  return el.innerHTML;
}

function renderQuestion() {
  const question = examState.questions[examState.current];
  if (!question) return;

  $('exam_subject').textContent = examState.subject;
  $('exam_progress').textContent =
    `Question ${examState.current + 1} of ${examState.questions.length}`;
  $('question_number').textContent = `Question ${examState.current + 1}`;
  $('answered_count').textContent =
    `${Object.keys(examState.answers).length} answered`;
  $('question_text').textContent = question.question ?? '';

  const selected = examState.answers[String(examState.current + 1)];
  const options = Array.isArray(question.options) ? question.options : [];

  $('question_options').innerHTML = options.map((option, index) => {
    const value = String.fromCharCode(65 + index);
    const checked = selected === value;
    return `<label class="exam-option${checked ? ' selected' : ''}">
      <input type="radio" name="exam_answer" value="${value}" ${checked ? 'checked' : ''}
        onchange="selectAnswer('${value}')">
      <span class="option-key">${value}</span>
      <span>${escapeHtml(option)}</span>
    </label>`;
  }).join('');

  $('prev_btn').disabled = examState.current === 0;
  $('next_btn').style.display =
    examState.current === examState.questions.length - 1 ? 'none' : '';
  $('submit_btn').style.display =
    examState.current === examState.questions.length - 1 ? '' : 'none';

  renderQuestionNav();
}

function selectAnswer(value) {
  examState.answers[String(examState.current + 1)] = value;
  saveExam();
  renderQuestion();
}

function goToQuestion(index) {
  if (index < 0 || index >= examState.questions.length) return;
  examState.current = index;
  saveExam();
  renderQuestion();
}

function previousQuestion() {
  goToQuestion(examState.current - 1);
}

function nextQuestion() {
  goToQuestion(examState.current + 1);
}

async function beginExam() {
  const examId = Number(new URLSearchParams(location.search).get('exam_id'));
  if (!examId) {
    showError('No exam selected. Return to Exams and choose an exam.');
    return;
  }

  const list = await api('GET', '/teachers/exams');
  if (!list.ok) {
    showError(list.data.error ?? 'Unable to load exam.');
    return;
  }

  const item = list.data.find(x => Number(x.exam?.id) === examId);
  if (!item) {
    showError('Exam not found or no longer available.');
    return;
  }

  if (item.attempts_left === 0) {
    showError('No attempts remaining for this exam.');
    return;
  }

  const res = await api('POST', '/teachers/exams/start', { exam_id: examId });
  if (!res.ok) {
    showError(res.data.error ?? 'Unable to start exam.');
    return;
  }

  const attempt = res.data.attempt;
  const questions = Array.isArray(res.data.questions) ? res.data.questions : [];

  if (!attempt?.id || !attempt.started_at || !questions.length) {
    showError('The exam did not return a usable attempt or questions.');
    return;
  }

  examState = {
    attemptId: attempt.id,
    examId,
    subject: item.exam.subject,
    timeLimit: Number(item.exam.time_limit),
    startedAt: attempt.started_at,
    questions,
    answers: {},
    current: 0,
  };

  saveExam();
  startExamSession();
}

function startExamSession() {
  $('exam_shell').style.display = '';
  $('exam_result').style.display = 'none';
  renderQuestion();
  updateTimer();
  clearInterval(window.examTimer);
  window.examTimer = setInterval(updateTimer, 1000);
}

async function submitExam(autoSubmitted = false) {
  if (!examState.attemptId) return;

  if (!autoSubmitted && remainingSeconds() <= 0) {
    return submitExam(true);
  }

  clearInterval(window.examTimer);
  $('submit_btn').disabled = true;
  $('next_btn').disabled = true;

  const res = await api('POST', '/teachers/exams/submit', {
    attempt_id: examState.attemptId,
    answers: examState.answers,
  });

  if (!res.ok) {
    $('submit_btn').disabled = false;
    $('next_btn').disabled = false;
    showError(res.data.error ?? 'Failed to submit exam.');
    return;
  }

  clearExam();
  $('exam_shell').style.display = 'none';
  $('exam_result').style.display = '';
  $('exam_timer').textContent = '00:00';
  $('exam_timer').classList.remove('expired');

  const score = Number(res.data.score);
  $('result_score').textContent =
    Number.isFinite(score) ? score.toFixed(1) + '%' : 'Submitted';
  $('result_detail').textContent = autoSubmitted
    ? 'The time limit was reached and your answers were submitted.'
    : 'Your answers were submitted successfully.';
}

document.addEventListener('DOMContentLoaded', beginExam);
