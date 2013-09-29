from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from suggestions.models import Suggestion


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


@receiver(m2m_changed, sender=Suggestion.actioned_by.through)
def actioned_receiver(sender, instance, action, **kw):
    if action == 'post_add':
        for id in kw['pk_set']:
            user = instance.actioned_by.get(pk=id)
            qs = Achievement.objects.filter(
                check=Achievement.ACTIONED,
                count__lte=user.suggestions_actioned.count(),
            )
            if qs.exists():
                for achievement in qs:
                    UserAchievement.objects.create(
                        user=user,
                        achievement=achievement
                    )


@receiver(m2m_changed, sender=Suggestion.liked_by.through)
def liked_receiver(sender, instance, action, **kw):
    if action == 'post_add':
        for id in kw['pk_set']:
            user = instance.liked_by.get(pk=id)
            qs = Achievement.objects.filter(
                check=Achievement.LIKED,
                count__lte=user.suggestions_liked.count()
            )
            if qs.exists():
                for achievement in qs:
                    UserAchievement.objects.create(
                        user=user,
                        achievement=achievement
                    )


@receiver(post_save, sender=Suggestion)
def submitted_receiver(sender, instance, **kw):
    if not instance.public and instance.submitted_by:
        qs = Achievement.objects.filter(
            check=Achievement.SUBMITTED,
            count__lte=instance.submitted_by.suggestions_submitted.count()
        )
        if qs.exists():
            for achievement in qs:
                UserAchievement.objects.create(
                    user=instance.submitted_by,
                    achievement=achievement
                )
