/* XBlog — editor.js (live SEO) */
document.addEventListener('DOMContentLoaded', () => {
  const titleInput  = document.getElementById('xEditorTitle');
  const slugEl      = document.getElementById('xSlugPreview');
  const focusKwEl   = document.getElementById('id_focus_kw');
  const metaTitleEl = document.getElementById('id_meta_title');
  const metaDescEl  = document.getElementById('id_meta_desc');
  const seoPanel    = document.getElementById('xSeoResults');
  const serpTitle   = document.getElementById('xSerpTitle');
  const serpDesc    = document.getElementById('xSerpDesc');
  const serpSlug    = document.getElementById('xSerpSlug');
  const mtCount     = document.getElementById('xMtCount');
  const mdCount     = document.getElementById('xMdCount');

  function slugify(s) {
    return s.toLowerCase().replace(/[^\w\s-]/g,'').replace(/\s+/g,'-').replace(/-+/g,'-').trim();
  }

  // Live slug
  titleInput?.addEventListener('input', () => {
    const slug = slugify(titleInput.value);
    if (slugEl) slugEl.textContent = slug || 'post-slug';
    if (serpSlug) serpSlug.textContent = slug;
    if (serpTitle && !metaTitleEl?.value) serpTitle.textContent = titleInput.value || 'Post Title';
    triggerSeo();
  });

  // Meta counters + SERP
  function updateCounter(el, countEl, min, max) {
    if (!el || !countEl) return;
    const l = el.value.length;
    countEl.textContent = l + '/' + max;
    countEl.className = 'xserp-meta-counter ' +
      (l >= min && l <= max ? 'ok' : l > max ? 'bad' : 'warn');
  }
  metaTitleEl?.addEventListener('input', () => {
    updateCounter(metaTitleEl, mtCount, 50, 60);
    if (serpTitle) serpTitle.textContent = metaTitleEl.value || titleInput?.value || 'Post Title';
    triggerSeo();
  });
  metaDescEl?.addEventListener('input', () => {
    updateCounter(metaDescEl, mdCount, 120, 160);
    if (serpDesc) serpDesc.textContent = metaDescEl.value || 'Post description…';
    triggerSeo();
  });
  focusKwEl?.addEventListener('input', triggerSeo);

  // Init counters
  if (metaTitleEl) updateCounter(metaTitleEl, mtCount, 50, 60);
  if (metaDescEl)  updateCounter(metaDescEl,  mdCount, 120, 160);

  // Debounce SEO
  let seoTimer;
  function triggerSeo() {
    clearTimeout(seoTimer);
    seoTimer = setTimeout(runSeo, 1200);
  }

  // Summernote hook
  if (window.$ && typeof $.fn.summernote !== 'undefined') {
    $(document).ready(() => {
      $('#id_content').on('summernote.change', triggerSeo);
    });
  }

  document.getElementById('xRunSeo')?.addEventListener('click', runSeo);

  async function runSeo() {
    if (!seoPanel) return;
    seoPanel.innerHTML = '<div style="text-align:center;padding:20px;color:var(--text-4);font-size:.8rem">Analyzing…</div>';

    let content = '';
    const ta = document.getElementById('id_content');
    if (ta) {
      if (window.$ && $('#id_content').data('summernote')) content = $('#id_content').summernote('code');
      else content = ta.value;
    }

    const payload = {
      title:     titleInput?.value || '',
      slug:      slugEl?.textContent || '',
      focus_kw:  focusKwEl?.value || '',
      meta_title:metaTitleEl?.value || '',
      meta_desc: metaDescEl?.value || '',
      content,
      excerpt:   document.querySelector('[name="excerpt"]')?.value || '',
      cover_alt: document.querySelector('[name="cover_alt"]')?.value || '',
      schema:    document.querySelector('[name="schema"]')?.value || 'BlogPosting',
      og_image:  !!document.querySelector('[name="og_image"]')?.files?.length,
    };

    try {
      const r = await fetch('/seo/live/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() },
        body: JSON.stringify(payload),
      });
      const d = await r.json();
      renderSeo(d);
    } catch {
      seoPanel.innerHTML = '<div style="text-align:center;padding:20px;color:var(--red);font-size:.8rem">Analysis failed.</div>';
    }
  }

  function renderSeo(d) {
    const icon = s => s === 'good' ? 'fa-check-circle' : s === 'ok' ? 'fa-exclamation-circle' : 'fa-times-circle';
    const checks = arr => arr.map(c => `
      <div class="xseo-check ${c.status}">
        <i class="fas ${icon(c.status)}"></i>
        <span class="xseo-check-msg">${c.msg}</span>
      </div>`).join('');

    const circ = 2 * Math.PI * 14; // r=14 of 18px circle
    const dash = (d.score / 100) * circ;

    seoPanel.innerHTML = `
      <div class="xseo-score-row">
        <div class="xscore-ring">
          <svg class="xscore-svg" viewBox="0 0 36 36">
            <circle class="xscore-bg" cx="18" cy="18" r="14"/>
            <circle class="xscore-arc ${d.seo_rating}" cx="18" cy="18" r="14"
              stroke-dasharray="${dash.toFixed(1)},${circ.toFixed(1)}"
              stroke-dashoffset="0"/>
          </svg>
          <div class="xscore-num">${d.score}</div>
        </div>
        <div class="xseo-badges">
          <span class="xseo-badge ${d.seo_rating}">SEO: ${d.seo_label}</span>
          <span class="xseo-badge ${d.read_rating}">Read: ${d.read_label}</span>
          <div class="xseo-wc">${d.wc} words · ${d.rt} min</div>
        </div>
      </div>
      <div class="xseo-section">SEO Checks</div>
      ${checks(d.seo_checks)}
      <div class="xseo-section">Readability</div>
      ${checks(d.read_checks)}`;
  }

  // Run on load if editing
  if (focusKwEl?.value) setTimeout(runSeo, 600);
});
