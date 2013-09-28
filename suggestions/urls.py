from django.conf.urls import patterns, url

import views


urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^my/$', views.UserView.as_view(), name='users'),
    url(r'^my/skip/$', views.SkipSuggestionView.as_view(), name='skip'),
    url(
        r'^(?P<slug>[\w-]+)/$',
        views.SuggestionView.as_view(),
        name='suggestion'
    ),
    url(
        r'^my/(?P<id>\d+)/like/$',
        views.LikeSuggestionView.as_view(),
        name='like'
    ),
)
