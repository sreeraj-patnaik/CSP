/**
 * CSP Portal — Core JavaScript
 * Scroll reveal, smooth anchor scrolling, global utilities
 */
'use strict';

// ── Scroll Reveal ───────────────────────────────────────────────────────────
(function initScrollReveal() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            entry.target.classList.add('revealed');
          }, i * 60);
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
  );

  document.querySelectorAll('.scroll-reveal').forEach((el) => observer.observe(el));
})();

// ── Animated Stat Counters ──────────────────────────────────────────────────
(function initCounters() {
  const counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const target = parseInt(el.dataset.count, 10);
      const duration = 1800;
      const start = performance.now();

      function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(eased * target).toLocaleString();
        if (progress < 1) requestAnimationFrame(update);
        else el.textContent = target.toLocaleString();
      }

      requestAnimationFrame(update);
      observer.unobserve(el);
    });
  }, { threshold: 0.5 });

  counters.forEach((c) => observer.observe(c));
})();

// ── GSAP Animations (runs if GSAP loaded) ───────────────────────────────────
window.addEventListener('load', () => {
  if (typeof gsap === 'undefined') return;

  gsap.registerPlugin(ScrollTrigger);

  // Hero entrance animation
  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
  tl.to('#hero-badge',  { opacity: 1, y: 0, duration: 0.7, delay: 0.3 }, 0)
    .to('#hero-title',  { opacity: 1, y: 0, duration: 0.9 }, 0.4)
    .to('#hero-sub',    { opacity: 1, y: 0, duration: 0.7 }, 0.7)
    .to('#hero-ctas',   { opacity: 1, y: 0, duration: 0.6 }, 0.9)
    .to('#hero-stats',  { opacity: 1, y: 0, duration: 0.6 }, 1.1);

  // Parallax on sections with [data-parallax]
  document.querySelectorAll('[data-parallax]').forEach((el) => {
    gsap.to(el, {
      yPercent: -20,
      ease: 'none',
      scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: true },
    });
  });
});

// ── HTMX Global Config ───────────────────────────────────────────────────────
if (typeof htmx !== 'undefined') {
  document.addEventListener('htmx:configRequest', (evt) => {
    const csrf = document.cookie.match(/csrftoken=([^;]+)/);
    if (csrf) evt.detail.headers['X-CSRFToken'] = csrf[1];
  });
}

// ── Toast Notifications ─────────────────────────────────────────────────────
window.CSP = window.CSP || {};

CSP.toast = function (message, type = 'info', duration = 4000) {
  const colors = {
    info:    'bg-accent-500/10 border-accent-500/30 text-accent-400',
    success: 'bg-green-500/10 border-green-500/30 text-green-400',
    warning: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
    error:   'bg-red-500/10 border-red-500/30 text-red-400',
  };
  const container = document.getElementById('toast-container') || (() => {
    const el = document.createElement('div');
    el.id = 'toast-container';
    el.className = 'fixed top-20 right-4 z-50 space-y-2';
    document.body.appendChild(el);
    return el;
  })();
  const toast = document.createElement('div');
  toast.className = `flex items-center gap-3 px-4 py-3 rounded-xl border backdrop-blur-sm shadow-lg transition-all duration-300 ${colors[type] || colors.info}`;
  toast.innerHTML = `<span class="text-sm">${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
};

// ── Global Error Handler ─────────────────────────────────────────────────────
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
});
