// ── Login / Register page ──
$('t_subjects_mount').innerHTML = subjectChecks('t_subjects');
if (session.token()) goHome(session.type());       // already signed in

function switchAuthTab(tab) {
  const tabs = document.querySelectorAll('#authTabs button');
  tabs[0].classList.toggle('active', tab === 'login');
  tabs[1].classList.toggle('active', tab === 'register');
  $('loginForm').style.display = tab === 'login' ? 'block' : 'none';
  $('registerForm').style.display = tab === 'register' ? 'block' : 'none';
}

function onTypeChange() {
  const type = $('r_type').value;
  document.querySelectorAll('.type-fields').forEach(el => el.style.display = 'none');
  if (type) $(`fields_${type}`).style.display = 'block';
}

// Read the account type from the JWT payload (base64url), store the session, return the type
function startSession(token) {
  const { type } = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
  session.save(token, type);
  return type;
}

async function doLogin() {
  const email = val('l_email'), password = $('l_password').value;
  if (!email || !password) return toast('Fill in email and password', 'error');
  const { ok, data } = await api('POST', '/auth/login', { email, password }, false);
  showResponse('loginResp', data, ok);
  if (!(ok && data.token)) return toast(data.error ?? 'Login failed', 'error');
  try {
    const type = startSession(data.token);
    toast('Logged in!');
    setTimeout(() => goHome(type), 600);
  } catch {
    toast('Login OK but could not read token payload', 'error');
  }
}

async function doRegister() {
  const type = $('r_type').value, email = val('r_email'), password = $('r_password').value;
  if (!type || !email || !password) return toast('Type, email and password are required', 'error');
  const extra = profileFields(type);
  if (extra === null) return toast('Fill in the required profile fields', 'error');

  const { ok, data } = await api('POST', '/auth/register', { email, password, type, ...extra }, false);
  showResponse('registerResp', data, ok);
  if (!ok) return toast(data.error ?? 'Registration failed', 'error');

  toast('Account created — logging in…');
  const login = await api('POST', '/auth/login', { email, password }, false);
  if (login.ok && login.data.token) {
    const t = startSession(login.data.token);
    setTimeout(() => goHome(t), 800);
  }
}

// Type-specific profile fields needed at registration; null when a required one is missing
function profileFields(type) {
  if (type === 'teacher') {
    const full_name = val('t_full_name'), subjects = checkedSubjects('t_subjects'), experience_years = parseInt($('t_exp').value);
    return full_name && subjects.length && !isNaN(experience_years) ? { full_name, subjects, experience_years } : null;
  }
  if (type === 'organization') {
    const org_name = val('o_name'), cac_number = val('o_cac'), location = val('o_location');
    return org_name && location ? { org_name, cac_number: cac_number || null, location } : null;
  }
  if (type === 'parent') {
    const name = val('p_name');
    return name ? { name } : null;
  }
  const full_name = val('rv_full_name');           // reviewer
  return full_name ? { full_name } : null;
}
