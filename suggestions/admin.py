from django.contrib import admin

from .models import Suggestion
from .forms import SuggestionAdminForm


class SuggestionAdmin(admin.ModelAdmin):
    form = SuggestionAdminForm
    list_display = ('__str__', 'public')
    fields = ('text', 'slug', 'public')
    prepopulated_fields = {'slug': ('text',)}
    list_filter = ('public',)
    search_fields = ('text',)
admin.site.register(Suggestion, SuggestionAdmin)
