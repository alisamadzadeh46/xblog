import json
from datetime import timedelta
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDay, TruncMonth
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from apps.blog.models import Post, Category, Comment, Newsletter, PageView
from apps.blog.forms import PostForm
from apps.accounts.models import User
from apps.seo.analyzer import SEOAnalyzer
from .models import SiteSettings


# ── Permission Mixins ─────────────────────────────────────────────────────────

class DashboardMixin(LoginRequiredMixin):
    """Any logged-in user who is an author, staff, or superuser."""
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_staff or request.user.is_superuser or
                request.user.is_author):
            messages.error(request,
                'You need author or staff access to use the dashboard. '
                'Ask an admin to grant you author access.')
            return redirect('blog:home')
        return super().dispatch(request, *args, **kwargs)


class StaffMixin(LoginRequiredMixin):
    """Staff or superuser only — authors get a helpful error, not a 403."""
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request,
                'This section requires staff access.')
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)


# ── Dashboard Home ────────────────────────────────────────────────────────────

class HomeView(DashboardMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        u, now = self.request.user, timezone.now()
        qs = Post.objects.all() if u.is_staff else Post.objects.filter(author=u)
        ctx.update({
            'total_posts': qs.count(),
            'pub':   qs.filter(status='published').count(),
            'draft': qs.filter(status='draft').count(),
            'pending_comments': Comment.objects.filter(status='pending').count(),
            'subscribers':  Newsletter.objects.filter(active=True).count(),
            'views_today':  PageView.objects.filter(created_at__date=now.date()).count(),
            'views_30d':    PageView.objects.filter(created_at__gte=now - timedelta(days=30)).count(),
            'recent_posts': qs.select_related('author', 'category').order_by('-created_at')[:8],
            'top_posts':    qs.filter(status='published').order_by('-views')[:5],
            'pending_list': Comment.objects.filter(status='pending')
                                   .select_related('post', 'author').order_by('-created_at')[:5],
            'views_chart': json.dumps([
                {'d': v['day'].strftime('%b %d'), 'n': v['c']}
                for v in PageView.objects
                    .filter(created_at__gte=now - timedelta(days=14))
                    .annotate(day=TruncDay('created_at'))
                    .values('day').annotate(c=Count('id')).order_by('day')
            ]),
            'cat_chart': json.dumps([
                {'l': c['category__name'] or 'Uncategorised', 'n': c['c']}
                for c in qs.filter(status='published')
                    .values('category__name').annotate(c=Count('id')).order_by('-c')[:6]
            ]),
        })
        return ctx


# ── Posts ─────────────────────────────────────────────────────────────────────

class PostListView(DashboardMixin, ListView):
    template_name       = 'dashboard/posts/list.html'
    context_object_name = 'posts'
    paginate_by         = 20

    def get_queryset(self):
        u  = self.request.user
        qs = Post.objects.select_related('author', 'category')
        if not u.is_staff:
            qs = qs.filter(author=u)
        s, cat, q = (self.request.GET.get(k) for k in ('s', 'cat', 'q'))
        if s:   qs = qs.filter(status=s)
        if cat: qs = qs.filter(category__slug=cat)
        if q:   qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))
        return qs.order_by('-created_at')

    def get_context_data(self, **kw):
        ctx  = super().get_context_data(**kw)
        u    = self.request.user
        base = Post.objects.all() if u.is_staff else Post.objects.filter(author=u)
        ctx.update({
            'cats': Category.objects.all(),
            'sf': self.request.GET.get('s', ''),
            'cf': self.request.GET.get('cat', ''),
            'qf': self.request.GET.get('q', ''),
            'counts':      {x: base.filter(status=x).count()
                            for x in ['draft', 'review', 'published', 'archived']},
            'total_count': base.count(),
        })
        return ctx


class PostCreateView(DashboardMixin, CreateView):
    model         = Post
    form_class    = PostForm
    template_name = 'dashboard/posts/editor.html'
    success_url   = reverse_lazy('dashboard:posts')

    def form_valid(self, form):
        form.instance.author = self.request.user
        if '_publish' in self.request.POST:
            form.instance.status       = 'published'
            form.cleaned_data['status'] = 'published'
            if not form.instance.published_at:
                form.instance.published_at = timezone.now()
        messages.success(self.request, 'Post created.')
        return super().form_valid(form)

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        ctx.update({'action': 'Create', 'categories': Category.objects.all()})
        return ctx


class PostEditView(DashboardMixin, UpdateView):
    model          = Post
    form_class     = PostForm
    template_name  = 'dashboard/posts/editor.html'
    success_url    = reverse_lazy('dashboard:posts')
    slug_field     = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self):
        p = get_object_or_404(Post, slug=self.kwargs['slug'])
        if not self.request.user.is_staff and p.author != self.request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return p

    def form_valid(self, form):
        if '_publish' in self.request.POST:
            form.instance.status       = 'published'
            form.cleaned_data['status'] = 'published'
            if not form.instance.published_at:
                form.instance.published_at = timezone.now()
        messages.success(self.request, 'Post saved.')
        return super().form_valid(form)

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        obj = self.object
        ctx.update({
            'action':     'Edit',
            'categories': Category.objects.all(),
            'seo': SEOAnalyzer({
                'title':      obj.title,   'slug':      obj.slug,
                'focus_kw':   obj.focus_kw,'meta_title':obj.meta_title,
                'meta_desc':  obj.meta_desc,'content':  obj.content,
                'excerpt':    obj.excerpt, 'cover_alt': obj.cover_alt,
                'schema':     obj.schema,  'og_image':  bool(obj.og_image),
            }).run(),
        })
        return ctx


class PostDeleteView(DashboardMixin, DeleteView):
    model          = Post
    template_name  = 'dashboard/posts/delete.html'
    success_url    = reverse_lazy('dashboard:posts')
    slug_field     = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self):
        p = get_object_or_404(Post, slug=self.kwargs['slug'])
        if not self.request.user.is_staff and p.author != self.request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return p

    def form_valid(self, form):
        messages.success(self.request, f'"{self.object.title}" deleted.')
        return super().form_valid(form)


class PostStatusView(DashboardMixin, View):
    def post(self, request, slug):
        p = get_object_or_404(Post, slug=slug)
        if not request.user.is_staff and p.author != request.user:
            return JsonResponse({'error': 'Forbidden'}, status=403)
        ns = json.loads(request.body).get('status')
        if ns in ['draft', 'review', 'published', 'archived']:
            p.status = ns
            if ns == 'published' and not p.published_at:
                p.published_at = timezone.now()
            p.save(update_fields=['status', 'published_at'])
            return JsonResponse({'status': p.status})
        return JsonResponse({'error': 'Invalid status'}, status=400)


# ── Categories ────────────────────────────────────────────────────────────────

class CategoryListView(DashboardMixin, ListView):
    model               = Category
    template_name       = 'dashboard/categories/list.html'
    context_object_name = 'cats'

    def get_queryset(self):
        return Category.objects.annotate(
            n=Count('posts', filter=Q(posts__status='published'))
        ).order_by('order', 'name')


class CategoryCreateView(DashboardMixin, CreateView):
    model         = Category
    template_name = 'dashboard/categories/form.html'
    fields        = ['name', 'description', 'cover', 'color', 'icon',
                     'order', 'is_featured', 'meta_title', 'meta_desc']
    success_url   = reverse_lazy('dashboard:categories')

    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" created.')
        return super().form_valid(form)


class CategoryEditView(DashboardMixin, UpdateView):
    model         = Category
    template_name = 'dashboard/categories/form.html'
    fields        = ['name', 'description', 'cover', 'color', 'icon',
                     'order', 'is_featured', 'meta_title', 'meta_desc']
    success_url   = reverse_lazy('dashboard:categories')

    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" updated.')
        return super().form_valid(form)


class CategoryDeleteView(DashboardMixin, DeleteView):
    model       = Category
    template_name = 'dashboard/categories/delete.html'
    success_url = reverse_lazy('dashboard:categories')

    def form_valid(self, form):
        messages.success(self.request, f'Category deleted.')
        return super().form_valid(form)


# ── Comments ──────────────────────────────────────────────────────────────────

class CommentListView(DashboardMixin, ListView):
    model               = Comment
    template_name       = 'dashboard/comments/list.html'
    context_object_name = 'comments'
    paginate_by         = 30

    def get_queryset(self):
        qs = Comment.objects.select_related('post', 'author').order_by('-created_at')
        s  = self.request.GET.get('s')
        return qs.filter(status=s) if s else qs

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        ctx.update({
            'sf':          self.request.GET.get('s', ''),
            'counts':      {x: Comment.objects.filter(status=x).count()
                            for x in ['pending', 'approved', 'spam']},
            'total_count': Comment.objects.count(),
        })
        return ctx


class CommentActionView(DashboardMixin, View):
    def post(self, request, pk):
        c = get_object_or_404(Comment, pk=pk)
        a = json.loads(request.body).get('action')
        if a in ['approved', 'spam', 'pending']:
            c.status = a
            c.save(update_fields=['status'])
            return JsonResponse({'status': c.status})
        if a == 'delete':
            c.delete()
            return JsonResponse({'deleted': True})
        return JsonResponse({'error': 'Bad action'}, status=400)


# ── Analytics ─────────────────────────────────────────────────────────────────

class AnalyticsView(DashboardMixin, TemplateView):
    template_name = 'dashboard/analytics.html'

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        now = timezone.now()
        u   = self.request.user
        qs  = Post.objects.published() if u.is_staff else Post.objects.published().filter(author=u)

        ctx.update({
            'v30': PageView.objects.filter(created_at__gte=now - timedelta(days=30)).count(),
            'v7':  PageView.objects.filter(created_at__gte=now - timedelta(days=7)).count(),
            'v1':  PageView.objects.filter(created_at__date=now.date()).count(),
            'top_posts': qs.order_by('-views')[:10],
            'top_refs': (
                PageView.objects.exclude(referer='')
                .values('referer').annotate(n=Count('id')).order_by('-n')[:8]
            ),
            'cat_perf': (
                Category.objects
                .annotate(
                    pc=Count('posts', filter=Q(posts__status='published')),
                    tv=Sum('posts__views')
                )
                .filter(pc__gt=0).order_by('-tv')[:8]
            ),
            'views_chart': json.dumps([
                {'d': v['day'].strftime('%b %d'), 'n': v['c']}
                for v in PageView.objects
                    .filter(created_at__gte=now - timedelta(days=30))
                    .annotate(day=TruncDay('created_at'))
                    .values('day').annotate(c=Count('id')).order_by('day')
            ]),
        })
        return ctx


# ── Newsletter ────────────────────────────────────────────────────────────────

class NewsletterView(DashboardMixin, ListView):
    model               = Newsletter
    template_name       = 'dashboard/newsletter/list.html'
    context_object_name = 'subs'
    paginate_by         = 50

    def get_queryset(self):
        qs = Newsletter.objects.order_by('-subscribed_at')
        s  = self.request.GET.get('s')
        if s == 'active': return qs.filter(active=True)
        if s == 'off':    return qs.filter(active=False)
        return qs

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        ctx.update({
            'total':  Newsletter.objects.count(),
            'active': Newsletter.objects.filter(active=True).count(),
            'sf':     self.request.GET.get('s', ''),
        })
        return ctx


# ── Users ─────────────────────────────────────────────────────────────────────

class UserListView(StaffMixin, ListView):
    model               = User
    template_name       = 'dashboard/users/list.html'
    context_object_name = 'users'
    paginate_by         = 30

    def get_queryset(self):
        return User.objects.annotate(
            pc=Count('posts', filter=Q(posts__status='published'))
        ).order_by('-date_joined')


class UserToggleView(StaffMixin, View):
    def post(self, request, pk):
        u = get_object_or_404(User, pk=pk)
        u.is_author = not u.is_author
        u.save(update_fields=['is_author'])
        return JsonResponse({'is_author': u.is_author})


# ── Settings ──────────────────────────────────────────────────────────────────

class SettingsView(StaffMixin, TemplateView):
    template_name = 'dashboard/settings.html'

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        ctx['s'] = SiteSettings.get()
        return ctx

    def post(self, request):
        s = SiteSettings.get()
        for f in ['site_name', 'tagline', 'twitter', 'facebook', 'instagram',
                  'linkedin', 'github', 'ga_id', 'footer_txt']:
            setattr(s, f, request.POST.get(f, ''))
        # youtube is optional — only save if the column exists
        if request.POST.get('youtube') is not None:
            try:
                s.youtube = request.POST.get('youtube', '')
            except Exception:
                pass
        s.comments_on   = 'comments_on'   in request.POST
        s.moderation_on = 'moderation_on' in request.POST
        s.newsletter_on = 'newsletter_on' in request.POST
        if 'logo' in request.FILES:
            s.logo = request.FILES['logo']
        s.save()
        messages.success(request, 'Settings saved.')
        return redirect('dashboard:settings')
