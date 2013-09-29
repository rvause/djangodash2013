import json

from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from django.views.generic import View
from django.http import HttpResponse

from .models import Suggestion, SuggestionCopy
from .views import LoginRequiredMixin, JSONResponseMixin


User = get_user_model()


class TestCaseWithSuggestion(TestCase):
    def setUp(self):
        self.suggestion = Suggestion.objects.create(
            text='How about this for {{them}}?',
            slug='how-about-this-for-them'
        )
        self.user = User.objects.create_user(
            username='test',
            email='test@example.com',
            password='test'
        )


class SuggestionModelTests(TestCaseWithSuggestion):
    def test_str(self):
        self.assertEqual(str(self.suggestion), 'How about this for them?')

    def test_defaults(self):
        self.assertTrue(self.suggestion.public)

    def test_manager_public(self):
        self.assertTrue(Suggestion.objects.public().count())
        self.suggestion.public = False
        self.suggestion.save()
        self.assertFalse(Suggestion.objects.public().count())

    def test_manager_get_random_for_user(self):
        suggestion_2 = Suggestion.objects.create(
            text='How about that for {{them}}?',
            slug='how-about-that-for-them'
        )
        self.assertIn(
            Suggestion.objects.get_random_for_user(self.user),
            [self.suggestion, suggestion_2]
        )
        self.suggestion.actioned_by.add(self.user)
        # Would fail at least sometimes
        self.assertEqual(
            Suggestion.objects.get_random_for_user(self.user),
            suggestion_2
        )
        suggestion_2.actioned_by.add(self.user)
        # Hopefully would fail if it is run enough
        self.assertIn(
            Suggestion.objects.get_random_for_user(self.user),
            [self.suggestion, suggestion_2]
        )

    def test_get_text(self):
        self.assertEqual(
            self.suggestion.get_text(),
            'How about this for them?'
        )

    def test_make_unique_slug(self):
        self.suggestion.make_unique_slug()
        self.assertEqual(self.suggestion.slug, 'how-about-this-for-them')
        suggestion = Suggestion(text='How about this for them?')
        suggestion.make_unique_slug()
        self.assertEqual(suggestion.slug, 'how-about-this-for-them-1')


class SuggestionCopyModelTests(TestCaseWithSuggestion):
    def setUp(self):
        super(SuggestionCopyModelTests, self).setUp()
        self.copy = SuggestionCopy(
            suggestion=self.suggestion,
            user=self.user
        )

    def test_str(self):
        self.assertEqual(str(self.copy), str(self.suggestion))

    def test_defaults(self):
        self.assertEqual(timezone.now().date(), self.copy.created_on.date())

    def test_create_random_for_user_manager(self):
        copy = SuggestionCopy.objects.create_random_for_user(self.user)
        self.assertTrue(isinstance(copy, SuggestionCopy))
        self.assertEqual(copy.suggestion, self.suggestion)

    def test_create_from_suggestion_for_user_manager(self):
        copy = SuggestionCopy.objects.create_from_suggestion_for_user(
            self.suggestion,
            self.user
        )
        self.assertTrue(isinstance(copy, SuggestionCopy))
        self.assertEqual(copy.suggestion, self.suggestion)

    def test_get_text(self):
        self.assertEqual(self.copy.get_text(), self.suggestion.get_text())
        self.copy.them_text = 'him'
        self.assertEqual(self.copy.get_text(), 'How about this for him?')


class ViewMixinTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_login_required_mixin(self):
        class TestView(LoginRequiredMixin, View):
            def get(self, request, *ar, **kw):
                return HttpResponse('Okay')
        request = self.factory.get('/test-view/')
        request.user = AnonymousUser()
        response = TestView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        request.user = User(username='test', email='test@example.com')
        response = TestView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_json_response_mixin(self):
        class TestView(JSONResponseMixin, View):
            def get(self, request, *ar, **kw):
                return self.render_to_response({'this': 'that'})
        request = self.factory.get('/test-view/')
        response = TestView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '{"this": "that"}')
        self.assertEqual(response['content-type'], 'application/json')


class ViewsTests(TestCaseWithSuggestion):
    def login(self):
        self.client.login(username=self.user.username, password='test')

    def test_index(self):
        url = reverse('suggestions:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['content-type'])
        response = self.client.get(url, {'format': 'json'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('application/json', response['content-type'])

    def test_suggestion(self):
        url = self.suggestion.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_users(self):
        self.login()
        url = reverse('suggestions:users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['object_list'].count())

    def test_skip(self):
        self.login()
        url = reverse('suggestions:skip')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_actioned(self):
        self.login()
        copy = SuggestionCopy.objects.create(
            suggestion=self.suggestion,
            user=self.user
        )
        url = reverse('suggestions:actioned', args=(copy.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.suggestion, self.user.suggestions_actioned.all())

    def test_like(self):
        self.login()
        copy = SuggestionCopy.objects.create(
            suggestion=self.suggestion,
            user=self.user
        )
        url = reverse('suggestions:like', args=(copy.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['likes'], 1)

    def test_put_back(self):
        self.login()
        copy = SuggestionCopy.objects.create(
            suggestion=self.suggestion,
            user=self.user
        )
        url = reverse('suggestions:put_back', args=(copy.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertNotEqual(data['suggestion']['id'], copy.id)

    def test_update_text(self):
        self.login()
        copy = SuggestionCopy.objects.create(
            suggestion=self.suggestion,
            user=self.user
        )
        url = reverse('suggestions:update_text', args=(copy.id,))
        response = self.client.post(url, {'text': 'him'})
        self.assertEqual(response.status_code, 200)
        copy = SuggestionCopy.objects.get(pk=copy.id)
        self.assertEqual(copy.them_text, 'him')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
