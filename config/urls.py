from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from apps.blog.sitemaps import PostSitemap, CategorySitemap, StaticSitemap

sitemaps = {'posts': PostSitemap, 'categories': CategorySitemap, 'static': StaticSitemap}

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('',            include('apps.blog.urls',      namespace='blog')),
    path('accounts/',   include('apps.accounts.urls',  namespace='accounts')),
    path('dashboard/',  include('apps.dashboard.urls', namespace='dashboard')),
    path('seo/',        include('apps.seo.urls',       namespace='seo')),
    path('summernote/', include('django_summernote.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
