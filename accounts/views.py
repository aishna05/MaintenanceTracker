from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def signup_view(request):
    # If user is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation
        if not all([name, email, password, confirm_password]):
            messages.error(request, "All fields are required")
            return redirect('accounts:signup')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('accounts:signup')

        if User.objects.filter(username=email).exists():
            messages.error(request, "User already exists")
            return redirect('accounts:signup')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('accounts:signup')

        # Create user
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            
            # Log the user in
            login(request, user)
            messages.success(request, f"Welcome {name}! Your account has been created.")
            
            # Redirect to dashboard (without namespace if it's in root urls)
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return redirect('accounts:signup')

    return render(request, 'signup.html')


def login_view(request):
    # If user is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Email and password are required")
            return redirect('accounts:login')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            
            # Check if there's a 'next' parameter for redirect
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password")
            return redirect('accounts:login')

    return render(request, 'login.html')


@login_required(login_url='accounts:login')
def profile_view(request):
    """User profile view"""
    return render(request, 'profile.html', {'user': request.user})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect('accounts:login')