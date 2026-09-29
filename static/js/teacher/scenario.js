// ── Teacher scenario + video ──
async function loadScenario() {
  const res = await api('GET', '/teachers/scenario');
  showResponse('scenarioResp', res.data, res.ok);
  if (!res.ok) return toast(res.data.error ?? 'Failed', 'error');
  const s = res.data;
  $('scenario_view').innerHTML = `
    <div class="card" style="background:var(--surface2)">
      <div class="flex-row" style="margin-bottom:10px">
        <span class="badge badge-blue">${s.subject ?? '—'}</span>
        <span class="badge badge-gray">${s.level ?? '—'}</span>
        <span class="badge ${s.generated_by === 'ai' ? 'badge-yellow' : 'badge-gray'}">${s.generated_by}</span>
      </div>
      <p style="line-height:1.6">${s.prompt_text ?? '—'}</p>
      <p class="hint" style="margin-top:8px">Scenario ID: ${s.id}</p>
    </div>`;
  $('vid_scenario_id').value = $('confirm_scenario_id').value = s.id ?? '';
}

function doRequestUploadUrl() {
  const scenario_id = parseInt($('vid_scenario_id').value);
  if (isNaN(scenario_id)) return toast('Get a scenario first', 'error');
  return send('POST', '/teachers/video/upload-url', { scenario_id }, { resp: 'uploadUrlResp', msg: 'Upload URL received' });
}

const doConfirmUpload = () => send('POST', '/teachers/video/confirm',
  { scenario_id: parseInt($('confirm_scenario_id').value), video_url: val('confirm_video_url') },
  { resp: 'confirmResp', msg: 'Upload confirmed', done: loadVideos });

// ── Video pipeline status (polls while anything is still processing) ──
const VSTEPS = [['uploaded', 'Video uploaded'], ['ai_reviewing', 'AI reviewing'], ['ai_reviewed', 'AI review complete'],
  ['assigned', 'Human review assigned'], ['in_progress', 'Human review in progress'], ['completed', 'Completed']];

function vsteps(st) {
  if (st === 'failed') return '<ul class="steps"><li class="bad">✗ Processing failed</li></ul>';
  const i = VSTEPS.findIndex(s => s[0] === st);
  return '<ul class="steps">' + VSTEPS.map((s, n) => {
    const done = n < i || st === 'completed';
    return `<li class="${done ? 'done' : n === i ? 'cur' : ''}">${done ? '✓' : n === i ? '→' : '○'} ${s[1]}</li>`;
  }).join('') + '</ul>';
}

let vidPoll;
async function loadVideos() {
  clearTimeout(vidPoll);
  const list = asList(await api('GET', '/teachers/videos'));
  $('vid_list').innerHTML = list.length
    ? list.map(v => `<div class="card" style="margin-bottom:12px;background:var(--surface2)"><strong>${v.subject ?? 'Scenario'} · #${v.scenario_id}</strong>${vsteps(v.status)}</div>`).join('')
    : '<p class="hint">No videos yet.</p>';
  if (list.some(v => !['completed', 'failed'].includes(v.status))) vidPoll = setTimeout(loadVideos, 6000);
}

loadVideos();
