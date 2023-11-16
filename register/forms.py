from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  # Import User model from django.contrib.auth.models
from MelodyMatrix.models import UserProfile

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=250, required=False)
    last_name = forms.CharField(max_length=250, required=False)
    address = forms.CharField(max_length=400, required=False)
    city = forms.CharField(max_length=200, required=False)
    state = forms.CharField(max_length=100, required=False)
    zip = forms.IntegerField(required=False)

    class Meta:
        model = User  # Correctly reference the User model
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'address', 'city', 'state', 'zip']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        # Check if a UserProfile already exists for the user
        try:
            profile = user.userprofile
            # If the profile exists, update its fields
            profile.address = self.cleaned_data['address']
            profile.city = self.cleaned_data['city']
            profile.state = self.cleaned_data['state']
            profile.zip = self.cleaned_data['zip']
            profile.save()
        except UserProfile.DoesNotExist:
            # If the profile doesn't exist, create a new one
            UserProfile.objects.create(
                user=user,
                address=self.cleaned_data['address'],
                city=self.cleaned_data['city'],
                state=self.cleaned_data['state'],
                zip=self.cleaned_data['zip']
            )

        return user
