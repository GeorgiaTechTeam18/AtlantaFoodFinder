

from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from verify_email.email_handler import send_verification_email

from django.contrib import messages

from .models import Review

User = get_user_model()
def home(request):
    return render(request,'UserAuth/index.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Send verification email and create user
                inactive_user = send_verification_email(request, form)
                messages.success(request, 'Please verify your email address to complete registration.')
                return redirect('signin')
            except Exception as e:
                messages.error(request, f'Error sending email: {e}')
                return redirect('register')
    else:
        form = RegistrationForm()

    return render(request, 'UserAuth/register.html', {'form': form})


def signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Try to get the user object based on email
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home page after successful login
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('signin')

    return render(request, 'UserAuth/login.html')

def signout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return render(request,'UserAuth/logout.html')

def profile(request):
    reviews = Review.objects.filter(user=request.user)
    return render(request, 'UserAuth/profile.html', {'reviews': reviews})

