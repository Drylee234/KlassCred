// ── Employer profile (organization or parent) ──
const isOrg = session.type() === 'organization';
$('ep_org_fields').style.display = isOrg ? 'block' : 'none';
$('ep_parent_fields').style.display = isOrg ? 'none' : 'block';

async function loadProfile() {
  const res = await api('GET', '/employers/profile');
  const view = $('profile_view');
  if (!res.ok) { view.innerHTML = emptyState('⚠️', res.data.error ?? 'Error loading profile'); return; }
  const p = res.data;
  const field = (label, v) => `<div class="profile-field"><div class="label">${label}</div><div class="val">${v ?? '—'}</div></div>`;

  if (isOrg) {
    $('ep_org_name').value = p.org_name ?? '';
    $('ep_cac').value = p.cac_number ?? '';
    $('ep_location').value = p.location ?? '';
  } else {
    $('ep_p_name').value = p.name ?? '';
  }

  view.innerHTML = `
    <div class="profile-grid">
      ${field('Email', p.email)}
      ${field('Type', p.type ?? session.type())}
      ${field('Verified', badge(p.id_verified ? 'verified' : 'unverified', { verified: 'badge-green', unverified: 'badge-red' }))}
      ${field('Member since', p.created_at?.slice(0, 10))}
      ${isOrg ? field('Org name', p.org_name) + field('CAC number', p.cac_number) + field('Location', p.location) : field('Name', p.name)}
    </div>`;
}

const doUpdateProfile = () => send('PUT', '/employers/profile',
  isOrg ? { org_name: val('ep_org_name'), cac_number: val('ep_cac') || null, location: val('ep_location') || null }
        : { name: val('ep_p_name') },
  { resp: 'editProfileModalResp', msg: 'Profile updated', done: () => { closeModal('editProfileModal'); loadProfile(); } });

loadProfile();
