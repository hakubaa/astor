from django.conf.urls import url

from astor4tests.views import login_user

app_name = "astor4tests"
urlpatterns = [
    url(r'login$', login_user, name="login_user"),
]
