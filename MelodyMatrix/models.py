from django.db import models
from django.urls import reverse  # Used to generate URLs by reversing the URL patterns
import uuid  # Required for unique album instances
from django.contrib.auth.models import User
from datetime import date
from django import forms
from django.db.models.signals import post_save
from django.dispatch import receiver


class Genre(models.Model):
    """Model representing an album genre."""
    name = models.CharField(max_length=200, help_text='Enter an album genre (e.g.Country)')

    def __str__(self):
        """String for representing the Model object."""
        return self.name



class Artist(models.Model):
    """Model representing an artist."""
    artist_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this artist')
    summary = models.TextField(max_length=2000, help_text='Enter a brief background of the artist', null=True)
    artist_image = models.ImageField(upload_to='images/', null=True, blank=True)


    class Meta:
        ordering = ['artist_name']

    def get_absolute_url(self):
        """Returns the URL to access a particular artist instance."""
        return reverse('artist_detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.artist_name}'


class Album(models.Model):
    """Model representing an Album."""
    title = models.CharField(max_length=200, null=True)

    # Foreign Key used because album can only have one artist, but artists can have many albums
    artist = models.ForeignKey('Artist', on_delete=models.RESTRICT, null=True)
    summary = models.TextField(max_length=2000, help_text='Enter a brief summary of the album', null=True)

    # ManyToManyField used because genre can contain many albums. Albums can cover many genres.
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this album')

    duration = models.DurationField(help_text='Enter the duration of the album')
    tracks = models.IntegerField(help_text='Select the number of tracks')
    copies_available = models.IntegerField(default=0, help_text='Number of copies available')
    album_image = models.ImageField(upload_to='images/', null=True, blank=True)

    class Meta:
        permissions = (("can_add_album_instance", "Can add album instances"),)

    def __str__(self):
        return self.title

    def __str__(self):
        """String for representing the Model object."""
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this album."""
        return reverse('album_detail', args=[str(self.id)])

class Song(models.Model):
    title = models.CharField(max_length=200)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs')

    def __str__(self):
        return self.title


class AlbumInstance(models.Model):
    """Model representing a specific copy of an album (that can be loaned from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular album across whole library')
    album = models.ForeignKey('Album', on_delete=models.RESTRICT, null=True)
    format = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    LOAN_STATUS = (
        ('a', 'Available'), ('o', 'On loan'), ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='a',
    )
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        """Determines if the album is overdue based on due date and current date."""
        return bool(self.due_back and date.today() > self.due_back)

    class Meta:
        ordering = ['due_back']

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id} ({self.album.title})'

    def return_album(self):
        self.LOAN_STATUS = 'a'  # Set status to 'Available'
        self.borrower = None  # Remove the borrower
        self.due_back = None  # Reset due_back date
        self.save()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    first_name = models.CharField(max_length=250, null=True)
    last_name = models.CharField(max_length=250, null=True)
    address = models.CharField(max_length=400, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=100, null=True)
    zip = models.IntegerField(null=True)

    def __str__(self):
        return f'{self.user.username} Profile'  # Display users name

# Automatically create a UserProfile when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Automatically save the UserProfile when a User is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()



