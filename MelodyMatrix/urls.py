from django.urls import path
from . import views
from .views import return_album
from django.contrib import admin
from django.urls import path, include
from .views import search_view
from .views import profile
from .views import genre_detail, all_genres
from .views import view_profile

urlpatterns = [
        path('', views.index, name='index'),
        path('album_list/', views.AlbumListView.as_view(), name='album_list'),
        path('album_detail/<int:pk>', views.AlbumDetailView.as_view(), name='album_detail'),
        path('artists_list/', views.artist_list, name='artist_list'),
        path('artist_detail/<int:pk>', views.ArtistDetailView.as_view(), name='artist_detail'),
        path('my_vinyl/', views.LoanedAlbumsByUserListView.as_view(), name='my_vinyl'),
        path('artist/create/', views.ArtistCreate.as_view(), name='artist_create'),
        path('artist/<int:pk>/update/', views.ArtistUpdate.as_view(), name='artist_update'),
        path('artist/<int:pk>/delete/', views.artist_delete, name='artist_delete'),
        path('album/create/', views.AlbumCreate.as_view(), name='album_create'),
        path('album/<int:pk>/update/', views.AlbumUpdate.as_view(), name='album_update'),
        path('album/<int:pk>/delete/', views.album_delete, name='album_delete'),
        path('album/<uuid:pk>/loan/', views.loan_album_librarian, name='loan_album_librarian'),
        path('available/', views.AvailAlbumsListView.as_view(), name='all_available'),
        path('albuminstance/<uuid:pk>/return/', return_album, name='return_album'),
        path('user-management/', include('user_management.urls')),
        path('register/', include('register.urls')),
        path('search/', search_view, name='search'),
        path('profile/', profile, name='profile'),
        path('genre/<int:pk>/', genre_detail, name='genre_detail'),
        path('all_genres/', all_genres, name='all_genres'),
        path('view_profile/', view_profile, name='view_profile'),

]
