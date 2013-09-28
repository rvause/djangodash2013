from django.test import TestCase

from .models import Suggestion


class SuggestionModelTest(TestCase):
    def setUp(self):
        self.suggestion = Suggestion.objects.create(text='How about this?')

    def test_str(self):
        self.assertEqual(str(self.suggestion), 'How about this?')

    def test_defaults(self):
        self.assertTrue(self.suggestion.public)

    def test_manager_public(self):
        self.assertTrue(Suggestion.objects.public().count())
        self.suggestion.public = False
        self.suggestion.save()
        self.assertFalse(Suggestion.objects.public().count())
