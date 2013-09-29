import json

from django.views.generic import DetailView, ListView, View
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404

from .models import Suggestion, SuggestionCopy


class IndexView(DetailView):
    """
    The landing page for the site
    """
    model = Suggestion
    template_name = 'suggestions/index.html'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        try:
            return queryset.order_by('?')[0]
        except IndexError:
            raise ImproperlyConfigured('No suggestions are installed')

    def render_to_response(self, ctx, **kw):
        if 'format' in self.request.GET:
            if self.request.GET['format'] == 'json':
                return HttpResponse(
                    json.dumps(
                        {
                            'id': ctx['object'].id,
                            'suggestion': str(ctx['object']),
                            'url': ctx['object'].get_absolute_url()
                        }
                    ),
                    content_type='application/json'
                )
            return HttpResponseBadRequest('Format not supported')
        return super(IndexView, self).render_to_response(ctx, **kw)


class SuggestionView(DetailView):
    """
    A view for a single Suggestion
    """
    model = Suggestion


class LoginRequiredMixin(object):
    """
    Mixin to ensure a user is logged in; basically applies the login_required
    decorator from auth module.
    """
    @method_decorator(login_required)
    def dispatch(self, *ar, **kw):
        return super(LoginRequiredMixin, self).dispatch(*ar, **kw)


class GetSuggestionCopyQSMixin(object):
    """
    We want to get the 10 latest suggestions that the user has had copied
    or if there are none we create a new one.
    """
    def get_queryset(self):
        queryset = self.request.user.suggestions.all()[:10]
        if not queryset.count():
            SuggestionCopy.objects.create_random_for_user(self.request.user)
            return self.request.user.suggestions.all()[:10]
        return queryset


class UserView(LoginRequiredMixin, GetSuggestionCopyQSMixin, ListView):
    """
    The logged in user's view
    """
    template_name = 'suggestions/user.html'


class JSONResponseMixin(object):
    def render_to_response(self, ctx, **kw):
        return HttpResponse(json.dumps(ctx), 'application/json')


class SkipSuggestionView(
    LoginRequiredMixin,
    GetSuggestionCopyQSMixin,
    JSONResponseMixin,
    View
):
    """
    Skip over the current suggestion for the user and return a new suggestion
    """
    def get(self, request, *ar, **kw):
        self.get_queryset()[0].delete()
        queryset = self.get_queryset()
        return self.render_to_response({'suggestion': queryset[0].data})


class GetSuggestionCopySingleMixin(object):
    def get_queryset(self):
        queryset = self.request.user.suggestions.all()
        if not queryset.count():
            SuggestionCopy.objects.create_random_for_user(self.request.user)
            return self.request.user.suggestions.all()
        return queryset

    def get_object(self, id):
        return get_object_or_404(self.get_queryset(), pk=id)


class ActionSuggestionView(
    LoginRequiredMixin,
    GetSuggestionCopySingleMixin,
    JSONResponseMixin,
    View
):
    """
    Mark the current suggestion for the user as actioned and return a new
    suggestion
    """
    def get(self, request, *ar, **kw):
        obj = self.get_object(kw['id'])
        obj.suggestion.actioned_by.add(request.user)
        suggestion = SuggestionCopy.objects.create_random_for_user(
            request.user
        )
        return self.render_to_response({'suggestion': suggestion.data})


class LikeSuggestionView(
    LoginRequiredMixin,
    GetSuggestionCopySingleMixin,
    JSONResponseMixin,
    View
):
    """
    Mark a suggestion as liked by the user and return the amount of likes
    """
    def get(self, request, *ar, **kw):
        obj = self.get_object(kw['id'])
        obj.suggestion.liked_by.add(request.user)
        return self.render_to_response(
            {'likes': obj.suggestion.liked_by.count()}
        )

class PutBackView(
    LoginRequiredMixin,
    GetSuggestionCopySingleMixin,
    JSONResponseMixin,
    View
):
    """
    Put a crossed suggestion back to current by making a copy of it
    """
    def get(self, request, *ar, **kw):
        obj = self.get_object(kw['id'])
        self.get_queryset()[0].delete()
        suggestion = SuggestionCopy.objects.create_from_suggestion_for_user(
            obj.suggestion,
            request.user
        )
        return self.render_to_response({'suggestion': suggestion.data})


class UpdateTextView(
    LoginRequiredMixin,
    GetSuggestionCopySingleMixin,
    JSONResponseMixin,
    View
):
    """
    Update the text for "them" in the selected suggestion
    """
    def post(self, request, *ar, **kw):
        obj = self.get_object(kw['id'])
        if not 'text' in request.POST:
            return HttpResponseBadRequest('No text supplied')
        obj.them_text = request.POST['text']
        obj.save()
        return self.render_to_response({'status': 'success'})
