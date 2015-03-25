#!/usr/bin/python
#coding: utf-8

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from weibo.models import User

import json

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def login(request):
    url = 'https://api.weibo.com/oauth2/authorize'
    client_id = '225784211'
    redirect_uri = 'http://ligh.xyz/weibo/success'
    redirect_uri_callback = 'http://127.0.0.1:8000/weibo/success'
    paras = '?client_id=' + client_id + '&response_type=code&redirect_uri=' + redirect_uri_callback;
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
        ('redirect_uri', redirect_uri_callback),
        ('code', code),
        )

    import urllib, urllib2, httplib2
    req = urllib2.Request(url, urllib.urlencode(data))
    res_data = urllib2.urlopen(req).read()
    res = json.loads(res_data)

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

        url = 'https://api.weibo.com/2/users/show.json'
        paras = urllib.urlencode({
            'uid' : user.uid,
            'access_token' : user.access_token,
        })
        http = httplib2.Http()
        response, content = http.request(url + '?' + paras)
        info = json.loads(content)
        user.name = info['screen_name']
        user.save()
        request.session['uid'] = res['uid']
        return HttpResponseRedirect('/weibo/home/')


def home(request):
    if 'uid' not in request.session:
        return HttpResponseRedirect('/weibo/login/')
    user = User.objects.filter(uid = request.session['uid']).first()

    return render_to_response(
        'home_weibo.html', {
            'user' : user,
            'status' : 'Welcome',
        })


def release(request):
    if 'uid' not in request.session:
        return HttpResponseRedirect('/weibo/login/')
    user = User.objects.filter(uid = request.session['uid']).first()

    if (request.method == 'POST'):
        import urllib, urllib2
        url = 'https://api.weibo.com/2/statuses/update.json'
        content = request.POST['content']
        print content
        data = (
            ('status', content),
            ('access_token', user.access_token),
        )
        req = urllib2.Request(url, urllib.urlencode(data))
        res_data = urllib2.urlopen(req).read()
        res = json.loads(res_data)
        if 'error' in res:
            return HttpResponse(res_data)
        return render_to_response(
            'release_weibo.html', {
                'user' : user,
                'status' : u'微博成功发布',
            })
    else:
        return render_to_response(
            'release_weibo.html', {
                'user' : user,
                },
            context_instance = RequestContext(request)
        )


def retrieve(request):
    if 'uid' not in request.session:
        return HttpResponseRedirect('/weibo/login/')
    user = User.objects.filter(uid = request.session['uid']).first()

    return HttpResponseRedirect('/weibo/home/?action=retrieve')
