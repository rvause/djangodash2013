from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Suggestion


class TestCaseWithSuggestion(TestCase):
    def setUp(self):
        self.suggestion = Suggestion.objects.create(text='How about this?')


class SuggestionModelTests(TestCaseWithSuggestion):
    def test_str(self):
        self.assertEqual(str(self.suggestion), 'How about this?')

    def test_defaults(self):
        self.assertTrue(self.suggestion.public)

    def test_manager_public(self):
        self.assertTrue(Suggestion.objects.public().count())
        self.suggestion.public = False
        self.suggestion.save()
        self.assertFalse(Suggestion.objects.public().count())


class ViewsTests(TestCaseWithSuggestion):
    def test_index(self):
        url = reverse('suggestions:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['content-type'])
        response = self.client.get(url, {'format': 'json'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('application/json', response['content-type'])
