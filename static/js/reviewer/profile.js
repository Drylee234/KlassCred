// ── Reviewer profile ── (no profile endpoint yet; the token carries the identity)
$('profile_view').innerHTML = `
  <div class="profile-grid">
    <div class="profile-field"><div class="label">Account type</div><div class="val">Reviewer</div></div>
  </div>
  <p class="hint" style="margin-top:12px">Full reviewer profile endpoint not yet exposed — token carries identity.</p>`;
