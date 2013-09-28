from django.contrib import admin

from .models import Suggestion


class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'public')
    fields = ('text', 'public')
admin.site.register(Suggestion, SuggestionAdmin)
