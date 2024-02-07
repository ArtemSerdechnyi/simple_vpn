from urllib.parse import urlparse

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, UpdateView, ListView, DeleteView, DetailView, CreateView
from django.contrib.auth import login
from .forms import RegistrationForm, LoginUserForm, SiteForm
from .models import Site

from django.contrib.auth import get_user_model


class RegistrationView(CreateView):
    template_name = 'users/registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('users:account')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['request'] = self.request
        return form_kwargs


class LoginUserView(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'


class CreateSite(FormView):
    template_name = 'users/create_site.html'
    form_class = SiteForm
    success_url = reverse_lazy('users:account')

    def form_valid(self, form):
        site = form.save(commit=False)
        site.user = self.request.user
        site.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class DeleteSite(DeleteView):
    model = Site
    template_name = 'users/delete_site_confirm.html'
    success_url = reverse_lazy('users:account')

    def get_queryset(self):
        return Site.objects.filter(user=self.request.user)


class SiteStatistics(DetailView):
    model = Site
    template_name = 'users/statistics.html'
    context_object_name = 'site'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statistics'] = self.object.statistics()
        return context


class Account(ListView):
    model = get_user_model()
    template_name = 'users/account.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['user_sites'] = self.request.user.sites.all()
        return context


class UserSettings(UpdateView):
    model = get_user_model()
    fields = ['username', 'first_name', 'last_name', 'email']
    template_name = 'users/settings.html'
    success_url = reverse_lazy('users:account')
