from django.views.generic import CreateView, UpdateView, DetailView, View
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from .models import User
from .forms import RegisterForm, ProfileForm, LoginForm


class XLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class    = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Welcome back, {form.get_user().get_full_name() or form.get_user().username}!'
        )
        return super().form_valid(form)


class XLogoutView(View):
    """Accepts GET and POST — logs out and redirects to homepage."""

    def get(self, request, *args, **kwargs):
        return self._logout(request)

    def post(self, request, *args, **kwargs):
        return self._logout(request)

    def _logout(self, request):
        if request.user.is_authenticated:
            messages.success(request, 'You have been signed out.')
        logout(request)
        return redirect('/')


class RegisterView(CreateView):
    model         = User
    form_class    = RegisterForm
    template_name = 'accounts/register.html'
    success_url   = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('blog:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Account created! Sign in to continue.')
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, DetailView):
    model               = User
    template_name       = 'accounts/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model         = User
    form_class    = ProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url   = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated.')
        return super().form_valid(form)
