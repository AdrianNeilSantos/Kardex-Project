from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
# for email
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string






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

    return render(request, 'kardex_app/Authentication/register.html', data)

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

    return render(request, 'kardex_app/Authentication/sign-in.html')

def signOut(request):
    logout(request)
    return redirect('sign-in')

def changePassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/password-change')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    data = {
      "form": form,
    }

    return render(request, 'kardex_app/Authentication/password-change.html', data)


def forgotPassword(request):
    return render(request, 'kardex_app/Authentication/password-forgot.html')

def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = Nurse.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = 'kardex_app/Authentication/password-reset-email.html'
					c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'saianph1@gmail.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect ("/password-reset/done/")
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name='kardex_app/Authentication/password-reset.html', context={"password_reset_form":password_reset_form})

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