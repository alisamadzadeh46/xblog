/* XBlog — dashboard.js */
document.addEventListener('DOMContentLoaded', () => {

  // Theme (same logic)
  const html = document.documentElement;
  const btn  = document.getElementById('themeBtn');
  const icon = document.getElementById('themeIcon');
  html.setAttribute('data-theme', localStorage.getItem('xtheme') || 'dark');
  updateIcon(html.getAttribute('data-theme'));
  btn?.addEventListener('click', () => {
    const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('xtheme', next);
    updateIcon(next);
  });
  function updateIcon(t) {
    if (!icon) return;
    icon.className = t === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
  }

  // Sidebar toggle
  const sidebar = document.getElementById('xDashSidebar');
  document.getElementById('xDashToggle')?.addEventListener('click', () => sidebar?.classList.add('open'));
  document.getElementById('xDashClose')?.addEventListener('click',  () => sidebar?.classList.remove('open'));
  document.addEventListener('click', e => {
    if (sidebar?.classList.contains('open') && !sidebar.contains(e.target) &&
        !document.getElementById('xDashToggle')?.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  });

  // Alert close
  document.querySelectorAll('.xalert-close').forEach(b => b.addEventListener('click', () => b.closest('.xalert')?.remove()));
  document.querySelectorAll('.xalert[data-auto]').forEach(el => setTimeout(() => el.remove(), 4500));

  // Status select (quick toggle)
  document.querySelectorAll('.xstatus-select').forEach(sel => {
    sel.addEventListener('change', async function() {
      const url = this.dataset.url;
      const status = this.value;
      try {
        const r = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() },
          body: JSON.stringify({ status }),
        });
        const d = await r.json();
        dashToast('Status → ' + d.status, 'ok');
      } catch { dashToast('Failed.', 'err'); this.value = this.dataset.orig; }
    });
    sel.dataset.orig = sel.value;
  });

  // Pending comment approve/spam
  document.querySelectorAll('[data-comment-action]').forEach(btn => {
    btn.addEventListener('click', async function() {
      const id     = this.dataset.id;
      const action = this.dataset.commentAction;
      const r = await fetch(`/dashboard/comments/${id}/action/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() },
        body: JSON.stringify({ action }),
      });
      if (r.ok) {
        const row = this.closest('.xpc-item, tr');
        if (row) { row.style.opacity = '0'; row.style.transition = 'opacity .2s'; setTimeout(() => row.remove(), 200); }
        dashToast(action === 'approved' ? 'Approved!' : 'Marked as spam.', 'ok');
      }
    });
  });

  // Editor tabs
  document.querySelectorAll('.xeditor-tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const group = this.closest('[data-tabs]') || this.closest('.xeditor-main');
      group?.querySelectorAll('.xeditor-tab-btn').forEach(b => b.classList.remove('active'));
      group?.querySelectorAll('.xeditor-tab-pane').forEach(p => p.classList.remove('active'));
      this.classList.add('active');
      group?.querySelector('[data-tab="' + this.dataset.target + '"]')?.classList.add('active');
    });
  });

  function dashToast(msg, type = '') {
    let stack = document.querySelector('.xtoast-stack');
    if (!stack) {
      stack = document.createElement('div');
      stack.className = 'xtoast-stack';
      document.body.appendChild(stack);
    }
    const t = document.createElement('div');
    t.className = 'xtoast ' + type;
    t.textContent = msg;
    stack.appendChild(t);
    setTimeout(() => t.remove(), 3000);
  }
  window.csrf = () => document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1] || '';
});
