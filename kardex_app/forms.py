from django.forms import ModelForm, TextInput, PasswordInput, CharField, DateInput, IntegerField, DateTimeField, HiddenInput, NumberInput
from django.contrib.postgres.forms import SimpleArrayField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from datetime import datetime

from .models import *

User = get_user_model()

class KardexForm(ModelForm):
    class Meta:
        model = Kardex
        fields = "__all__"


class NurseCreationForm(UserCreationForm):
    attrs = { 'class': 'form-control', 'id':'floatingInput', 'placeholder':'Enter Password' , 'required': True, } 
    password1 =  CharField( widget=PasswordInput(attrs=attrs) )
    password2 =  CharField( widget=PasswordInput(attrs=attrs) )
    class Meta:
        model = Nurse
        fields = ['first_name', 'last_name', 'username', 'email', 'birthday', 'sex', 'ward', 'department', 'nurse_level', 'on_duty', 'picture', 'password1', 'password2']
        widgets = { 
            #insert bootstrap designs here
            'first_name': TextInput( attrs={ 'class': 'form-control', 'id':'firstNameInput', 'placeholder':'Enter First Name', 'required': True, } ),
            'last_name': TextInput( attrs={ 'class': 'form-control', 'id':'lastNameInput', 'placeholder':'Enter Last Name', 'required': True, } ),
            'username': TextInput( attrs={ 'class': 'form-control', 'id':'usernameInput' , 'placeholder':'Enter Username', 'required': True, } ),
            'email': TextInput( attrs={ 'type':'email', 'class': 'form-control', 'id':'emailInput', 'placeholder':'Enter Email Address', 'required': True, } ),
            'sex': TextInput( attrs={ 'class': 'form-control', 'id':'sexInput', 'placeholder':'Enter sex', 'required': False, } ),
            'birthday': DateInput( attrs={ 'class': 'form-control', 'id':'birthdayInput', 'placeholder':'Enter birthday', 'required': False, } ),
            'ward': TextInput( attrs={ 'class': 'form-control', 'id':'wardInput' , 'placeholder':'Enter Ward Name/s', 'required': True, } ),
            'department': TextInput( attrs={ 'class': 'form-control', 'id':'departmentInput' , 'placeholder':'Enter Department Name/s', 'required': True, } ),
            'nurse_level': TextInput( attrs={ 'class': 'form-control', 'id':'nurseLevelInput' , 'placeholder':'Enter Nurse Level', 'required': True, } ),
            'on_duty': TextInput( attrs={ 'class': 'form-control', 'id':'onDutyInput' , 'placeholder':'Enter time on duty for the entire week', 'required': True, } ),
            'password1': PasswordInput( attrs={ 'class': 'form-control', 'id':'passwordInput' , 'placeholder':'Enter Password', 'required': True, } ),
            'password2': PasswordInput( attrs={ 'class': 'form-control', 'id':'password2Input' , 'placeholder':'Enter Password (again)', 'required': True, } ),
        }


class NurseUpdateForm(ModelForm):
    class Meta:
        model = Nurse
        fields = ['username', 'email', 'first_name', 'last_name', 'email', 'sex', 'birthday', 'ward', 'department', 'on_duty', 'nurse_level', 'picture']
        widgets = {
            'username': TextInput( attrs={ 'class': 'form-control', 'id':'floatingInput', 'placeholder':'Enter Username', 'required': True, } ),
            'first_name': TextInput( attrs={ 'class': 'form-control', 'id':'floatingInput', 'placeholder':'Enter name', 'required': False, } ),
            'last_name': TextInput( attrs={ 'class': 'form-control', 'id':'floatingInput', 'placeholder':'Enter name', 'required': False, } ),
            'email': TextInput( attrs={ 'type':'email', 'class': 'form-control', 'id':'floatingInput', 'placeholder':'Enter Email Address', 'required': False, } ),
            'sex': TextInput( attrs={ 'class': 'form-control', 'id':'floatingInput', 'placeholder':'Enter sex', 'required': False, } ),
            'birthday': DateInput( attrs={ 'class': 'form-control', 'id':'floatingInput', 'placeholder':'Enter birthday', 'required': False, } ),
            'ward': TextInput( attrs={ 'class': 'form-control', 'id':'floatingInput' , 'placeholder':'Enter Ward Name', 'required': True, } ),
            'department': TextInput( attrs={ 'class': 'form-control', 'id':'floatingInput' , 'placeholder':'Enter Department Name', 'required': True, } ),
            'on_duty': TextInput( attrs={ 'class': 'form-control', 'id':'floatingInput' , 'placeholder':'Enter time on duty for the entire week in the format 0600-1800,0600-1800,...', 'required': True, } ),
            'nurse_level': TextInput( attrs={ 'class': 'form-control', 'id':'floatingInput' , 'placeholder':'Enter Nurse Level', 'required': True, } ),
        }