from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib import messages
from .forms import RegistrationForm
from django.contrib.auth.models import User

# Create your views here.
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('home')  # Redirect to a homepage or dashboard
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request=request,template_name='login/index.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Create user
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')  # Redirect to login page
        else:
            for error in form.errors:
                messages.error(request, form.errors[error])
    else:
        form = RegistrationForm()
    return render(request=request,template_name='registration/index.html')

def forgot_password(request):
    return render(request=request,template_name="forgot_password/index.html")

def reset_password(request,uuid):
    return render(request=request,template_name="reset_password/index.html")