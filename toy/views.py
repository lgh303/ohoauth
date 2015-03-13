#!/usr/bin/python
#coding: utf-8

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from toy.models import User

def index(request):
    return render_to_response(
        'index.html', {
            })


def success(request):
    return HttpResponse('success')


def list_users(request):
    users_str = ' | '
    for user in User.objects.all():
        users_str = users_str + user.name + ' | '
    return HttpResponse(users_str)
        


