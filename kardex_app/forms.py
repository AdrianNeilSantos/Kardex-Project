from django.forms import ModelForm
from .models import *

class KardexForm(ModelForm):
    class Meta:
        model = Kardex
        fields = "__all__"