from django.db import models
from django.db.models.query import QuerySet
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class SuggestionQuerySet(QuerySet):
    """
    Provide custom queryset methods for Suggestions
    """
    def public(self):
        return self.filter(public=True)


class SuggestionManager(models.Manager):
    """
    Provides custom methods for Suggestion.objects
    """
    use_for_related_fields = True

    def get_query_set(self):
        return SuggestionQuerySet(self.model, using=self._db)

    def public(self):
        return self.get_query_set().public()


class Suggestion(models.Model):
    """
    Stores the suggestions for the site, the only data that drives it really.
    """
    text = models.CharField(
        _('text'),
        max_length=255,
        help_text=_('The actual text content for the suggestion')
    )

    # When a user it logged in they can mark the suggestion as done or skipped
    actioned_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('actioned by'),
        related_name='suggestions_actioned',
        help_text=_('Users that have actioned the suggestion'),
        blank=True
    )
    skipped_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('skipped by'),
        related_name='suggestions_skipped',
        help_text=_('Users that skipped the suggestion'),
        blank=True
    )
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('liked by'),
        related_name='suggestions_liked',
        help_text=_('Users that liked the suggestion'),
        blank=True
    )

    # Used if we add functionality for user's to submit suggestions
    public = models.BooleanField(
        _('public'),
        default=True,
        help_text=_('If this is checked then the suggestion is public')
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('submitted by'),
        related_name='suggestions_submitted',
        help_text=_('The user that submitted this suggestion'),
        null=True
    )

    objects = SuggestionManager()

    class Meta:
        app_label = 'suggestions'
        ordering = ['text']
        verbose_name = _('suggestion')
        verbose_name_plural = _('suggestions')

    def __str__(self):
        return self.text
