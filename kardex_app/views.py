from django.shortcuts import render, redirect
from .models import *


# Create your views here.
def home(request):
    return render(request, 'kardex_app/main.html')


# Authentication
def register(request):
    return render(request, 'kardex_app/Authentication/register.html')

def signIn(request):
    return render(request, 'kardex_app/Authentication/signIn.html')

def changePassword(request):
    return render(request, 'kardex_app/Authentication/changePassword.html')

def forgotPassword(request):
    return render(request, 'kardex_app/Authentication/forgotPassword.html')

# End of Authentication


#Kardex
def dashboard(request):
    kardexs = Kardex.objects.all()
    data = {"kardexs": kardexs}

    return render(request, 'kardex_app/Kardex/dashboard.html', data)


#End of Kardex




#Generate Reports


#End of Generate Reports