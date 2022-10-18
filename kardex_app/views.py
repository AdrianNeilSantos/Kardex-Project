from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'kardex_app/main.html')


# Authentication
def register(request):
    form = NurseCreationForm()
    if( request.method == "POST"):
        form = NurseCreationForm(request.POST)
        if( form.is_valid() ):
            form.save()
            messages.success(request, "Account was created for "+form.cleaned_data.get("username"))
            return redirect('/sign-in')

    data = {"form": form}

    return render(request, 'kardex_app/authentication/register.html', data)

def signIn(request):
    if(request.method == "POST"):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        nurse = authenticate(request, username=username, password=password)
        
        if nurse is not None:
            login(request, nurse)
            print("Login Success.")
            return redirect('/')
        else:
            print("Login Fail.")
            messages.error(request, "Incorrect password or username.")

    return render(request, 'kardex_app/authentication/sign-in.html')

def signOut(request):
    logout(request)
    return redirect('sign-in')

def changePassword(request):
    return render(request, 'kardex_app/authentication/change-password.html')

def forgotPassword(request):
    return render(request, 'kardex_app/authentication/forgot-password.html')

# End of Authentication


#Kardex
def dashboard(request):
    kardexs = Kardex.objects.all()
    data = {"kardexs": kardexs}

    return render(request, 'kardex_app/kardex/dashboard.html', data)


def createKardex(request):
    form = KardexForm()
    if(request.method == "POST"):
        form = KardexForm(request.POST)
        if(form.is_valid()):
            form.save()
            return redirect("/dashboard")
    data = {"form": form}
    return render(request, 'kardex_app/kardex/create-kardex.html', data)

def updateKardex(request, pk):
    kardex = Kardex.objects.get(id=pk)
    form = KardexForm(instance=kardex)

    if(request.method == "POST"):
        form = KardexForm(request.POST, instance=kardex)
        if(form.is_valid()):
            form.save()
            return redirect("/dashboard")

    data = {"form": form}
    return render(request, 'kardex_app/kardex/update-kardex.html', data)

def viewKardex(request, pk):
    kardex = Kardex.objects.get(id=pk)
    data = {"kardex": kardex}
    return render(request, 'kardex_app/kardex/view-kardex.html', data)


def deleteKardex(request, pk):
    kardex = Kardex.objects.get(id=pk)
    kardex.delete()
    return redirect("/dashboard")


#End of Kardex


#Nurse

def nurseDashboard(request):
    nurses = Nurse.objects.all()
    data = {"nurses": nurses}
    return render(request, 'kardex_app/Nurse/dashboard.html', data)

def createNurse(request):
    form = NurseCreationForm()
    if(request.method == "POST"):
        form = NurseCreationForm(request.POST)
        if(form.is_valid()):
            form.save()
            return redirect("/nurse-dashboard")
    data = {"form": form}
    return render(request, 'kardex_app/Nurse/create-nurse.html', data)

def updateNurse(request, pk):
    nurse = Nurse.objects.get(id=pk)
    form = NurseUpdateForm(instance=nurse)

    if(request.method == "POST"):
        form = NurseUpdateForm(request.POST, instance=nurse)
        if(form.is_valid()):
            form.save()
            return redirect("/nurse-dashboard")

    data = {"form": form}
    return render(request, 'kardex_app/Nurse/update-nurse.html', data)

def viewNurse(request, pk):
    nurse = Nurse.objects.get(id=pk)
    data = {"nurse": nurse}
    return render(request, 'kardex_app/Nurse/view-nurse.html', data)


def deleteNurse(request, pk):
    nurse = Nurse.objects.get(id=pk)
    nurse.delete()
    return redirect("/nurse-dashboard")

#End of Nurse




#generate-reports
def generateReports(request):
    return render(request, 'kardex_app/generate-reports/generate-reports.html')


#End of generate-reports