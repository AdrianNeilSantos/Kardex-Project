from django.shortcuts import render, redirect

# Create your views here.
def home(request):
    return render(request, 'kardex_app/main.html')


# Authentication Thingz
def register(request):
    return render(request, 'kardex_app/Authentication/register.html')

def signIn(request):
    return render(request, 'kardex_app/Authentication/signIn.html')

def changePassword(request):
    return render(request, 'kardex_app/Authentication/changePassword.html')

def forgotPassword(request):
    return render(request, 'kardex_app/Authentication/forgotPassword.html')

# End of Authentication Thingz