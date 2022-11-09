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
    print(timezone.now())
    kardexs = list(Kardex.objects.all()[:100])
    for kardex in kardexs:
        if kardex.name is None:
            kardex.formatted_name = ''
        else:
            kardex.formatted_name = f"{kardex.name.split().pop()}, {' '.join(kardex.name.split()[:-1])}"
    context = { 'kardexs': kardexs }

    return render(request, 'kardex_app/kardex/dashboard.html', context)

@login_required(login_url=login_URL)
def createKardex(request):
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

    nurse_on_duty = nurse.on_duty.split(',')[datetime.datetime.now().weekday()] \
        if nurse.on_duty and nurse.on_duty.split(',').length > 1 else '(Missing On Duty Schedule)'
    formatted_nurse_on_duty = '(Missing On Duty Schedule)'
    if 'Missing' not in nurse_on_duty:
        formatted_nurse_on_duty = map(lambda time: \
            f'{ time[:2] }:{ time[:-2] }AM' \
            if int(time) < 1300 \
            else f'{ int(time[:2]) - 12 }:{ time[:-2] }PM', \
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
    visiting_nurse = Nurse.objects.get(id=request.user.id)
    target_nurse = Nurse.objects.get(id=pk)

    form = NurseUpdateForm(instance=visiting_nurse)

    if(request.method == "POST"):
        form = NurseUpdateForm(request.POST, request.FILES, instance=visiting_nurse)
        if(form.is_valid()):
            form.save()
            return redirect(f'/profile/{pk}')

    nurse_on_duty = target_nurse.on_duty.split(',')[datetime.datetime.now().weekday()] \
        if target_nurse.on_duty and target_nurse.on_duty.split(',').length > 1 else '(Missing On Duty Schedule)'
    formatted_nurse_on_duty = '(Missing On Duty Schedule)'
    if 'Missing' not in nurse_on_duty:
        formatted_nurse_on_duty = map(lambda time: \
            f'{ time[:2] }:{ time[:-2] }AM' \
            if int(time) < 1300 \
            else f'{ int(time[:2]) - 12 }:{ time[:-2] }PM', \
            nurse_on_duty.split('-'))
        formatted_nurse_on_duty = f'{ formatted_nurse_on_duty[0] } - { formatted_nurse_on_duty[1] }'
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
    return render(request, 'kardex_app/nurse/nurse-dashboard.html', context)

def createNurse(request):
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
        print("THIS IS POST")
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
    return render(request, 'kardex_app/generate-reports/generate-reports.html')


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



def generate_front_1(work_book, style_head_row, style_data_row):
    ws_front1 = work_book.add_sheet(u'FRONT1')
    context_header = get_context_front()
    
    #Adjusts colum widths
    edit_col_width(ws_front1, 1, 15)
    edit_col_width(ws_front1, 2, 12)
    edit_col_width(ws_front1, 3, 12)

    START_COL = 0
    END_COL = 13
    START_ROW = 6
    current_row = START_ROW

    
    current_row = add_front_header(ws_front1,current_row,START_COL,END_COL)


    for context in context_header:
        current_row = add_section(ws_front1, current_row, START_COL, END_COL, context, style_head_row)
        current_row = add_data(ws_front1, context_header[context], current_row, END_COL, style_data_row)





def generate_front_2(work_book, style_head_row, style_data_row):
    ws_front2 = work_book.add_sheet(u'FRONT2')



def generate_front_3(work_book, style_head_row, style_data_row):
    ws_front2 = work_book.add_sheet(u'FRONT3')


def generate_back_1(work_book, style_head_row, style_data_row):
    ws_front2 = work_book.add_sheet(u'BACK1')

    context_header = get_context_back()
    
    #Adjusts colum widths
    edit_col_width(ws_front2, 1, 15)
    edit_col_width(ws_front2, 2, 12)
    edit_col_width(ws_front2, 3, 12)

    START_COL = 0
    END_COL = 13
    START_ROW = 0
    current_row = START_ROW

    
    current_row = add_front_header(ws_front2,current_row,START_COL,END_COL)


    for context in context_header:
        current_row = add_section(ws_front2, current_row, START_COL, END_COL, context, style_head_row)
        current_row = add_data(ws_front2, context_header[context], current_row, END_COL, style_data_row)




def generate_back_2(work_book, style_head_row, style_data_row):
    ws_front2 = work_book.add_sheet(u'BACK2')


def generate_back_3(work_book, style_head_row, style_data_row):
    ws_front2 = work_book.add_sheet(u'BACK3')


#Excel Utilities

def add_front_header(ws,current_row,START_COL,END_COL):
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

    ws.write(current_row,0, 'FOR THE 24 HRS ENDED MIDNIGHT OF')
    ws.write_merge(current_row,current_row,4,6, "07-SEP-22")
    ws.write(current_row,9, 'FLOOR/SECTION:')
    ws.write_merge(current_row,current_row,11,END_COL, "COVID")
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
        ws.write(current_row,0, kardex.id, style_data_row)
        ws.write(current_row,1, kardex.name, style_data_row)
        ws.write(current_row,2, kardex.age, style_data_row)
        ws.write_merge(current_row,current_row,3, 8, kardex.sex, style_data_row)
        ws.write_merge(current_row,current_row,9,END_COL, kardex.sex, style_data_row)
        current_row += 1 

    current_row += 1
    return current_row



def get_context_front():
    admission = Kardex.objects.all()
    discharges = Kardex.objects.all()
    death = Kardex.objects.all()

    context = {"ADMISSION": admission, "DISCHARGES": discharges, "DEATH":death}

    return context


def get_context_back():
    trans_in = Kardex.objects.all()
    trans_out = Kardex.objects.all()
    trans_other = Kardex.objects.all()

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
def generate_census_XLSX(request):
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

    generate_front_1(work_book, style_head_row, style_data_row)
    generate_back_1(work_book, style_head_row, style_data_row)
    generate_front_2(work_book, style_head_row, style_data_row)
    generate_back_2(work_book, style_head_row, style_data_row)
    generate_front_3(work_book, style_head_row, style_data_row)
    generate_back_3(work_book, style_head_row, style_data_row)
    
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
        all_kardex = Kardex.objects.all()
        serializers = KardexSerializer(all_kardex, many=True)
        return Response(serializers.data)

class PaginatedKardexList(APIView, LimitOffsetPagination):
    def get(self, request, format=None):
        relevant_kardex = Kardex.objects.all()

        target_nurse = request.GET.get('nurse', '')
        if target_nurse:
            relevant_kardex = relevant_kardex.filter(Q(edited_by__contains=[target_nurse]))

        target_name = request.GET.get('name', '')
        if target_name:
            relevant_kardex = relevant_kardex.filter(Q(name__icontains=target_name))

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
    query = request.data.get('query', '')

    if query:
        results = Kardex.objects.filter(Q(name__icontains=query))
        serializer = KardexSerializer(results, many=True)
        return Response(serializer.data)
    else:
        return Response({'Kardexs': []})

class NurseList(APIView):
    def get(self, request, format=None):
        all_nurse = Nurse.objects.all()
        serializers = NurseSerializer(all_nurse, many=True)
        return Response(serializers.data)

class PaginatedNurseList(APIView, LimitOffsetPagination):
    def get(self, request, format=None):
        all_nurse = Nurse.objects.all()
        results = self.paginate_queryset(all_nurse, request, view=self)
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

def formKardexComparisons(kardex1, kardex2):
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
