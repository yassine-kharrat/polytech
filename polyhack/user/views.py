from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, LoginForm
from .models import User
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type')

        # Validate passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'register.html')

        # Validate user type
        if user_type not in ['teacher', 'student']:
            messages.error(request, "Invalid user type.")
            return render(request, 'register.html')

        try:
            # Create and save the user
            user = User.objects.create_user(
                email=email,
                name=name,
                password=password,
                user_type=user_type
            )
            login(request, user)
            messages.success(request, f"Registration successful! You are now logged in as a {user_type}.")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return render(request, 'register.html')

    return render(request, 'register.html')


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.name}!")
            return redirect('/')  # Redirect to home page
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'login.html')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {'user': request.user})

def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('/')