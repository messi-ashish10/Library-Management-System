from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse

# Create your views here.

def home(request):
    return render(request, 'library/home.html')

# Login view
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse("Invalid credentials")
    return render(request, 'library/login.html')

# Logout view
def logout_view(request):
    logout(request)
    return render(request, 'library/logout.html')

# Register view
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'library/register.html', {'form': form})

# About view
def about_view(request):
    return render(request, 'library/about.html')

# Contact view
def contact_view(request):
    if request.method == "POST":
        # Handle form submission here
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        # Save the message to the database or send an email
        return HttpResponse("Thank you for reaching out to us!")
    return render(request, 'library/contact.html')
