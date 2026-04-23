from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Post, Category

class PostSitemap(Sitemap):
    changefreq='weekly'; priority=0.9
    def items(self): return Post.objects.published()
    def lastmod(self, o): return o.updated_at
    def location(self, o): return o.get_absolute_url()

class CategorySitemap(Sitemap):
    changefreq='weekly'; priority=0.7
    def items(self): return Category.objects.all()
    def location(self, o): return o.get_absolute_url()

class StaticSitemap(Sitemap):
    priority=1.0; changefreq='daily'
    def items(self): return ['blog:home','blog:search']
    def location(self, i): return reverse(i)
