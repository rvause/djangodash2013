from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


class Achievement(models.Model):
    """
    Achievement model to configure and store achievements of users
    """
    ACTIONED, LIKED, SUBMITTED = (
        'suggestions_actioned',
        'suggestions_liked',
        'suggestions_submitted'
    )
    CHECK_CHOICES = (
        (ACTIONED, _('Completed')),
        (LIKED, _('Liked')),
        (SUBMITTED, _('Submitted'))
    )

    # Details of the achievement
    name = models.CharField(
        _('name'),
        max_length=50,
        help_text=_('Display name for the achievement')
    )
    slug = models.SlugField(
        _('slug'),
        max_length=60,
        unique=True,
        help_text=_('A friendly identifier for the achievement in urls')
    )
    description = models.CharField(
        _('description'),
        max_length=255,
        help_text=_('A short description of the achievement')
    )

    # Definition of achievement
    check = models.CharField(
        _('check relation'),
        max_length=50,
        choices=CHECK_CHOICES,
        help_text=_('The relation you wish to total up')
    )
    count = models.PositiveIntegerField(
        _('count'),
        help_text=_('The count required in to achieve this')
    )

    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('users'),
        through='UserAchievement',
        help_text=_('Users that have achieved this')
    )

    class Meta:
        app_label = 'achievements'
        ordering = ['check', 'count']
        verbose_name=_('achievement')
        verbose_name_plural=_('achievements')

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """
    Store extra data for the user's relationship with Achievement
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='achievements'
    )
    achievement = models.ForeignKey(Achievement)
    achieved_on = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'achievements'
        ordering = ['-achieved_on']
