/* ══════════════════════════════════════════════
   app.js — XBlog Frontend
   ══════════════════════════════════════════════ */
(() => {
'use strict';

const html = document.documentElement;

// ── Theme ────────────────────────────────────
const stored = localStorage.getItem('xblog-theme') || 'dark';
html.setAttribute('data-theme', stored);

function toggleTheme() {
  const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('xblog-theme', next);
  document.querySelectorAll('.theme-icon').forEach(el => {
    el.className = `theme-icon fas ${next === 'dark' ? 'fa-moon' : 'fa-sun'}`;
  });
}
document.querySelectorAll('[data-theme-toggle]').forEach(el => el.addEventListener('click', toggleTheme));

// init icon
document.querySelectorAll('.theme-icon').forEach(el => {
  el.className = `theme-icon fas ${stored === 'dark' ? 'fa-moon' : 'fa-sun'}`;
});

// ── Reading progress ─────────────────────────
const bar = document.getElementById('progress');
if (bar) {
  window.addEventListener('scroll', () => {
    const total = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = total > 0 ? Math.min(100, window.scrollY / total * 100) + '%' : '0%';
  }, { passive: true });
}

// ── Back to top ──────────────────────────────
const btt = document.getElementById('back-top');
if (btt) {
  window.addEventListener('scroll', () => btt.classList.toggle('show', window.scrollY > 500), { passive: true });
  btt.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

// ── Toast system ─────────────────────────────
function toast(msg, type = 'info', duration = 3500) {
  let stack = document.querySelector('.toast-stack');
  if (!stack) {
    stack = document.createElement('div');
    stack.className = 'toast-stack';
    document.body.appendChild(stack);
  }
  const icons = { success: 'fa-check-circle', error: 'fa-times-circle', info: 'fa-info-circle' };
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<i class="toast-icon fas ${icons[type]||icons.info}"></i><span class="toast-msg">${msg}</span><button class="toast-close" onclick="this.parentElement.remove()"><i class="fas fa-times"></i></button>`;
  stack.appendChild(t);
  setTimeout(() => { t.classList.add('out'); setTimeout(() => t.remove(), 200); }, duration);
}
window.xToast = toast;

// ── CSRF helper ──────────────────────────────
function csrf() {
  return document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1] || '';
}
window.xCsrf = csrf;

// ── Newsletter (AJAX) ────────────────────────
document.querySelectorAll('[data-nl-form]').forEach(form => {
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = form.querySelector('[type=submit]');
    const orig = btn.textContent;
    btn.disabled = true; btn.textContent = '…';
    try {
      const r = await fetch(form.action, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': csrf() },
        body: new FormData(form),
      });
      const d = await r.json();
      toast(d.msg || 'Done!', d.ok ? 'success' : 'error');
      if (d.ok) form.reset();
    } catch { toast('Network error.', 'error'); }
    finally { btn.disabled = false; btn.textContent = orig; }
  });
});

// ── Mobile nav ───────────────────────────────
const mobileMenu = document.getElementById('mobileMenu');
document.querySelectorAll('[data-nav-toggle]').forEach(el =>
  el.addEventListener('click', () => mobileMenu?.classList.toggle('open'))
);

// ── Auto-dismiss flash messages ───────────────
document.querySelectorAll('.flash-msg').forEach(el => {
  setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 4000);
});

})();
