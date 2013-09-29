from django.conf.urls import patterns, url

import views


urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^my/$', views.UserView.as_view(), name='users'),
    url(r'^my/add/$', views.AddSuggestionView.as_view(), name='add'),
    url(r'^my/skip/$', views.SkipSuggestionView.as_view(), name='skip'),
    url(
        r'^(?P<slug>[\w-]+)/$',
        views.SuggestionView.as_view(),
        name='suggestion'
    ),
    url(
        r'^my/(?P<id>\d+)/actioned/$',
        views.ActionSuggestionView.as_view(),
        name='actioned'
    ),
    url(
        r'^my/(?P<id>\d+)/put-back/$',
        views.PutBackView.as_view(),
        name='put_back'
    ),
    url(
        r'^my/(?P<id>\d+)/like/$',
        views.LikeSuggestionView.as_view(),
        name='like'
    ),
    url(
        r'^my/(?P<id>\d+)/update-text/$',
        views.UpdateTextView.as_view(),
        name='update_text'
    ),
)
