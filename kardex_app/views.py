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

from django.utils import timezone

import datetime
import pytz

def splitToLists(query_dict):
    list_keys = [
        'extra_fields', 'extra_field_values',
        'label_markers', 'label_values',
        'edited_by', 'edited_at',
    ]
    for key in query_dict.keys():
        if (key in list_keys):
            query_dict[key] = query_dict[key].split(';;')
    return query_dict

def stripValues(query_dict):
    for key in query_dict.keys():
        if isinstance(query_dict[key], str):
            query_dict[key] = query_dict[key].strip()
        else:
            query_dict[key] = [value.strip() for value in query_dict[key]]
    return query_dict

def formatKardex(kardex):
    kardex.edited_by_names = [f"{Nurse.objects.get(id=id).username}" for id in kardex.edited_by]
    return kardex

def formKardexDict(kardex):
    kardex_dict = {
        'Name of Ward': kardex.name_of_ward,
        'IVF': kardex.ivf,
        'Laboratory Work-Ups': kardex.laboratory_work_ups or '',
        'Medications': kardex.medications or '',
        'Side Drip': kardex.side_drip or '',
        'Special Notations': kardex.special_notations or '',
        'Referrals': kardex.referrals or '',
        'Name': kardex.name,
        'Age/Sex': f"{ kardex.age }/{ kardex.sex }" if kardex.age and kardex.sex else '',
        'Date/Time': kardex.date_time or '',
        'Hospital #': kardex.hospital_num or '',
        'DX': kardex.dx or '',
        'DRS': kardex.drs or '',
        'Diet': kardex.diet or '',
        'Extra Fields': ';;'.join(filter(None, kardex.extra_fields)) if len(kardex.extra_fields) else '',
        'Extra Field Values': ';;'.join(filter(None, kardex.extra_field_values)) if len(kardex.extra_field_values) else '',
        'Label Markers': ';;'.join(filter(None, kardex.label_markers)) if len(kardex.label_markers) else '',
        'Label Values': ';;'.join(filter(None, kardex.label_values)) if len(kardex.label_values) else '',
        'Edited By': kardex.edited_by or '',
        'Edited At': kardex.edited_at or ''
    }
    return kardex_dict

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

    context = {"form": form}

    return render(request, 'kardex_app/Authentication/register.html', context)

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
    
    context = {
      "form": form,
    }

    return render(request, 'kardex_app/Authentication/password-change.html', context)


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
    if (not request.user.is_authenticated):
        return redirect('/sign-in')
    
    print(timezone.now())
    kardexs = list(Kardex.objects.all())
    for kardex in kardexs:
        if kardex.name is None:
            kardex.formatted_name = ''
        else:
            kardex.formatted_name = f"{kardex.name.split().pop()}, {' '.join(kardex.name.split()[:-1])}"
    context = { 'kardexs': kardexs }

    return render(request, 'kardex_app/kardex/dashboard.html', context)


def createKardex(request):
    if (not request.user.is_authenticated):
        return redirect('/sign-in')
    
    form = KardexForm()
    if(request.method == "POST"):
        post = request.POST.copy() # to make it mutable
        post.update(splitToLists(post))
        post.update(stripValues(post))
        form = KardexForm(post)
        if(form.is_valid()):
            form.save()
            return redirect("/dashboard")
    context = { "form": form }
    return render(request, 'kardex_app/kardex/create-kardex.html', context)

def updateKardex(request, pk):
    if (not request.user.is_authenticated):
        return redirect('/sign-in')
    
    kardex = Kardex.objects.get(id=pk)
    form = KardexForm(instance=kardex)
    if(request.method == "POST"):
        post = request.POST.copy()
        post.update(splitToLists(post))
        post.update(stripValues(post))
        form = KardexForm(post, instance=kardex)
        if(form.is_valid()):
            form.save()
            return redirect("/dashboard")

    kardex = formatKardex(kardex)
    kardex_history = [formKardexDict(query_dict.instance) for query_dict in kardex.history.all()]
    context = {
        'form': form,
        'kardex': kardex,
        'kardex_history': kardex_history
    }
    return render(request, 'kardex_app/kardex/update-kardex.html', context)

def viewKardex(request, pk):
    if (not request.user.is_authenticated):
        return redirect('/sign-in')
    
    kardex = Kardex.objects.get(id=pk)
    kardex = formatKardex(kardex)
    kardex_history = [formKardexDict(query_dict.instance) for query_dict in kardex.history.all()]
    context = {
        'kardex': kardex,
        'kardex_history': kardex_history
    }
    return render(request, 'kardex_app/kardex/view-kardex.html', context)


def deleteKardex(request, pk):
    if (not request.user.is_authenticated):
        return redirect('/sign-in')
    
    kardex = Kardex.objects.get(id=pk)
    kardex.delete()
    return redirect("/dashboard")


#End of Kardex


#Nurse

def nurseDashboard(request):
    nurses = Nurse.objects.all()
    context = {"nurses": nurses}
    return render(request, 'kardex_app/Nurse/dashboard.html', context)

def createNurse(request):
    form = NurseCreationForm()
    if(request.method == "POST"):
        form = NurseCreationForm(request.POST, request.FILES)
        if(form.is_valid()):
            form.save()
            return redirect("/nurse-dashboard")
    context = {"form": form}
    return render(request, 'kardex_app/Nurse/create-nurse.html', context)

def updateNurse(request, pk):
    nurse = Nurse.objects.get(id=pk)
    form = NurseUpdateForm(instance=nurse)

    if(request.method == "POST"):
        form = NurseUpdateForm(request.POST, request.FILES, instance=nurse)
        if(form.is_valid()):
            form.save()
            return redirect("/nurse-dashboard")

    context = {"form": form}
    return render(request, 'kardex_app/Nurse/update-nurse.html', context)

def viewNurse(request, pk):
    nurse = Nurse.objects.get(id=pk)
    context = {"nurse": nurse}
    return render(request, 'kardex_app/Nurse/view-nurse.html', context)


def deleteNurse(request, pk):
    nurse = Nurse.objects.get(id=pk)
    nurse.delete()
    return redirect("/nurse-dashboard")

#End of Nurse




#generate-reports
def generateReports(request):
    return render(request, 'kardex_app/generate-reports/generate-reports.html')


#End of generate-reports