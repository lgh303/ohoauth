#!/usr/bin/python
#coding: utf-8

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response


def index(request):
    return render_to_response(
        'index_weibo.html', {
            })


def success(request):
    return HttpResponse("Log in successfully!")

