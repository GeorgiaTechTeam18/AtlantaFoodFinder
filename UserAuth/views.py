from django.contrib.auth.context_processors import auth
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

User = get_user_model()
def home(request):
    return render(request,'UserAuth/index.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['password2']


        user = User.objects.create_user(username, email, password)

        user.save()

        messages.success(request, f'Account created for {first_name} {last_name}!')
        return redirect('signin')

    return render(request,'UserAuth/register.html')


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
    return render(request,'UserAuth/logout.html')

