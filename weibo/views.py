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


def users(request):
    response = {}
    response['users'] = []
    for user in User.objects.all():
        user_data = {}
        user_data['uid'] = user.uid
        user_data['name'] = user.name
        response['users'].append(user_data)
    return HttpResponse(json.dumps(response))


def posts(request, user_id):
    user = User.objects.filter(uid = user_id)
    if not user:
        error = {'error' : 'uid not found'}
        return HttpResponse(json.dumps(error))
    user = user.first()
    response_json = retrieve_weibo(user.uid, user.access_token)
    response = {}
    response['uid'] = user.uid
    if 'error' in response_json:
        response['error'] = 'This user has expired...'
        return HttpResponse(json.dumps(response))
    response['posts'] = []
    text = ''
    for item in response_json['statuses']:
        response['posts'].append(item['text'])
        text += item['text'] + ','
    if 'keywords' in request.GET:
        if request.GET['keywords'] == '1':
            res, keys = get_keywords(text)
            response['keywords'] = keys.strip(',').split(',')
    return HttpResponse(json.dumps(response, ensure_ascii=False))


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
        request.session.set_expiry(0)
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
            text = ""
            for item in response_json['statuses']:
                template_data['weibo_text_list'].append(item['text'])
                text += item['text'] + ','
            response, keywords = get_keywords(text)
            template_data['keyword_ret_code'] = response['status']
            if response['status'] == '200':
                template_data['keywords'] = keywords
                template_data['keywords_length'] = response['content-length']
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


def get_keywords(content):
    url = 'http://api.yutao.us/api/keyword/'
    http = httplib2.Http()
    return http.request(url + content.replace('/', ''))
