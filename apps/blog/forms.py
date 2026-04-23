from django import forms
from django_summernote.widgets import SummernoteWidget
from .models import Post, Comment, Newsletter


class PostForm(forms.ModelForm):
    """
    Post creation/edit form.
    NOTE: 'status' is intentionally excluded — the editor controls it via
    the status <select> widget in the toolbar, and the Publish button sets
    it via form_valid() in the view. Including 'status' here as a hidden
    field caused the "draft null" bug.
    """

    class Meta:
        model = Post
        fields = [
            'title', 'category', 'tags', 'excerpt', 'content',
            'cover', 'cover_alt', 'cover_cap', 'og_image',
            'is_featured', 'is_pinned', 'allow_comments', 'level',
            'focus_kw', 'meta_title', 'meta_desc',
            'canonical', 'no_index', 'no_follow', 'schema',
            # status is handled separately in the toolbar + view
            'status',
        ]
        widgets = {
            'title':      forms.TextInput(attrs={
                'class': 'xeditor-title',
                'placeholder': 'Post title…',
                'id': 'xEditorTitle',
            }),
            'excerpt':    forms.Textarea(attrs={
                'class': 'xform-input', 'rows': 2,
                'placeholder': 'Short excerpt — auto-generated if empty',
            }),
            'content':    SummernoteWidget(),
            'cover_alt':  forms.TextInput(attrs={'class': 'xform-input'}),
            'cover_cap':  forms.TextInput(attrs={'class': 'xform-input'}),
            'focus_kw':   forms.TextInput(attrs={
                'class': 'xform-input', 'id': 'id_focus_kw',
                'placeholder': 'e.g. django blog seo',
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'xform-input', 'id': 'id_meta_title', 'maxlength': 70,
            }),
            'meta_desc':  forms.Textarea(attrs={
                'class': 'xform-input', 'id': 'id_meta_desc',
                'rows': 2, 'maxlength': 160,
            }),
            'canonical':  forms.URLInput(attrs={'class': 'xform-input'}),
            'status':     forms.Select(attrs={'class': 'xform-input', 'id': 'xStatusSelect'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make non-essential fields optional so draft saves don't fail
        for f in ['excerpt', 'cover', 'cover_alt', 'cover_cap', 'og_image',
                  'focus_kw', 'meta_title', 'meta_desc', 'canonical']:
            if f in self.fields:
                self.fields[f].required = False


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['guest_name', 'guest_email', 'content']
        widgets = {
            'guest_name':  forms.TextInput(attrs={
                'class': 'xform-input', 'placeholder': 'Name *',
            }),
            'guest_email': forms.EmailInput(attrs={
                'class': 'xform-input', 'placeholder': 'Email *',
            }),
            'content':     forms.Textarea(attrs={
                'class': 'xform-input', 'rows': 3,
                'placeholder': 'Share your thoughts…',
            }),
        }

    def clean_content(self):
        c = self.cleaned_data.get('content', '').strip()
        if len(c) < 3:
            raise forms.ValidationError('Comment is too short.')
        return c


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['email', 'name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'xform-input', 'placeholder': 'your@email.com',
            }),
            'name': forms.TextInput(attrs={
                'class': 'xform-input', 'placeholder': 'Your name (optional)',
            }),
        }
