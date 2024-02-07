from django.urls import path, re_path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('<slug:name>/<str:netloc>/', views.Pars.as_view(), name='parse2'),
    re_path(r'^(?P<name>[-a-zA-Z0-9_]+)/(?P<netloc>[^/]+)/(?P<path>.*)/?$', views.Pars.as_view(), name='parse3'),
    # re_path(r'^(?P<name>[-a-zA-Z0-9_]+)/(?P<netloc>[^/]+)/(?P<path>[^?]*)(?P<query>[^/]*)/?$', views.Pars.as_view(), name='parse3'),
    # re_path(r'^(?P<name>.*)(?P<netloc>.*)(?P<path>.*)(?P<query>.*)', views.Pars.as_view(), name='parse3'),
]
