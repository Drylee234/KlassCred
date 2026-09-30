// ── Reviewer: verify users ──
const VACT = [
  { label: 'Inspect', fn: async tc => {
      const r = await api('GET', `/reviewer/verification/teachers/${tc.id}`);

  } },
  { label: 'Verify', fn: tc => send(
      'POST',
      `/reviewer/verification/teachers/${tc.id}/approve`,
      {},
      { msg: 'Teacher verified ✓', done: refreshVerify }
  ) },
  { label: 'Reject', fn: tc => {
      const reason = prompt('Rejection reason?');
      if (reason) send(
        'POST',
        `/reviewer/verification/teachers/${tc.id}/reject`,
        { reason },
        { msg: 'Teacher rejected', done: refreshVerify }
      );
  } },
];

function employerRow(employer) {
  const d = document.createElement('div');
  d.className = 'tp-item employer-item';
  d.innerHTML = `
    <div>
      <strong>${employer.name ?? '—'}</strong>
      <span class="hint">#${employer.id} · ${employer.type}</span>
      <div class="hint">${employer.email ?? ''}${employer.location ? ' · ' + employer.location : ''}</div>
      <div class="hint">${employer.id_verified ? 'Verified' : 'Pending verification'}</div>
    </div>
    <div class="flex-row"></div>
  `;

  const verify = document.createElement('button');
  verify.className = 'btn btn-sm';
  verify.textContent = 'Verify';
  verify.onclick = () => send(
    'POST',
    `/verify/${employer.type}/${employer.id}`,
    undefined,
    { msg: `${employer.name} verified ✓`, done: refreshEmployers }
  );

  d.lastElementChild.appendChild(verify);
  return d;
}

function employerPicker(mountId) {
  const m = $(mountId);
  m.innerHTML = '<div class="search-shell"><span class="search-icon">⌕</span><input placeholder="Search name, email, CAC number or location…"></div><div class="tp-results employer-results"></div>';

  const inp = m.querySelector('input');
  const out = m.querySelector('.tp-results');
  let timer;

  const run = async () => {
    const query = inp.value.trim();
    out.classList.add('is-loading');

    const res = await api(
      'GET',
      `/reviewer/employers?q=${encodeURIComponent(query)}`
    );

    out.classList.remove('is-loading');
    const list = asList(res);
    out.innerHTML = list.length
      ? ''
      : '<p class="hint search-empty">No employers found.</p>';

    list.forEach(employer => out.appendChild(employerRow(employer)));
    requestAnimationFrame(() => out.classList.add('is-visible'));
  };

  inp.addEventListener('input', () => {
    clearTimeout(timer);
    out.classList.remove('is-visible');
    timer = setTimeout(run, 250);
  });

  inp.addEventListener('focus', () => {
    if (!out.children.length) run();
  });

  return { refresh: run };
}

const vPicker = teacherPicker('v_picker', {
  path: '/reviewer/teachers',
  actions: VACT
});

const ePicker = employerPicker('e_picker');

const refreshEmployers = () => ePicker.refresh();
const refreshVerify = () => {
  loadPending();
  vPicker.refresh();
  ePicker.refresh();
};

function switchVerifyTab(tab) {
  document.querySelectorAll('.verify-tab').forEach(button => {
    button.classList.toggle('active', button.dataset.tab === tab);
  });

  document.querySelectorAll('.verify-panel').forEach(panel => {
    panel.classList.toggle('active', panel.id === `${tab}_panel`);
  });

  if (tab === 'employers') ePicker.refresh();
}

async function loadPending() {
  const box = $('v_pending');
  const list = asList(await api('GET', '/reviewer/verification/pending'));

  box.innerHTML = list.length
    ? ''
    : '<p class="hint">Nothing pending.</p>';

  list.forEach(tc => box.appendChild(teacherRow(tc, VACT)));
}

loadPending();
