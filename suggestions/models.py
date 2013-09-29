from django.db import models
from django.db.models.query import QuerySet
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured


class SuggestionQuerySet(QuerySet):
    """
    Provide custom queryset methods for Suggestions
    """
    def public(self):
        return self.filter(public=True)

    def get_random_for_user(self, user):
        # First see if we can get a suggestion the user never used before
        try:
            return self.exclude(actioned_by__in=[user]).order_by('?')[0]
        except IndexError:
            # Then we try and get a suggestion they did not get recently
            try:
                return self.exclude(
                    pk__in=[
                        s.suggestion.id for s in user.suggestions.all()[:10]
                    ]
                )[0]
            except IndexError:
                # Then we just try and get anything
                try:
                    return self.order_by('?')[0]
                except IndexError:
                    raise ImproperlyConfigured('No suggestions are installed')


class SuggestionManager(models.Manager):
    """
    Provides custom methods for Suggestion.objects
    """
    use_for_related_fields = True

    def get_query_set(self):
        return SuggestionQuerySet(self.model, using=self._db)

    def public(self):
        return self.get_query_set().public()

    def get_random_for_user(self, user):
        return self.get_query_set().get_random_for_user(user)


class Suggestion(models.Model):
    """
    Stores the suggestions for the site, the only data that drives it really.
    """
    text = models.CharField(
        _('text'),
        max_length=255,
        help_text=_('The actual text content for the suggestion')
    )
    slug = models.SlugField(
        _('slug'),
        max_length=255,
        unique=True,
        help_text=_('A friendly identifier for the suggestion used in urls')
    )

    # When a user it logged in they can mark the suggestion as done or skipped
    actioned_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('actioned by'),
        related_name='suggestions_actioned',
        help_text=_('Users that have actioned the suggestion'),
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
        return self.get_text()

    @models.permalink
    def get_absolute_url(self):
        return ('suggestions:suggestion', (), {'slug': self.slug})

    def get_text(self):
        return self.text.replace('{{them}}', 'them')

    def make_unique_slug(self):
        """
        Make a unique slug
        """
        slug = new_slug = slugify(self.text)
        counter = 0
        while True:
            try:
                obj = self.__class__.objects.get(slug=new_slug)
                if obj.id == self.id:
                    break
                counter += 1
                new_slug = '%s-%d' % (slug, counter)
            except self.__class__.DoesNotExist:
                break
        self.slug = new_slug


class SuggestionCopyManager(models.Manager):
    """
    Provides extra methods for SuggestionCopy.objects
    """
    use_for_related_fields = True

    def create_random_for_user(self, user):
        """
        Get a random suggestion and create it for the user
        """
        suggestion = Suggestion.objects.get_random_for_user(user)
        return self.create(suggestion=suggestion, user=user)

    def create_from_suggestion_for_user(self, suggestion, user):
        return self.create(suggestion=suggestion, user=user)


class SuggestionCopy(models.Model):
    """
    Copy of a suggestion that adds potential customisation of the them_text

    Implemented this way because it will make selecting suggestions for display
    a lot more simple
    """
    suggestion = models.ForeignKey(Suggestion)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='suggestions'
    )
    # This can be blank if it is not really customised
    them_text = models.CharField(max_length=50, blank=True)

    created_on = models.DateTimeField(default=timezone.now)

    objects = SuggestionCopyManager()

    class Meta:
        app_label = 'suggestions'
        ordering = ['-created_on']
        verbose_name = _('suggestion copy')
        verbose_name_plural = _('suggestion copy')

    def __str__(self):
        return self.get_text()

    def get_suggestion_url(self):
        return self.suggestion.get_absolute_url()

    @models.permalink
    def get_actioned_url(self):
        return ('suggestions:actioned', (), {'id': self.id})

    @models.permalink
    def get_put_back_url(self):
        return ('suggestions:put_back', (), {'id': self.id})

    @models.permalink
    def get_like_url(self):
        return ('suggestions:like', (), {'id': self.id})

    @models.permalink
    def get_update_text_url(self):
        return ('suggestions:update_text', (), {'id': self.id})

    def get_text(self):
        if self.them_text:
            return self.suggestion.text.replace('{{them}}', self.them_text)
        return self.suggestion.get_text()

    def _get_data(self):
        return {
            'id': self.id,
            'text': self.get_text(),
            'likes': self.suggestion.liked_by.count(),
            'actions': self.suggestion.actioned_by.count(),
            'urls': {
                'suggestion': self.get_suggestion_url(),
                'actioned': self.get_actioned_url(),
                'put_back': self.get_put_back_url(),
                'like': self.get_like_url(),
                'update_text': self.get_update_text_url()
            }
        }

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = self._get_data()
        return self._data
