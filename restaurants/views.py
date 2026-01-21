# restaurants/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def custom_login(request):
    error = None
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('/admin/')  # redirect to admin dashboard
        else:
            error = "Invalid username or password"
    return render(request, 'login.html', {'error': error})
