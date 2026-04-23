from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import F
from taggit.managers import TaggableManager
import re
import json


class Category(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    cover       = models.ImageField(upload_to='categories/', blank=True, null=True)
    color       = models.CharField(max_length=7, default='#ffffff')
    icon        = models.CharField(max_length=60, blank=True)
    order       = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    meta_title  = models.CharField(max_length=70, blank=True)
    meta_desc   = models.CharField(max_length=160, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})

    def published_count(self):
        return self.posts.filter(status='published').count()

    def __str__(self):
        return self.name


class PostManager(models.Manager):
    def published(self):
        return self.filter(status='published', published_at__lte=timezone.now())

    def featured(self):
        return self.published().filter(is_featured=True)

    def trending(self):
        return self.published().order_by('-views')[:6]


class Post(models.Model):
    STATUS = [('draft','Draft'),('review','Review'),('published','Published'),('archived','Archived')]
    LEVEL  = [('beginner','Beginner'),('intermediate','Intermediate'),('advanced','Advanced')]
    SCHEMA = [('BlogPosting','Blog Post'),('Article','Article'),('NewsArticle','News Article')]

    title       = models.CharField(max_length=255)
    slug        = models.SlugField(unique=True, max_length=255, blank=True)
    author      = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='posts')
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    tags        = TaggableManager(blank=True)
    excerpt     = models.TextField(max_length=500, blank=True)
    content     = models.TextField(blank=True, default='')

    cover       = models.ImageField(upload_to='posts/%Y/%m/', blank=True, null=True)
    cover_alt   = models.CharField(max_length=200, blank=True)
    cover_cap   = models.CharField(max_length=300, blank=True)
    og_image    = models.ImageField(upload_to='og/', blank=True, null=True)

    status          = models.CharField(max_length=20, choices=STATUS, default='draft', db_index=True)
    is_featured     = models.BooleanField(default=False)
    is_pinned       = models.BooleanField(default=False)
    allow_comments  = models.BooleanField(default=True)
    # published_at is nullable — drafts have no date
    published_at    = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    views        = models.PositiveIntegerField(default=0)
    likes        = models.PositiveIntegerField(default=0)
    reading_time = models.PositiveIntegerField(default=1)
    level        = models.CharField(max_length=20, choices=LEVEL, default='beginner')

    focus_kw   = models.CharField(max_length=100, blank=True)
    meta_title = models.CharField(max_length=70,  blank=True)
    meta_desc  = models.CharField(max_length=160, blank=True)
    canonical  = models.URLField(blank=True)
    no_index   = models.BooleanField(default=False)
    no_follow  = models.BooleanField(default=False)
    schema     = models.CharField(max_length=20, choices=SCHEMA, default='BlogPosting')

    objects = PostManager()

    class Meta:
        # Use created_at as the primary sort so NULLs in published_at never cause issues
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['-created_at']),
        ]

    def save(self, *args, **kwargs):
        # Auto-slug
        if not self.slug:
            base = slugify(self.title)
            s, n = base, 1
            while Post.objects.filter(slug=s).exclude(pk=self.pk).exists():
                s = f'{base}-{n}'
                n += 1
            self.slug = s

        # Set published_at when first publishing
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()

        # Auto-excerpt
        if not self.excerpt and self.content:
            plain = re.sub(r'<[^>]+>', ' ', self.content)
            words = plain.split()
            self.excerpt = ' '.join(words[:50]) + ('…' if len(words) > 50 else '')

        # Reading time
        plain = re.sub(r'<[^>]+>', ' ', self.content or '')
        wc = len(plain.split())
        self.reading_time = max(1, wc // 200)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post', kwargs={'slug': self.slug})

    def seo_title(self):
        return self.meta_title or self.title

    def seo_desc(self):
        return self.meta_desc or self.excerpt

    def hit(self):
        """Increment view count atomically."""
        Post.objects.filter(pk=self.pk).update(views=F('views') + 1)

    def word_count(self):
        plain = re.sub(r'<[^>]+>', ' ', self.content or '')
        return len(plain.split())

    def schema_ld(self, request=None):
        """Return JSON-LD schema string — safe against NULL published_at."""
        from django.conf import settings as dj_settings
        d = {
            '@context':     'https://schema.org',
            '@type':        self.schema,
            'headline':     self.title,
            'description':  self.seo_desc(),
            'dateModified': self.updated_at.isoformat(),
            'author': {
                '@type': 'Person',
                'name':  str(self.author),
            },
            'publisher': {
                '@type': 'Organization',
                'name':  dj_settings.SITE_NAME,
            },
        }
        if self.published_at:
            d['datePublished'] = self.published_at.isoformat()
        if self.cover:
            d['image'] = f'{dj_settings.SITE_URL}{self.cover.url}'
        return json.dumps(d, indent=2)

    def display_date(self):
        """Safe date for templates — falls back to created_at if not published."""
        return self.published_at or self.created_at

    def __str__(self):
        return self.title


class Comment(models.Model):
    STATUS = [('pending','Pending'),('approved','Approved'),('spam','Spam')]

    post        = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent      = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    author      = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True, blank=True)
    guest_name  = models.CharField(max_length=100, blank=True)
    guest_email = models.EmailField(blank=True)
    content     = models.TextField(max_length=2000)
    status      = models.CharField(max_length=20, choices=STATUS, default='pending', db_index=True)
    ip          = models.GenericIPAddressField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def author_name(self):
        return str(self.author) if self.author else (self.guest_name or 'Anonymous')

    def author_avatar(self):
        if self.author:
            return self.author.avatar_url()
        name = (self.guest_name or 'A').replace(' ', '+')
        return f'https://ui-avatars.com/api/?name={name}&background=111&color=fff&size=64&bold=true'

    def __str__(self):
        return f'{self.author_name()} on {self.post}'


class PostLike(models.Model):
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    user       = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True, blank=True)
    ip         = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['post', 'user'],
                condition=models.Q(user__isnull=False),
                name='unique_post_user_like',
            ),
        ]


class Newsletter(models.Model):
    email         = models.EmailField(unique=True)
    name          = models.CharField(max_length=100, blank=True)
    active        = models.BooleanField(default=True)
    token         = models.CharField(max_length=64, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class PageView(models.Model):
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='page_views')
    path       = models.CharField(max_length=500)
    ip         = models.GenericIPAddressField(null=True, blank=True)
    user       = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    referer    = models.URLField(blank=True)
    ua         = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
