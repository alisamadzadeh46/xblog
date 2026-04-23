from django.conf import settings
def seo_context(request):
    return {'site_name': settings.SITE_NAME,'site_url': settings.SITE_URL,'site_desc': settings.SITE_DESCRIPTION,'site_tagline': settings.SITE_TAGLINE}
