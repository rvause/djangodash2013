from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from suggestions.models import Suggestion

from .models import Achievement, UserAchievement


User = get_user_model()


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='test',
            email='test@example.com',
            password='test'
        )
        self.achievement = Achievement.objects.create(
            name='Test Achievement',
            slug='test-achievement',
            description='A test achievement',
            check=Achievement.ACTIONED,
            count=1
        )


class AchievementModelTests(BaseTestCase):
    def test_str(self):
        self.assertEqual(str(self.achievement), 'Test Achievement')


class UserAchievementModelTests(BaseTestCase):
    def setUp(self):
        super(UserAchievementModelTests, self).setUp()
        self.ua = UserAchievement.objects.create(
            user=self.user,
            achievement=self.achievement
        )

    def test_defaults(self):
        self.assertEqual(self.ua.achieved_on.date(), timezone.now().date())

    def test_actioned_receiver(self):
        suggestion = Suggestion.objects.create(
            text='Test Suggestion',
            slug='test-suggestion'
        )
        suggestion.actioned_by.add(self.user)
        self.assertIn(self.achievement, self.user.achievement_set.all())
