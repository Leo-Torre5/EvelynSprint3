# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from .forms import RegisterForm

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()

            # Get the new user info and set the group for this user to LibraryMember
            user = User.objects.get(username=form.cleaned_data['username'])
            lib_group = Group.objects.get(name='LibraryMember')
            user.groups.add(lib_group)
            user.save()

            return redirect('login')

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})
