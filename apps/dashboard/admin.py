from django.contrib import admin
from .models import SiteSettings
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, r): return not SiteSettings.objects.exists()
    def has_delete_permission(self, r, o=None): return False
