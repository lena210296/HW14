from django.contrib import admin

from .models import Author, Quote


class QuoteAdmin(admin.ModelAdmin):
    list_display = ['content', 'author']
    list_filter = ['content']
    search_fields = ['content', 'author__name']


admin.site.register(Quote, QuoteAdmin)

admin.site.register(Author)
