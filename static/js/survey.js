'use strict';

(function () {
  var currentStep = 1;
  var usesInternet = null;
  var TOTAL_STEPS = 3;

  /* ─── Helpers ─────────────────────────────────────────────────── */

  function show(el) { if (el) el.style.display = 'block'; }
  function hide(el) { if (el) el.style.display = 'none'; }

  function setHidden(name, value) {
    var inp = document.querySelector('input[data-field="' + name + '"]');
    if (inp) inp.value = value;
  }

  function getHidden(name) {
    var inp = document.querySelector('input[data-field="' + name + '"]');
    return inp ? inp.value : '';
  }

  /* ─── Radio selection ─────────────────────────────────────────── */

  window.selectRadio = function (name, value, el) {
    // deselect all siblings in the same group
    document.querySelectorAll('[data-group="' + name + '"]').forEach(function (btn) {
      btn.classList.remove('selected');
    });
    el.classList.add('selected');
    setHidden(name, value);

    // Internet branching
    if (name === 'uses_internet') {
      usesInternet = (value === 'true');
    }
    // Show fraud description textarea if "yes"
    if (name === 'faced_fraud') {
      var desc = document.getElementById('fraud-desc-section');
      if (desc) desc.style.display = (value === 'yes') ? 'block' : 'none';
    }
    hideErr(name);
  };

  /* ─── Checkbox (multi-select) ──────────────────────────────────── */

  window.toggleCheckbox = function (name, value, el) {
    el.classList.toggle('selected');
    var hiddenInp = document.querySelector('input[data-field="' + name + '"]');
    if (!hiddenInp) return;
    var current = [];
    try { current = JSON.parse(hiddenInp.value || '[]'); } catch (e) {}
    var idx = current.indexOf(value);
    if (idx === -1) { current.push(value); } else { current.splice(idx, 1); }
    hiddenInp.value = JSON.stringify(current);
    hideErr(name);
  };

  /* ─── Navigation ───────────────────────────────────────────────── */

  window.nextStep = function () {
    if (!validateStep(currentStep)) return;

    var next = currentStep + 1;

    // Skip internet-usage step if they said No
    if (next === 2 && usesInternet === false) {
      clearInternetInputs();
      next = 3;
    }

    goToStep(next);
  };

  window.prevStep = function () {
    var prev = currentStep - 1;
    if (prev === 2 && usesInternet === false) prev = 1;
    goToStep(prev);
  };

  function goToStep(n) {
    hide(document.getElementById('step-' + currentStep));
    show(document.getElementById('step-' + n));
    currentStep = n;
    updateUI();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function clearInternetInputs() {
    var step2 = document.getElementById('step-2');
    if (!step2) return;
    step2.querySelectorAll('input').forEach(function (inp) {
      if (inp.type !== 'submit') inp.value = inp.type === 'checkbox' ? '' : '';
    });
  }

  /* ─── Progress UI ─────────────────────────────────────────────── */

  function updateUI() {
    var pct = Math.round((currentStep / TOTAL_STEPS) * 100);
    var bar = document.getElementById('progress-bar');
    if (bar) bar.style.width = pct + '%';

    var lbl = document.getElementById('current-step-label');
    if (lbl) lbl.textContent = currentStep;

    var btnPrev = document.getElementById('btn-prev');
    var btnNext = document.getElementById('btn-next');
    var btnSub  = document.getElementById('btn-submit');

    if (btnPrev) btnPrev.style.display = currentStep > 1 ? 'inline-flex' : 'none';

    var isLast = (currentStep === TOTAL_STEPS);
    if (btnNext) btnNext.style.display = isLast ? 'none' : 'inline-flex';
    if (btnSub)  btnSub.style.display  = isLast ? 'inline-flex' : 'none';

    // progress dots
    for (var i = 1; i <= TOTAL_STEPS; i++) {
      var dot = document.getElementById('ps-' + i);
      if (!dot) continue;
      dot.classList.remove('complete', 'current');
      if (i < currentStep) dot.classList.add('complete');
      else if (i === currentStep) dot.classList.add('current');
    }
  }

  /* ─── Validation ──────────────────────────────────────────────── */

  function validateStep(step) {
    var container = document.getElementById('step-' + step);
    if (!container) return true;

    var ok = true;

    container.querySelectorAll('input[data-field][data-required]').forEach(function (inp) {
      var val = inp.value.trim();
      if (!val || val === '[]') {
        showErr(inp.dataset.field);
        ok = false;
      }
    });

    container.querySelectorAll('select[required]').forEach(function (sel) {
      if (!sel.value) {
        showErr(sel.name);
        ok = false;
      }
    });

    return ok;
  }

  function showErr(name) {
    var el = document.getElementById('err-' + name);
    if (el) el.style.display = 'block';
  }

  function hideErr(name) {
    var el = document.getElementById('err-' + name);
    if (el) el.style.display = 'none';
  }

  /* ─── Submit ───────────────────────────────────────────────────── */
  var form = document.getElementById('survey-form');
  if (form) {
    form.addEventListener('submit', function () {
      var btn = document.getElementById('btn-submit');
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Submitting…';
      }
    });
  }

  /* ─── Init ────────────────────────────────────────────────────── */
  // Hide all steps except step-1
  for (var i = 2; i <= TOTAL_STEPS; i++) {
    var s = document.getElementById('step-' + i);
    if (s) s.style.display = 'none';
  }
  show(document.getElementById('step-1'));
  updateUI();
})();
