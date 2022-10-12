from django.shortcuts import render, redirect
from .models import *
from .forms import *

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


def createKardex(request):
    form = KardexForm()

    if(request.method == "POST"):
        form = KardexForm(request.POST)
        if(form.is_valid()):
            form.save()
            return redirect("/dashboard")

    data = {"form": form}
    return render(request, 'kardex_app/Kardex/createKardex.html', data)

def updateKardex(request, pk):
    kardex = Kardex.objects.get(id=pk)
    form = KardexForm(instance=kardex)

    if(request.method == "POST"):
        form = KardexForm(request.POST, instance=kardex)
        if(form.is_valid()):
            form.save()
            return redirect("/dashboard")

    data = {"form": form}
    return render(request, 'kardex_app/Kardex/updateKardex.html', data)

def viewKardex(request, pk):
    kardex = Kardex.objects.get(id=pk)
    data = {"kardex": kardex}
    return render(request, 'kardex_app/Kardex/viewKardex.html', data)


def deleteKardex(request, pk):
    kardex = Kardex.objects.get(id=pk)
    kardex.delete()
    return redirect("/dashboard")


#End of Kardex




#Generate Reports
def generateReports(request):
    return render(request, 'kardex_app/Generate Reports/generateReports.html')


#End of Generate Reports