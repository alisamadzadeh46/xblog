"""
Management command: python manage.py seed
- Fixes any missing DB columns via safe ALTER TABLE
- Creates superuser, staff, and author accounts
- Seeds categories, posts (with real HTML content), comments, newsletter subscribers
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection
from django.utils import timezone
from django.utils.text import slugify
import random


User = get_user_model()

# ── Helpers ───────────────────────────────────────────────────────────────────

def safe_add_column(cursor, table, column, col_type, default="''"):
    """Add column only if it doesn't exist — works on PostgreSQL."""
    cursor.execute(f"""
        SELECT column_name FROM information_schema.columns
        WHERE table_name='{table}' AND column_name='{column}'
    """)
    if not cursor.fetchone():
        cursor.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {col_type} NOT NULL DEFAULT {default}"
        )
        return True
    return False


# ── Fake content ──────────────────────────────────────────────────────────────

CATEGORIES = [
    {'name': 'Technology',  'color': '#6366f1', 'icon': 'fas fa-microchip',    'description': 'Software, hardware, and the digital frontier.'},
    {'name': 'Design',      'color': '#ec4899', 'icon': 'fas fa-palette',      'description': 'UI/UX, typography, and visual craft.'},
    {'name': 'Business',    'color': '#f59e0b', 'icon': 'fas fa-briefcase',    'description': 'Strategy, startups, and the economy.'},
    {'name': 'Science',     'color': '#10b981', 'icon': 'fas fa-flask',        'description': 'Research, discovery, and the natural world.'},
    {'name': 'Culture',     'color': '#8b5cf6', 'icon': 'fas fa-book-open',    'description': 'Arts, literature, film, and society.'},
    {'name': 'Health',      'color': '#ef4444', 'icon': 'fas fa-heartbeat',    'description': 'Wellness, fitness, and modern medicine.'},
]

POST_DATA = [
    {
        'title': 'The Future of AI: What to Expect in 2026 and Beyond',
        'category': 'Technology',
        'tags': ['AI', 'machine learning', 'future'],
        'featured': True, 'pinned': True,
        'excerpt': 'Artificial intelligence is no longer science fiction. From large language models to autonomous agents, we examine what the next wave of AI will look like and how it will reshape industries.',
        'content': '''<p>Artificial intelligence has crossed a threshold. What once lived in research papers and university labs now powers everything from email clients to medical diagnostics. But we are still in the early innings of a transformation that will take decades to fully unfold.</p>

<h2>Large Language Models Grow Up</h2>
<p>The story of AI in 2025 was largely the story of language models finding their footing in production environments. Hallucination rates dropped. Tool use became reliable. Enterprises stopped treating AI assistants as party tricks and started integrating them into core workflows.</p>
<p>In 2026, the conversation has shifted from <em>what can these models do</em> to <em>how do we build reliable systems on top of them</em>. That is a healthy maturation.</p>

<h2>Autonomous Agents: From Demo to Reality</h2>
<p>Agent frameworks like LangGraph and AutoGen crossed the chasm from experimental to production-ready. Teams are deploying agents that can:</p>
<ul>
<li>Browse the web and synthesize research reports autonomously</li>
<li>Write, test, and deploy code with minimal human oversight</li>
<li>Manage calendars, emails, and meeting scheduling end-to-end</li>
<li>Monitor dashboards and send alerts with natural-language summaries</li>
</ul>
<p>The bottleneck is no longer the model — it is the human workflow design around it.</p>

<h2>The Hardware Race</h2>
<p>NVIDIA's dominance is being challenged from multiple directions. AMD's MI300X has found real traction in cloud providers. Google's TPU v5 powers the majority of its internal training workloads. Apple's Neural Engine chips are making on-device inference genuinely competitive with cloud calls for many tasks.</p>
<blockquote>The most important hardware trend is not raw performance — it is power efficiency. Running a 70B parameter model on a laptop battery was impossible in 2023. It is table stakes in 2026.</blockquote>

<h2>What Comes Next</h2>
<p>The models getting the most research attention right now are multimodal reasoning systems — models that can look at a spreadsheet, a codebase, and a Slack thread simultaneously and reason across all three. That capability, at production reliability, will be the next step-change.</p>
<p>We are also watching the emergence of <strong>world models</strong> — AI systems that build internal representations of how the physical world behaves, not just statistical patterns in text. This is the prerequisite for the next generation of robotics.</p>

<h2>The Regulatory Landscape</h2>
<p>The EU AI Act is now in force. The US has a patchwork of executive orders and voluntary commitments. China has its own regulatory framework. For global companies, compliance has become a full-time function.</p>
<p>The companies that thrive will be those that treat safety and interpretability not as compliance burdens but as engineering challenges worth solving.</p>

<h2>Conclusion</h2>
<p>The future of AI is not a single breakthrough moment. It is a thousand boring-sounding improvements in reliability, latency, cost, and interpretability — each one making the technology a bit more useful, a bit more trustworthy, and a bit more deeply woven into the fabric of how we work and live.</p>''',
    },
    {
        'title': 'Why Typography is the Most Underrated Skill in Design',
        'category': 'Design',
        'tags': ['typography', 'UX', 'fonts'],
        'featured': True,
        'excerpt': 'Most designers spend hours on color and layout but minutes on type. This is a mistake. Typography is the invisible architecture of communication — and getting it wrong breaks everything.',
        'content': '''<p>Open any design portfolio and you will see the same conversation happening. Colors are carefully chosen. Grids are precisely calculated. Animations are lovingly crafted. And then the type is set in Inter at 16px and everyone moves on.</p>
<p>This is the design industry's dirty secret: most practitioners treat typography as a default setting, not a craft. And it shows.</p>

<h2>Type Sets the Tone Before Words Do</h2>
<p>A user reads the <em>feeling</em> of your type before they read the words. A serif set at generous line-height communicates authority and calm. A compressed sans-serif in uppercase reads as urgent and modern. A humanist type with irregular weight contrast feels personal and approachable.</p>
<p>These are not subtle differences. They are the difference between a product that users trust and one they feel vaguely uncomfortable using without being able to say why.</p>

<h2>The Variable Font Revolution</h2>
<p>Variable fonts changed the economics of typography on the web. Instead of loading four separate files for Regular, Bold, Italic, and Bold Italic, a single variable font file can express the entire design space of a typeface — weight, width, optical size, slant, and more — via CSS axes.</p>
<pre><code>font-variation-settings: 'wght' 650, 'opsz' 32;
</code></pre>
<p>Fraunces, the typeface used in this publication, is a variable font. Its optical size axis means the letterforms at 12px are different from the letterforms at 72px — optimized for legibility at small sizes, expressiveness at large ones.</p>

<h2>Scale Systems That Actually Work</h2>
<p>The modular scale is the most reliable tool for creating typographic harmony. Pick a ratio — 1.25, 1.333, 1.5, or the golden ratio 1.618 — and derive your size steps mathematically.</p>
<blockquote>Do not pick font sizes based on what looks good in isolation. Pick them based on their relationship to each other.</blockquote>
<p>A scale built on 1.333 (perfect fourth) starting from 16px gives you: 12, 16, 21, 28, 37, 49. These numbers have an inherent musical quality when used together.</p>

<h2>Line Length, Leading, and the Reading Rhythm</h2>
<p>The research on optimal line length is remarkably consistent: 60–75 characters per line is the sweet spot for sustained reading. Shorter and the eye makes too many jumps. Longer and it loses its place returning to the start of the next line.</p>
<p>Leading (line height) should scale with line length. For a narrow column, 1.4 feels right. For a wide measure, you need 1.7 or more. This is why a single line-height value for all text is always a compromise.</p>

<h2>The Practical Checklist</h2>
<ul>
<li>Set your base size at 16–18px. Not 14. Not 12.</li>
<li>Use a modular scale. Do not pick sizes arbitrarily.</li>
<li>Limit yourself to two typefaces maximum, three if you have a very good reason.</li>
<li>Check your type on mobile first. Desktop is where type looks easy.</li>
<li>Use optical sizing where available.</li>
<li>Measure your line length. Count the characters.</li>
</ul>
<p>Typography is the one design skill that compounds over time. Every hour you spend studying it pays dividends for the rest of your career.</p>''',
    },
    {
        'title': 'Building a Profitable SaaS in 2026: Lessons from the Trenches',
        'category': 'Business',
        'tags': ['SaaS', 'startup', 'entrepreneurship'],
        'featured': False,
        'excerpt': 'After three failed attempts and one successful exit, here is what I wish I had known about building software businesses that actually make money.',
        'content': '''<p>The SaaS landscape of 2026 looks nothing like the easy-money era of 2020–2022. Interest rates normalized. Venture capital tightened. The "grow at all costs" playbook stopped working. And for the first time in a decade, bootstrapped, profitable businesses became genuinely cool again.</p>

<h2>The Metrics That Actually Matter</h2>
<p>I spent two years obsessing over MRR and DAU before I understood the real numbers: <strong>Net Revenue Retention</strong> and <strong>Time to Value</strong>.</p>
<p>NRR above 100% means your existing customers are spending more over time than you are losing to churn. That is the engine of compounding growth. Everything else is noise until you have this working.</p>
<p>Time to Value is how long it takes a new user to get their first meaningful result from your product. If it is longer than 10 minutes, you have a problem. If it is longer than 30, you probably do not have a business.</p>

<h2>Distribution is the Moat Now</h2>
<p>In 2026, building the product is the easy part. Every developer has access to the same APIs, the same cloud infrastructure, the same AI capabilities. The companies winning are the ones that figured out distribution.</p>
<blockquote>Your product is not the software. Your product is the distribution system that gets the software in front of people who will pay for it.</blockquote>
<p>The channels that are working right now: SEO-first content strategies, community building around the problem space (not the product), and integration partnerships with complementary tools that already have your audience.</p>

<h2>Pricing: Stop Leaving Money on the Table</h2>
<p>Most early-stage SaaS founders underprice by a factor of 2–5x. They price based on what they think the software "should" cost, not what the value delivered is worth.</p>
<p>A rule of thumb: your annual price should be no more than 10% of the annual value your product delivers. If your project management tool saves a team 5 hours per week at $100/hour, that is $26,000 per year in value. $2,600/year is a reasonable price.</p>

<h2>The AI Advantage</h2>
<p>AI has not made it easier to build SaaS. It has made it easier to build <em>features</em>. The companies using AI most effectively are the ones embedding it invisibly into the core value proposition — not bolting on a chatbot.</p>
<p>The products I am most jealous of right now are the ones where you genuinely cannot tell where human-written software ends and AI-generated behavior begins. That seamlessness is the goal.</p>''',
    },
    {
        'title': 'CRISPR Beyond Headlines: What Gene Editing Can Actually Do Today',
        'category': 'Science',
        'tags': ['CRISPR', 'genetics', 'medicine'],
        'featured': False,
        'excerpt': 'The gene editing revolution has been "five years away" for a decade. But 2025 saw the first approved CRISPR therapies reach patients. Here is what is real, what is hype, and what comes next.',
        'content': '''<p>CRISPR-Cas9 was discovered in 2012. It promised to let scientists edit DNA with the precision of a word processor. For years, the promise outpaced the reality. Then, in late 2023, the FDA approved the first two CRISPR-based therapies. And the field has not looked back.</p>

<h2>What Is Actually Approved</h2>
<p>Casgevy, developed by Vertex and CRISPR Therapeutics, treats sickle cell disease and transfusion-dependent beta-thalassemia. It works by editing patients' own stem cells to reactivate fetal hemoglobin production — a switch that is normally turned off after birth.</p>
<p>The results are remarkable. In clinical trials, 97% of patients with sickle cell disease had no severe pain crises for at least 12 months after treatment. For a disease that causes excruciating episodes and has limited treatment options, this is genuinely transformative.</p>

<h2>The Delivery Problem</h2>
<p>The central technical challenge in gene editing is not the editing itself — the CRISPR machinery works reliably. It is getting the editing machinery to the right cells in a living patient.</p>
<p>The current approved therapies work by removing cells from the patient, editing them outside the body, and reinfusing them. This is expensive, complex, and only works for blood-related diseases where you can access the relevant cells easily.</p>
<blockquote>In vivo delivery — editing genes directly inside the body — is the holy grail. It would make gene therapy accessible for diseases of the liver, lung, muscle, and brain. The lipid nanoparticle technology developed for mRNA vaccines is now being adapted for this purpose.</blockquote>

<h2>Beyond Single-Gene Diseases</h2>
<p>The early CRISPR successes target diseases caused by mutations in a single gene. Sickle cell disease. Beta-thalassemia. Certain forms of blindness. These are relatively straightforward targets because you can correct one mutation and fix the disease.</p>
<p>The harder problems — cardiovascular disease, Alzheimer's, most cancers — involve dozens or hundreds of genes interacting with environmental factors. These will require more sophisticated approaches: base editing, prime editing, and epigenome editing tools that are now moving through clinical trials.</p>

<h2>The Cost Barrier</h2>
<p>Casgevy costs approximately $2.2 million per treatment. This is not gouging — it reflects the genuine complexity of the manufacturing process. But it raises profound questions about access.</p>
<p>The most important unsolved problem in gene therapy is not scientific. It is economic. How do we build pricing and payment models for one-time curative treatments that are affordable to healthcare systems?</p>''',
    },
    {
        'title': 'The Quiet Renaissance of Long-Form Writing',
        'category': 'Culture',
        'tags': ['writing', 'media', 'newsletters'],
        'featured': False,
        'excerpt': 'In an era of algorithmically optimized content, readers are seeking out longer, slower, more considered writing. The newsletter boom is just the beginning of a deeper shift.',
        'content': '''<p>Something strange happened to media in the last few years. Attention spans were supposed to collapse. TikTok was supposed to make everything short. The conventional wisdom held that the future belonged to the 30-second clip, the viral tweet, the hot take.</p>
<p>And yet. Substack has millions of paid subscribers. Longreads and narrative nonfiction are thriving. Podcasts routinely run three hours. People are reading — and paying — for depth.</p>

<h2>The Attention Economy Correction</h2>
<p>The short-form content explosion was real. It is also self-limiting. When everything competes for attention with algorithmically optimized dopamine loops, readers eventually develop a tolerance. The scroll becomes joyless. The feed becomes noise.</p>
<p>Long-form writing offers something qualitatively different: the feeling of going somewhere with your reading time. Of arriving somewhere you could not have predicted. Of understanding something you did not understand before.</p>

<h2>What Makes Long-Form Work</h2>
<p>The essays and articles that find large audiences share specific qualities that have nothing to do with length and everything to do with intention:</p>
<ul>
<li><strong>A specific, defensible argument.</strong> Not "social media is complicated" but "social media optimizes for outrage because outrage is the emotion most likely to trigger sharing."</li>
<li><strong>Evidence that surprises.</strong> The reader should encounter at least one piece of information that updates their model of the world.</li>
<li><strong>A writer who is visibly thinking.</strong> Not performing certainty, but working something out on the page.</li>
<li><strong>Sentences that are worth reading individually.</strong> Long-form that succeeds is not padded short-form.</li>
</ul>

<h2>The Economics Have Changed</h2>
<p>The newsletter model — writers paid directly by readers, with no advertiser intermediary — has created a viable economic structure for long-form journalism for the first time in decades.</p>
<p>The implications are not just financial. When a writer is accountable to readers rather than advertisers, the incentive structure changes. Depth becomes a selling point rather than a liability. Nuance becomes something readers pay for rather than a reason to skip.</p>
<blockquote>We are not living through the death of reading. We are living through the death of the advertiser-supported media model that made writing cheap and shallow.</blockquote>
<p>What replaces it is still being invented. But the evidence suggests it will involve longer writing, not shorter.</p>''',
    },
    {
        'title': 'Sleep Science: Everything You Believe Is Probably Wrong',
        'category': 'Health',
        'tags': ['sleep', 'neuroscience', 'wellness'],
        'featured': False,
        'excerpt': 'Eight hours. No screens before bed. Wake up at the same time every day. The advice is everywhere. The science says it is more complicated — and more forgiving — than you think.',
        'content': '''<p>Sleep research is one of those fields where popular understanding lags the science by about fifteen years. The advice that circulates on productivity blogs and wellness influencer accounts is a mixture of solid research, outdated consensus, and myth with no scientific basis whatsoever.</p>
<p>Let us sort through what we actually know.</p>

<h2>The Eight-Hour Myth</h2>
<p>The "eight hours" number comes from a simple arithmetic calculation: if the average adult sleeps around 7–8 hours, the recommendation should be 8 hours. But "average" is doing a lot of work there.</p>
<p>Sleep need is genuinely individual. The range for healthy adults is 6–10 hours, with genetic factors accounting for a significant portion of that variation. The DEC2 gene mutation, for example, allows carriers to function optimally on six hours. About 3% of the population carries it.</p>
<p>The better question is not "how many hours did I sleep?" but "how do I feel after 16 hours awake?" If the answer is fine, you probably slept enough.</p>

<h2>Sleep Architecture Matters More Than Duration</h2>
<p>Not all sleep is equal. A night of sleep cycles through stages: light sleep, deep slow-wave sleep (SWS), and REM sleep. These serve different functions.</p>
<ul>
<li><strong>SWS</strong> is when the glymphatic system clears metabolic waste from the brain, including amyloid beta, associated with Alzheimer's. It is also critical for declarative memory consolidation.</li>
<li><strong>REM sleep</strong> is when procedural memory is consolidated and emotional processing occurs. Dreaming happens predominantly in REM.</li>
</ul>
<p>Alcohol is the most common disruptor of sleep architecture. It helps you fall asleep (sedation) while suppressing REM and fragmenting sleep in the second half of the night. The net effect is worse sleep quality even if duration appears normal.</p>

<h2>Chronotypes Are Real</h2>
<p>The division of people into "morning larks" and "night owls" is not a character trait or a lifestyle choice. It is biology. The PER3 gene is one of several genes that regulate circadian phase, and variation in these genes produces genuine differences in when the sleep drive peaks.</p>
<blockquote>Telling a night owl to go to bed at 10pm is like telling a left-handed person to write with their right hand. They can do it. It will not be natural or optimal.</blockquote>
<p>The research on shift workers makes this concrete: people whose work schedules misalign with their chronotypes have measurably higher rates of metabolic syndrome, cardiovascular disease, and mood disorders.</p>

<h2>What Actually Helps</h2>
<p>The interventions with the strongest evidence base are also the most boring: consistent wake time (more important than consistent bedtime), temperature (a bedroom around 18°C/65°F facilitates sleep onset), and light exposure (bright light in the morning anchors the circadian clock).</p>
<p>Screen time before bed is real but overstated. The blue light effect is modest. The more significant issue is that screens are cognitively stimulating — not that they emit a particular wavelength.</p>''',
    },
    {
        'title': 'Django 5.2: What\'s New and Why It Matters',
        'category': 'Technology',
        'tags': ['Django', 'Python', 'web development'],
        'featured': False,
        'excerpt': 'Django 5.2 is a long-term support release. Here is a practical guide to the most important changes and how to take advantage of them in your projects.',
        'content': '''<p>Django 5.2 landed in April 2025 as the framework's latest long-term support (LTS) release — the version that enterprises and cautious developers will be on for the next several years. It is not a revolutionary release, but it is a deeply satisfying one. The rough edges are smoother. The new features are genuinely useful.</p>

<h2>Composite Primary Keys</h2>
<p>This has been one of the most requested features in Django's history. You can now define a composite primary key across multiple fields:</p>
<pre><code>class Order(models.Model):
    class Meta:
        pk = CompositePrimaryKey("shop_id", "order_id")

    shop_id  = models.IntegerField()
    order_id = models.IntegerField()
    total    = models.DecimalField(max_digits=10, decimal_places=2)
</code></pre>
<p>This matters enormously for working with existing databases that were not designed with Django's single-column pk assumption. It also improves performance in partitioned databases where the partition key is part of the natural key.</p>

<h2>Improved Form Rendering</h2>
<p>Django's form rendering has been overhauled with a new template-based system that replaces the old string-concatenation approach. Forms now render with proper HTML5 attributes by default, including <code>required</code>, <code>minlength</code>, and <code>type="email"</code>.</p>
<p>The practical win: your forms will work with browser-native validation out of the box. You still want server-side validation — always — but the first line of defense is now free.</p>

<h2>Middleware Improvements</h2>
<p>The <code>SecurityMiddleware</code> now sets the <code>Permissions-Policy</code> header by default, blocking access to sensitive browser APIs (camera, microphone, geolocation) unless explicitly permitted. This is good security practice that previously required manual configuration.</p>

<h2>The Migration to 5.2</h2>
<p>If you are upgrading from 4.2 LTS, the migration path is well-documented. The deprecations introduced in 5.0 and 5.1 are now hard errors, so you will need to address them. Run your test suite against a 5.2 install before upgrading production.</p>
<p>If you are starting a new project, start on 5.2. It is stable, well-supported, and will receive security patches until April 2028.</p>''',
    },
    {
        'title': 'Color Theory for Interface Designers: A Practical Guide',
        'category': 'Design',
        'tags': ['color', 'UI design', 'accessibility'],
        'featured': False,
        'excerpt': 'Color is the most visceral element of interface design. It is also the most systematically misunderstood. Here is how to use it with intention rather than instinct.',
        'content': '''<p>Most designers learn color by doing — accumulating intuitions about what works through trial and error. This produces designers who can make beautiful screens but cannot articulate why they made the choices they made, or systematically fix it when something feels wrong.</p>
<p>A more structural understanding of color theory produces more reliable results.</p>

<h2>The HSL Mental Model</h2>
<p>Hexadecimal color codes are for machines. For human reasoning, the HSL (Hue, Saturation, Lightness) model is far more useful. It maps to how we actually perceive and talk about color:</p>
<ul>
<li><strong>Hue</strong>: the base color (0–360°, where 0 is red, 120 is green, 240 is blue)</li>
<li><strong>Saturation</strong>: how pure vs. grey the color is (0% is grey, 100% is pure)</li>
<li><strong>Lightness</strong>: how light or dark (0% is black, 100% is white, 50% is the pure hue)</li>
</ul>
<p>When you work in HSL, adjusting one axis while holding the others constant gives predictable, harmonious results. This is why design tokens expressed in HSL are more maintainable than hex values.</p>

<h2>Building a Palette Systematically</h2>
<p>A useful design system palette has three components:</p>
<p><strong>Neutrals</strong>: a grey scale with subtle warmth or coolness baked in. Pure greys (equal R, G, B values) look sterile and slightly purple on screen. A neutral with 5–10° of hue shift toward stone or zinc reads as intentional.</p>
<p><strong>Accent colors</strong>: 1–2 deliberate color choices that carry semantic meaning. In most interfaces, one accent for interactive elements and one for semantic states (success, warning, error) is sufficient.</p>
<p><strong>Semantic tokens</strong>: named variables that separate the <em>what</em> from the <em>which</em>. <code>--color-interactive</code> references your accent. <code>--color-danger</code> references your error red. Swap the underlying values and the interface theme changes without touching components.</p>

<h2>Accessibility is Not Optional</h2>
<p>WCAG 2.1 AA requires a contrast ratio of 4.5:1 for normal text and 3:1 for large text. These are minimums, not targets. For body text in a reading-heavy interface, aim for 7:1.</p>
<p>The most common accessibility failure in UI design: grey text on white backgrounds. If your secondary text color passes contrast checks at 100% opacity but you have reduced it to 60% opacity in your component, your effective contrast ratio just fell below the threshold.</p>''',
    },
]

COMMENTS_CONTENT = [
    "Really insightful article. The section on practical implementation was particularly helpful for my current project.",
    "I've been following this topic for a while and this is one of the clearest explanations I've seen. Thank you.",
    "Interesting perspective, though I'd push back a bit on the third point. My experience has been different.",
    "Bookmarking this for later. Exactly the kind of deep-dive I was looking for.",
    "The data you cited is fascinating. Do you have a link to the original research?",
    "This changed how I think about the problem. Going to try the approach you suggested this week.",
    "Great writing as always. The analogy in the second section really clicked for me.",
    "I shared this with my team. We've been debating this exact issue for months.",
    "Well researched and clearly written. More of this, please.",
    "The point about the economics is something people rarely talk about. Really appreciated the honesty.",
    "I was skeptical at first but by the end you had me convinced. The evidence is pretty compelling.",
    "Minor correction: the study you mentioned was actually published in 2023, not 2022. Otherwise excellent.",
]

SUBSCRIBER_EMAILS = [
    ('alex.morgan@gmail.com', 'Alex Morgan'),
    ('sofia.chen@outlook.com', 'Sofia Chen'),
    ('james.okafor@yahoo.com', 'James Okafor'),
    ('priya.nair@hotmail.com', 'Priya Nair'),
    ('tom.walker@protonmail.com', 'Tom Walker'),
    ('maria.santos@gmail.com', 'Maria Santos'),
    ('david.kim@outlook.com', 'David Kim'),
    ('emma.johansson@gmail.com', 'Emma Johansson'),
    ('carlos.mendez@yahoo.com', 'Carlos Mendez'),
    ('anna.petrova@gmail.com', 'Anna Petrova'),
    ('ben.oduya@gmail.com', 'Ben Oduya'),
    ('lisa.zimmermann@outlook.com', 'Lisa Zimmermann'),
    ('hassan.ali@protonmail.com', 'Hassan Ali'),
    ('yuki.tanaka@gmail.com', 'Yuki Tanaka'),
    ('claire.dupont@hotmail.com', 'Claire Dupont'),
]


class Command(BaseCommand):
    help = 'Fix DB schema issues and seed the database with realistic fake data'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true',
                            help='Clear existing data before seeding')

    def handle(self, *args, **options):
        from apps.blog.models import Category, Post, Comment, Newsletter, PageView
        from apps.dashboard.models import SiteSettings

        self.stdout.write(self.style.MIGRATE_HEADING('\n🔧  Fixing database schema...\n'))
        self._fix_schema()

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            PageView.objects.all().delete()
            Comment.objects.all().delete()
            Post.objects.all().delete()
            Category.objects.all().delete()
            Newsletter.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.MIGRATE_HEADING('\n👥  Creating users...\n'))
        admin, author1, author2 = self._create_users()

        self.stdout.write(self.style.MIGRATE_HEADING('\n📁  Creating categories...\n'))
        cats = self._create_categories()

        self.stdout.write(self.style.MIGRATE_HEADING('\n📝  Creating posts...\n'))
        posts = self._create_posts(cats, [author1, author2])

        self.stdout.write(self.style.MIGRATE_HEADING('\n💬  Creating comments...\n'))
        self._create_comments(posts, [author1, author2])

        self.stdout.write(self.style.MIGRATE_HEADING('\n📧  Creating newsletter subscribers...\n'))
        self._create_subscribers()

        self.stdout.write(self.style.MIGRATE_HEADING('\n⚙️   Creating site settings...\n'))
        self._create_settings()

        self.stdout.write(self.style.SUCCESS('\n✅  Done! Fake data seeded successfully.\n'))
        self.stdout.write(f'   Admin:   http://127.0.0.1:8000/admin/')
        self.stdout.write(f'   Blog:    http://127.0.0.1:8000/')
        self.stdout.write(f'   Dashboard: http://127.0.0.1:8000/dashboard/')
        self.stdout.write(f'\n   Login: admin / admin123\n')

    # ── Schema fix ────────────────────────────────────────────────

    def _fix_schema(self):
        with connection.cursor() as cur:
            fixes = [
                ('dashboard_sitesettings', 'youtube', 'varchar(200)', "''"),
            ]
            for table, col, dtype, default in fixes:
                added = safe_add_column(cur, table, col, dtype, default)
                if added:
                    self.stdout.write(f'  Added column {table}.{col}')
                else:
                    self.stdout.write(f'  Column {table}.{col} already exists ✓')
        connection.commit()

    # ── Users ─────────────────────────────────────────────────────

    def _create_users(self):
        admin, _ = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@xblog.dev', 'first_name': 'Admin',
            'last_name': 'User', 'is_staff': True, 'is_superuser': True,
            'is_author': True, 'bio': 'Site administrator and editor-in-chief.',
        })
        admin.set_password('admin123')
        admin.save()
        self.stdout.write(f'  admin / admin123  (superuser)')

        author1, _ = User.objects.get_or_create(username='sarah_writes', defaults={
            'email': 'sarah@xblog.dev', 'first_name': 'Sarah',
            'last_name': 'Mitchell', 'is_author': True,
            'bio': 'Science and technology journalist. Former researcher at MIT Media Lab.',
            'twitter': 'sarah_writes', 'github': 'sarahmitchell',
        })
        author1.set_password('author123')
        author1.save()
        self.stdout.write(f'  sarah_writes / author123  (author)')

        author2, _ = User.objects.get_or_create(username='marco_design', defaults={
            'email': 'marco@xblog.dev', 'first_name': 'Marco',
            'last_name': 'Rossi', 'is_author': True,
            'bio': 'Product designer and design systems nerd. Building better interfaces one pixel at a time.',
            'twitter': 'marco_design',
        })
        author2.set_password('author123')
        author2.save()
        self.stdout.write(f'  marco_design / author123  (author)')

        return admin, author1, author2

    # ── Categories ────────────────────────────────────────────────

    def _create_categories(self):
        from apps.blog.models import Category
        cats = {}
        for i, data in enumerate(CATEGORIES):
            cat, _ = Category.objects.get_or_create(
                name=data['name'],
                defaults={
                    'slug': slugify(data['name']),
                    'color': data['color'],
                    'icon': data['icon'],
                    'description': data['description'],
                    'order': i,
                    'is_featured': i < 4,
                }
            )
            cats[data['name']] = cat
            self.stdout.write(f'  {cat.name}')
        return cats

    # ── Posts ─────────────────────────────────────────────────────

    def _create_posts(self, cats, authors):
        from apps.blog.models import Post
        posts = []
        for i, data in enumerate(POST_DATA):
            author = authors[i % len(authors)]
            cat    = cats.get(data['category'])
            slug   = slugify(data['title'])

            if Post.objects.filter(slug=slug).exists():
                post = Post.objects.get(slug=slug)
                posts.append(post)
                self.stdout.write(f'  Skipped (exists): {post.title[:50]}')
                continue

            post = Post.objects.create(
                title       = data['title'],
                slug        = slug,
                author      = author,
                category    = cat,
                excerpt     = data['excerpt'],
                content     = data['content'],
                status      = 'published',
                published_at= timezone.now() - timezone.timedelta(days=random.randint(1, 120)),
                is_featured = data.get('featured', False),
                is_pinned   = data.get('pinned', False),
                views       = random.randint(120, 8400),
                likes       = random.randint(5, 340),
                level       = random.choice(['beginner', 'intermediate', 'advanced']),
                focus_kw    = data['tags'][0] if data.get('tags') else '',
                meta_title  = data['title'][:60],
                meta_desc   = data['excerpt'][:155],
            )

            if data.get('tags'):
                post.tags.add(*data['tags'])

            posts.append(post)
            self.stdout.write(f'  Created: {post.title[:55]}')

        return posts

    # ── Comments ──────────────────────────────────────────────────

    def _create_comments(self, posts, authors):
        from apps.blog.models import Comment
        count = 0
        for post in posts:
            if Comment.objects.filter(post=post).exists():
                continue
            n_comments = random.randint(2, 5)
            for j in range(n_comments):
                author = random.choice(authors + [None])
                c = Comment.objects.create(
                    post        = post,
                    author      = author if author else None,
                    guest_name  = '' if author else random.choice(['Alex K.', 'Jordan L.', 'Sam T.', 'Riley P.']),
                    guest_email = '' if author else f'reader{j}@example.com',
                    content     = random.choice(COMMENTS_CONTENT),
                    status      = 'approved',
                    ip          = f'192.168.1.{random.randint(1, 254)}',
                )
                count += 1
                # One pending comment per post
                if j == 0:
                    Comment.objects.create(
                        post       = post,
                        guest_name = 'New Reader',
                        guest_email= 'newreader@example.com',
                        content    = 'Just found this blog. Really enjoying the content so far!',
                        status     = 'pending',
                        ip         = '10.0.0.1',
                    )
                    count += 1
        self.stdout.write(f'  Created {count} comments')

    # ── Newsletter ────────────────────────────────────────────────

    def _create_subscribers(self):
        from apps.blog.models import Newsletter
        import secrets
        count = 0
        for email, name in SUBSCRIBER_EMAILS:
            _, created = Newsletter.objects.get_or_create(
                email=email,
                defaults={'name': name, 'active': True, 'token': secrets.token_hex(16)}
            )
            if created: count += 1
        self.stdout.write(f'  Created {count} subscribers ({Newsletter.objects.count()} total)')

    # ── Settings ──────────────────────────────────────────────────

    def _create_settings(self):
        from apps.dashboard.models import SiteSettings
        s = SiteSettings.get()
        s.site_name    = 'XBlog'
        s.tagline      = 'Think. Write. Publish.'
        s.twitter      = 'https://twitter.com/xblog'
        s.github       = 'https://github.com/xblog'
        s.linkedin     = 'https://linkedin.com/company/xblog'
        s.footer_txt   = 'A modern blog platform built with Django 5.2.'
        s.comments_on  = True
        s.moderation_on= True
        s.newsletter_on= True
        try:
            s.youtube = 'https://youtube.com/@xblog'
        except Exception:
            pass
        s.save()
        self.stdout.write('  Site settings saved')
