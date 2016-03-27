"""gensimserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.views.decorators.clickjacking import xframe_options_exempt

from .views import MyView, PageView, AnalyticView


urlpatterns = [
    url(r'^api/$', MyView.as_view()),
    # url(r'^votube/(?P<word>[a-zA-Z]+)/', PageView.as_view()),
    url(r'^votube/clip/$', PageView.as_view(template_name="controls/clip_player.html")),
    url(r'^votube/movie/$', PageView.as_view(template_name="controls/sidebar.html")),
    url(r'^votube/view/$', AnalyticView.as_view()),
    url(r'^votube/$', xframe_options_exempt(PageView.as_view(template_name="index.html"))),
]
