# XBlog — Django 6 Blog Platform

X (Twitter)-inspired editorial blog with a real-time SEO analyzer, expert dashboard, and pure black design system.

## Stack
- **Django 6** + PostgreSQL
- **Instrument Serif** (headlines) + **Geist** (UI) fonts
- **X-style** design: pure black `#000`, 1px borders, zero box-shadows on cards
- **Yoast-style SEO Analyzer** — 20 live checks, real-time SERP preview
- Class-based views throughout

## Quick Start

```bash
# 1. Install
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env   # fill in your DB credentials

# 3. Database
psql -U postgres -c "CREATE DATABASE xblog;"
python manage.py makemigrations
python manage.py migrate

# 4. Superuser
python manage.py createsuperuser

# 5. Run
python manage.py runserver
```

Open http://localhost:8000

## Key URLs
| URL | Description |
|-----|-------------|
| `/` | Blog homepage |
| `/dashboard/` | Expert dashboard |
| `/admin/` | Django admin |
| `/accounts/login/` | Sign in |
| `/sitemap.xml` | XML sitemap |
| `/robots.txt` | Robots file |

## Dashboard Features
- **Overview** — Stats, Chart.js views chart, doughnut chart, top posts, pending comments
- **Post Editor** — Summernote editor, live SEO panel (20 checks), SERP preview, meta counters
- **Posts** — Filterable list, inline status toggle, bulk select
- **Categories** — CRUD with color pickers
- **Comments** — One-click approve/spam/delete
- **Analytics** — 30-day views bar chart, top posts, referrers, category performance
- **Newsletter** — Subscriber list with export-ready table
- **Users** — Toggle author permissions
- **Settings** — Site name, social links, feature toggles

## SEO Checks (20)
Focus keyword · title · meta desc · slug · intro · density · headings · alt text · meta title length · meta desc length · content length · heading structure · links · OG image · schema · sentence length · passive voice · transition words · paragraph length · subheading distribution

## Site
for visiting site : https://alisamadzadeh46.github.io/xblog/
