from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.text import slugify


class User(AbstractUser):
    email      = models.EmailField(unique=True)
    avatar     = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio        = models.TextField(max_length=500, blank=True)
    website    = models.URLField(blank=True)
    twitter    = models.CharField(max_length=100, blank=True)
    linkedin   = models.CharField(max_length=200, blank=True)
    github     = models.CharField(max_length=100, blank=True)
    is_author  = models.BooleanField(default=False)
    author_slug= models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = 'User'

    def save(self, *args, **kwargs):
        if not self.author_slug:
            base = slugify(self.get_full_name() or self.username)
            slug, n = base, 1
            while User.objects.filter(author_slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'; n += 1
            self.author_slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:author', kwargs={'slug': self.author_slug})

    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        name = (self.get_full_name() or self.username).replace(' ', '+')
        return f'https://ui-avatars.com/api/?name={name}&background=000&color=fff&size=128&bold=true'

    def post_count(self):
        return self.posts.filter(status='published').count()

    def __str__(self):
        return self.get_full_name() or self.username
