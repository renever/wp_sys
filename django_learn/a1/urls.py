from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('a1.views',
    # Examples:
    # url(r'^$', 'django_learn.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'a1_index',name='a1_index'),
    url(r'a2/', 'a2',name='a2'),


)
