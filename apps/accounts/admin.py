from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username','email','get_full_name','is_author','is_staff']
    list_editable = ['is_author']
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('avatar','bio','website','twitter','linkedin','github','is_author','author_slug')}),
    )
