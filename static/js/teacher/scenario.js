// ── Teacher scenario + video ──
const MAX_VIDEO_MB = 200;
let pickedFile = null;
let recStream = null, recorder = null, recChunks = [], recTimer = null, recStart = 0;
let vidPoll;

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
        <span class="badge ${s.generated_by === 'ai' ? 'badge-yellow' : 'badge-gray'}">${s.generated_by ?? ''}</span>
      </div>
      <p style="line-height:1.6">${s.prompt_text ?? '—'}</p>
      <p class="hint" style="margin-top:8px">Scenario ID: ${s.id}</p>
    </div>`;
  $('vid_scenario_id').value = s.id ?? '';
}

function onFilePicked(file) {
  if (!file) return;
  if (!file.type.startsWith('video/')) return toast('Choose a video file', 'error');
  if (file.size > MAX_VIDEO_MB * 1024 * 1024)
    return toast(`Video is over ${MAX_VIDEO_MB} MB`, 'error');

  clearPicked();
  pickedFile = file;
  $('vid_preview').src = URL.createObjectURL(file);
  $('vid_meta').textContent = `${file.name} · ${(file.size / 1048576).toFixed(1)} MB`;
  $('vid_picked').style.display = 'block';
  $('up_status').textContent = '';
}

function clearPicked() {
  pickedFile = null;
  const v = $('vid_preview');
  if (v) { v.removeAttribute('src'); v.load(); }
  $('vid_picked').style.display = 'none';
  $('up_prog_wrap').style.display = 'none';
}

async function startCamera() {
  try {
    recStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    $('rec_live').srcObject = recStream;
    $('rec_live').play();
    $('rec_panel').style.display = 'block';
  } catch (e) {
    toast('Camera or microphone blocked: ' + e.message, 'error');
  }
}

function startRec() {
  recChunks = [];
  const mime = ['video/webm;codecs=vp9,opus', 'video/webm', 'video/mp4']
    .find(m => window.MediaRecorder && MediaRecorder.isTypeSupported(m));

  recorder = new MediaRecorder(recStream, mime ? { mimeType: mime } : undefined);
  recorder.ondataavailable = e => { if (e.data.size) recChunks.push(e.data); };
  recorder.onstop = () => {
    const type = (recorder.mimeType || 'video/webm').split(';')[0];
    const ext = type.includes('mp4') ? 'mp4' : 'webm';
    onFilePicked(new File(recChunks, `recording-${Date.now()}.${ext}`, { type }));
    stopCamera();
  };

  recorder.start(1000);
  recStart = Date.now();
  $('rec_start').style.display = 'none';
  $('rec_stop').style.display = '';
  $('rec_time').style.display = '';
  recTimer = setInterval(() => {
    $('rec_time').textContent = fmtTime(Date.now() - recStart);
  }, 500);
}

function stopRec() {
  if (recorder?.state === 'recording') recorder.stop();
}

function stopCamera() {
  clearInterval(recTimer);
  recStream?.getTracks().forEach(t => t.stop());
  recStream = null;
  $('rec_panel').style.display = 'none';
  $('rec_start').style.display = '';
  $('rec_stop').style.display = 'none';
  $('rec_time').style.display = 'none';
}

async function doRequestUploadUrl() {
  const scenario_id = parseInt($('vid_scenario_id').value);
  if (!scenario_id) {
    toast('Get a scenario first', 'error');
    return null;
  }

  const res = await api('POST', '/teachers/video/upload-url', { scenario_id });
  showResponse('uploadUrlResp', res.data, res.ok);
  if (!res.ok) {
    toast(res.data.error ?? 'Could not prepare upload', 'error');
    return null;
  }
  return res.data;
}

async function doUpload() {
  if (!pickedFile) return toast('Choose or record a video first', 'error');

  const sign = await doRequestUploadUrl();
  if (!sign) return;

  if (typeof ByteshipClient !== 'function')
    return toast('Byteship browser SDK failed to load', 'error');

  const scenarioId = parseInt($('vid_scenario_id').value);
  const client = new ByteshipClient({ uploadToken: sign.upload_token });

  const safeName = pickedFile.name.replace(/[^a-zA-Z0-9._-]/g, '_');
  const path = `${sign.folder}/${Date.now()}-${safeName}`;

  $('btn_upload').disabled = true;
  $('up_prog_wrap').style.display = 'block';
  $('up_status').textContent = 'Uploading video to Byteship…';

  try {
    const result = await client.upload(pickedFile, {
      path,
      visibility: 'public',
    });

    const videoUrl = result.url ?? result.file?.url;
    if (!videoUrl) throw new Error('Byteship upload completed without a video URL');

    $('up_status').textContent = 'Upload complete — starting review…';

    const confirm = await api('POST', '/teachers/video/confirm', {
      scenario_id: scenarioId,
      video_url: videoUrl,
    });

    showResponse('confirmResp', confirm.data, confirm.ok);

    if (!confirm.ok) {
      toast(confirm.data.error ?? 'Upload succeeded, but confirmation failed', 'error');
      return;
    }

    toast('Video uploaded and submitted for review');
    clearPicked();
    loadVideos();
  } catch (e) {
    $('up_status').textContent = e.message;
    toast(e.message, 'error');
  } finally {
    $('btn_upload').disabled = false;
  }
}

const VSTEPS = [
  ['uploaded', 'Video uploaded'],
  ['ai_reviewing', 'AI reviewing'],
  ['ai_reviewed', 'AI review complete'],
  ['assigned', 'Human review assigned'],
  ['in_progress', 'Human review in progress'],
  ['completed', 'Completed']
];

function vsteps(st) {
  if (st === 'failed') return '<ul class="steps"><li class="bad">✗ Processing failed</li></ul>';
  const i = VSTEPS.findIndex(s => s[0] === st);
  return '<ul class="steps">' + VSTEPS.map((s, n) => {
    const done = n < i || st === 'completed';
    return `<li class="${done ? 'done' : n === i ? 'cur' : ''}">${done ? '✓' : n === i ? '→' : '○'} ${s[1]}</li>`;
  }).join('') + '</ul>';
}

async function loadVideos() {
  clearTimeout(vidPoll);
  const list = asList(await api('GET', '/teachers/videos'));
  $('vid_list').innerHTML = list.length
    ? list.map(v => `<div class="card" style="margin-bottom:12px;background:var(--surface2)">
        <strong>${v.subject ?? 'Scenario'} · #${v.scenario_id}</strong>
        ${vsteps(v.status)}
      </div>`).join('')
    : '<p class="hint">No videos yet.</p>';

  if (list.some(v => !['completed', 'failed'].includes(v.status)))
    vidPoll = setTimeout(loadVideos, 6000);
}

loadVideos();