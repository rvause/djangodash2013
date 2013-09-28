from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Suggestion, SuggestionCopy


User = get_user_model()


class TestCaseWithSuggestion(TestCase):
    def setUp(self):
        self.suggestion = Suggestion.objects.create(
            text='How about this for {{them}}?',
            slug='how-about-this-for-them'
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
        self.user = User.objects.create_user(
            username='test',
            email='test@example.com',
            password='test'
        )
        self.copy = SuggestionCopy(
            suggestion=self.suggestion,
            user=self.user
        )

    def test_str(self):
        self.assertEqual(str(self.copy), str(self.suggestion))

    def test_defaults(self):
        self.assertEqual(timezone.now().date(), self.copy.created_on.date())

    def test_get_text(self):
        self.assertEqual(self.copy.get_text(), self.suggestion.get_text())
        self.copy.them_text = 'him'
        self.assertEqual(self.copy.get_text(), 'How about this for him?')


class ViewsTests(TestCaseWithSuggestion):
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
