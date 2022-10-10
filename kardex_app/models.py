from datetime import date
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Kardex(models.Model):
    patientName = models.CharField(max_length=50, null=True, blank=True)
    sex = models.CharField(max_length=10, null=True, default='Male', blank=True)
    age = models.IntegerField(
        null=True,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ]
    )
    dateTime = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    hospitalNum = models.IntegerField(null=True)
    bedNum = models.IntegerField(null=True)
    doctorInCharge = models.CharField(max_length=50, null=True, blank=True)
    hospitalName = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.patientName