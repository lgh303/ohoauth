#!/usr/bin/python
#coding: utf-8

from django.db import models

class User(models.Model):
    uid = models.CharField(max_length=20, blank=False, unique = True)
    access_token = models.CharField(max_length=50)
    expires_in = models.CharField(max_length=20)
    rtime = models.DateTimeField(auto_now = True)
