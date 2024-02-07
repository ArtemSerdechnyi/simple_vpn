from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from django.contrib.auth import get_user_model, authenticate, login

from .models import Site


class LoginUserForm(AuthenticationForm):
    class Meta:
        models = get_user_model()
        fields = ['username', 'password', ]


class RegistrationForm(UserCreationForm):

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    class Meta:
        model = get_user_model()
        fields = ['username', 'password1', 'password2', ]

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            auth_user = authenticate(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password1']
            )
            login(self.request, auth_user)

        return user


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['name', 'origin_url']
