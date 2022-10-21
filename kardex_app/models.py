from datetime import date
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class Kardex(models.Model):
    name_of_ward = models.CharField(max_length=255, null=True, blank=True)
    ivf = models.TextField(null=True, blank=True)
    laboratory_work_ups = models.TextField(null=True, blank=True)
    medications = models.TextField(null=True, blank=True)
    side_drip = models.TextField(null=True, blank=True)
    special_notations = models.TextField(null=True, blank=True)
    referrals = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    age = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MaxValueValidator(125),
            MinValueValidator(0)
        ]
    )
    sex = models.CharField(max_length=255, default='Male', null=True, blank=True)
    date_time = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    hospital_num = models.CharField(max_length=255, null=True, blank=True)
    dx = models.TextField(null=True, blank=True)
    drs = models.CharField(max_length=255, null=True, blank=True)
    diet = models.CharField(max_length=255, null=True, blank=True)
    extra_fields = ArrayField(
        models.CharField(max_length=255, null=True, blank=True),
        null=True,
        blank=True
    )
    extra_field_values = ArrayField(
        models.TextField(null=True, blank=True),
        null=True,
        blank=True
    )
    label_markers = ArrayField(
        models.CharField(max_length=255, null=True, blank=True),
        null=True,
        blank=True
    )
    label_values = ArrayField(
        models.CharField(max_length=255, null=True, blank=True),
        null=True,
        blank=True
    )
    date_added = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.patientName



# Create your models here.
class Nurse(AbstractUser):
    # blank: False = required
    birthday = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    sex = models.CharField(max_length=10, default='Male', null=True, blank=True)
    
    def __str__(self):
        return self.username



# class Kardex(models.Model):
#     patientName = models.CharField(max_length=50, null=True, blank=True)
#     sex = models.CharField(max_length=10, default='Male', null=True, blank=True)
#     age = models.IntegerField(
#         null=True,
#         validators=[
#             MaxValueValidator(100),
#             MinValueValidator(0)
#         ]
#     )
#     dateTime = models.DateTimeField(auto_now_add=False, null=True, blank=True)
#     hospitalNum = models.IntegerField(null=True)
#     bedNum = models.IntegerField(null=True)
#     doctorInCharge = models.CharField(max_length=50, null=True, blank=True)
#     hospitalName = models.CharField(max_length=50, null=True, blank=True)

#     def __str__(self):
#         return self.patientName



# # Create your models here.
# class Nurse(AbstractUser):
#     # blank: False = required
#     birthday = models.DateTimeField(auto_now_add=False, null=True, blank=True)
#     sex = models.CharField(max_length=10, default='Male', null=True, blank=True)
    
#     def __str__(self):
#         return self.username
