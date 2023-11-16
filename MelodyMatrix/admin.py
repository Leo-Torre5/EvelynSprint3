from django.contrib import admin
from .models import Album, Song, Artist, Genre, AlbumInstance
from .models import UserProfile

class AlbumInstanceInline(admin.TabularInline):
    model = AlbumInstance
    extra = 1  # Number of empty forms to display


class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'copies_available', ]  # Add copies_available to the list view
    inlines = [AlbumInstanceInline]  # Add the AlbumInstanceInline


admin.site.register(Artist)
admin.site.register(Genre)
admin.site.register(Song)
admin.site.register(UserProfile)


@admin.register(AlbumInstance)
class AlbumInstanceAdmin(admin.ModelAdmin):
    list_display = ('album', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('album', 'format', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )

# Register the Album model with the custom admin class
admin.site.register(Album, AlbumAdmin)