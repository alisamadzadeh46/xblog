/* XBlog main.js — v2 */
(function () {
  'use strict';

  // ── Theme ────────────────────────────────────────────────────────
  const html     = document.documentElement;
  const themeBtn = document.getElementById('themeBtn');
  const themeIco = document.getElementById('themeIcon');
  const saved    = localStorage.getItem('xtheme') || 'dark';
  html.setAttribute('data-theme', saved);
  setIcon(saved);

  themeBtn?.addEventListener('click', () => {
    const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('xtheme', next);
    setIcon(next);
  });

  function setIcon(t) {
    if (!themeIco) return;
    themeIco.className = t === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
  }

  // ── Mobile nav ───────────────────────────────────────────────────
  const burger    = document.getElementById('navBurger');
  const mobileNav = document.getElementById('mobileNav');
  const mClose    = document.getElementById('mobileClose');
  burger?.addEventListener('click',  () => mobileNav?.classList.add('open'));
  mClose?.addEventListener('click',  () => mobileNav?.classList.remove('open'));
  document.addEventListener('click', e => {
    if (!mobileNav?.contains(e.target) && !burger?.contains(e.target))
      mobileNav?.classList.remove('open');
  });

  // ── Reading progress ─────────────────────────────────────────────
  const rp = document.getElementById('rp');
  if (rp) {
    const update = () => {
      const h   = document.documentElement;
      const pct = h.scrollTop / (h.scrollHeight - h.clientHeight) * 100;
      rp.style.width = Math.min(100, pct || 0) + '%';
    };
    window.addEventListener('scroll', update, { passive: true });
  }

  // ── Back to top ──────────────────────────────────────────────────
  const btt = document.getElementById('btt');
  if (btt) {
    window.addEventListener('scroll', () => btt.classList.toggle('show', scrollY > 400), { passive: true });
    btt.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  // ── Flash / alert auto-dismiss ───────────────────────────────────
  document.querySelectorAll('.xflash[data-auto], .xalert[data-auto]').forEach(el => {
    setTimeout(() => { el.style.opacity = '0'; el.style.transition = 'opacity .3s'; setTimeout(() => el.remove(), 300); }, 4000);
  });
  document.querySelectorAll('.xflash-close, .xalert-close').forEach(btn => {
    btn.addEventListener('click', () => btn.closest('.xflash, .xalert')?.remove());
  });

  // ── Newsletter AJAX ──────────────────────────────────────────────
  document.querySelectorAll('.xnl-form-el').forEach(form => {
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      const orig = btn.innerHTML;
      btn.disabled = true; btn.innerHTML = '…';
      try {
        const r = await fetch(form.action, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': csrf() },
          body: new FormData(form),
        });
        const d = await r.json();
        toast(d.msg || 'Done!', d.ok ? 'ok' : 'err');
        if (d.ok) form.reset();
      } catch { toast('Network error.', 'err'); }
      finally { btn.disabled = false; btn.innerHTML = orig; }
    });
  });

  // ── Globals ──────────────────────────────────────────────────────
  window.csrf = () =>
    document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1] || '';

  window.toast = (msg, type = '') => {
    const stack = document.querySelector('.xtoast-stack') || (() => {
      const s = document.createElement('div');
      s.className = 'xtoast-stack';
      document.body.appendChild(s);
      return s;
    })();
    const t = document.createElement('div');
    t.className = 'xtoast ' + type;
    t.textContent = msg;
    stack.appendChild(t);
    setTimeout(() => t.remove(), 3500);
  };
})();
