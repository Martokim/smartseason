from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('fields:dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('fields:dashboard')
        error = 'Invalid username or password.'

    return render(request, 'users/login.html', {'error': error})


@login_required
def logout_view(request):
    logout(request)
    return redirect('users:login')