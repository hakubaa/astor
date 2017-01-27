from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse


def login_user(request):
    user = User.objects.filter(username="spider").first()
    if not user:
        user = User.objects.create_user("spider", "spider@jago.com", "spider")
    login(request, user)
    return HttpResponse()