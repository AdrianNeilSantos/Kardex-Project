from io import StringIO
from urllib import response
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
from django.http import HttpResponse, Http404
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string

from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa

from django.utils import timezone

import pandas as pd
import xlwt

from datetime import date
import operator
from functools import reduce

# for REST API
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import LimitOffsetPagination

from .serializers import KardexSerializer, NurseSerializer

login_URL = "/sign-in/"

# Create your views here.
def home(request):
    return render(request, 'kardex_app/home.html')


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
            return redirect('/dashboard/')
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

@login_required(login_url=login_URL)
def dashboard(request):
    # print(timezone.now())
    kardexs = list(Kardex.objects.all()[:100])
    context = { 'kardexs': kardexs }

    return render(request, 'kardex_app/kardex/dashboard.html', context)

@login_required(login_url=login_URL)
def createKardex(request):
    form = KardexForm()
    if(request.method == "POST"):
        post = request.POST.copy() # to make it mutable
        new_post = {
            'is_admission' : '1' if post.get('is_admission') == '1' else '',
            'is_discharges' : '1' if post.get('is_discharges') == '1' else '',
            'is_death' : '1' if post.get('is_death') == '1' else '',
            'is_trans_in' : '1' if post.get('is_trans_in') == '1' else '',
            'is_trans_out' : '1' if post.get('is_trans_out') == '1' else '',
            'is_trans_other' : '1' if post.get('is_trans_other') == '1' else ''
        }
        post.update(new_post)
        post.update(splitToLists(post))
        post.update(stripValues(post))
        form = KardexForm(post)
        if(form.is_valid()):
            form.save()
            return redirect("/dashboard")
    context = { "form": form }
    return render(request, 'kardex_app/kardex/create-kardex.html', context)


@login_required(login_url=login_URL)
def updateKardex(request, pk):    
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
    kardex_history_qset = kardex.history.all()
    kardex_history = [formKardexDict(query_dict.instance) for query_dict in kardex_history_qset]
    kardex_comparisons = [
        formKardexComparisons(kardex_history_qset[i+1].instance, kardex_history_qset[i].instance) \
        for i in range(kardex_history_qset.count()-1)
    ]
    flat_kardex_comparisons = list(pd.json_normalize(kardex_comparisons).T.to_dict().values())
    kardex_comparison_values = [
        flattenNestedLists(flat_dict.values()) for flat_dict in flat_kardex_comparisons
    ]
    context = {
        'form': form,
        'kardex': kardex,
        'kardex_history': kardex_history,
        'kardex_comparisons': kardex_comparisons,
        'kardex_comparison_values': kardex_comparison_values
    }
    return render(request, 'kardex_app/kardex/update-kardex.html', context)


@login_required(login_url=login_URL)
def viewKardex(request, pk):    
    kardex = Kardex.objects.get(id=pk)
    kardex = formatKardex(kardex)
    kardex_history_qset = kardex.history.all()
    kardex_history = [formKardexDict(query_dict.instance) for query_dict in kardex_history_qset]
    kardex_comparisons = [
        formKardexComparisons(kardex_history_qset[i+1].instance, kardex_history_qset[i].instance) \
        for i in range(kardex_history_qset.count()-1)
    ]
    flat_kardex_comparisons = list(pd.json_normalize(kardex_comparisons).T.to_dict().values())
    kardex_comparison_values = [
        flattenNestedLists(flat_dict.values()) for flat_dict in flat_kardex_comparisons
    ]
    context = {
        'kardex': kardex,
        'kardex_history': kardex_history,
        'kardex_comparisons': kardex_comparisons,
        'kardex_comparison_values': kardex_comparison_values
    }
    return render(request, 'kardex_app/kardex/view-kardex.html', context)


@login_required(login_url=login_URL)
def deleteKardex(request, pk):
    kardex = Kardex.objects.get(id=pk)
    kardex.delete()
    return redirect("/dashboard")


#End of Kardex


#Nurse

def viewProfile(request):
    nurse = Nurse.objects.get(id=request.user.id)

    form = NurseUpdateForm(instance=nurse)

    if(request.method == "POST"):
        form = NurseUpdateForm(request.POST, request.FILES, instance=nurse)
        if(form.is_valid()):
            form.save()
            return redirect("/view-profile")

    nurse_on_duty = nurse.on_duty.split(',')[datetime.now().weekday()] \
        if nurse.on_duty and len(nurse.on_duty.split(',')) > 1 else '(Missing On Duty Schedule)'
    formatted_nurse_on_duty = '(Missing On Duty Schedule)'
    if 'Missing' not in nurse_on_duty:
        formatted_nurse_on_duty = map(lambda time: \
            f'{ time[:2] }:{ time[-2:] }AM' \
            if int(time) < 1300 \
            else f'{ int(time[:2]) - 12 }:{ time[-2:] }PM', \
            nurse_on_duty.split('-'))
        formatted_nurse_on_duty = f'{ formatted_nurse_on_duty[0] } - { formatted_nurse_on_duty[1] }'
    context = {
        'nurse': nurse,
        'form': form,
        'nurse_age': calculate_age(nurse.birthday),
        'nurse_on_duty': nurse_on_duty,
        'formatted_nurse_on_duty': formatted_nurse_on_duty
    }
    return render(request, 'kardex_app/nurse/view-profile.html', context)

def profile(request, pk):
    visiting_nurse = request.user
    target_nurse = Nurse.objects.get(id=pk)

    if not request.user.is_superuser and visiting_nurse != target_nurse:
        return redirect(f'/profile/{visiting_nurse.id}')

    form = NurseUpdateForm(instance=target_nurse)
    if (request.method == "POST"):
        # print(request.POST)
        post = request.POST.copy()
        birthday = datetime.strptime(post.get('birthday'), '%Y-%m-%d').date()
        post.update({
            'birthday': birthday
        })
        # print(post)
        form = NurseUpdateForm(post, request.FILES, instance=target_nurse)
        # print(form.errors)
        if (form.is_valid()):
            form.save()
            return redirect(f'/profile/{pk}')

    nurse_on_duty = target_nurse.on_duty.split(',')[datetime.now().weekday()] \
        if target_nurse.on_duty and len(target_nurse.on_duty.split(',')) > 1 else '(Missing On Duty Schedule)'
    formatted_nurse_on_duty = '(Missing On Duty Schedule)'
    # print('nurse_on_duty', nurse_on_duty)
    # print(nurse_on_duty.split('-')[0][:2], nurse_on_duty.split('-')[0][-2:])
    if 'Missing' not in nurse_on_duty:
        formatted_nurse_on_duty = list(map(lambda time: \
            f'{ time[:2] }:{ time[-2:] }AM' \
            if int(time) < 1300 \
            else f'{ int(time[:2]) - 12 }:{ time[-2:] }PM', \
            nurse_on_duty.split('-')))
        formatted_nurse_on_duty = f'{ formatted_nurse_on_duty[0] } - { formatted_nurse_on_duty[1] }'
    # print(formatted_nurse_on_duty)
    context = {
        'nurse': target_nurse,
        'form': form,
        'nurse_age': calculate_age(target_nurse.birthday),
        'nurse_on_duty': nurse_on_duty,
        'formatted_nurse_on_duty': formatted_nurse_on_duty
    }
    return render(request, 'kardex_app/nurse/profile.html', context)



def nurseDashboard(request):
    nurses = Nurse.objects.all()
    context = {"nurses": nurses}

    if not request.user.is_superuser:
        return redirect('dashboard')

    return render(request, 'kardex_app/nurse/nurse-dashboard.html', context)

def createNurse(request):
    if not request.user.is_superuser:
        return redirect('dashboard')

    form = NurseCreationForm()
    if(request.method == "POST"):
        form = NurseCreationForm(request.POST, request.FILES)
        if(form.is_valid()):
            form.save()
            return redirect("/nurse-dashboard")
    context = {"form": form}
    return render(request, 'kardex_app/nurse/create-nurse.html', context)

def updateNurse(request, pk):
    nurse = Nurse.objects.get(id=pk)
    form = NurseUpdateForm(instance=nurse)

    if(request.method == "POST"):
        # print("THIS IS POST")
        form = NurseUpdateForm(request.POST, request.FILES, instance=nurse)
        if(form.is_valid()):
            form.save()
            return redirect(f"/view-profile")

    context = {"form": form, "nurse": nurse}
    return render(request, 'kardex_app/nurse/update-nurse.html', context)

def viewNurse(request, pk):
    nurse = Nurse.objects.get(id=pk)
    context = {"nurse": nurse}
    return render(request, 'kardex_app/nurse/view-nurse.html', context)


def deleteNurse(request, pk):
    nurse = Nurse.objects.get(id=pk)
    nurse.delete()
    return redirect("/nurse-dashboard")

#End of Nurse




#generate-reports
def generateReports(request):
    #Get list of all wards available
    kardexs = Kardex.objects.all()

    departments = []

    for kardex in kardexs:
        department = kardex.department
        if department not in departments:
            departments.append(department)

    context = {"departments": departments}

    return render(request, 'kardex_app/generate-reports/generate-reports.html', context)


  #Generating PDFS
def bed_tags_PDF(request):
    template_path = "kardex_app/generate-reports/PDFs/bed-tags.html"
    kardexs = Kardex.objects.all()
    context = {"user": request.user, "kardexs": kardexs}
    fileName = "bed_tags"

    return render_to_PDF(template_path, context, fileName)

def diet_list_PDF(request):
    template_path = "kardex_app/generate-reports/PDFs/diet-list.html"
    kardexs = Kardex.objects.all()
    context = {"user": request.user, "kardexs": kardexs}
    fileName = "diet_list"

    return render_to_PDF(template_path, context, fileName)


def intravenous_fluid_tags_PDF(request):
    template_path = "kardex_app/generate-reports/PDFs/intravenous-fluid-tags.html"
    kardexs = Kardex.objects.all()
    
    context = {"user": request.user, "kardexs": kardexs}
    fileName = "intravenous-fluid-tags"

    return render_to_PDF(template_path, context, fileName)


def medication_cards_PDF(request):
    template_path = "kardex_app/generate-reports/PDFs/medication-cards.html"
    kardexs = Kardex.objects.all()
    context = {"user": request.user, "kardexs": kardexs}
    fileName = "medication-cards"

    return render_to_PDF(template_path, context, fileName)


def medication_endorsement_sheet_PDF(request):
    template_path = "kardex_app/generate-reports/PDFs/medication-endorsement-sheet.html"
    kardexs = Kardex.objects.all()
    context = {"user": request.user, "kardexs": kardexs}
    fileName = "medication-endorsement-sheet"

    return render_to_PDF(template_path, context, fileName)

def nursing_endorsement_sheet_PDF(request):
    template_path = "kardex_app/generate-reports/PDFs/nursing-endorsement-sheet.html"
    kardexs = Kardex.objects.all()
    context = {"user": request.user, "kardexs": kardexs}
    fileName = "nursing-endorsement-sheet"

    return render_to_PDF(template_path, context, fileName)

def special_notes_PDF(request):
    template_path = "kardex_app/generate-reports/PDFs/special-notes.html"
    kardexs = Kardex.objects.all()
    context = {"user": request.user, "kardexs": kardexs}
    fileName = "special-notes"

    return render_to_PDF(template_path, context, fileName)


def ward_census_PDF(request):
    template_path = "kardex_app/generate-reports/PDFs/ward-census.html"
    kardexs = Kardex.objects.all()
    context = {"user": request.user, "kardexs": kardexs}
    fileName = "ward-census"

    return render_to_PDF(template_path, context, fileName)


#Utility Function

def render_to_PDF(template_src, context_dict, fileName):
    template_path = template_src
    context = context_dict
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="'+str(fileName)+'.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pdf = pisa.CreatePDF(html, dest=response)

    if not pdf.err:
        return response



def generate_front_1(work_book, style_head_row, style_data_row, department, request):
    ws = work_book.add_sheet(u'FRONT1')
    context_header = get_context_front(department)
    dept = department
    #Adjusts colum widths
    edit_col_width(ws, 1, 15)
    edit_col_width(ws, 2, 12)
    edit_col_width(ws, 3, 12)

    START_COL = 0
    END_COL = 13
    START_ROW = 6
    current_row = START_ROW

    
    current_row = add_front_header(ws,current_row,START_COL,END_COL, department)


    #[start, end] format
    row_admission = [0, 0]
    row_discharges = [0, 0]
    row_death = [0, 0]

    for context in context_header:
        current_row = add_section(ws, current_row, START_COL, END_COL, context, style_head_row)
        data_start_row = current_row
        if context == "CENSUS OF PATIENTS":
            continue
        if context == "ADMISSION":
            row_admission[0] = data_start_row
        elif context == "DISCHARGES":
            row_discharges[0] = data_start_row
        elif context == "DEATH":
            row_death[0] = data_start_row

        current_row = add_data(ws, context_header[context], current_row, END_COL, style_data_row)

        if context == "ADMISSION":
            row_admission[1] = current_row - 1
        elif context == "DISCHARGES":
            row_discharges[1] = current_row - 1
        elif context == "DEATH":
            row_death[1] = current_row - 1

    #Generating census report headers




    departments = ["MED", "OB", "GYNE", "PED", 'SURG-A', 'SURG-P', 'OPHTHA', 'ENT', 'ORTHO', 'SICK BB', 'WELL BB']

    current_col = 0
    for department in departments:
        if current_col == 0:
            ws.write_merge(current_row,current_row, current_col, 2, 'DEPARTMENT', style_head_row)
            current_col += 3
        
        ws.write(current_row,current_col, department, style_head_row)
        current_col += 1


    style_census_categories = xlwt.easyxf("""    
        align:
            wrap on,
            vert center,
            horiz left;
        borders:
            left THIN,
            right THIN,
            top THIN,
            bottom THIN;
        font:
            name Calibri,
            colour_index Black,
            height 200;
        """
    )


    style_census_data = xlwt.easyxf("""    
        align:
            wrap on,
            vert center,
            horiz right;
        borders:
            left THIN,
            right THIN,
            top THIN,
            bottom THIN;
        font:
            name Calibri,
            bold on,
            colour_index Black,
            height 200;
        """
    )

    categories = ["Remaining from yesterday MN report", "Admission", "Transfer in from other floor", "Total of No. 1,2,3", "Discharges (Alive) this census day",
                    "Transfer out from other floor", "Deaths", "Total No. of 5,6,7", "Remaining at 12 MN 4 minus 8", "Admission & Discharge on the same day (including death)",
                    "Total in-pt. service days of care (9+10)"
                ]
    
    
    #Generating census of patients categories and data
    current_row += 1
    current_col = 3

    #retrieve count of back
    context_back = get_context_back(dept)
    trans_in_count = len(context_back["TRANS-IN"])
    trans_out_count = len(context_back["TRANS-OUT"])
    trans_other_count = len(context_back["TRANSFER TO OTHER HOSPITAL"])

    row_trans_in = 6
    row_trans_out = row_trans_in + 4


    row_census = [0] * 11
    for category in categories:
        ws.write_merge(current_row,current_row,0,2, f'{categories.index(category) + 1}. {category}', style_census_categories)
        for department in departments:
            if category == "Remaining from yesterday MN report":
                ws.write(current_row, current_col, xlwt.Formula("0"), style_census_data)
                row_census[0] = current_row + 1
            elif category == "Admission":
                ws.write(current_row, current_col, xlwt.Formula(f'COUNTIF($A${row_admission[0]}:$A${row_admission[1]};"{department}")'), style_census_data)
                row_census[1] = current_row + 1
            elif category == "Transfer in from other floor":
                ws.write(current_row, current_col, xlwt.Formula(f'COUNTIF(BACK1!$A${row_trans_in}:$A${row_trans_in+trans_in_count};"{department}")'), style_census_data)
                row_census[2] = current_row + 1
            elif category == "Total of No. 1,2,3":
                ws.write(current_row, current_col, xlwt.Formula(f'SUM({chr(65 + current_col)}{row_census[0]}:{chr(65 + current_col)}{row_census[2]})'), style_census_data)
                row_census[3] = current_row + 1
            elif category == "Discharges (Alive) this census day":
                ws.write(current_row, current_col, xlwt.Formula(f'COUNTIF($A${row_discharges[0]}:$A${row_discharges[1]};"{department}")'), style_census_data)
                row_census[4] = current_row + 1
            elif category == "Transfer out from other floor":
                ws.write(current_row, current_col, xlwt.Formula(f'COUNTIF(BACK1!$A${row_trans_out}:$A${row_trans_out+trans_out_count};"{department}")'), style_census_data)
                row_census[5] = current_row + 1
            elif category == "Deaths":
                ws.write(current_row, current_col, xlwt.Formula(f'COUNTIF($A${row_death[0]}:$A${row_death[1]};"{department}")'), style_census_data)
                row_census[6] = current_row + 1
            elif category == "Total No. of 5,6,7":
                ws.write(current_row, current_col, xlwt.Formula(f'SUM({chr(65 + current_col)}{row_census[4]}:{chr(65 + current_col)}{row_census[6]})'), style_census_data)
                row_census[7] = current_row + 1
            elif category == "Remaining at 12 MN 4 minus 8":
                ws.write(current_row, current_col, xlwt.Formula(f'{chr(65 + current_col)}{row_census[3]}-{chr(65 + current_col)}{row_census[7]}'), style_census_data)
                row_census[8] = current_row + 1
            elif category == "Admission & Discharge on the same day (including death)":
                ws.write(current_row, current_col, xlwt.Formula(f'0'), style_census_data)
                row_census[9] = current_row + 1
            elif category == "Total in-pt. service days of care (9+10)":
                ws.write(current_row, current_col, xlwt.Formula(f'{chr(65 + current_col)}{row_census[8]}+{chr(65 + current_col)}{row_census[9]}'), style_census_data)
                row_census[10] = current_row + 1
            current_col += 1
        current_col = 3
        current_row += 1

    current_row += 1
#f"COUNTIF($A${row_admission[0]}:$A${row_admission[1]};MED)")

    #Generating bottom summary
    ws.write(current_row,0, 'Total Admission:') 
    ws.write(current_row,2, 'NEURO:') 
    ws.write(current_row,5, 'URO:') 
    ws.write(current_row,8, 'POST OP:')
    ws.write(current_row,11, 'OTHERS:')

    current_row += 1
    ws.write(current_row,0, 'Total Discharges:') 

    current_row += 1
    ws.write(current_row,0, 'Last:') 

    current_row += 1
    ws.write(current_row,0, 'Today:')
    ws.write_merge(current_row,current_row,3,4, 'Prepared by:')


    style_prepared_by = xlwt.easyxf("""    
        align:
            wrap on,
            vert center,
            horiz left;
        borders:
            bottom THIN;
        font:
            name Calibri,
            bold on,
            colour_index Black,
            height 220;
        """
    )

    ws.write_merge(current_row,current_row,5,8, f'{request.user.first_name} {request.user.last_name}', style_prepared_by)
    

    style_date = xlwt.easyxf("""    
        align:
            wrap on,
            vert center,
            horiz left;
        borders:
            bottom THIN;
        font:
            name Calibri,
            bold on,
            colour_index Black,
            height 220;
        """
    )
    
    ws.write(current_row,10, 'Date:')
    ws.write_merge(current_row,current_row,11,13, '07-Sep-22', style_date)



def generate_front_2(work_book, style_head_row, style_data_row, department, request):
    
    ws = work_book.add_sheet(u'FRONT2')
    context_header = get_context_front(department)
    
    #Adjusts colum widths
    edit_col_width(ws, 1, 15)
    edit_col_width(ws, 2, 12)
    edit_col_width(ws, 3, 12)

    START_COL = 0
    END_COL = 13
    START_ROW = 6
    current_row = START_ROW

    
    current_row = add_front_header(ws,current_row,START_COL,END_COL, department)


    for context in context_header:
        current_row = add_section(ws, current_row, START_COL, END_COL, context, style_head_row)
        if context == "CENSUS OF PATIENTS":
            continue
        current_row = add_data(ws, context_header[context], current_row, END_COL, style_data_row)

    #Generating census report headers




    departments = ["MED", "OB", "GYNE", "PED", 'SURG-A', 'SURG-P', 'OPHTHA', 'ENT', 'ORTHO', 'SICK BB', 'WELL BB']

    current_col = 0
    for department in departments:
        if current_col == 0:
            ws.write_merge(current_row,current_row, current_col, 2, 'DEPARTMENT', style_head_row)
            current_col += 3
        
        ws.write(current_row,current_col, department, style_head_row)
        current_col += 1


    style_census_categories = xlwt.easyxf("""    
        align:
            wrap on,
            vert center,
            horiz left;
        borders:
            left THIN,
            right THIN,
            top THIN,
            bottom THIN;
        font:
            name Calibri,
            colour_index Black,
            height 200;
        """
    )


    style_census_data = xlwt.easyxf("""    
        align:
            wrap on,
            vert center,
            horiz right;
        borders:
            left THIN,
            right THIN,
            top THIN,
            bottom THIN;
        font:
            name Calibri,
            bold on,
            colour_index Black,
            height 200;
        """
    )

    categories = ["Remaining from yesterday MN report", "Admission", "Transfer in from other floor", "Total of No. 1,2,3", "Discharges (Alive) this census day",
                    "Transfer out from other floor", "Deaths", "Total No. of 5,6,7", "Remaining at 12 MN 4 minus 8", "Admission & Discharge on the same day (including death)",
                    "Total in-pt. service days of care (9+10)"
                ]
    
    
    #Generating census of patients categories and data
    current_row += 1
    current_col = 3
    for category in categories:
        ws.write_merge(current_row,current_row,0,2, f'{categories.index(category) + 1}. {category}', style_census_categories)
        for department in departments:
            ws.write(current_row, current_col, "", style_census_data)
            current_col += 1
        current_col = 3
        current_row += 1

    current_row += 1


    #Generating bottom summary
    ws.write(current_row,0, 'Total Admission:') 
    ws.write(current_row,2, 'NEURO:') 
    ws.write(current_row,5, 'URO:') 
    ws.write(current_row,8, 'POST OP:')
    ws.write(current_row,11, 'OTHERS:')

    current_row += 1
    ws.write(current_row,0, 'Total Discharges:') 

    current_row += 1
    ws.write(current_row,0, 'Last:') 

    current_row += 1
    ws.write(current_row,0, 'Today:')
    ws.write_merge(current_row,current_row,3,4, 'Prepared by:')


    style_prepared_by = xlwt.easyxf("""    
        align:
            wrap on,
            vert center,
            horiz left;
        borders:
            bottom THIN;
        font:
            name Calibri,
            bold on,
            colour_index Black,
            height 220;
        """
    )

    ws.write_merge(current_row,current_row,5,8, '', style_prepared_by)
    

    style_date = xlwt.easyxf("""    
        align:
            wrap on,
            vert center,
            horiz left;
        borders:
            bottom THIN;
        font:
            name Calibri,
            bold on,
            colour_index Black,
            height 220;
        """
    )
    
    ws.write(current_row,10, 'Date:')
    ws.write_merge(current_row,current_row,11,13, '07-Sep-22', style_date)



def generate_front_3(work_book, style_head_row, style_data_row, department, request):

    ws = work_book.add_sheet(u'FRONT3')
    context_header = get_context_front(department)
    
    #Adjusts colum widths
    edit_col_width(ws, 1, 15)
    edit_col_width(ws, 2, 12)
    edit_col_width(ws, 3, 12)

    START_COL = 0
    END_COL = 13
    START_ROW = 6
    current_row = START_ROW

    
    current_row = add_front_header(ws,current_row,START_COL,END_COL, department)


    for context in context_header:
        current_row = add_section(ws, current_row, START_COL, END_COL, context, style_head_row)
        if context == "CENSUS OF PATIENTS":
            continue
        current_row = add_data(ws, context_header[context], current_row, END_COL, style_data_row)

    #Generating census report headers




    departments = ["MED", "OB", "GYNE", "PED", 'SURG-A', 'SURG-P', 'OPHTHA', 'ENT', 'ORTHO', 'SICK BB', 'WELL BB']

    current_col = 0
    for department in departments:
        if current_col == 0:
            ws.write_merge(current_row,current_row, current_col, 2, 'DEPARTMENT', style_head_row)
            current_col += 3
        
        ws.write(current_row,current_col, department, style_head_row)
        current_col += 1


    style_census_categories = xlwt.easyxf("""    
        align:
            wrap on,
            vert center,
            horiz left;
        borders:
            left THIN,
            right THIN,
            top THIN,
            bottom THIN;
        font:
            name Calibri,
            colour_index Black,
            height 200;
        """
    )


    style_census_data = xlwt.easyxf("""    
        align:
            wrap on,
            vert center,
            horiz right;
        borders:
            left THIN,
            right THIN,
            top THIN,
            bottom THIN;
        font:
            name Calibri,
            bold on,
            colour_index Black,
            height 200;
        """
    )

    categories = ["Remaining from yesterday MN report", "Admission", "Transfer in from other floor", "Total of No. 1,2,3", "Discharges (Alive) this census day",
                    "Transfer out from other floor", "Deaths", "Total No. of 5,6,7", "Remaining at 12 MN 4 minus 8", "Admission & Discharge on the same day (including death)",
                    "Total in-pt. service days of care (9+10)"
                ]
    
    
    #Generating census of patients categories and data
    current_row += 1
    current_col = 3
    for category in categories:
        ws.write_merge(current_row,current_row,0,2, f'{categories.index(category) + 1}. {category}', style_census_categories)
        for department in departments:
            ws.write(current_row, current_col, "", style_census_data)
            current_col += 1
        current_col = 3
        current_row += 1

    current_row += 1


    #Generating bottom summary
    ws.write(current_row,0, 'Total Admission:') 
    ws.write(current_row,2, 'NEURO:') 
    ws.write(current_row,5, 'URO:') 
    ws.write(current_row,8, 'POST OP:')
    ws.write(current_row,11, 'OTHERS:')

    current_row += 1
    ws.write(current_row,0, 'Total Discharges:') 

    current_row += 1
    ws.write(current_row,0, 'Last:') 

    current_row += 1
    ws.write(current_row,0, 'Today:')
    ws.write_merge(current_row,current_row,3,4, 'Prepared by:')


    style_prepared_by = xlwt.easyxf("""    
        align:
            wrap on,
            vert center,
            horiz left;
        borders:
            bottom THIN;
        font:
            name Calibri,
            bold on,
            colour_index Black,
            height 220;
        """
    )

    ws.write_merge(current_row,current_row,5,8, '', style_prepared_by)
    

    style_date = xlwt.easyxf("""    
        align:
            wrap on,
            vert center,
            horiz left;
        borders:
            bottom THIN;
        font:
            name Calibri,
            bold on,
            colour_index Black,
            height 220;
        """
    )
    
    ws.write(current_row,10, 'Date:')
    ws.write_merge(current_row,current_row,11,13, '07-Sep-22', style_date)





def generate_back_1(work_book, style_head_row, style_data_row, department, request):
    ws = work_book.add_sheet(u'BACK1')

    context_header = get_context_back(department)
    
    #Adjusts colum widths
    edit_col_width(ws, 1, 15)
    edit_col_width(ws, 2, 12)
    edit_col_width(ws, 3, 12)

    START_COL = 0
    END_COL = 13
    START_ROW = 0
    current_row = START_ROW

    
    current_row = add_front_header(ws,current_row,START_COL,END_COL, department)


    for context in context_header:
        current_row = add_section(ws, current_row, START_COL, END_COL, context, style_head_row)
        current_row = add_data(ws, context_header[context], current_row, END_COL, style_data_row)

    ws.write(current_row,0, 'TOTAL')





def generate_back_2(work_book, style_head_row, style_data_row, department, request):
    ws = work_book.add_sheet(u'BACK2')

    context_header = get_context_back(department)
    
    #Adjusts colum widths
    edit_col_width(ws, 1, 15)
    edit_col_width(ws, 2, 12)
    edit_col_width(ws, 3, 12)

    START_COL = 0
    END_COL = 13
    START_ROW = 0
    current_row = START_ROW

    
    current_row = add_front_header(ws,current_row,START_COL,END_COL, department)


    for context in context_header:
        current_row = add_section(ws, current_row, START_COL, END_COL, context, style_head_row)
        current_row = add_data(ws, context_header[context], current_row, END_COL, style_data_row)

    ws.write(current_row,0, 'TOTAL')


def generate_back_3(work_book, style_head_row, style_data_row, department, request):
    ws = work_book.add_sheet(u'BACK3')

    context_header = get_context_back(department)
    
    #Adjusts colum widths
    edit_col_width(ws, 1, 15)
    edit_col_width(ws, 2, 12)
    edit_col_width(ws, 3, 12)

    START_COL = 0
    END_COL = 13
    START_ROW = 0
    current_row = START_ROW

    
    current_row = add_front_header(ws,current_row,START_COL,END_COL, department)


    for context in context_header:
        current_row = add_section(ws, current_row, START_COL, END_COL, context, style_head_row)
        current_row = add_data(ws, context_header[context], current_row, END_COL, style_data_row)

    ws.write(current_row,0, 'TOTAL')


#Excel Utilities

def add_front_header(ws,current_row,START_COL,END_COL,department):
    if "FRONT" in ws.name:
        style_sheet_header = xlwt.easyxf("""    
            align:
                wrap on,
                vert center,
                horiz center;
            borders:
                bottom THIN;
            font:
                name Calibri,
                colour_index Black,
                bold on,
                height 280;
            """
        )
        ws.write_merge(current_row,current_row,START_COL,END_COL, "HOSPITAL CENSUS REPORT", style_sheet_header)
        current_row += 2

    style_label = xlwt.easyxf("""    
            font:
                name Calibri,
                colour_index Black,
                height 240;
            """
        )

    style_value = xlwt.easyxf("""    
            align:
                wrap on;
            borders:
                bottom THIN;
            font:
                name Calibri,
                colour_index Black,
                bold on,
                height 280;
            """
        )

    ws.write(current_row,0, 'FOR THE 24 HRS ENDED MIDNIGHT OF:', style_label)
    ws.write_merge(current_row,current_row,3,6, "07-SEP-22", style_value)
    ws.write(current_row,9, 'FLOOR/SECTION:', style_label)
    ws.write_merge(current_row,current_row,11,END_COL, department, style_value)
    current_row += 2

    return current_row


def add_section(ws, current_row, START_COL, END_COL, header_name, style_head_row):
    
    style_section_header = xlwt.easyxf("""    
        align:
            wrap on,
            vert center,
            horiz center;
        font:
            name Calibri,
            colour_index Black,
            bold on,
            underline 1,
            height 240;
        """
    )
    ws.write_merge(current_row,current_row,START_COL,END_COL, header_name, style_section_header)
    current_row += 2

    if(header_name == "CENSUS OF PATIENTS"):
        return current_row
    # Generate worksheet head row data.
    ws.write(current_row,0, 'WARD AND BED NO.', style_head_row) 
    ws.write(current_row,1, 'TIME', style_head_row) 
    ws.write(current_row,2, 'CASE NO.', style_head_row) 
    ws.write_merge(current_row,current_row, 3, 8, 'NAME', style_head_row)
    ws.write_merge(current_row,current_row, 9, END_COL, 'DIAGNOSIS AND CONDITION', style_head_row)
    current_row += 1

    return current_row





def add_data(ws, kardexs, current_row, END_COL, style_data_row):
    for kardex in kardexs:
        ws.write(current_row,0, f'{kardex.name_of_ward}', style_data_row)
        ws.write(current_row,1, kardex.date_time, style_data_row)
        ws.write(current_row,2, kardex.case_num, style_data_row)
        ws.write_merge(current_row,current_row,3, 8, f'{kardex.first_name}, {kardex.last_name}', style_data_row)
        ws.write_merge(current_row,current_row,9,END_COL, f'{kardex.dx}, {kardex.condition}', style_data_row)
        current_row += 1 

    current_row += 1
    return current_row



def get_context_front(department):
    admission = Kardex.objects.filter(Q(department=department) & Q(is_admission=True))
    discharges = Kardex.objects.filter(Q(department=department) & Q(is_discharges=True))
    death = Kardex.objects.filter(Q(department=department) & Q(is_death=True))
    census = Kardex.objects.all()

    context = {"ADMISSION": admission, "DISCHARGES": discharges, "DEATH": death, "CENSUS OF PATIENTS": census}

    return context


def get_context_back(department):
    trans_in = Kardex.objects.filter(Q(department=department) & Q(is_trans_in=True))
    trans_out = Kardex.objects.filter(Q(department=department) & Q(is_trans_out=True))
    trans_other = Kardex.objects.filter(Q(department=department) & Q(is_trans_other=True))

    context = {"TRANS-IN": trans_in, "TRANS-OUT": trans_out, "TRANSFER TO OTHER HOSPITAL":trans_other}

    return context


def edit_row_height(ws, target_row, height):
    header_row = ws.row(target_row-1)
    tall_style = xlwt.easyxf(f'font:height {height * 20};') # 36pt: divide by 20
    header_row.set_style(tall_style)

def edit_col_width(ws, target_col, width):
    header_col = ws.col(target_col-1)
    header_col.width = 256 * width   #20 char


  #Generating ALL XLSX
def generate_census_XLSX(request, department):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    fileName = "census"
    response['Content-Disposition'] = 'attachment;filename="'+str(fileName)+'.xls"'

    style_head_row = xlwt.easyxf("""    
        align:
            wrap on,
            vert center,
            horiz center;
        borders:
            left THIN,
            right THIN,
            top THIN,
            bottom THIN;
        font:
            name Calibri,
            colour_index Black,
            bold on,
            height 240;
        """
    )

    style_data_row = xlwt.easyxf("""
        align:
            wrap on,
            vert center,
            horiz center;
        font:
            name Calibri,
            bold off,
            height 240;
        borders:
            left THIN,
            right THIN,
            top THIN,
            bottom THIN;

        """
    )

    # Set data row date string format.
    style_data_row.num_format_str = 'M/D/YY'

    work_book = xlwt.Workbook(encoding = 'utf-8')


    generate_back_1(work_book, style_head_row, style_data_row, department,request)
    generate_back_2(work_book, style_head_row, style_data_row, department,request)
    generate_back_3(work_book, style_head_row, style_data_row, department,request)
    generate_front_1(work_book, style_head_row, style_data_row, department,request)
    generate_front_2(work_book, style_head_row, style_data_row, department,request)
    generate_front_3(work_book, style_head_row, style_data_row, department,request)

    
    write_excel_report(work_book, response)

    return response


def write_excel_report(work_book, response):
    output = BytesIO()
    work_book.save(output)
    output.seek(0)
    response.write(output.getvalue()) 


#End of generate-reports


# for REST API
class KardexList(APIView):
    def get(self, request, format=None):
        requesting_nurse = request.user
        kardexs = Kardex.objects.all()
        kardexs = kardexs.filter(reduce(operator.or_,
            (Q(name_of_ward__icontains=ward) for ward in requesting_nurse.ward.split(',')))
        )
        kardexs = kardexs.filter(reduce(operator.or_,
            (Q(department__icontains=department) for department in requesting_nurse.department.split(',')))
        )
        serializers = KardexSerializer(kardexs, many=True)
        return Response(serializers.data)

class PaginatedKardexList(APIView, LimitOffsetPagination):
    def get(self, request, format=None):
        requesting_nurse = request.user
        relevant_kardex = Kardex.objects.all()

        relevant_kardex = relevant_kardex.filter(reduce(operator.or_,
            (Q(name_of_ward__icontains=ward) for ward in requesting_nurse.ward.split(','))
        ))

        relevant_kardex = relevant_kardex.filter(reduce(operator.or_,
            (Q(department__icontains=department) for department in requesting_nurse.department.split(',')))
        )

        target_nurse = request.GET.get('nurse', '')
        if target_nurse:
            relevant_kardex = relevant_kardex.filter(Q(edited_by__icontains=target_nurse))

        target_name = request.GET.get('name', '')
        if target_name:
            relevant_kardex = relevant_kardex.filter(
                Q(last_name__icontains=target_name) | Q(first_name__icontains=target_name)
            )

        target_min_date = request.GET.get('min-date', '')
        if target_min_date:
            split_min_date = target_min_date.split('-')
            date_format = ['%Y', '%m', '%d']
            target_min_date = timezone.make_aware(datetime.strptime('-'.join(split_min_date), '-'.join(date_format[:len(split_min_date)])))
            relevant_kardex = relevant_kardex.filter(Q(date_time__gte=target_min_date) | Q(date_added__gte=target_min_date))

        target_max_date = request.GET.get('max-date', '')
        if target_max_date:
            split_max_date = target_max_date.split('-')
            date_format = ['%Y', '%m', '%d']
            target_max_date = timezone.make_aware(datetime.strptime('-'.join(split_max_date), '-'.join(date_format[:len(split_max_date)])))
            relevant_kardex = relevant_kardex.filter(Q(date_time__lte=target_max_date) | Q(date_added__lte=target_max_date))

        results = self.paginate_queryset(relevant_kardex, request, view=self)
        serializers = KardexSerializer(results, many=True)
        return self.get_paginated_response(serializers.data)

@api_view(['POST'])
def kardex_search(request):
    requesting_nurse = request.user
    query = request.data.get('query', '')

    if query:
        results = Kardex.objects.filter(Q(name__icontains=query))
        results = results.filter(reduce(operator.or_,
            (Q(name_of_ward__icontains=ward) for ward in requesting_nurse.ward.split(',')))
        )
        results = results.filter(reduce(operator.or_,
            (Q(department__icontains=department) for department in requesting_nurse.department.split(',')))
        )
        
        serializer = KardexSerializer(results, many=True)
        return Response(serializer.data)
    else:
        return Response({'Kardexs': []})

class NurseList(APIView):
    def get(self, request, format=None):
        all_nurse = Nurse.objects.all()
        nurses = all_nurse.filter(reduce(operator.or_,
            (Q(ward__icontains=ward) for ward in request.user.ward.split(',')))
        )
        nurses = nurses.filter(reduce(operator.or_,
            (Q(department__icontains=department) for department in request.user.department.split(',')))
        )
        serializers = NurseSerializer(nurses, many=True)
        return Response(serializers.data)

# class PaginatedNurseList(APIView, LimitOffsetPagination):
#     def get(self, request, format=None):
#         all_nurse = Nurse.objects.all()
#         nurses = all_nurse.filter(reduce(operator.or_,
#             (Q(ward__icontains=ward) for ward in request.user.ward.split(',')))
#         )
#         nurses = nurses.filter(reduce(operator.or_,
#             (Q(department__icontains=department) for department in request.user.department.split(',')))
#         )
#         results = self.paginate_queryset(nurses, request, view=self)
#         serializers = NurseSerializer(results, many=True)
#         return self.get_paginated_response(serializers.data)

class PaginatedNurseList(APIView, LimitOffsetPagination):
    def get(self, request, format=None):
        requesting_nurse = request.user
        visible_nurses = Nurse.objects.all()

        if request.META['HTTP_REFERER'].endswith('nurse-dashboard/'):
            visible_nurses = visible_nurses.filter(reduce(operator.or_,
                (Q(ward__icontains=ward) for ward in requesting_nurse.ward.split(','))
            ))

            visible_nurses = visible_nurses.filter(reduce(operator.or_,
                (Q(department__icontains=department) for department in requesting_nurse.department.split(',')))
            )

        target_name = request.GET.get('name', '')
        if target_name:
            visible_nurses = visible_nurses.filter(
                Q(last_name__icontains=target_name) | Q(first_name__icontains=target_name)
            )

        on_duty_filters = {}
        target_min_on_duty = request.GET.get('min-on-duty', '')
        if target_min_on_duty:
            on_duty_filters['on_duty__istartswith'] = target_min_on_duty

        target_max_on_duty = request.GET.get('max-on-duty', '')
        if target_max_on_duty:
            on_duty_filters['on_duty__iendswith'] = target_max_on_duty
        
        visible_nurses = visible_nurses.filter(**on_duty_filters)

        results = self.paginate_queryset(visible_nurses, request, view=self)
        serializers = NurseSerializer(results, many=True)
        return self.get_paginated_response(serializers.data)

@api_view(['POST'])
def nurse_search(request):
    query = request.data.get('query', '')

    if query:
        results = Nurse.objects.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
        serializer = NurseSerializer(results, many=True)
        return Response(serializer.data)
    else:
        return Response({'Nurses': []})


# class InsideOnDuty(Lookup):
#     lookup_name = 'iod'

#     def as_sql(self, compiler, connection):
#         lhs, lhs_params = compiler.compile(self.lhs)
#         rhs, rhs_params = compiler.compile(self.rhs)
#         params = lhs_params + rhs_params
#         return "DATE(%s) = DATE(%s)" % (lhs, rhs), params

# code adapted from and thanks to
# https://stackoverflow.com/a/17867797
def flattenNestedLists(A):
    rt = []
    for i in A:
        if isinstance(i, list): rt.extend(flattenNestedLists(i))
        else: rt.append(i)
    return rt

def calculate_age(born):
    today = date.today()
    if born:
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    else:
        return 0

def strToBool(value):
    if value == '1' or lower(value) == 'true':
        return True
    elif value == '0' or lower(value) == 'false':
        return False
    else:
        return None

def splitToLists(query_dict):
    list_keys = [
        'extra_fields', 'extra_field_values',
        'label_markers', 'label_values',
        'edited_by', 'edited_at',
    ]
    for key in query_dict.keys():
        print(list_keys)
        print('key', key, key in list_keys)
        if (key in list_keys):
            print('bad action')
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
        'Name of Ward': kardex.name_of_ward or '',
        'IVF': kardex.ivf or '',
        'Laboratory Work-Ups': kardex.laboratory_work_ups or '',
        'Medications': kardex.medications or '',
        'Side Drip': kardex.side_drip or '',
        'Special Notations': kardex.special_notations or '',
        'Referrals': kardex.referrals or '',
        'First Name': kardex.first_name,
        'Last Name': kardex.last_name,
        'Age/Sex': f"{ kardex.age }/{ kardex.sex }" if kardex.age and kardex.sex else '',
        'Date/Time': kardex.date_time or '',
        'Hospital #': kardex.hospital_num or '',
        'Bed #': kardex.bed_num or '',
        'Case #': kardex.case_num or '',
        'Condition': kardex.condition or '',
        'Department': kardex.department or '',
        'DX': kardex.dx or '',
        'DRS': kardex.drs or '',
        'Diet': kardex.diet or '',
        'Category': '0' if kardex.is_admission else \
            '1' if kardex.is_discharges else \
            '2' if kardex.is_death else '3',
        'Transfer Type': '0' if kardex.is_trans_in else \
            '1' if kardex.is_trans_out else \
            '2' if kardex.is_trans_other else '3',
        'Extra Fields': [field if field else '' for field in kardex.extra_fields],
        'Extra Field Values': [value if value else '' for value in kardex.extra_field_values],
        'Label Markers': [marker if marker else '' for marker in kardex.label_markers],
        'Label Values': [value if value else '' for value in kardex.label_values],
        'Edited By': kardex.edited_by or '',
        'Edited At': kardex.edited_at or ''
    }
    return kardex_dict

def formKardexComparisons(kardex1, kardex2):
    kardex_comparisons = {
        'Name of Ward': 'Revision' if kardex1.name_of_ward != kardex2.name_of_ward else '',
        'IVF': 'Revision' if kardex1.ivf != kardex2.ivf else '',
        'Laboratory Work-Ups': 'Revision' if kardex1.laboratory_work_ups != kardex2.laboratory_work_ups else '',
        'Medications': 'Revision' if kardex1.medications != kardex2.medications else '',
        'Side Drip': 'Revision' if kardex1.side_drip != kardex2.side_drip else '',
        'Special Notations': 'Revision' if kardex1.special_notations != kardex2.special_notations else '',
        'Referrals': 'Revision' if kardex1.referrals != kardex2.referrals else '',
        'First Name': 'Revision' if kardex1.first_name != kardex2.first_name else '',
        'Last Name': 'Revision' if kardex1.last_name != kardex2.last_name else '',
        'Age/Sex': 'Revision' if f"{ kardex1.age }/{ kardex1.sex }" != f"{ kardex2.age }/{ kardex2.sex }" else '',
        'Date/Time': 'Revision' if kardex1.date_time != kardex2.date_time else '',
        'Hospital #': 'Revision' if kardex1.hospital_num != kardex2.hospital_num else '',
        'Bed #': 'Revision' if kardex1.bed_num != kardex2.bed_num else '',
        'Case #': 'Revision' if kardex1.case_num != kardex2.case_num else '',
        'Condition': 'Revision' if kardex1.condition != kardex2.condition else '',
        'Category': 'Revision' if kardex1.is_admission != kardex2.is_admission or \
            kardex1.is_discharges != kardex2.is_discharges or \
            kardex1.is_death != kardex2.is_death else '',
        'Transfer Type': 'Revision' if kardex1.is_trans_in != kardex2.is_trans_in or \
            kardex1.is_trans_out != kardex2.is_trans_out or \
            kardex1.is_trans_other != kardex2.is_trans_other else '',
        'Department': 'Revision' if kardex1.department != kardex2.department else '',
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
    if (len(kardex1.extra_fields) != len(kardex2.extra_fields)):
        kardex_comparisons['Extra Fields'] += \
            ['Deletion' for i in range(len(kardex2.extra_fields), len(kardex1.extra_fields))] \
            if len(kardex1.extra_fields) > len(kardex2.extra_fields) \
            else ['Addition' for i in range(len(kardex1.extra_fields), len(kardex2.extra_fields))]
    if (len(kardex1.extra_field_values) != len(kardex2.extra_field_values)):
        kardex_comparisons['Extra Field Values'] += \
            ['Deletion' for i in range(len(kardex2.extra_field_values), len(kardex1.extra_field_values))] \
            if len(kardex1.extra_field_values) > len(kardex2.extra_field_values) \
            else ['Addition' for i in range(len(kardex1.extra_field_values), len(kardex2.extra_field_values))]
    if (len(kardex1.label_markers) != len(kardex2.label_markers)):
        kardex_comparisons['Label Markers'] += \
            ['Deletion' for i in range(len(kardex2.label_markers), len(kardex1.label_markers))] \
            if len(kardex1.label_markers) > len(kardex2.label_markers) \
            else ['Addition' for i in range(len(kardex1.label_markers), len(kardex2.label_markers))]
    if (len(kardex1.label_values) != len(kardex2.label_values)):
        kardex_comparisons['Label Values'] += \
            ['Deletion' for i in range(len(kardex2.label_values), len(kardex1.label_values))] \
            if len(kardex1.label_values) > len(kardex2.label_values) \
            else ['Addition' for i in range(len(kardex1.label_values), len(kardex2.label_values))]
    return kardex_comparisons
