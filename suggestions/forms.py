from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Suggestion


class SuggestionAdminForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ('text', 'slug', 'public')

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        queryset = Suggestion.objects.all()
        if self.instance.id:
            queryset = queryset.exclude(pk=self.instance.id)
        try:
            queryset.get(slug=slug)
            raise forms.ValidationError(_('Please create a unique slug'))
        except:
            pass
        return slug


class AddSuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ('text',)

    def save(self, user, commit=True):
        obj = super(AddSuggestionForm, self).save(commit=False)
        obj.public = False
        obj.make_unique_slug()
        obj.submitted_by = user
        if commit:
            obj.save()
        return obj
