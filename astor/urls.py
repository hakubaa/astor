from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^account/', include("astoraccount.urls")),
    url(r'^', include("astormain.urls"))
]