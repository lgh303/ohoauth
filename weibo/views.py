#!/usr/bin/python
#coding: utf-8

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from weibo.models import User

import json


def index(request):
    return render_to_response(
        'index_weibo.html', {
            })


def login(request):
    url = 'https://api.weibo.com/oauth2/authorize'
    client_id = '225784211'
    redirect_uri = 'http://ligh.xyz/weibo/success'
    redirect_uri_callback = 'http://127.0.0.1:8000/weibo/success'
    paras = '?client_id=' + client_id + '&response_type=code&redirect_uri=' + redirect_uri;
    return HttpResponseRedirect(url + paras)


def success(request):
    if 'code' in request.GET:
        code = request.GET['code']
    else:
        return HttpResponse('ERROR : No code returned')
    url = 'https://api.weibo.com/oauth2/access_token'
    redirect_uri_callback = 'http://127.0.0.1:8000/weibo/success'
    redirect_uri = 'http://ligh.xyz/weibo/success'
    data = (
        ('client_id', '225784211'),
        ('client_secret', '5bd2774944d0d0f4599c4b69bcd1b813'),
        ('grant_type', 'authorization_code'),
        ('redirect_uri', redirect_uri),
        ('code', code),
        )
    import urllib, urllib2
    req = urllib2.Request(url, urllib.urlencode(data))
    res_data = urllib2.urlopen(req)
    res = json.loads(res_data.read())

    if 'uid' not in res or 'access_token' not in res:
        return HttpResponse(res)
    else:
        user_list = User.objects.filter(uid = res['uid'])
        if not user_list:
            user = User(uid = res['uid'])
        else:
            user = user_list.first()
        user.access_token = res['access_token']
        user.expires_in = res['expires_in']
        user.save()
        return HttpResponse(res)

