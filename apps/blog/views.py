from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, F
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from .models import Post, Category, Comment, Newsletter, PostLike
from .forms import CommentForm, NewsletterForm


# ─────────────────────────────────────────────────────────────────────────────
class HomeView(ListView):
    model               = Post
    template_name       = 'blog/home.html'
    context_object_name = 'posts'
    paginate_by         = settings.POSTS_PER_PAGE
    allow_empty         = True    # never 404 on empty queryset
    paginate_orphans    = 2       # avoid a tiny orphan last page

    def get(self, request, *args, **kwargs):
        """Redirect out-of-range page numbers to last valid page."""
        from django.core.paginator import InvalidPage, Paginator
        try:
            return super().get(request, *args, **kwargs)
        except (InvalidPage, Exception) as e:
            if 'page' in str(e).lower() or 'invalid' in str(e).lower():
                qs    = self.get_queryset()
                pager = Paginator(qs, self.paginate_by)
                last  = pager.num_pages
                from django.shortcuts import redirect as _redirect
                return _redirect(f'/?page={last}')
            raise

    def get_queryset(self):
        return (
            Post.objects.published()
            .select_related('author', 'category')
            .prefetch_related('tags')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['hero_post']  = (
            Post.objects.published().filter(is_pinned=True).first()
            or Post.objects.published().first()
        )
        ctx['featured']   = Post.objects.featured().select_related('author', 'category')[:3]
        ctx['trending']   = Post.objects.trending()
        ctx['categories'] = Category.objects.annotate(
            n=Count('posts', filter=Q(posts__status='published'))
        ).filter(n__gt=0)[:8]
        ctx['nl_form']    = NewsletterForm()
        return ctx


# ─────────────────────────────────────────────────────────────────────────────
class PostDetailView(DetailView):
    model               = Post
    template_name       = 'blog/post.html'
    context_object_name = 'post'

    def get_object(self):
        post = get_object_or_404(
            Post.objects.select_related('author', 'category')
                        .prefetch_related('tags'),
            slug=self.kwargs['slug'],
        )
        # Published posts are visible to everyone
        if post.status == 'published':
            return post
        # Unpublished: staff, superuser, or the post's own author can preview
        user = self.request.user
        if user.is_authenticated and (
            user.is_staff or user.is_superuser or user == post.author
        ):
            return post
        # Everyone else → 404
        raise PermissionDenied

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Only count views for published posts
        if self.object.status == 'published':
            self.object.hit()
        return response

    def get_context_data(self, **kwargs):
        ctx  = super().get_context_data(**kwargs)
        post = self.object

        # Comments (threaded, approved only)
        comments = (
            Comment.objects.filter(post=post, status='approved', parent=None)
                   .select_related('author')
                   .prefetch_related('replies__author')
        )
        pager = Paginator(comments, 10)
        ctx['comments']      = pager.get_page(self.request.GET.get('cp', 1))
        ctx['comment_count'] = Comment.objects.filter(post=post, status='approved').count()
        ctx['comment_form']  = CommentForm()

        # Related posts
        ctx['related'] = (
            Post.objects.published()
                .filter(Q(category=post.category) | Q(tags__in=post.tags.all()))
                .exclude(pk=post.pk).distinct()[:4]
        )

        # Like status
        ip = self.request.META.get('REMOTE_ADDR')
        if self.request.user.is_authenticated:
            ctx['liked'] = PostLike.objects.filter(post=post, user=self.request.user).exists()
        else:
            ctx['liked'] = PostLike.objects.filter(post=post, ip=ip).exists()

        # Prev / next — safe against NULL published_at
        if post.published_at:
            pub = Post.objects.published()
            ctx['prev_post'] = pub.filter(
                published_at__lt=post.published_at
            ).order_by('-published_at').first()
            ctx['next_post'] = pub.filter(
                published_at__gt=post.published_at
            ).order_by('published_at').first()
        else:
            ctx['prev_post'] = None
            ctx['next_post'] = None

        # JSON-LD schema (safe against missing published_at)
        ctx['schema_ld'] = post.schema_ld(self.request)

        # Draft preview banner
        ctx['is_preview'] = (post.status != 'published')

        ctx['nl_form'] = NewsletterForm()
        return ctx


# ─────────────────────────────────────────────────────────────────────────────
class CategoryView(ListView):
    template_name       = 'blog/category.html'
    context_object_name = 'posts'
    paginate_by         = settings.POSTS_PER_PAGE
    allow_empty         = True
    paginate_orphans    = 2

    def get_queryset(self):
        self.cat = get_object_or_404(Category, slug=self.kwargs['slug'])
        return (
            Post.objects.published()
                .filter(category=self.cat)
                .select_related('author')
                .prefetch_related('tags')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['category'] = self.cat
        return ctx


# ─────────────────────────────────────────────────────────────────────────────
class TagView(ListView):
    template_name       = 'blog/tag.html'
    context_object_name = 'posts'
    paginate_by         = settings.POSTS_PER_PAGE
    allow_empty         = True
    paginate_orphans    = 2

    def get_queryset(self):
        self.tag_slug = self.kwargs['slug']
        return (
            Post.objects.published()
                .filter(tags__slug=self.tag_slug)
                .select_related('author', 'category')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tag']      = self.tag_slug.replace('-', ' ').title()
        ctx['tag_slug'] = self.tag_slug
        return ctx


# ─────────────────────────────────────────────────────────────────────────────
class AuthorView(ListView):
    template_name       = 'blog/author.html'
    context_object_name = 'posts'
    paginate_by         = settings.POSTS_PER_PAGE
    allow_empty         = True
    paginate_orphans    = 2

    def get_queryset(self):
        from apps.accounts.models import User
        self.author = get_object_or_404(User, author_slug=self.kwargs['slug'])
        return (
            Post.objects.published()
                .filter(author=self.author)
                .select_related('category')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['author'] = self.author
        return ctx


# ─────────────────────────────────────────────────────────────────────────────
class SearchView(ListView):
    template_name       = 'blog/search.html'
    context_object_name = 'posts'
    paginate_by         = settings.POSTS_PER_PAGE
    allow_empty         = True
    paginate_orphans    = 2

    def get_queryset(self):
        self.q = self.request.GET.get('q', '').strip()
        if len(self.q) < 2:
            return Post.objects.none()
        return (
            Post.objects.published()
                .filter(
                    Q(title__icontains=self.q)
                    | Q(content__icontains=self.q)
                    | Q(excerpt__icontains=self.q)
                    | Q(tags__name__icontains=self.q)
                )
                .distinct()
                .select_related('author', 'category')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q']     = self.q
        ctx['count'] = self.get_queryset().count()
        return ctx


# ─────────────────────────────────────────────────────────────────────────────
class CommentView(View):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug, status='published')
        if not post.allow_comments:
            return JsonResponse({'error': 'Comments are disabled.'}, status=403)

        form = CommentForm(request.POST)
        if form.is_valid():
            c         = form.save(commit=False)
            c.post    = post
            c.ip      = request.META.get('REMOTE_ADDR')
            if request.user.is_authenticated:
                c.author = request.user
                if request.user.is_staff or request.user == post.author:
                    c.status = 'approved'
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    c.parent = Comment.objects.get(id=parent_id, post=post)
                except Comment.DoesNotExist:
                    pass
            c.save()

            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({
                    'ok':       True,
                    'approved': c.status == 'approved',
                    'msg':      'Comment posted!' if c.status == 'approved'
                                else 'Comment submitted — awaiting moderation.',
                    'comment':  {
                        'id':        c.id,
                        'author':    c.author_name(),
                        'avatar':    c.author_avatar(),
                        'content':   c.content,
                        'date':      c.created_at.strftime('%b %d, %Y'),
                        'parent_id': c.parent_id,
                    },
                })
            messages.success(request, 'Comment submitted.')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'msg': 'Please fill all required fields.'})
            messages.error(request, 'Please fix the errors below.')

        return redirect(post.get_absolute_url() + '#comments')


# ─────────────────────────────────────────────────────────────────────────────
class LikeView(View):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug, status='published')
        ip   = request.META.get('REMOTE_ADDR')

        if request.user.is_authenticated:
            obj, created = PostLike.objects.get_or_create(post=post, user=request.user)
        else:
            obj, created = PostLike.objects.get_or_create(post=post, ip=ip)

        if not created:
            obj.delete()
            Post.objects.filter(pk=post.pk).update(likes=F('likes') - 1)
            liked = False
        else:
            Post.objects.filter(pk=post.pk).update(likes=F('likes') + 1)
            liked = True

        post.refresh_from_db()
        return JsonResponse({'liked': liked, 'count': post.likes})


# ─────────────────────────────────────────────────────────────────────────────
class SubscribeView(View):
    def post(self, request):
        form    = NewsletterForm(request.POST)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if form.is_valid():
            import secrets
            email     = form.cleaned_data['email']
            obj, new  = Newsletter.objects.get_or_create(email=email)
            if new:
                obj.name  = form.cleaned_data.get('name', '')
                obj.token = secrets.token_hex(32)
                obj.save()
                msg = "You're subscribed! 🎉"
            else:
                msg = "You're already on the list!"
            if is_ajax:
                return JsonResponse({'ok': True, 'msg': msg})
            messages.success(request, msg)
        else:
            if is_ajax:
                return JsonResponse({'ok': False, 'msg': 'Please enter a valid email.'})
            messages.error(request, 'Invalid email address.')

        return redirect(request.META.get('HTTP_REFERER', '/'))


# ─────────────────────────────────────────────────────────────────────────────
from django.views.generic import TemplateView

class RobotsView(TemplateView):
    template_name = 'robots.txt'
    content_type  = 'text/plain'
