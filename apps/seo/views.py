import json
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .analyzer import SEOAnalyzer

class LiveAnalyzeView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'error': 'Bad JSON'}, status=400)
        result = SEOAnalyzer(data).run()
        return JsonResponse(result)
