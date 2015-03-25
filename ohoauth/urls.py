from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    (r'^$', 'toy.views.index'),
    (r'^shanbay/$', 'shanbay.views.index'),
    (r'^shanbay/success/$', 'shanbay.views.success'),
    (r'^weibo/login/$', 'weibo.views.login'),
    (r'^weibo/success/$', 'weibo.views.success'),
    (r'^weibo/home/$', 'weibo.views.home'),
    (r'^weibo/release/$', 'weibo.views.release'),
    (r'^weibo/retrieve/$', 'weibo.views.retrieve'),
)
