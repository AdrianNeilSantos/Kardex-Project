from django.forms import ModelForm, TextInput, PasswordInput, CharField, HiddenInput, NumberInput
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import get_user_model
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
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        widgets = { 
            #insert bootstrap designs here
            'first_name': TextInput( attrs={ 'class': 'form-control', 'id':'floatingInput', 'placeholder':'Enter First Name', 'required': True, } ),
            'last_name': TextInput( attrs={ 'class': 'form-control', 'id':'floatingInput', 'placeholder':'Enter Last Name', 'required': True, } ),
            'username': TextInput( attrs={ 'class': 'form-control', 'id':'floatingInput' , 'placeholder':'Enter Username', 'required': True, } ),
            'email': TextInput( attrs={ 'type':'email', 'class': 'form-control', 'id':'floatingInput', 'placeholder':'Enter Email Address', 'required': True, } ),
        }