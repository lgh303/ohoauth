from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    (r'^$', 'toy.views.index'),
    (r'^success/$', 'toy.views.success'),
    (r'^users/$', 'toy.views.list_users'),
)
