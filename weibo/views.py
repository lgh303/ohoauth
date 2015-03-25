#!/usr/bin/python
#coding: utf-8

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from weibo.models import User
import urllib, urllib2, httplib2
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

        info = user_info(user.uid, user.access_token)
        user.name = info['screen_name']

        user.save()
        request.session['uid'] = res['uid']
        return HttpResponseRedirect('/weibo/home/')


def home(request):
    if 'uid' not in request.session:
        return HttpResponseRedirect('/weibo/login/')
    user = User.objects.filter(uid = request.session['uid']).first()

    template_data = {}
    template_data['user'] = user
    template_data['action'] = 'none'
    template_data['status'] = 'none'

    if 'action' in request.GET:
        if request.GET['action'] == 'release':
            template_data['action'] = 'release'
            if (request.method == 'POST'):
                content = request.POST['content']
                if not content:
                    template_data['status'] = u'微博内容不能为空'
                    return render_to_response(
                        'home_weibo.html',template_data,
                        context_instance = RequestContext(request)
                    )
                response_json = release_weibo(content, user.access_token)
                if 'error' in response_json:
                    template_data['status'] = response_json['error']
                    return render_to_response(
                        'home_weibo.html',template_data,
                        context_instance = RequestContext(request)
                    )
                template_data['status'] = u'微博成功发布'
            return render_to_response(
                'home_weibo.html',template_data,
                context_instance = RequestContext(request)
            )
        elif request.GET['action'] == 'retrieve':
            template_data['action'] = 'retrieve'
            response_json = retrieve_weibo(user.uid, user.access_token)
            template_data['weibo_text_list'] = []
            for item in response_json['statuses']:
                template_data['weibo_text_list'].append(item['text'])
            return render_to_response(
                'home_weibo.html',template_data,
                context_instance = RequestContext(request)
            )
    return render_to_response(
        'home_weibo.html',template_data,
        context_instance = RequestContext(request)
    )


def user_info(uid, access_token):
    url = 'https://api.weibo.com/2/users/show.json'
    paras = urllib.urlencode({
        'uid' : uid,
        'access_token' : access_token,
    })
    http = httplib2.Http()
    response, content = http.request(url + '?' + paras)
    return json.loads(content)


def release_weibo(content, access_token):
    url = 'https://api.weibo.com/2/statuses/update.json'
    data = (
        ('status', content),
        ('access_token', access_token),
    )
    req = urllib2.Request(url, urllib.urlencode(data))
    res_data = urllib2.urlopen(req).read()
    return json.loads(res_data)


def retrieve_weibo(uid, access_token):
    url = 'https://api.weibo.com/2/statuses/user_timeline.json'
    paras = urllib.urlencode({
        'uid' : uid,
        'access_token' : access_token,
    })
    http = httplib2.Http()
    response, content = http.request(url + '?' + paras)
    return json.loads(content)
