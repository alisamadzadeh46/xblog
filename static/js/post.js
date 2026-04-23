/* XBlog — post.js */
document.addEventListener('DOMContentLoaded', () => {

  // ToC
  const prose = document.getElementById('xprose');
  const toc   = document.getElementById('xToc');
  if (prose && toc) {
    const heads = prose.querySelectorAll('h2,h3');
    if (heads.length >= 2) {
      heads.forEach((h, i) => {
        if (!h.id) h.id = 'h-' + i;
        const a = document.createElement('a');
        a.href = '#' + h.id;
        a.textContent = h.textContent;
        a.className = 'xtoc-link' + (h.tagName === 'H3' ? ' xtoc-h3' : '');
        toc.appendChild(a);
      });
      const io = new IntersectionObserver(entries => {
        entries.forEach(e => {
          toc.querySelector(`[href="#${e.target.id}"]`)?.classList.toggle('active', e.isIntersecting);
        });
      }, { rootMargin: '-80px 0px -65% 0px' });
      heads.forEach(h => io.observe(h));
    }
  }

  // Like
  const likeBtn = document.getElementById('xLikeBtn');
  const likeCnt = document.getElementById('xLikeCount');
  likeBtn?.addEventListener('click', async () => {
    const r = await fetch(likeBtn.dataset.url, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf(), 'X-Requested-With': 'XMLHttpRequest' }
    });
    const d = await r.json();
    likeCnt.textContent = d.count;
    likeBtn.classList.toggle('liked', d.liked);
    const ico = likeBtn.querySelector('i');
    ico.className = d.liked ? 'fas fa-heart' : 'far fa-heart';
    likeBtn.style.transform = 'scale(1.25)';
    setTimeout(() => likeBtn.style.transform = '', 180);
  });

  // Copy link
  document.getElementById('xCopyLink')?.addEventListener('click', function() {
    navigator.clipboard.writeText(location.href).then(() => {
      const i = this.querySelector('i');
      i.className = 'fas fa-check';
      this.style.borderColor = 'var(--green)';
      setTimeout(() => { i.className = 'fas fa-link'; this.style.borderColor = ''; }, 1800);
    });
  });

  // Reply
  const parentInput = document.getElementById('xParentId');
  const replyBanner = document.getElementById('xReplyBanner');
  const replyName   = document.getElementById('xReplyName');
  const cancelReply = document.getElementById('xCancelReply');

  document.querySelectorAll('.xci-reply-btn').forEach(b => {
    b.addEventListener('click', () => {
      if (parentInput) parentInput.value = b.dataset.id;
      if (replyName)   replyName.textContent = b.dataset.author;
      if (replyBanner) replyBanner.classList.remove('d-none');
      document.querySelector('.xcomment-form-box')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      document.querySelector('#xCommentForm textarea')?.focus();
    });
  });
  cancelReply?.addEventListener('click', () => {
    if (parentInput) parentInput.value = '';
    replyBanner?.classList.add('d-none');
  });

  // Comment submit
  const cf = document.getElementById('xCommentForm');
  cf?.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = cf.querySelector('button[type="submit"]');
    const orig = btn.innerHTML;
    btn.disabled = true; btn.innerHTML = '…';
    const r = await fetch(cf.action, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf(), 'X-Requested-With': 'XMLHttpRequest' },
      body: new FormData(cf),
    });
    const d = await r.json();
    if (d.ok) {
      cf.reset();
      if (parentInput) parentInput.value = '';
      replyBanner?.classList.add('d-none');
      if (d.approved) appendComment(d.comment);
      toast(d.msg, 'ok');
    } else {
      toast(d.msg || 'Error.', 'err');
    }
    btn.disabled = false; btn.innerHTML = orig;
  });

  function appendComment(c) {
    const list = document.getElementById('xCommentList');
    if (!list) return;
    list.querySelector('.xempty')?.remove();
    const html = `
      <div class="xcomment-item${c.parent_id ? ' reply':''}" id="xc-${c.id}">
        <img src="${c.avatar}" class="xci-avatar" alt="${c.author}">
        <div class="xci-body">
          <div class="xci-header">
            <span class="xci-name">${c.author}</span>
            <span class="xci-date">Just now</span>
          </div>
          <div class="xci-text">${c.content}</div>
        </div>
      </div>`;
    if (c.parent_id) {
      const parent = document.getElementById('xc-' + c.parent_id);
      let replies = parent?.querySelector('.xci-replies');
      if (!replies && parent) {
        replies = document.createElement('div');
        replies.className = 'xci-replies';
        parent.querySelector('.xci-body').appendChild(replies);
      }
      replies?.insertAdjacentHTML('beforeend', html);
    } else {
      list.insertAdjacentHTML('afterbegin', html);
    }
  }
});
