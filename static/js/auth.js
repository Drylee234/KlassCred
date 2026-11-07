// ── Login / Register page ──
$('t_subjects_mount').innerHTML = subjectChecks('t_subjects');
let googleOnboardingToken = null;
let googleSignInCompleted = false;

function readJwtPayload(token) {
  const segment = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
  const padded = segment + '='.repeat((4 - segment.length % 4) % 4);
  return JSON.parse(atob(padded));
}

const authFragment = new URLSearchParams(location.hash.slice(1));
const googleToken = authFragment.get('kc_google_token');
const googleError = authFragment.get('kc_oauth_error');
if (googleToken || googleError) history.replaceState(null, '', location.pathname + location.search);

if (googleToken) {
  try {
    const claims = readJwtPayload(googleToken);
    if (claims.purpose === 'google_onboarding') {
      googleOnboardingToken = googleToken;
      $('r_email').value = claims.email;
      $('r_email').disabled = true;
      $('r_email_field').style.display = 'none';
      $('r_password_field').style.display = 'none';
      $('googleOnboardingNote').style.display = 'block';
      switchAuthTab('register');
    } else {
      const type = startSession(googleToken);
      googleSignInCompleted = true;
      toast('Signed in with Google!');
      setTimeout(() => goHome(type), 600);
    }
  } catch {
    toast('Google sign-in could not be completed. Please try again.', 'error');
  }
}
if (googleError) {
  const messages = {
    google_not_configured: 'Google sign-in is not configured yet.',
    google_email_unverified: 'Use a Google account with a verified email.',
    google_signin_failed: 'Google sign-in failed. Please try again.',
  };
  toast(messages[googleError] ?? 'Google sign-in failed.', 'error');
}

if (googleOnboardingToken || googleSignInCompleted) {
  // The OAuth callback already established the next step or started a session.
} else if (session.token() && !session.expired()) goHome(session.type());
else session.clear(); // stale/expired token: forget it

try {                                                                // note left by endSession()
  const notice = sessionStorage.getItem('kc_notice');
  if (notice) { sessionStorage.removeItem('kc_notice'); toast(notice, 'error'); }
} catch {}

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
  const { type, admin } = readJwtPayload(token);
  const homeType = admin ? 'admin' : type;
  session.save(token, homeType);
  return homeType;
}

async function doLogin() {
  const email = val('l_email'), password = $('l_password').value;
  if (!email || !password) return toast('Fill in email and password', 'error');
  const { ok, data } = await api('POST', '/auth/login', { email, password }, false);

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
  if (!type || !email || (!googleOnboardingToken && !password)) return toast('Type, email and password are required', 'error');
  const extra = profileFields(type);
  if (extra === null) return toast('Fill in the required profile fields', 'error');

  if (googleOnboardingToken) {
    const { ok, data } = await api('POST', '/auth/google/complete', {
      onboarding_token: googleOnboardingToken, type, ...extra,
    }, false);
    if (!(ok && data.token)) return toast(data.error ?? 'Google sign-up failed', 'error');
    googleOnboardingToken = null;
    const homeType = startSession(data.token);
    toast('Account created!');
    setTimeout(() => goHome(homeType), 600);
    return;
  }

  const { ok, data } = await api('POST', '/auth/register', { email, password, type, ...extra }, false);

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
