"""Yoast-style SEO Analyzer — 24 checks"""
import re
from django.conf import settings

GOOD, OK, POOR = 'good', 'ok', 'poor'

def _strip(html):
    return re.sub(r'<[^>]+>', ' ', html or '')

class SEOAnalyzer:
    def __init__(self, data: dict):
        """data keys: title, slug, focus_kw, meta_title, meta_desc, content,
                      excerpt, cover_alt, schema, og_image (bool)"""
        self.title    = data.get('title','')
        self.slug     = data.get('slug','')
        self.kw       = data.get('focus_kw','').lower().strip()
        self.mt       = data.get('meta_title','') or self.title
        self.md       = data.get('meta_desc','')  or data.get('excerpt','')
        self.raw      = data.get('content','')
        self.content  = _strip(self.raw)
        self.cover_alt= data.get('cover_alt','').lower()
        self.schema   = data.get('schema','')
        self.has_og   = bool(data.get('og_image'))
        self.words    = self.content.split()
        self.wc       = len(self.words)
        self.checks   = []
        self._score   = 0

    def _add(self, name, status, msg, pts, cat='seo'):
        self.checks.append({'name':name,'status':status,'msg':msg,'pts':pts,'cat':cat})
        if status == GOOD: self._score += pts

    def _kw_in(self, text):
        return self.kw in text.lower() if self.kw else False

    # ── SEO ──────────────────────────────────────────
    def c_focus_kw(self):
        if self.kw: self._add('Focus keyword', GOOD, f'Keyword set: "{self.kw}"', 5)
        else:       self._add('Focus keyword', POOR, 'No focus keyword. Set one to optimize.', 0)

    def c_kw_title(self):
        if not self.kw: return
        if self._kw_in(self.title): self._add('Keyword in title', GOOD, 'Focus keyword in post title.', 10)
        else: self._add('Keyword in title', POOR, 'Focus keyword not in title.', 0)

    def c_kw_meta_desc(self):
        if not self.kw: return
        if self._kw_in(self.md): self._add('Keyword in meta desc', GOOD, 'Focus keyword in meta description.', 8)
        else: self._add('Keyword in meta desc', POOR, 'Add focus keyword to meta description.', 0)

    def c_kw_slug(self):
        if not self.kw: return
        kw_slug = re.sub(r'\s+','-',self.kw)
        if kw_slug in self.slug: self._add('Keyword in URL', GOOD, 'Focus keyword in URL slug.', 7)
        else: self._add('Keyword in URL', OK, 'Consider adding keyword to URL.', 3)

    def c_kw_intro(self):
        if not self.kw: return
        intro = ' '.join(self.words[:100]).lower()
        if self.kw in intro: self._add('Keyword in intro', GOOD, 'Focus keyword in first paragraph.', 9)
        else: self._add('Keyword in intro', POOR, 'Add keyword within first 100 words.', 0)

    def c_kw_density(self):
        if not self.kw or not self.wc: return
        count = self.content.lower().count(self.kw)
        d = (count / self.wc) * 100
        mn, mx = settings.SEO_KW_DENSITY_MIN, settings.SEO_KW_DENSITY_MAX
        if mn <= d <= mx: self._add('Keyword density', GOOD, f'{d:.1f}% density (target {mn}–{mx}%).', 8)
        elif d < mn:      self._add('Keyword density', OK,   f'{d:.1f}% — too low. Aim {mn}–{mx}%.', 4)
        else:             self._add('Keyword density', POOR, f'{d:.1f}% — too high! Max {mx}%.', 0)

    def c_kw_headings(self):
        if not self.kw: return
        hs = re.findall(r'<h[2-4][^>]*>(.*?)</h[2-4]>', self.raw, re.I|re.S)
        if any(self.kw in _strip(h).lower() for h in hs):
            self._add('Keyword in headings', GOOD, 'Focus keyword in a subheading.', 7)
        else:
            self._add('Keyword in headings', OK, 'Add keyword to at least one H2/H3.', 3)

    def c_kw_alt(self):
        if not self.kw: return
        alts = re.findall(r'alt=["\']([^"\']*)["\']', self.raw, re.I)
        alts.append(self.cover_alt)
        if any(self.kw in a.lower() for a in alts):
            self._add('Keyword in image alt', GOOD, 'Focus keyword found in image alt.', 5)
        else:
            self._add('Keyword in image alt', OK, 'Add keyword to an image alt attribute.', 2)

    def c_meta_title_len(self):
        l = len(self.mt)
        mn, mx = settings.SEO_TITLE_MIN, settings.SEO_TITLE_MAX
        if mn <= l <= mx: self._add('Meta title length', GOOD, f'{l} chars (ideal {mn}–{mx}).', 8)
        elif l < mn:      self._add('Meta title length', OK,   f'{l} chars — too short. Aim {mn}–{mx}.', 4)
        else:             self._add('Meta title length', POOR, f'{l} chars — too long! Keep ≤{mx}.', 0)

    def c_meta_desc_len(self):
        l = len(self.md)
        mn, mx = settings.SEO_DESC_MIN, settings.SEO_DESC_MAX
        if mn <= l <= mx: self._add('Meta description length', GOOD, f'{l} chars (ideal {mn}–{mx}).', 8)
        elif l < mn:      self._add('Meta description length', OK,   f'{l} chars — too short.', 4)
        else:             self._add('Meta description length', POOR, f'{l} chars — too long!', 0)

    def c_content_len(self):
        mn = settings.SEO_WORDS_MIN
        if self.wc >= mn:          self._add('Content length', GOOD, f'{self.wc} words — good length!', 10)
        elif self.wc >= mn // 2:   self._add('Content length', OK,   f'{self.wc} words — aim for {mn}+.', 5)
        else:                      self._add('Content length', POOR, f'Only {self.wc} words. Min {mn}.', 0)

    def c_headings(self):
        h2 = len(re.findall(r'<h2', self.raw, re.I))
        h3 = len(re.findall(r'<h3', self.raw, re.I))
        if h2 >= 2: self._add('Headings structure', GOOD, f'{h2} H2 + {h3} H3 headings. Well structured!', 7)
        elif h2==1: self._add('Headings structure', OK,   'Add more H2 subheadings.', 3)
        else:       self._add('Headings structure', POOR, 'No H2 headings found. Add subheadings.', 0)

    def c_links(self):
        internal = len(re.findall(r'href=["\'][^"\']*["\']', self.raw))
        external = len(re.findall(r'href=["\']https?://', self.raw))
        if internal >= 2 and external >= 1:
            self._add('Internal links', GOOD, f'{internal} links ({external} external). Good!', 7)
        elif internal >= 1:
            self._add('Internal links', OK, 'Add more internal + 1 external link.', 3)
        else:
            self._add('Internal links', POOR, 'No links found. Add internal & external links.', 0)

    def c_og_image(self):
        if self.has_og: self._add('OG / Social image', GOOD, 'OG image set — great for sharing!', 5)
        else:           self._add('OG / Social image', OK,   'Set an OG image for social previews.', 2)

    def c_schema(self):
        if self.schema: self._add('Schema markup', GOOD, f'Schema type "{self.schema}" configured.', 5)
        else:           self._add('Schema markup', OK,   'Select a schema type.', 2)

    # ── Readability ───────────────────────────────────
    def c_sentence_len(self):
        sentences = [s.strip() for s in re.split(r'[.!?]+', self.content) if len(s.split())>2]
        if not sentences: return
        long_pct = sum(1 for s in sentences if len(s.split())>20) / len(sentences) * 100
        if long_pct < 25:  self._add('Sentence length', GOOD, f'{long_pct:.0f}% long sentences. Good!', 8, 'readability')
        elif long_pct < 50:self._add('Sentence length', OK,   f'{long_pct:.0f}% sentences >20 words. Shorten some.', 4, 'readability')
        else:              self._add('Sentence length', POOR, f'{long_pct:.0f}% too long. Use shorter sentences.', 0, 'readability')

    def c_passive(self):
        p = len(re.findall(r'\b(is|are|was|were|be|been|being)\s+\w+ed\b', self.content, re.I))
        s = max(len(re.split(r'[.!?]+', self.content)), 1)
        pct = p / s * 100
        if pct < 10:  self._add('Passive voice', GOOD, f'{pct:.0f}% passive sentences. Active voice dominates!', 6, 'readability')
        elif pct < 20:self._add('Passive voice', OK,   f'{pct:.0f}% passive. Aim for <10%.', 3, 'readability')
        else:         self._add('Passive voice', POOR, f'{pct:.0f}% passive voice — too high.', 0, 'readability')

    def c_transitions(self):
        tw = ['however','therefore','furthermore','moreover','consequently','additionally',
              'nevertheless','meanwhile','first','second','finally','in conclusion',
              'for example','in addition','as a result','on the other hand','in fact']
        found = sum(1 for t in tw if t in self.content.lower())
        s = max(len(re.split(r'[.!?]+', self.content)), 1)
        pct = found / s * 100
        if pct >= 30:  self._add('Transition words', GOOD, f'{found} transition words. Great flow!', 6, 'readability')
        elif pct >= 15:self._add('Transition words', OK,   f'{found} transitions. Add more for flow.', 3, 'readability')
        else:          self._add('Transition words', POOR, 'Few transitions. Add: however, therefore, etc.', 0, 'readability')

    def c_paragraph_len(self):
        parts = re.split(r'\n{2,}|<p>|</p>', self.content)
        paras = [p.strip() for p in parts if len(p.split())>5]
        if not paras: return
        long = sum(1 for p in paras if len(p.split())>150)
        if long == 0:   self._add('Paragraph length', GOOD, 'All paragraphs well sized!', 6, 'readability')
        elif long <= 2: self._add('Paragraph length', OK,   f'{long} long paragraph(s). Break them up.', 3, 'readability')
        else:           self._add('Paragraph length', POOR, f'{long} paragraphs too long (>150 words each).', 0, 'readability')

    def c_subheading_dist(self):
        sections = re.split(r'<h[2-4][^>]*>', self.raw, flags=re.I)
        if len(sections) <= 1: return
        long = sum(1 for s in sections if len(_strip(s).split()) > 300)
        if long == 0: self._add('Subheading distribution', GOOD, 'Content well split between headings.', 6, 'readability')
        else:         self._add('Subheading distribution', OK,   f'{long} section(s) >300 words. Add a subheading.', 3, 'readability')

    # ── Run ──────────────────────────────────────────
    def run(self):
        for m in [self.c_focus_kw,self.c_kw_title,self.c_kw_meta_desc,self.c_kw_slug,
                  self.c_kw_intro,self.c_kw_density,self.c_kw_headings,self.c_kw_alt,
                  self.c_meta_title_len,self.c_meta_desc_len,self.c_content_len,
                  self.c_headings,self.c_links,self.c_og_image,self.c_schema,
                  self.c_sentence_len,self.c_passive,self.c_transitions,
                  self.c_paragraph_len,self.c_subheading_dist]:
            m()

        max_pts = sum([5,10,8,7,9,8,7,5,8,8,10,7,7,5,5,8,6,6,6,6])
        score   = min(100, int(self._score / max_pts * 100)) if max_pts else 0

        seo_ch  = [c for c in self.checks if c['cat']=='seo']
        read_ch = [c for c in self.checks if c['cat']=='readability']

        def rating(checks):
            poor = sum(1 for c in checks if c['status']==POOR)
            if poor > 3: return POOR, 'Needs improvement'
            if poor > 1: return OK,   'OK'
            return GOOD, 'Good'

        sr, sl = rating(seo_ch)
        rr, rl = rating(read_ch)
        if score < 40: sr, sl = POOR, 'Needs improvement'
        elif score < 70: sr, sl = OK, 'OK'

        return {
            'score': score,
            'seo_rating': sr, 'seo_label': sl,
            'read_rating': rr,'read_label': rl,
            'seo_checks':  seo_ch,
            'read_checks': read_ch,
            'wc': self.wc,
            'rt': max(1, self.wc // 200),
            'kw': self.kw,
        }
