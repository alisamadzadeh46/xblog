from .models import Category, Post
from django.db.models import Count, Q

def global_context(request):
    cats = Category.objects.annotate(n=Count('posts',filter=Q(posts__status='published'))).filter(n__gt=0).order_by('order','name')[:8]
    return {
        'nav_cats':    cats,
        'recent_posts':Post.objects.published().select_related('author')[:5],
    }
