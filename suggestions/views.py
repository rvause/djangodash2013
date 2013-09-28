import json

from django.views.generic import DetailView, ListView
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Suggestion


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
                    json.dumps({'suggestion': str(ctx['object'])}),
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


class UserView(LoginRequiredMixin, ListView):
    """
    The logged in user's view
    """
    template_name = 'suggestions/user.html'

    def get_queryset(self):
        queryset = self.request.user.suggestions.all()[:10]
        if not queryset:
            pass
