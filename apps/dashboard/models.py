from django.db import models


class SiteSettings(models.Model):
    """
    Global site settings. Only ONE row ever exists (pk=1).

    After downloading v8, run these commands once to add the youtube column:
        python manage.py migrate dashboard --fake 0001
        python manage.py migrate dashboard
    """
    site_name    = models.CharField(max_length=100, default='XBlog')
    tagline      = models.CharField(max_length=200, blank=True)
    logo         = models.ImageField(upload_to='site/', blank=True, null=True)
    twitter      = models.URLField(blank=True)
    facebook     = models.URLField(blank=True)
    instagram    = models.URLField(blank=True)
    linkedin     = models.URLField(blank=True)
    github       = models.URLField(blank=True)
    # youtube added by migration 0002 — run: python manage.py migrate dashboard
    ga_id        = models.CharField(max_length=30, blank=True)
    footer_txt   = models.TextField(blank=True)
    comments_on   = models.BooleanField(default=True)
    moderation_on = models.BooleanField(default=True)
    newsletter_on = models.BooleanField(default=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Settings'

    def __str__(self):
        return self.site_name

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def youtube_url(self):
        """Safe getter — returns empty string if youtube column doesn't exist yet."""
        try:
            return self.__class__.objects.values_list('youtube', flat=True).get(pk=self.pk)
        except Exception:
            return ''
