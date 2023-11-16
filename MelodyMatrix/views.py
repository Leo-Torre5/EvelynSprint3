from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import LoanAlbumForm, AlbumForm, SearchForm, UserUpdateForm, ProfileUpdateForm  # Add UserUpdateForm here
import datetime
from django.shortcuts import redirect
from django.db.models import Count
from django.contrib.auth import get_user_model
from .models import UserProfile
from .models import Album, Artist, AlbumInstance, Genre, Song
from .forms import UserUpdateForm, ProfileUpdateForm
from django.http import Http404
from django.contrib.auth import get_user_model
from .models import UserProfile



def index(request):
    """View function for home page of the site."""
    num_albums = Album.objects.all().count()
    num_instances = AlbumInstance.objects.all().count()
    num_instances_available = AlbumInstance.objects.filter(status__exact='a').count()
    num_artists = Artist.objects.count() # Add this line to get the count of artists.

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1


    context = {
        'num_albums': num_albums,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_artists': num_artists,# Include num_artists in the context
        'num_visits': num_visits,}
    return render(request, 'MelodyMatrix/index.html', context=context)


def artist_list(request):
    artists = Artist.objects.all()  # Replace with your actual query
    return render(request, 'MelodyMatrix/artist_list.html', {'artist_list': artists})


def artist_detail(request, artist_id):
    artist = Artist.objects.get(pk=artist_id)
    return render(request, 'MelodyMatrix/artist_detail.html', {'artist': artist})


def all_genres(request):
    genres = Genre.objects.all()
    return render(request, 'MelodyMatrix/all_genres.html', {'genres': genres})


def genre_detail(request, pk):
    genre = get_object_or_404(Genre, pk=pk)
    artists = Artist.objects.filter(genre=genre)
    albums = Album.objects.filter(genre=genre)

    context = {
        'genre': genre,
        'artists': artists,
        'albums': albums,
    }

    return render(request, 'MelodyMatrix/genre_detail.html', context)


class AlbumListView( generic.ListView):
    model = Album

class AlbumDetailView(generic.DetailView):
    model = Album

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_copies'] = self.object.albuminstance_set.filter(status='a')
        return context


class ArtistListView( generic.ListView):
    model = Artist



class ArtistDetailView(generic.DetailView):
    model = Artist


class LoanedAlbumsByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing albums on loan or reserved to the current user."""
    model = AlbumInstance
    template_name = 'MelodyMatrix/my_vinyl.html'
    paginate_by = 10

    def get_queryset(self):
        return AlbumInstance.objects.filter(borrower=self.request.user, status__in=['o', 'r']).order_by('due_back')


class ArtistCreate(CreateView):
    model = Artist
    fields = ['artist_name', 'summary', 'genre', 'artist_image']

    def form_valid(self, form):
        post = form.save(commit=False)
        post.save()
        return HttpResponseRedirect(reverse('artist_list'))

class ArtistUpdate(UpdateView):
    model = Artist
    fields = ['artist_name', 'summary', 'genre', 'artist_image']

    def form_valid(self, form):
        post = form.save(commit=False)
        post.save()
        return HttpResponseRedirect(reverse('artist_list'))

class AlbumCreate(CreateView):
    model = Album
    form_class = AlbumForm  # Use the new form class
    template_name = 'MelodyMatrix/album_form.html'

    def form_valid(self, form):
        # You can add any additional logic here if needed
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('album_list')  # Update with your actual URL for the list of albums

class AlbumUpdate(UpdateView):
    model = Album
    form_class = AlbumForm  # Use the new form class
    template_name = 'MelodyMatrix/album_form.html'

    def form_valid(self, form):
        # You can add any additional logic here if needed
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('album_list')  # Update with your actual URL for the list of albums


def artist_delete(request, pk):
    artist = get_object_or_404(Artist, pk=pk)

    try:
        artist_name = artist.artist_name
        artist.delete()
        messages.success(request, f'{artist_name} has been deleted')
    except:
        messages.error(request, f'{artist.artist_name} cannot be deleted. Albums exist for this artist')

    return redirect('artist_list')


def album_delete(request, pk):
    album = get_object_or_404(Album, pk=pk)

    try:
        album_title = album.title
        album.delete()
        messages.success(request, f'{album_title} has been deleted')
    except ProtectedError:
        messages.error(request, f'{album.title} cannot be deleted. Artists exist for this album')

    return redirect('album_list')


class AvailAlbumsListView(generic.ListView):
    model = AlbumInstance
    template_name = 'MelodyMatrix/albuminstance_list_available.html'
    paginate_by = 10

    def get_queryset(self):
        return AlbumInstance.objects.all().order_by('album__title')



def loan_album_librarian(request, pk):
    album_instance = get_object_or_404(AlbumInstance, pk=pk)

    if request.method == 'POST':
        form = LoanAlbumForm(request.POST, instance=album_instance)

        if form.is_valid():
            # Retrieve the due_back from the form
            due_back = form.cleaned_data['due_back']

            # Update the AlbumInstance fields
            album_instance = form.save(commit=False)
            album_instance.due_back = due_back
            album_instance.LOAN_STATUS = 'o'  # Update the status to 'On loan'
            album_instance.save()

            return HttpResponseRedirect(reverse('all_available'))

    else:
        form = LoanAlbumForm(instance=album_instance,
                             initial={'album_title': album_instance.album.title,
                                      'due_back': album_instance.due_back})

    return render(request, 'MelodyMatrix/loan_album_librarian.html', {'form': form})


def return_album(request, pk):
    album_instance = get_object_or_404(AlbumInstance, pk=pk)

    if request.method == 'POST':
        form = LoanAlbumForm(request.POST, instance=album_instance)

        if form.is_valid():
            # Instead of using the form data, directly update the model instance
            status = form.cleaned_data['status']

            if status == 'a':
                album_instance.status = 'a'
                album_instance.borrower = None
                album_instance.due_back = None
                album_instance.save()
                messages.success(request, f'Album "{album_instance.album.title}" has been returned.')
            else:
                album_instance.status = 'o'
                album_instance.borrower = form.cleaned_data['borrower']
                album_instance.due_back = datetime.date.today() + datetime.timedelta(weeks=4)
                album_instance.save()
                messages.success(request, f'Album "{album_instance.album.title}" has been loaned to {album_instance.borrower.username}.')

            return redirect('all_available')

    else:
        # Set the default status in the model instance
        album_instance.status = 'a'
        album_instance.save()

        form = LoanAlbumForm(instance=album_instance, initial={'album_title': album_instance.album.title})

    return render(request, 'MelodyMatrix/return_album.html', {'form': form, 'album_instance': album_instance})


def search_view(request):
    query = request.GET.get('query')

    if query:
        # Perform your search logic here
        artists = Artist.objects.filter(artist_name__icontains=query)
        albums = Album.objects.filter(title__icontains=query)
        genres = Genre.objects.filter(name__icontains=query)
        songs = Song.objects.filter(title__icontains=query)

        # Get the albums for the songs
        song_albums = [song.album for song in songs]

        context = {
            'query': query,
            'artists': artists,
            'albums': albums,
            'genres': genres,
            'songs': zip(songs, song_albums),
        }
    else:
        context = {'query': None}

    return render(request, 'search_results.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user after registration

            # Create a UserProfile for the new user
            UserProfile.objects.create(user=user)

            return redirect('index')
    else:
        form = UserCreationForm()

    return render(request, 'register/register.html', {'form': form})






def profile(request):
    User = get_user_model()

    # Ensure there is a UserProfile instance for the user
    if not hasattr(request.user, 'userprofile'):
        UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.userprofile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }

    return render(request, 'profile.html', context)

def view_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    context = {'user_profile': user_profile}
    return render(request, 'view_profile.html', context)

