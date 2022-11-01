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

import os
from django.template.loader import get_template
from xhtml2pdf import pisa

from django.utils import timezone

import pandas as pd

# code adapted from and thanks to
# https://stackoverflow.com/a/17867797
def flatten_nested_lists(A):
    rt = []
    for i in A:
        if isinstance(i, list): rt.extend(flatten_nested_lists(i))
        else: rt.append(i)
    return rt

def split_to_lists(query_dict):
    list_keys = [
        'extra_fields', 'extra_field_values',
        'label_markers', 'label_values',
        'edited_by', 'edited_at',
    ]
    for key in query_dict.keys():
        if key in list_keys:
            query_dict[key] = query_dict[key].split(';;')
    return query_dict

def strip_values(query_dict):
    for key in query_dict.keys():
        if isinstance(query_dict[key], str):
            query_dict[key] = query_dict[key].strip()
        else:
            query_dict[key] = [value.strip() for value in query_dict[key]]
    return query_dict

def format_kardex(kardex):
    kardex.edited_by_names = [f"{Nurse.objects.get(id=id).username}" for id in kardex.edited_by]
    return kardex

def form_kardex_dict(kardex):
    kardex_dict = {
        'Name of Ward': kardex.name_of_ward or '',
        'IVF': kardex.ivf or '',
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
        'Extra Fields': [field if field else '' for field in kardex.extra_fields],
        'Extra Field Values': [value if value else '' for value in kardex.extra_field_values],
        'Label Markers': [marker if marker else '' for marker in kardex.label_markers],
        'Label Values': [value if value else '' for value in kardex.label_values],
        'Edited By': kardex.edited_by or '',
        'Edited At': kardex.edited_at or ''
    }
    return kardex_dict

def form_kardex_comparisons(kardex1, kardex2):
    kardex_comparisons = {
        'Name of Ward': 'Revision' if kardex1.name_of_ward != kardex2.name_of_ward else '',
        'IVF': 'Revision' if kardex1.ivf != kardex2.ivf else '',
        'Laboratory Work-Ups': 'Revision' if kardex1.laboratory_work_ups != kardex2.laboratory_work_ups else '',
        'Medications': 'Revision' if kardex1.medications != kardex2.medications else '',
        'Side Drip': 'Revision' if kardex1.side_drip != kardex2.side_drip else '',
        'Special Notations': 'Revision' if kardex1.special_notations != kardex2.special_notations else '',
        'Referrals': 'Revision' if kardex1.referrals != kardex2.referrals else '',
        'Name': 'Revision' if kardex1.name != kardex2.name else '',
        'Age/Sex': 'Revision' if f"{ kardex1.age }/{ kardex1.sex }" != f"{ kardex2.age }/{ kardex2.sex }" else '',
        'Date/Time': 'Revision' if kardex1.date_time != kardex2.date_time else '',
        'Hospital #': 'Revision' if kardex1.hospital_num != kardex2.hospital_num else '',
        'DX': 'Revision' if kardex1.dx != kardex2.dx else '',
        'DRS': 'Revision' if kardex1.drs != kardex2.drs else '',
        'Diet': 'Revision' if kardex1.diet != kardex2.diet else '',
        'Extra Fields': ['Revision' if field1 != field2 else '' \
            for field1, field2 in zip(kardex1.extra_fields, kardex2.extra_fields)
        ],
        'Extra Field Values': ['Revision' if value1 != value2 else '' \
            for value1, value2 in zip(kardex1.extra_field_values, kardex2.extra_field_values)
        ],
        'Label Markers': ['Revision' if marker1 != marker2 else '' \
            for marker1, marker2 in zip(kardex1.label_markers, kardex2.label_markers)
        ],
        'Label Values': ['Revision' if value1 != value2 else '' \
            for value1, value2 in zip(kardex1.label_values, kardex2.label_values)
        ],
    }
    if len(kardex1.extra_fields) != len(kardex2.extra_fields):
        kardex_comparisons['Extra Fields'] += \
            ['Deletion' for i in range(len(kardex2.extra_fields), len(kardex1.extra_fields))] \
            if len(kardex1.extra_fields) > len(kardex2.extra_fields) \
            else ['Addition' for i in range(len(kardex1.extra_fields), len(kardex2.extra_fields))]
    if len(kardex1.extra_field_values) != len(kardex2.extra_field_values):
        kardex_comparisons['Extra Field Values'] += \
            ['Deletion' for i in range(len(kardex2.extra_field_values), len(kardex1.extra_field_values))] \
            if len(kardex1.extra_field_values) > len(kardex2.extra_field_values) \
            else ['Addition' for i in range(len(kardex1.extra_field_values), len(kardex2.extra_field_values))]
    if len(kardex1.label_markers) != len(kardex2.label_markers):
        kardex_comparisons['Label Markers'] += \
            ['Deletion' for i in range(len(kardex2.label_markers), len(kardex1.label_markers))] \
            if len(kardex1.label_markers) > len(kardex2.label_markers) \
            else ['Addition' for i in range(len(kardex1.label_markers), len(kardex2.label_markers))]
    if len(kardex1.label_values) != len(kardex2.label_values):
        kardex_comparisons['Label Values'] += \
            ['Deletion' for i in range(len(kardex2.label_values), len(kardex1.label_values))] \
            if len(kardex1.label_values) > len(kardex2.label_values) \
            else ['Addition' for i in range(len(kardex1.label_values), len(kardex2.label_values))]
    return kardex_comparisons

# Create your views here.
def home(request):
    return render(request, 'kardex_app/main.html')


# Authentication
def register(request):
    form = NurseCreationForm()
    if request.method == "POST":
        form = NurseCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account was created for "+form.cleaned_data.get("username"))
            return redirect('/sign-in')

    context = {"form": form}

    return render(request, 'kardex_app/Authentication/register.html', context)

def sign_in(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        nurse = authenticate(request, username=username, password=password)
        if nurse is not None:
            login(request, nurse)
            print("Login Success.")
            return redirect('/')
        print("Login Fail.")
        messages.error(request, "Incorrect password or username.")

    return render(request, 'kardex_app/Authentication/sign-in.html')

def sign_out(request):
    logout(request)
    return redirect('sign-in')

def change_password(request):
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


def forgot_password(request):
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
    if not request.user.is_authenticated:
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


def create_kardex(request):
    if not request.user.is_authenticated:
        return redirect('/sign-in')
    form = KardexForm()
    if request.method == "POST":
        post = request.POST.copy() # to make it mutable
        post.update(split_to_lists(post))
        post.update(strip_values(post))
        form = KardexForm(post)
        if form.is_valid():
            form.save()
            return redirect("/dashboard")
    context = { "form": form }
    return render(request, 'kardex_app/kardex/create-kardex.html', context)

def update_kardex(request, pk):
    if not request.user.is_authenticated:
        return redirect('/sign-in')
    kardex = Kardex.objects.get(id=pk)
    form = KardexForm(instance=kardex)
    if request.method == "POST":
        post = request.POST.copy()
        post.update(split_to_lists(post))
        post.update(strip_values(post))
        form = KardexForm(post, instance=kardex)
        if form.is_valid():
            form.save()
            return redirect("/dashboard")

    kardex = format_kardex(kardex)
    kardex_history_qset = kardex.history.all()
    kardex_history = [form_kardex_dict(query_dict.instance) for query_dict in kardex_history_qset]
    kardex_comparisons = [
        form_kardex_comparisons(kardex_history_qset[i+1].instance, kardex_history_qset[i].instance) \
        for i in range(kardex_history_qset.count()-1)
    ]
    flat_kardex_comparisons = list(pd.json_normalize(kardex_comparisons).T.to_dict().values())
    print('kardex_comparisons', kardex_comparisons)
    kardex_comparison_values = [
        flatten_nested_lists(flat_dict.values()) for flat_dict in flat_kardex_comparisons
    ]
    context = {
        'form': form,
        'kardex': kardex,
        'kardex_history': kardex_history,
        'kardex_comparisons': kardex_comparisons,
        'kardex_comparison_values': kardex_comparison_values
    }
    return render(request, 'kardex_app/kardex/update-kardex.html', context)

def view_kardex(request, pk):
    if not request.user.is_authenticated:
        return redirect('/sign-in')
    kardex = Kardex.objects.get(id=pk)
    kardex = format_kardex(kardex)
    kardex_history = [form_kardex_dict(query_dict.instance) for query_dict in kardex.history.all()]
    context = {
        'kardex': kardex,
        'kardex_history': kardex_history
    }
    return render(request, 'kardex_app/kardex/view-kardex.html', context)

def delete_kardex(request, pk):
    if not request.user.is_authenticated:
        return redirect('/sign-in')
    kardex = Kardex.objects.get(id=pk)
    kardex.delete()
    return redirect("/dashboard")
#End of Kardex

#Nurse
def nurse_dashboard(request):
    nurses = Nurse.objects.all()
    context = {"nurses": nurses}
    return render(request, 'kardex_app/Nurse/dashboard.html', context)

def create_nurse(request):
    form = NurseCreationForm()
    if request.method == "POST":
        form = NurseCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("/nurse-dashboard")
    context = {"form": form}
    return render(request, 'kardex_app/Nurse/create-nurse.html', context)

def update_nurse(request, pk):
    nurse = Nurse.objects.get(id=pk)
    form = NurseUpdateForm(instance=nurse)

    if request.method == "POST":
        form = NurseUpdateForm(request.POST, request.FILES, instance=nurse)
        if form.is_valid():
            form.save()
            return redirect("/nurse-dashboard")

    context = {"form": form}
    return render(request, 'kardex_app/Nurse/update-nurse.html', context)

def view_nurse(request, pk):
    nurse = Nurse.objects.get(id=pk)
    context = {"nurse": nurse}
    return render(request, 'kardex_app/Nurse/view-nurse.html', context)


def delete_nurse(request, pk):
    nurse = Nurse.objects.get(id=pk)
    nurse.delete()
    return redirect("/nurse-dashboard")

#End of Nurse




#generate-reports
def generate_reports(request):
    return render(request, 'kardex_app/generate-reports/generate-reports.html')


def bed_tags_pdf(request):
    template_path = "kardex_app/generate-reports/bed-tags.html"
    kardexs = Kardex.objects.all()
    context = {"user": request.user, "kardexs": kardexs}
    fileName = "bed_tags"

    # PDF Generator
    #Note: Separating to a function is ideal but currently not working
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="'+str(fileName)+'.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pdf = pisa.CreatePDF(html, dest=response)

    if not pdf.err:
        return response


def diet_list_pdf(request):
    template_path = "kardex_app/generate-reports/diet-list.html"
    kardexs = Kardex.objects.all()
    context = {"user": request.user, "kardexs": kardexs}
    fileName = "diet_list"

    # PDF Generator
    #Note: Separating to a function is ideal but currently not working
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="'+str(fileName)+'.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pdf = pisa.CreatePDF(html, dest=response)

    if not pdf.err:
        return response


def intravenous_fluid_tags_pdf(request):
    template_path = "kardex_app/generate-reports/intravenous-fluid-tags.html"
    kardexs = Kardex.objects.all()
    context = {"user": request.user, "kardexs": kardexs}
    fileName = "intravenous-fluid-tags"

    # PDF Generator
    #Note: Separating to a function is ideal but currently not working
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="'+str(fileName)+'.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pdf = pisa.CreatePDF(html, dest=response)

    if not pdf.err:
        return response


def medication_cards_pdf(request):
    template_path = "kardex_app/generate-reports/medication-cards.html"
    kardexs = Kardex.objects.all()
    context = {"user": request.user, "kardexs": kardexs}
    fileName = "medication-cards"

    # PDF Generator
    #Note: Separating to a function is ideal but currently not working
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="'+str(fileName)+'.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pdf = pisa.CreatePDF(html, dest=response)

    if not pdf.err:
        return response


def medication_endorsement_sheet_pdf(request):
    template_path = "kardex_app/generate-reports/medication-endorsement-sheet.html"
    kardexs = Kardex.objects.all()
    context = {"user": request.user, "kardexs": kardexs}
    fileName = "medication-endorsement-sheet"

    # PDF Generator
    #Note: Separating to a function is ideal but currently not working
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="'+str(fileName)+'.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pdf = pisa.CreatePDF(html, dest=response)

    if not pdf.err:
        return response

def nursing_endorsement_sheet_pdf(request):
    template_path = "kardex_app/generate-reports/nursing-endorsement-sheet.html"
    kardexs = Kardex.objects.all()
    context = {"user": request.user, "kardexs": kardexs}
    fileName = "nursing-endorsement-sheet"

    # PDF Generator
    #Note: Separating to a function is ideal but currently not working
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="'+str(fileName)+'.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pdf = pisa.CreatePDF(html, dest=response)

    if not pdf.err:
        return response

def special_notes_pdf(request):
    template_path = "kardex_app/generate-reports/special-notes.html"
    kardexs = Kardex.objects.all()
    context = {"user": request.user, "kardexs": kardexs}
    fileName = "special-notes"

    # PDF Generator
    #Note: Separating to a function is ideal but currently not working
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="'+str(fileName)+'.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pdf = pisa.CreatePDF(html, dest=response)

    if not pdf.err:
        return response


def ward_census_pdf(request):
    template_path = "kardex_app/generate-reports/ward-census.html"
    kardexs = Kardex.objects.all()
    context = {"user": request.user, "kardexs": kardexs}
    fileName = "ward-census"

    # PDF Generator
    #Note: Separating to a function is ideal but currently not working
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="'+str(fileName)+'.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pdf = pisa.CreatePDF(html, dest=response)

    if not pdf.err:
        return response

#Utility Function

def render_to_pdf(template_src, context_dict, fileName):
    template_path = template_src
    context = context_dict
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="'+str(fileName)+'.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pdf = pisa.CreatePDF(html, dest=response)

    if not pdf.err:
        return response

#End of generate-reports