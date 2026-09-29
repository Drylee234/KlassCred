// ── Teacher profile ──
async function loadProfile() {
  const res = await api('GET', '/teachers/profile');
  if (!res.ok) { $('profile_view').innerHTML = emptyState('⚠️', res.data.error ?? 'Could not load profile'); return; }
  const p = res.data;
  $('profile_view').innerHTML = `
    <div class="profile-grid">
      <div class="profile-field"><div class="label">Full name</div><div class="val">${p.full_name ?? '—'}</div></div>
      <div class="profile-field"><div class="label">Email</div><div class="val">${p.email ?? '—'}</div></div>
      <div class="profile-field"><div class="label">Experience</div><div class="val">${p.experience_years ?? '—'} yrs</div></div>
      <div class="profile-field"><div class="label">Verified</div><div class="val">${badge(p.id_verified ? 'verified' : 'unverified', { verified: 'badge-green', unverified: 'badge-red' })}</div></div>
      <div class="profile-field"><div class="label">Profile complete</div><div class="val">${badge(p.profile_complete ? 'yes' : 'no', { yes: 'badge-green', no: 'badge-yellow' })}</div></div>
      <div class="profile-field"><div class="label">Member since</div><div class="val">${p.created_at ? p.created_at.slice(0, 10) : '—'}</div></div>
    </div>
    <div class="mt-16">
      <div class="label">Subjects</div>
      <div class="chip-list">${(p.subjects ?? []).map(s => `<span class="chip">${s}</span>`).join('') || '—'}</div>
    </div>`;

  // pre-fill the edit modal
  $('ep_full_name').value = p.full_name ?? '';
  $('ep_subjects_mount').innerHTML = subjectChecks('ep_subjects', p.subjects ?? []);
  $('ep_exp').value = p.experience_years ?? '';
}

const doUpdateProfile = () => send('PUT', '/teachers/profile', {
  full_name: val('ep_full_name'),
  subjects: checkedSubjects('ep_subjects'),
  experience_years: parseInt($('ep_exp').value) || 0,
}, { resp: 'editProfileModalResp', msg: 'Profile updated', done: () => { closeModal('editProfileModal'); loadProfile(); } });

loadProfile();
