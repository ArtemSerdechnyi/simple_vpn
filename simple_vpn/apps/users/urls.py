from django.contrib import admin
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path, include

from . import views

app_name = 'users'

urlpatterns = [
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('account/', views.Account.as_view(), name='account'),
    path('account/settings/<int:pk>/', views.UserSettings.as_view(), name='user_settings'),
    path('account/create-site/', views.CreateSite.as_view(), name='create_site'),
    path('account/delete-site/<int:pk>/', views.DeleteSite.as_view(), name='delete_site'),
    path('account/statistics/<int:pk>/', views.SiteStatistics.as_view(), name='statistics'),

]
