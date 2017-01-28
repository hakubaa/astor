from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.http import HttpResponse


User = get_user_model()


def login_user(request):
    user = User.objects.filter(username="spider").first()
    if not user:
        user = User.objects.create_user(username="spider", password="spider")
    login(request, user)
    return HttpResponse()