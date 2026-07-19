/**
 * Cricket Ticket Booking System – Client-Side Validation
 * Covers: login, registration, match creation, seat plan, booking
 */

// ─── Helpers ─────────────────────────────────────────────────────────────────
const setValid   = (el) => { el.classList.add('is-valid');   el.classList.remove('is-invalid'); };
const setInvalid = (el) => { el.classList.add('is-invalid'); el.classList.remove('is-valid'); };
const clearState = (el) => { el.classList.remove('is-valid','is-invalid'); };

function showFeedback(el, msg) {
  const fb = el.nextElementSibling;
  if (fb && fb.classList.contains('invalid-feedback')) fb.textContent = msg;
}
function hideFeedback(el) {
  const fb = el.nextElementSibling;
  if (fb && fb.classList.contains('invalid-feedback')) fb.textContent = '';
}

const PATTERNS = {
  email:  /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  mobile: /^[6-9]\d{9}$/,
  name:   /^[A-Za-z\s'.'-]{3,100}$/,
};

// ─── Single-field validators ──────────────────────────────────────────────────
function validateEmail(el) {
  const v = el.value.trim();
  if (!v)                          { setInvalid(el); showFeedback(el,'Email is required.'); return false; }
  if (!PATTERNS.email.test(v))     { setInvalid(el); showFeedback(el,'Enter a valid email address.'); return false; }
  setValid(el); hideFeedback(el);  return true;
}

function validatePassword(el, minLen = 8) {
  const v = el.value;
  if (!v)                          { setInvalid(el); showFeedback(el,'Password is required.'); return false; }
  if (v.length < minLen)           { setInvalid(el); showFeedback(el,`Password must be at least ${minLen} characters.`); return false; }
  setValid(el); hideFeedback(el);  return true;
}

function validatePasswordStrength(el) {
  const v = el.value;
  const hasUpper  = /[A-Z]/.test(v);
  const hasLower  = /[a-z]/.test(v);
  const hasDigit  = /\d/.test(v);
  const hasSpecial= /[!@#$%^&*(),.?":{}|<>_\-]/.test(v);
  const score = [v.length >= 8, hasUpper, hasLower, hasDigit, hasSpecial].filter(Boolean).length;

  const bar   = document.getElementById('strengthBar');
  const label = document.getElementById('strengthLabel');
  if (!bar || !label) return score;

  const levels = [
    { pct:0,   color:'#e0e0e0', text:'' },
    { pct:20,  color:'#ef5350', text:'Very Weak' },
    { pct:40,  color:'#ff7043', text:'Weak' },
    { pct:60,  color:'#ffa726', text:'Fair' },
    { pct:80,  color:'#66bb6a', text:'Strong' },
    { pct:100, color:'#2e7d32', text:'Very Strong' },
  ];
  const lvl = levels[Math.min(score, 5)];
  bar.style.width     = lvl.pct + '%';
  bar.style.background= lvl.color;
  label.textContent   = lvl.text;
  label.style.color   = lvl.color;
  return score;
}

function validateName(el) {
  const v = el.value.trim();
  if (!v)                          { setInvalid(el); showFeedback(el,'Name is required.'); return false; }
  if (v.length < 3)                { setInvalid(el); showFeedback(el,'Name must be at least 3 characters.'); return false; }
  if (v.length > 100)              { setInvalid(el); showFeedback(el,'Name must not exceed 100 characters.'); return false; }
  if (!/^[A-Za-z\s'.]+$/.test(v)) { setInvalid(el); showFeedback(el,'Name may only contain letters, spaces, and apostrophes.'); return false; }
  setValid(el); hideFeedback(el);  return true;
}

function validateMobile(el) {
  const v = el.value.trim();
  if (!v)                          { setInvalid(el); showFeedback(el,'Mobile number is required.'); return false; }
  if (!PATTERNS.mobile.test(v))    { setInvalid(el); showFeedback(el,'Enter a valid 10-digit Indian mobile number (starts with 6-9).'); return false; }
  setValid(el); hideFeedback(el);  return true;
}

function validateMinLength(el, min, label) {
  const v = el.value.trim();
  if (!v)           { setInvalid(el); showFeedback(el,`${label} is required.`); return false; }
  if (v.length < min){ setInvalid(el); showFeedback(el,`${label} must be at least ${min} characters.`); return false; }
  setValid(el); hideFeedback(el); return true;
}

function validatePositiveNumber(el, label) {
  const v = parseFloat(el.value);
  if (isNaN(v) || v <= 0) { setInvalid(el); showFeedback(el,`${label} must be a positive number.`); return false; }
  setValid(el); hideFeedback(el); return true;
}

function validatePositiveInt(el, label) {
  const v = parseInt(el.value, 10);
  if (isNaN(v) || v < 1)  { setInvalid(el); showFeedback(el,`${label} must be a positive integer.`); return false; }
  setValid(el); hideFeedback(el); return true;
}

// ─── Login Form ───────────────────────────────────────────────────────────────
(function initLoginForm() {
  const form = document.getElementById('loginForm');
  if (!form) return;
  const emailEl    = form.querySelector('[name="email"]');
  const passwordEl = form.querySelector('[name="password"]');

  emailEl   ?.addEventListener('blur', () => validateEmail(emailEl));
  passwordEl?.addEventListener('blur', () => validatePassword(passwordEl, 6));

  form.addEventListener('submit', function(e) {
    let ok = true;
    if (!validateEmail(emailEl))          ok = false;
    if (!validatePassword(passwordEl, 6)) ok = false;
    if (!ok) { e.preventDefault(); e.stopPropagation(); }
  });
})();

// ─── Registration Form ────────────────────────────────────────────────────────
(function initRegForm() {
  const form = document.getElementById('regForm');
  if (!form) return;
  const nameEl    = form.querySelector('[name="name"]');
  const emailEl   = form.querySelector('[name="email"]');
  const mobileEl  = form.querySelector('[name="mobile"]');
  const passEl    = form.querySelector('[name="password"]');
  const pass2El   = form.querySelector('[name="confirm_password"]');
  const typeEl    = form.querySelector('[name="user_type"]');

  nameEl  ?.addEventListener('blur', () => validateName(nameEl));
  emailEl ?.addEventListener('blur', () => validateEmail(emailEl));
  mobileEl?.addEventListener('blur', () => validateMobile(mobileEl));
  passEl  ?.addEventListener('input', () => {
    validatePasswordStrength(passEl);
    validatePassword(passEl, 8);
    if (pass2El?.value) validateConfirmPass();
  });
  passEl  ?.addEventListener('blur', () => validatePassword(passEl, 8));
  pass2El ?.addEventListener('blur', validateConfirmPass);

  function validateConfirmPass() {
    if (!pass2El) return true;
    if (pass2El.value !== passEl.value) {
      setInvalid(pass2El); showFeedback(pass2El,'Passwords do not match.'); return false;
    }
    setValid(pass2El); hideFeedback(pass2El); return true;
  }

  function validateSelect(el, label) {
    if (!el.value) { setInvalid(el); showFeedback(el,`${label} is required.`); return false; }
    setValid(el); hideFeedback(el); return true;
  }

  form.addEventListener('submit', function(e) {
    let ok = true;
    if (!validateName(nameEl))              ok = false;
    if (!validateEmail(emailEl))            ok = false;
    if (!validateMobile(mobileEl))          ok = false;
    if (!validatePassword(passEl, 8))       ok = false;
    if (!validateConfirmPass())             ok = false;
    if (!validateSelect(typeEl,'User type'))ok = false;
    if (!ok) { e.preventDefault(); e.stopPropagation(); }
  });
})();

// ─── Match Form ───────────────────────────────────────────────────────────────
(function initMatchForm() {
  const form = document.getElementById('matchForm');
  if (!form) return;
  const venueEl  = form.querySelector('[name="venue_name"]');
  const locEl    = form.querySelector('[name="location"]');
  const t1El     = form.querySelector('[name="team1"]');
  const t2El     = form.querySelector('[name="team2"]');
  const startEl  = form.querySelector('[name="start_time"]');
  const endEl    = form.querySelector('[name="end_time"]');

  venueEl?.addEventListener('blur', () => validateMinLength(venueEl, 3, 'Venue name'));
  locEl  ?.addEventListener('blur', () => validateMinLength(locEl,   3, 'Location'));
  t1El   ?.addEventListener('blur', () => validateMinLength(t1El,    2, 'Team 1 name'));
  t2El   ?.addEventListener('blur', () => { validateMinLength(t2El, 2, 'Team 2 name'); checkTeams(); });

  function checkTeams() {
    if (!t1El || !t2El) return true;
    const v1 = t1El.value.trim().toLowerCase();
    const v2 = t2El.value.trim().toLowerCase();
    if (v1 && v2 && v1 === v2) {
      setInvalid(t2El); showFeedback(t2El,'Team 2 must be different from Team 1.');
      return false;
    }
    return true;
  }

  function validateDateRange() {
    if (!startEl || !endEl) return true;
    if (!startEl.value) { setInvalid(startEl); showFeedback(startEl,'Start time is required.'); return false; }
    setValid(startEl);
    if (!endEl.value)   { setInvalid(endEl);   showFeedback(endEl,  'End time is required.');   return false; }
    const s = new Date(startEl.value), e = new Date(endEl.value);
    if (e <= s) { setInvalid(endEl); showFeedback(endEl,'End time must be after start time.'); return false; }
    setValid(endEl); return true;
  }

  startEl?.addEventListener('change', () => { setValid(startEl); validateDateRange(); });
  endEl  ?.addEventListener('change', validateDateRange);

  form.addEventListener('submit', function(e) {
    let ok = true;
    if (!validateMinLength(venueEl, 3, 'Venue name'))   ok = false;
    if (!validateMinLength(locEl,   3, 'Location'))     ok = false;
    if (!validateMinLength(t1El,    2, 'Team 1 name'))  ok = false;
    if (!validateMinLength(t2El,    2, 'Team 2 name'))  ok = false;
    if (!checkTeams())                                  ok = false;
    if (!validateDateRange())                           ok = false;
    if (!ok) { e.preventDefault(); e.stopPropagation(); }
  });
})();

// ─── Seat Plan Form ───────────────────────────────────────────────────────────
(function initSeatForm() {
  const form = document.getElementById('seatForm');
  if (!form) return;
  const colEl   = form.querySelector('[name="column_name"]');
  const rowEl   = form.querySelector('[name="row_name"]');
  const startEl = form.querySelector('[name="start_seat"]');
  const endEl   = form.querySelector('[name="end_seat"]');
  const priceEl = form.querySelector('[name="seat_price"]');

  function validateColumnName(el) {
    const v = el.value.trim().toUpperCase();
    if (!v)                  { setInvalid(el); showFeedback(el,'Column name is required.'); return false; }
    if (!/^[A-Z]{1,5}$/.test(v)) { setInvalid(el); showFeedback(el,'Column: 1–5 uppercase letters (e.g. A, GA, VIP).'); return false; }
    el.value = v;
    setValid(el); hideFeedback(el); return true;
  }

  function validateSeatRange() {
    const s = parseInt(startEl?.value, 10);
    const e = parseInt(endEl?.value,   10);
    if (isNaN(s) || s < 1) { setInvalid(startEl); showFeedback(startEl,'Start seat must be ≥ 1.'); return false; }
    setValid(startEl);
    if (isNaN(e) || e < s) { setInvalid(endEl);   showFeedback(endEl,'End seat must be ≥ Start seat.'); return false; }
    const count = e - s + 1;
    if (count > 500)       { setInvalid(endEl);   showFeedback(endEl,'Cannot add more than 500 seats at once.'); return false; }
    setValid(endEl); return true;
  }

  colEl  ?.addEventListener('blur', () => validateColumnName(colEl));
  rowEl  ?.addEventListener('blur', () => validateMinLength(rowEl, 1, 'Row name'));
  startEl?.addEventListener('change', validateSeatRange);
  endEl  ?.addEventListener('change', validateSeatRange);
  priceEl?.addEventListener('blur',  () => validatePositiveNumber(priceEl,'Seat price'));

  form.addEventListener('submit', function(e) {
    let ok = true;
    if (!validateColumnName(colEl))                       ok = false;
    if (!validateMinLength(rowEl,  1, 'Row name'))        ok = false;
    if (!validateSeatRange())                             ok = false;
    if (!validatePositiveNumber(priceEl, 'Seat price'))   ok = false;
    if (!ok) { e.preventDefault(); e.stopPropagation(); }
  });
})();

// ─── Booking Form ─────────────────────────────────────────────────────────────
(function initBookingForm() {
  const form = document.getElementById('bookingForm');
  if (!form) return;

  const payEl  = form.querySelector('[name="payment_text"]');
  const msgEl  = document.getElementById('seatSelectionMsg');
  const totalEl= document.getElementById('totalAmount');
  const countEl= document.getElementById('selectedCount');
  const listEl = document.getElementById('selected-seats-list');

  // Handle seat checkbox clicks
  form.querySelectorAll('.seat-checkbox').forEach(cb => {
    cb.addEventListener('change', function() {
      const lbl = this.closest('.seat-btn');
      if (this.checked) lbl?.classList.add('selected-seat');
      else              lbl?.classList.remove('selected-seat');
      updateSummary();
    });
  });

  // Seat buttons (click on the visible div acts as checkbox toggle)
  form.querySelectorAll('.seat-btn.available').forEach(btn => {
    btn.addEventListener('click', function(e) {
      if (e.target.tagName === 'INPUT') return; // let checkbox handle itself
      const cb = this.querySelector('.seat-checkbox');
      if (cb) { cb.checked = !cb.checked; cb.dispatchEvent(new Event('change')); }
    });
  });

  function updateSummary() {
    const checked = form.querySelectorAll('.seat-checkbox:checked');
    let total = 0;
    const names = [];
    checked.forEach(cb => {
      total += parseFloat(cb.dataset.price || 0);
      names.push(cb.dataset.label);
    });
    if (totalEl)  totalEl.textContent  = '₹' + total.toFixed(2);
    if (countEl)  countEl.textContent  = checked.length;
    if (listEl) {
      listEl.innerHTML = names.length
        ? names.map(n=>`<span class="badge bg-light text-dark border me-1 mb-1">${n}</span>`).join('')
        : '<span class="text-white-50 small">No seats selected yet</span>';
    }
    if (msgEl) msgEl.style.display = checked.length ? 'none' : 'block';
  }
  updateSummary();

  payEl?.addEventListener('blur', () => {
    const v = payEl.value.trim();
    if (!v || v.length < 5) { setInvalid(payEl); showFeedback(payEl,'Enter a valid payment reference (min. 5 characters).'); }
    else { setValid(payEl); hideFeedback(payEl); }
  });

  form.addEventListener('submit', function(e) {
    let ok = true;
    const checked = form.querySelectorAll('.seat-checkbox:checked');
    if (checked.length === 0) {
      if (msgEl) { msgEl.style.display='block'; msgEl.textContent='Please select at least one seat before confirming.'; }
      ok = false;
    }
    const pv = payEl?.value.trim();
    if (!pv || pv.length < 5) {
      if (payEl) { setInvalid(payEl); showFeedback(payEl,'Enter a valid payment reference (min. 5 characters).'); }
      ok = false;
    }
    if (!ok) { e.preventDefault(); e.stopPropagation(); }
  });
})();

// ─── Auto-dismiss flash messages ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.alert-flash').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .5s, max-height .5s';
      el.style.opacity = '0'; el.style.maxHeight = '0'; el.style.overflow='hidden';
      setTimeout(()=> el.remove(), 500);
    }, 4000);
  });
});
