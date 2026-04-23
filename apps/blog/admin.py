from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Post, Category, Comment, Newsletter, PageView

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','published_count','is_featured','order']
    list_editable= ['is_featured','order']
    prepopulated_fields = {'slug':('name',)}

@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display  = ['title','author','category','status','views','published_at']
    list_filter   = ['status','category']
    list_editable = ['status']
    search_fields = ['title','author__username']
    prepopulated_fields = {'slug':('title',)}
    readonly_fields = ['views','likes','reading_time','created_at','updated_at']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ['author_name','post','status','created_at']
    list_editable = ['status']
    list_filter   = ['status']
    actions = ['approve','spam']
    def approve(self, r, qs): qs.update(status='approved')
    def spam(self,    r, qs): qs.update(status='spam')
    approve.short_description = 'Approve'
    spam.short_description    = 'Mark spam'

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email','name','active','subscribed_at']
