from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

W = lambda t,p='': {'class':'xform-input','placeholder':p,'autocomplete':'off'} if t!='file' else {'class':'xform-file'}

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={**W('t','Username or email'),'autofocus':True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs=W('t','Password')))

class RegisterForm(UserCreationForm):
    email      = forms.EmailField(widget=forms.EmailInput(attrs=W('t','Email address')))
    first_name = forms.CharField(widget=forms.TextInput(attrs=W('t','First name')))
    last_name  = forms.CharField(widget=forms.TextInput(attrs=W('t','Last name')))
    class Meta:
        model  = User
        fields = ('username','email','first_name','last_name','password1','password2')
        widgets= {'username': forms.TextInput(attrs=W('t','Username'))}
    def __init__(self,*a,**k):
        super().__init__(*a,**k)
        self.fields['password1'].widget.attrs.update(W('t','Password'))
        self.fields['password2'].widget.attrs.update(W('t','Confirm password'))

class ProfileForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ('first_name','last_name','email','bio','avatar','website','twitter','linkedin','github')
        widgets= {f: forms.TextInput(attrs=W('t')) for f in ('first_name','last_name','email','website','twitter','linkedin','github')}
        widgets['bio']    = forms.Textarea(attrs={**W('t'),'rows':3})
        widgets['email']  = forms.EmailInput(attrs=W('t'))
        widgets['avatar'] = forms.FileInput(attrs=W('file'))
