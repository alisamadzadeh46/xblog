from .models import PageView, Post

class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        resp = self.get_response(request)
        if request.method == 'GET' and resp.status_code == 200:
            path = request.path
            skip = ('/admin/','/static/','/media/','/dashboard/','/seo/','/summernote/')
            if not any(path.startswith(s) for s in skip):
                try:
                    post = None
                    if '/post/' in path:
                        slug = path.strip('/').split('/')[-1]
                        post = Post.objects.filter(slug=slug).first()
                    PageView.objects.create(
                        post=post, path=path,
                        ip=request.META.get('REMOTE_ADDR'),
                        user=request.user if request.user.is_authenticated else None,
                        referer=request.META.get('HTTP_REFERER','')[:500],
                        ua=request.META.get('HTTP_USER_AGENT','')[:300],
                    )
                except: pass
        return resp
