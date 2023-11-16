from .models import AlbumInstance
from django import forms
from .models import Album
from .models import UserProfile
from django.contrib.auth.models import User



class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)


class LoanAlbumForm(forms.ModelForm):
    """Form for a librarian to loan albums."""
    album_title = forms.CharField(disabled=True, required=False)

    # Add a DateField for the due date
    due_back = forms.DateField(widget=forms.SelectDateWidget)

    class Meta:
        # Display only the album title, borrower, status, and due date to the librarian
        model = AlbumInstance
        fields = ('album_title', 'borrower', 'status', 'due_back',)


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'artist', 'summary', 'genre', 'copies_available', 'album_image']

# Create a UserUpdateForm to update a username and email

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image', 'first_name', 'last_name', 'address', 'city', 'state', 'zip']

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['image'].widget.attrs['class'] = 'form-control'
        self.fields['image'].label = ''  # Remove the label
        self.fields['image'].help_text = ''  # Remove the help text

    def as_crispy_field(self, *args, **kwargs):
        # Override the as_crispy_field method to remove the "Currently:" part
        return super().as_crispy_field(*args, **kwargs).replace("Currently:", "")
